import requests
from datetime import datetime
import sqlite3

#weather cred
api = "05d3b05f0bcd4116aa9110249252205"
URL = f"http://api.worldweatheronline.com/premium/v1/weather.ashx"


def instance():
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    return {"Date":date_str,"time":time_str}
    
def db_cv(db_path="detections_yolov5.db"):
    """Fetch and print the last detection entry from the SQLite database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get the last inserted row (based on rowid)
        cursor.execute("SELECT * FROM detections ORDER BY rowid DESC LIMIT 1")
        row = cursor.fetchone()

        if row:
            frame_id, timestamp, label, confidence, x, y, w, h = row
            age = 32
            #return {"gender":"male","age":32,"conf":0.82}
            result= {"age":age,"gender": label,"conf": confidence}
            print(result)
            return {
                "age":age,
                "gender": label,
                "conf": confidence,
            }
        else:
            return None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()
    
    

def getweather(CITY):
    params = {
    "key": api,
    "q": CITY,
    "format": "json",
    "num_of_days": 0,
    "cc": "yes"  # current conditions
}
    response = requests.get(URL, params=params)
    data = response.json()

    # Extract current weather
    current = data['data']['current_condition'][0]
    temp_C = current['temp_C']
    weather_desc = current['weatherDesc'][0]['value']
    Temp_in_c= str(temp_C),
    weather = weather_desc
    print(f"🌡️ Temperature: {temp_C}°C")
    print(f"🌤️ Weather: {weather_desc}")

    return {"Temp":Temp_in_c,
            "Weather":weather}