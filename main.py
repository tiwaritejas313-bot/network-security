from network_security.components.data_ingestion import DataIngestion
from network_security.entity.config_entity import DataIngestionConfig
from network_security.entity.config_entity import TrainingPipelineConfig
from network_security.network_logger.logger import logging
from network_security.exception.exception import NetworkSecurityException
from network_security.components.data_validation import DataValidation
from network_security.entity.config_entity import DataValidationConfig
from network_security.components.data_transformation import DataTransformation
from network_security.entity.config_entity import DataTransformationConfig
import os
import sys

if __name__ == "__main__":
    try:
        training_pipeline_config=TrainingPipelineConfig()
        data_ingestion_config=DataIngestionConfig(training_pipeline_config)
        logging.info("Initiating data ingestion")
        data_ingestion=DataIngestion(data_ingestion_config)
        dataIngestionartifact=data_ingestion.initiate_data_ingestion()
        logging.info("Initiation of data ingestion completed")
        print(dataIngestionartifact)
        data_validation_config = DataValidationConfig(training_pipeline_config)
        data_validation = DataValidation(
    data_ingestion_artifact=dataIngestionartifact,
    data_validation_config=data_validation_config
)
        logging.info("Inititate data validation")
        data_validation_artifact=data_validation.initiate_data_validation()
        logging.info("Initiation of data validation completed")
        print(data_validation_artifact)
        data_transformation_config=DataTransformationConfig(training_pipeline_config)
        data_transformation=DataTransformation(data_validation_artifact=data_validation_artifact,data_transformation_config=data_transformation_config)
        logging.info("Initiating data transformation")
        data_transformation_artifact=data_transformation.initiate_data_transformation()
        logging.info("Initiation of data transformation completed")
        print(data_transformation_artifact)
    except Exception as e:
        raise NetworkSecurityException(e, sys)