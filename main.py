from datetime import datetime
from email import header
from fastapi import FastAPI, Request
from pydantic import BaseModel
from playsound import playsound
import config
import hashlib
import hmac
import httpx
import json
import math
import pytz
import random
import time

app = FastAPI()
api_key = config.API_KEY
content_type = "application/json"

class VappWebhook(BaseModel):
    version: str
    tenant: str
    networkID: str
    deviceID: str
    type: str
    ts: int
    data: dict

def generate_hmac(req_method, req_uri, content_md5 = ""):
    date_time = datetime.now(pytz.utc)
    timestamp = math.floor(date_time.timestamp())
    header_time = date_time.strftime("%a, %d %b %Y %H:%M:%S GMT")
    nonce = random.randint(2000, 65000)

    if (content_md5 != ""):        
        hmac_input = f"{req_method}:{req_uri}:{content_md5}:{content_type}:{timestamp}:{nonce}"
    else:
        hmac_input = f"{req_method}:{req_uri}:{timestamp}:{nonce}"

    hmac_output = hmac.new(key=api_key.encode('utf-8'), msg=hmac_input.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    
    hmac_dict = {
        "header_time": header_time,
        "hmac_output": hmac_output,
        "nonce": nonce
    }

    return hmac_dict


@app.get("/")
def read_root():    
    return {"Hello": "World"}


@app.post("/vapp")
def vapp(payload: VappWebhook):
    # payload_dict = payload.dict() 
    # print (f"payload_dict: {payload.data}")
    
    if (payload.type == "area"):
        start_strobe("blue")
        start_tone("area-counting.wav")
        playsound("area-counting.wav")        
        time.sleep(3)
        stop_strobe()        
        print (f"There are {payload.data['presence_thr']} person stay at water dispenser area for {payload.data['presence_time']} seconds.")
        # print (payload.data)
    elif (payload.type == "occupancy"):
        print (f"There are {payload.data['occupancy']} person trigger occupancy alert.")
    elif (payload.type == "presence"):
        print (f"There are {payload.data['people']} person trigger presence alert.")
    elif (payload.type == "social"):
        start_strobe("red")
        start_tone("social-distancing.wav")
        playsound("social-distancing.wav")
        time.sleep(3)
        stop_strobe()        
        print (f"There are {payload.data['people']} person trigger social distancing alert.")
    
    return payload


@app.get("/strobe/start")
def start_strobe(color1="red"):
    request_method = "POST"
    target = config.STROBE_IP
    request_uri = "/api/controls/strobe/start"    
    strobe_settings = {
        "pattern": "3",
        "color1": color1,
        "color2": "blue",
        "ledlvl": "55",
        "holdover": False
    }    

    content_md5 = hashlib.md5(json.dumps(strobe_settings).encode('utf-8')).hexdigest()

    hmac_dict = generate_hmac(request_method, request_uri, content_md5)

    headers = {
        "Content-Type": content_type,
        "Content-MD5": content_md5,
        "Authorization": f"hmac admin:{hmac_dict['nonce']}:{hmac_dict['hmac_output']}",
        "Date": hmac_dict['header_time']
    }

    response = httpx.post(f"http://{target}{request_uri}", headers=headers, json=strobe_settings)
    # return f"Response status code: {response.status_code} and input: {hmac_input} and output: {hmac_output} and headers: {headers}"
    return f"Response status code: {response.status_code}"


@app.get("/strobe/stop")
def stop_strobe():
    request_method = "POST"
    target = config.STROBE_IP
    request_uri = "/api/controls/strobe/stop"

    hmac_dict = generate_hmac(request_method, request_uri)

    headers = {
        "Authorization": f"hmac admin:{hmac_dict['nonce']}:{hmac_dict['hmac_output']}",
        "Date": hmac_dict['header_time']
    }

    response = httpx.post(f"http://{target}{request_uri}", headers=headers)
    # return f"Response status code: {response.status_code} and input: {hmac_input} and output: {hmac_output} and headers: {headers}"
    return f"Response status code: {response.status_code}"


@app.get("/tone/start")
def start_tone(path="social-distancing.wav"):
    request_method = "POST"

    target = config.TONE_IP
    request_uri = "/api/controls/tone/start"    
    tone_settings = {
        "path": path,
        "loop": False
    }    

    content_md5 = hashlib.md5(json.dumps(tone_settings).encode('utf-8')).hexdigest()

    hmac_dict = generate_hmac(request_method, request_uri, content_md5)

    headers = {
        "Content-Type": content_type,
        "Content-MD5": content_md5,
        "Authorization": f"hmac admin:{hmac_dict['nonce']}:{hmac_dict['hmac_output']}",
        "Date": hmac_dict['header_time']
    }

    response = httpx.post(f"http://{target}{request_uri}", headers=headers, json=tone_settings)
    # return f"Response status code: {response.status_code} and input: {hmac_input} and output: {hmac_output} and headers: {headers}"
    return f"Response status code: {response.status_code}"


@app.get("/tone/stop")
def stop_tone():
    request_method = "POST"
    target = config.TONE_IP
    request_uri = "/api/controls/tone/stop"

    hmac_dict = generate_hmac(request_method, request_uri)

    headers = {
        "Authorization": f"hmac admin:{hmac_dict['nonce']}:{hmac_dict['hmac_output']}",
        "Date": hmac_dict['header_time']
    }

    response = httpx.post(f"http://{target}{request_uri}", headers=headers)
    # return f"Response status code: {response.status_code} and input: {hmac_input} and output: {hmac_output} and headers: {headers}"
    return f"Response status code: {response.status_code}"