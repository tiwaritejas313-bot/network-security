
from network_security.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact
)
from network_security.entity.config_entity import DataValidationConfig
from network_security.exception.exception import NetworkSecurityException
from network_security.network_logger.logger import logging
from network_security.constants.trainingPipeline import SCHEMA_FILE_PATH
from network_security.utils.main_utils.utils import (
    read_yaml_file,
    write_yaml_file
)

import os
import sys
import pandas as pd
from scipy.stats import ks_2samp


class DataValidation:

    def __init__(
        self,
        data_ingestion_artifact: DataIngestionArtifact,
        data_validation_config: DataValidationConfig
    ):
        try:
            logging.info("Data validation started")

            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self.schema_config = read_yaml_file(SCHEMA_FILE_PATH)

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def validate_number_of_columns(
        self,
        dataframe: pd.DataFrame
    ) -> bool:
        try:
            schema = self.schema_config["columns"]
            number_of_columns = len(schema)

            logging.info(
                f"Required number of columns: {number_of_columns}"
            )
            logging.info(
                f"DataFrame number of columns: {len(dataframe.columns)}"
            )

            if len(dataframe.columns) == number_of_columns:
                logging.info("DataFrame has the required number of columns")
                return True

            logging.info(
                "DataFrame does not have the required number of columns"
            )
            return False

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def detect_dataset_drift(
        self,
        base_df: pd.DataFrame,
        current_df: pd.DataFrame,
        threshold: float = 0.05
    ) -> bool:
        try:
            status = True
            report = {}

            for column in base_df.columns:
                if column not in current_df.columns:
                    report[column] = {
                        "p_value": None,
                        "drift_status": True
                    }
                    status = False
                    continue

                d1 = base_df[column].dropna()
                d2 = current_df[column].dropna()

                statistics = ks_2samp(d1, d2)
                drift_detected = bool(statistics.pvalue < threshold)

                report[column] = {
                    "p_value": float(statistics.pvalue),
                    "drift_status": drift_detected
                }

                if drift_detected:
                    status = False

            drift_report_file_path = (
                self.data_validation_config.drift_report_file_path
            )

            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path, exist_ok=True)

            write_yaml_file(
                file_path=drift_report_file_path,
                content=report
            )

            return status

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            logging.info("Initiating data validation")

            train_file_path = (
                self.data_ingestion_artifact.trained_file_path
            )
            test_file_path = (
                self.data_ingestion_artifact.test_file_path
            )

            train_df = self.read_data(file_path=train_file_path)
            test_df = self.read_data(file_path=test_file_path)

            train_status = self.validate_number_of_columns(
                dataframe=train_df
            )
            test_status = self.validate_number_of_columns(
                dataframe=test_df
            )

            if not train_status or not test_status:
                raise Exception(
                    "Train or test DataFrame does not contain the "
                    "required number of columns."
                )

            # Check data drift
            drift_status = self.detect_dataset_drift(
                base_df=train_df,
                current_df=test_df
            )

            # Save validated train and test datasets
            dir_path = os.path.dirname(
                self.data_validation_config.valid_train_file_path
            )
            os.makedirs(dir_path, exist_ok=True)

            train_df.to_csv(
                self.data_validation_config.valid_train_file_path,
                index=False,
                header=True
            )

            test_df.to_csv(
                self.data_validation_config.valid_test_file_path,
                index=False,
                header=True
            )

            data_validation_artifact = DataValidationArtifact(
                valid_train_file_path=(
                    self.data_validation_config.valid_train_file_path
                ),
                valid_test_file_path=(
                    self.data_validation_config.valid_test_file_path
                ),
                invalid_train_file_path=(
                    self.data_validation_config.invalid_train_file_path
                ),
                invalid_test_file_path=(
                    self.data_validation_config.invalid_test_file_path
                ),
                drift_report_file_path=(
                    self.data_validation_config.drift_report_file_path
                ),
                validation_status=drift_status
            )

            logging.info("Data validation completed")
            return data_validation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
