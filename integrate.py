
import os
import os.path
import numpy as np
from fastapi import FastAPI, File,  HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import datetime
from datetime import date
import logging
from logging.handlers import TimedRotatingFileHandler
import requests
from datetime import datetime
from utils import getweather, db_cv, instance, db_mongo
from pydantic import BaseModel
import pandas as pd


app = FastAPI()
origins = [
    "http://localhost", "http:localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


df = pd.read_csv("adv_map.csv")

# Input model
class UserInput(BaseModel):
    age: int
    emotion: str
    gender: str
    temp: int
    weather: str

logpath = datetime.now().strftime("%Y-%m-%d") + ".log"
print(logpath)
log_file = os.path.join("enrichlogs", logpath)
handler = TimedRotatingFileHandler(filename=log_file,
                                   when="midnight",
                                   interval=1,
                                   backupCount=31)
formater = logging.Formatter("%(asctime)s %(thread)s | %(levelname)s | %(message)s",
                             datefmt="%Y-%m-%d %H:%M:%S")
handler.setFormatter(formater)
handler.setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.INFO)
logging.getLogger().addHandler(handler)
logging.info("log initiated")


@app.get("/ping")  # to test ping on api
async def ping():
    logging.info("API is active")
    return "Hello, I am alive"

@app.get("/logdaterange")
async def logdaterange(
        start: date = Query(default=None, example="2024-02-22"), end: date = Query(default=None, example="2024-02-22")):
    if date is None:
        return "Date parameter is required", 400
    log_lines = []
    current_date = start
    while current_date <= end:
        log_file_path = f'enrichlogs/{(current_date)}.log'
        try:
            with open(log_file_path, 'r') as file:
                log_lines.extend(file.readlines())
        except FileNotFoundError:
            print(f"File {log_file_path} not found.")
            logging.warning("No log for this day")
        current_date += datetime.timedelta(days=1)
    return log_lines


@app.post("/adv_predict")
async def adv_predict():
    try:
        time_date=instance()
        #cv_results=db_cv()
        cv_results=db_mongo()
        weather_serv = getweather("Mumbai")
        combined_result = {**time_date, **cv_results, **weather_serv}
        print("combined_result",combined_result)
        return combined_result 
    
    except Exception as e:
        logging.exception(e)
        #for default handling
        return {
            'Date': "",
            'time': "",
            'gender': "default",
            'mood': "",
            'conf': "",
            'Temp': "",
            'weather': ""
         }


@app.post("/recommend")
def recommend_video(user: UserInput):
    # Filter DataFrame
    mask = (
        (df["age"] == user.age) &
        #(df["emotion"] == user.emotion) &
        (df["gender"] == user.gender) &
        (df["temp"] == user.temp) &
        (df["weather"] == user.weather)
    )
    results = df[mask]

    if not results.empty:
        links = results["adv_link"].unique().tolist()
        return {"status": "success", "recommended_links": links}
    else:
        return {"status": "no_match", "message": "No exact match found."}

@app.post("/integ_recommend")
def intrg_recommend_video(user: UserInput):
    try:
            time_date=instance()
            cv_results=db_mongo()
            print("cv_results - ",cv_results)
            weather_serv = getweather("Mumbai")
            combined_result = { **cv_results, **weather_serv}
            # Filter DataFrame
            age = cv_results["age"]
            emotion = "happy" #combined_result["mood"]
            gender = cv_results["gender"]
            temp = weather_serv["Temp"]
            weather = weather_serv["Weather"]
            print("temp - ",temp)
            print("weather - ",weather)
            print("combined_result - ",combined_result)

            mask = (
                (df["age"] == age) &
                (df["emotion"] == emotion) &
                (df["gender"] == gender) &
                (df["temp"] == temp) &
                (df["weather"] == weather)
            )
            
            results = df[mask]
            if not results.empty:
                links = results["adv_link"].unique().tolist()
                return {"status": "success","inst":time_date, "param":combined_result ,"recommended_links": links[0]}
            else:
                return {"status": "no_match", "message": "No exact match found."}

    
    except Exception as e:
        logging.exception(e)
        #for default handling
        return {
            'Date': "",
            'time': "",
            'gender': "default",
            'mood': "",
            'conf': "",
            'Temp': "",
            'weather': ""
        }

    


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)


