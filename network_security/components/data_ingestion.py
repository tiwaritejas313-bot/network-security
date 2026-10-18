import os
import sys
import pandas as pd
import numpy as np
import json
from network_security.exception.exception import NetworkSecurityException
from network_security.network_logger.logger import logging
from network_security.entity.config_entity import DataIngestionConfig
import pymongo
from typing import List
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv
from network_security.entity.artifact_entity import DataIngestionArtifact
load_dotenv()
MONGO_DB_URL=os.getenv("MONGO_DB_URL")

class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
            self.mongo_client=None
            self.database=None
            self.collection=None
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_collection_as_dataframe(self):
        try:
          database_name=self.data_ingestion_config.database_name
          collection_name=self.data_ingestion_config.collection_name
          self.mongo_client=pymongo.MongoClient(MONGO_DB_URL)
          self.database=self.mongo_client[database_name]
          self.collection=self.database[collection_name]
          data = list(self.collection.find())
          df = pd.DataFrame(data)
          if "_id"in df.columns.to_list():
            df=df.drop("_id",axis=1)

          return df
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def export_data_into_feature_store(self,dataframe:pd.DataFrame):
      try:
        feature_store_file_path=self.data_ingestion_config.feature_store_file_path
        #creating folder
        dir_name=os.path.dirname(feature_store_file_path)
        os.makedirs(dir_name,exist_ok=True)

        dataframe.to_csv(feature_store_file_path,index=False,header=True)
        logging.info(f"Data exported to feature store: {feature_store_file_path}")
        return dataframe

      except Exception as e:
        raise NetworkSecurityException(e, sys)
    
    def split_data_as_train_test(self,dataframe:pd.DataFrame):
        try:
            train_set,test_set=train_test_split(
                dataframe,
                test_size=self.data_ingestion_config.train_test_split_ratio,
                random_state=42
            )
            logging.info("performed train test split")
            logging.info("exited split_data_as_train_test method")
            dir_path=os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path,exist_ok=True)
            logging.info("Exporting train and test file path")
            train_set.to_csv(self.data_ingestion_config.training_file_path,index=False,header=True)
            test_set.to_csv(self.data_ingestion_config.testing_file_path,index=False,header=True)
            logging.info("Exported train and test file path")
            return train_set,test_set
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_ingestion(self) :
        try:
            logging.info("Initiating data ingestion")
            dataframe=self.export_collection_as_dataframe()
            dataframe=self.export_data_into_feature_store(dataframe)
            train_set,test_set=self.split_data_as_train_test(dataframe)
            dataIngestion_artifact=DataIngestionArtifact(
                self.data_ingestion_config.training_file_path,
                self.data_ingestion_config.testing_file_path
            )
            logging.info("Initiating data ingestion")
            return dataIngestion_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)