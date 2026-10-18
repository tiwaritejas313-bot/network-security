
import os
import sys
import json
import certifi
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient

from network_security.network_logger.logger import logging
from network_security.exception.exception import NetworkSecurityException

load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")


class NetworkDataExtract:
    def __init__(self):
        try:
            self.mongo_client = None
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def csv_to_json(self, file_path):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)
            records = list(json.loads(data.T.to_json()).values())
            return records
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def insert_data_toMongo(self, records, database, collections):
        try:
            if not MONGO_DB_URL:
                raise ValueError("MONGO_DB_URL is missing from the .env file")

            self.mongo_client = MongoClient(
                MONGO_DB_URL,
                tlsCAFile=certifi.where()
            )

            self.database = self.mongo_client[database]
            self.collection = self.database[collections]

            self.collection.insert_many(records)
            return len(records)

        except Exception as e:
            raise NetworkSecurityException(e, sys)

        finally:
            if self.mongo_client is not None:
                self.mongo_client.close()


if __name__ == "__main__":
    FILE_PATH = "network_data/phishingdata.csv"
    DATABASE = "network_security"
    COLLECTIONS = "phishing_data"

    network_dataextract = NetworkDataExtract()

    records = network_dataextract.csv_to_json(FILE_PATH)
    print(f"Number of records: {len(records)}")

    inserted_count = network_dataextract.insert_data_toMongo(
        records, DATABASE, COLLECTIONS
    )

    print(f"Number of records inserted: {inserted_count}")
