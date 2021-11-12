import requests
import sys
import cv2
import base64
from concurrent.futures import ThreadPoolExecutor

sys.path.append("..")

from config.config import ALARM_SERVER_URL, KEY_FORMAT

def send(**message):
    # message:
    # sn
    # algorithm_id
    # timestamp
    # image
    # detect_result
    try:
        base64_str = cv2.imencode('.jpg', message.get("image"))[1].tostring()
        base64_str = base64.b64encode(base64_str).decode()
        requests.post(
            ALARM_SERVER_URL, 
            json={
                "sn": message.get("sn"),
                "algorithm_id": message.get("algorithm_id"),
                "timestamp": message.get("timestamp"),
                "image": base64_str,
                "detect_result": message.get("detect_result")
            },
            timeout=3)
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)

class Alarmer():

    def __init__(self) -> None:
        # key="{sn}{algorithm_id}" value=timestamp
        self.last_alarm_timestamp = {}
        self.alram_interval = {}
        self.pool = ThreadPoolExecutor(20)
    
    def put(self, **message):
        # make this a async call
        sn = message.get("sn")
        algorithm_id = message.get("algorithm_id")
        timestamp = message.get("timestamp")
        key = KEY_FORMAT.format(sn, algorithm_id)
        if timestamp - self.last_alarm_timestamp.get(key, 0) > self.alram_interval.get(key, 0):
            self.last_alarm_timestamp[key] = timestamp
            self.pool.submit(send, **message)

_alarmer = Alarmer()

def global_alarmer():
    global _alarmer
    return _alarmer