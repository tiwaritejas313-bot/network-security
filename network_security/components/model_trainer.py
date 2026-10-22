
import os
import sys
import mlflow



from network_security.exception.exception import NetworkSecurityException
from network_security.network_logger.logger import logging

from network_security.entity.artifact_entity import (
    DataTransformationArtifact,
    ModelTrainerArtifact
)

from network_security.entity.config_entity import ModelTrainerConfig

from network_security.utils.main_utils.utils import (
    save_object,
    load_object,
    load_numpy_array_data,
    evaluate_model
)

from network_security.utils.ml_utils.metric.classification_metric import (
    get_classification_score
)

from network_security.utils.ml_utils.model.estimator import ModelEstimator

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    AdaBoostClassifier,
    GradientBoostingClassifier
)
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC

import dagshub
dagshub.init(repo_owner='tiwaritejas313-bot', repo_name='network-security', mlflow=True)

class ModelTrainer:

    def __init__(
        self,
        model_trainer_config: ModelTrainerConfig,
        data_transformation_artifact: DataTransformationArtifact
    ):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def track_mlflow(self,best_model,classification_metric):
        try:
            with mlflow.start_run():
                f1_score=classification_metric.f1_score
                precision_score=classification_metric.precision_score
                recall_score=classification_metric.recall_score
                accuracy_score=classification_metric.accuracy_score
                mlflow.log_metric("f1_score",f1_score)
                mlflow.log_metric("precision_score",precision_score)
                mlflow.log_metric("recall_score",recall_score)
                mlflow.log_metric("accuracy_score",accuracy_score)
                
                mlflow.sklearn.log_model(
                    sk_model=best_model,
                    artifact_path="model",
                    skops_trusted_types=["sklearn.tree._tree.Tree"]
                )

                
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def train_model(self, X_train, y_train, X_test, y_test):
        try:
            models = {
                "LogisticRegression": LogisticRegression(max_iter=2000),
                "KNeighborsClassifier": KNeighborsClassifier(),
                "RandomForestClassifier": RandomForestClassifier(),
                "AdaBoostClassifier": AdaBoostClassifier(),
                "GradientBoostingClassifier": GradientBoostingClassifier(),
                "DecisionTreeClassifier": DecisionTreeClassifier(),
                
                "SVC": SVC()
            }

            params = {
                "LogisticRegression": [
                    {
                        "penalty": ["l1", "l2"],
                        "C": [0.1, 1, 10],
                        "solver": ["liblinear"]
                    },
                    {
                        "penalty": ["elasticnet"],
                        "C": [0.1, 1, 10],
                        "solver": ["saga"],
                        "l1_ratio": [0.5]
                    }
                ],

                "KNeighborsClassifier": {
                    "n_neighbors": [3, 5, 7],
                    "weights": ["uniform", "distance"],
                    "metric": ["minkowski", "euclidean"]
                },

                "RandomForestClassifier": {
                    "n_estimators": [8, 16, 32, 64],
                    "criterion": ["gini", "entropy"]
                },

                "AdaBoostClassifier": {
                    "n_estimators": [8, 16, 32, 64],
                    "learning_rate": [0.1, 0.5, 1.0]
                },

                "GradientBoostingClassifier": {
                    "n_estimators": [8, 16, 32, 64],
                    "learning_rate": [0.1, 0.05, 0.01],
                    "subsample": [0.7, 0.8, 1.0]
                },

                "DecisionTreeClassifier": {
                    "criterion": ["gini", "entropy", "log_loss"]
                },

                "SVC": {
                    "C": [0.1, 1, 10],
                    "kernel": ["linear", "rbf"],
                    "gamma": ["scale", "auto"]
                }
            }

            # Evaluate candidate models
            model_report = evaluate_model(
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
                models=models,
                params=params
            )

            logging.info(f"Model report: {model_report}")

            # Select best model based on evaluation score
            best_model_score = max(model_report.values())

            best_model_name = list(model_report.keys())[
                list(model_report.values()).index(best_model_score)
            ]

            logging.info(f"Best model name: {best_model_name}")
            logging.info(f"Best model score: {best_model_score}")

            # Get selected fitted model
            best_model = models[best_model_name]

            logging.info("Model training completed")

            # Predictions
            y_train_pred = best_model.predict(X_train)
            y_test_pred = best_model.predict(X_test)

            # Classification metrics
            classification_train_metric = get_classification_score(
                y_true=y_train,
                y_pred=y_train_pred
            )
            self.track_mlflow(best_model,classification_train_metric)

            classification_test_metric = get_classification_score(
                y_true=y_test,
                y_pred=y_test_pred
            )
            self.track_mlflow(best_model,classification_test_metric)

            # Load preprocessor
            preprocessor = load_object(
                file_path=self.data_transformation_artifact
                .transformed_object_file_path
            )

            # Create model directory
            model_dir_path = os.path.dirname(
                self.model_trainer_config.trained_model_file_path
            )

            os.makedirs(model_dir_path, exist_ok=True)

            # Create final model estimator
            network_model = ModelEstimator(
                preprocessor=preprocessor,
                model=best_model
            )

            # Save trained model
            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=network_model
            )
            save_object("final_model/model.pkl",best_model)

            # Model trainer artifact
            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=(
                    self.model_trainer_config.trained_model_file_path
                ),
                train_metric_artifact=classification_train_metric,
                test_metric_artifact=classification_test_metric
            )

            logging.info(
                f"Model trainer artifact: {model_trainer_artifact}"
            )

            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            logging.info("Initiating model training")
            logging.info("Loading train and test data")

            train_file_path = (
                self.data_transformation_artifact.transformed_train_file_path
            )

            test_file_path = (
                self.data_transformation_artifact.transformed_test_file_path
            )

            # Load training and testing NPY arrays
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)

            logging.info("Train and test data loaded")

            # Split features and target
            X_train, y_train = train_arr[:, :-1], train_arr[:, -1]
            X_test, y_test = test_arr[:, :-1], test_arr[:, -1]

            # Train and evaluate models
            model_trainer_artifact = self.train_model(
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test
            )

            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
