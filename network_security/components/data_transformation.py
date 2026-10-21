
import sys
import os
import pandas as pd
import numpy as np

from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline

from network_security.constants.trainingPipeline import (
    TARGET_COLOUMN,
    DATA_TRANSFORMATION_IMPUTER_PARAMS
)

from network_security.network_logger.logger import logging
from network_security.exception.exception import NetworkSecurityException

from network_security.entity.config_entity import DataTransformationConfig

from network_security.entity.artifact_entity import (
    DataTransformationArtifact,
    DataValidationArtifact
)

from network_security.utils.main_utils.utils import (
    save_numpy_array_data,
    save_object
)


class DataTransformation:

    def __init__(
        self,
        data_validation_artifact: DataValidationArtifact,
        data_transformation_config: DataTransformationConfig
    ):
        try:
            self.data_validation_artifact = data_validation_artifact
            self.data_transformation_config = data_transformation_config

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            logging.info(f"Reading data from {file_path}")

            df = pd.read_csv(file_path)

            return df

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    @staticmethod
    def get_data_transformer_object() -> Pipeline:
        try:
            imputer = KNNImputer(
                **DATA_TRANSFORMATION_IMPUTER_PARAMS
            )

            logging.info("Data transformer object created")

            processor = Pipeline([
                ("imputer", imputer)
            ])

            return processor

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def initiate_data_transformation(self) -> DataTransformationArtifact:
        try:
            logging.info("Initiating data transformation")

            # STEP 1: Read validated datasets
            train_df = self.read_data(
                self.data_validation_artifact.valid_train_file_path
            )

            test_df = self.read_data(
                self.data_validation_artifact.valid_test_file_path
            )

            # STEP 2: Separate training features and target
            input_feature_train_df = train_df.drop(
                columns=[TARGET_COLOUMN]
            )

            target_feature_train_df = train_df[TARGET_COLOUMN]

            target_feature_train_df = target_feature_train_df.replace(
                -1, 0
            )

            # STEP 3: Separate testing features and target
            input_feature_test_df = test_df.drop(
                columns=[TARGET_COLOUMN]
            )

            target_feature_test_df = test_df[TARGET_COLOUMN]

            target_feature_test_df = target_feature_test_df.replace(
                -1, 0
            )

            # STEP 4: Create the preprocessing pipeline
            preprocessor = self.get_data_transformer_object()

            # STEP 5: Fit only on training data
            preprocessor_object = preprocessor.fit(
                input_feature_train_df
            )

            # STEP 6: Transform training and testing features
            transformed_input_train_feature_array = (
                preprocessor_object.transform(
                    input_feature_train_df
                )
            )

            transformed_input_test_feature_array = (
                preprocessor_object.transform(
                    input_feature_test_df
                )
            )

            # STEP 7: Combine features and target
            train_arr = np.c_[
                transformed_input_train_feature_array,
                np.array(target_feature_train_df)
            ]

            test_arr = np.c_[
                transformed_input_test_feature_array,
                np.array(target_feature_test_df)
            ]

            # STEP 8: Save transformed arrays
            save_numpy_array_data(
                self.data_transformation_config.transformed_train_file_path,
                array=train_arr
            )

            save_numpy_array_data(
                self.data_transformation_config.transformed_test_file_path,
                array=test_arr
            )

            # STEP 9: Save the fitted preprocessing object
            save_object(
                self.data_transformation_config.preprocessor_object_path,
                preprocessor_object
            )

            # STEP 10: Create transformation artifact
            data_transformation_artifact = DataTransformationArtifact(
                transformed_train_file_path=(
                    self.data_transformation_config.transformed_train_file_path
                ),
                transformed_test_file_path=(
                    self.data_transformation_config.transformed_test_file_path
                ),
                transformed_object_file_path=(
                    self.data_transformation_config.preprocessor_object_path
                )
            )

            logging.info("Data transformation completed")

            return data_transformation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
