import yaml
import dill
import os,sys
import pickle
import numpy as np
import pandas as pd
from network_security.exception.exception import NetworkSecurityException
from network_security.network_logger.logger import logging

def read_yaml_file(file_path:str)->dict:
     try:
         with open(file_path,"rb") as yaml_file:
             return yaml.safe_load(yaml_file)
     except Exception as e:
         raise NetworkSecurityException(e, sys) from e
    
def write_yaml_file(file_path:str,content:object,replace:bool=False):
     try:
        if replace:
           if os.path.exists(file_path):
               os.remove(file_path)

        os.makedirs(os.path.dirname(file_path),exist_ok=True)
        with open(file_path,"w") as yaml_file:
            yaml.dump(content,yaml_file)
     except Exception as e:
         raise NetworkSecurityException(e, sys) from e


def save_numpy_array_data(file_path:str,array:np.array):
    try:
        dir_path=os.path.dirname(file_path)
        os.makedirs(dir_path,exist_ok=True)
        with open(file_path,"wb") as file_obj:
            np.save(file_obj,array)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e


def save_object(file_path:str,obj:object):
    try:
        os.makedirs(os.path.dirname(file_path),exist_ok=True)
        with open(file_path,"wb") as file_obj:
            pickle.dump(obj,file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e