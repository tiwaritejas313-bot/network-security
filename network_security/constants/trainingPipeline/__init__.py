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

DATA_INGESTION_COLLECTION_NAME:str="phishing_data"
DATA_INGESTION_DATABASE_NAME:str="network_security"
DATA_INGESTION_DIR_NAME:str="data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR:str="feature_store"
DATA_INGESTION_INGESTED_DIR:str="ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO:float=0.2
