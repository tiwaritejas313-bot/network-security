import sys
from network_security.constants.trainingPipeline import SAVED_MODEL_DIR,MODEL_FILE_NAME
from network_security.exception.exception import NetworkSecurityException
from network_security.network_logger.logger import logging
from network_security.utils.main_utils.utils import load_object

class ModelEstimator:
    def __init__(self,preprocessor,model):
        try:
            self.preprocessor=preprocessor
            self.model=model
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def predict(self,x):
        try:
            logging.info("Prediction started")
            x_transform=self.preprocessor.transform(x)
            y_hat=self.model.predict(x_transform)

            logging.info("Prediction completed")
            return y_hat
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
  
    
