import os
import sys
import pandas as pd
import numpy as np

TARGET_COLOUMN:str="Result"
PIPELINE_NAME:str="network_security"
PIPELINE_ARTIFACTS:str="ARTIFACTS"
FILE_NAME:str="phishingdata.csv"
TRAIN_FILE_NAME:str="train.csv"
TEST_FILE_NAME:str="test.csv"

SCHEMA_FILE_PATH=os.path.join("data_schema","schema.yaml")

DATA_INGESTION_COLLECTION_NAME:str="phishing_data"
DATA_INGESTION_DATABASE_NAME:str="network_security"
DATA_INGESTION_DIR_NAME:str="data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR:str="feature_store"
DATA_INGESTION_INGESTED_DIR:str="ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO:float=0.2

"""
DATA VALIDATION DIR
"""
DATA_VALIDATION_DIR_NAME:str="data_validation"
DATA_VALIDATION_STATUS_FILE_NAME:str="report.yaml"
DATA_VALIDATION_VALID_DIR:str="validated"
DATA_VALIDATION_INVALID_DIR:str="invalid"
DATA_VALIDATION_DRIFT_REPORT_DIR:str="drift_report"

DATA_VALIDATION_VALID_TRAIN_FILE_NAME: str = "train.csv"
DATA_VALIDATION_VALID_TEST_FILE_NAME: str = "test.csv"

DATA_VALIDATION_INVALID_TRAIN_FILE_NAME: str = "train.csv"
DATA_VALIDATION_INVALID_TEST_FILE_NAME: str = "test.csv"

DATA_VALIDATION_DRIFT_REPORT_FILE_NAME: str = "drift_report.yaml"
PREPROCESSING_OBJECT_FILE_NAME:str="preprocesssing.pkl"

""" DATA TRANSFORMATION INFO"""
DATA_TRANSFORMATION_DIR_NAME:str="data_transformation"
DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR:str="transformed"
DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR:str="transformed object"
DATA_TRANSFORMATION_PREPROCESSOR_DIR:str="preprocessor"
DATA_TRANSFORMATION_PREPROCESSOR_OBJECT__FILE_NAME:str="preprocessor.pkl"

###knn imputer
DATA_TRANSFORMATION_IMPUTER_PARAMS:dict={
    "missing_values":np.nan,
    "weights":"uniform",
    "n_neighbors":3,
}