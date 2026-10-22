import os,sys
import certifi
import pymongo
import uvicorn
from fastapi import FastAPI,File,UploadFile,Request
from sklearn.preprocessing import LabelEncoder
from network_security.exception.exception import NetworkSecurityException
from network_security.network_logger.logger import logging
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse
import pandas as pd
from network_security.utils.main_utils.utils import load_object
from network_security.utils.ml_utils.model.estimator import ModelEstimator
from network_security.constants.trainingPipeline import DATA_INGESTION_DATABASE_NAME,DATA_INGESTION_COLLECTION_NAME



ca=certifi.where()
from dotenv import load_dotenv
load_dotenv()
from network_security.pipeline.training_pipeline import TrainingPipeline
mongo_db_url=os.getenv("mongoDB_url_key")
print(mongo_db_url)
client=pymongo.MongoClient(mongo_db_url,tlsCAFile=ca)
database=client[DATA_INGESTION_DATABASE_NAME]
collection=client[DATA_INGESTION_COLLECTION_NAME]

app=FastAPI()
origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from fastapi.templating import Jinja2Templates
templates=Jinja2Templates(directory="./templates")
@app.get("/",tags=["authentication"])
async def root():
    return RedirectResponse(url="/docs")

@app.get("/train")
async def train_route():
    try:
        training_pipeline=TrainingPipeline()
        training_pipeline.run_pipeline()
        return {"message": "Training completed successfully"}
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e

@app.post("/predict",tags=["prediction"])
async def predict(request:Request,file: UploadFile=File(...)):
    
    try:
        
        df = pd.read_csv(file.file)
        df.columns = df.columns.str.strip().str.lower()
        df.columns = df.columns.str.replace("registeration", "registration")
        df.columns = df.columns.str.replace("popupwidnow", "popupwindow")
        preprocessor=load_object("final_model/preprocessing.pkl")
        final_model=load_object("final_model/model.pkl")
        network_model=ModelEstimator(preprocessor=preprocessor,model=final_model)
        print(df.iloc[0])
        y_pred=network_model.predict(df)
        print(y_pred)
        df['predicted_column']=y_pred
        print(df['predicted_column'])
        df.to_csv("prediction_output/output.csv")
        table_html=df.to_html(classes='table table-striped')

        
        return templates.TemplateResponse(
            request=request,
            name="table.html",
            context={"table": table_html}
        )
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e



if __name__=="__main__":
    app_run(app,host="localhost",port=8234)
    