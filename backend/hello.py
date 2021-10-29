from flask import Flask, request
import cv2
import sys
from flask.json import jsonify
from vidgear.gears import CamGear


sys.path.append("..")
from detectors.yolov5_detect import yolov5_detect
from worker.dispatcher import Dispatcher
from worker.recorder import Recorder
app = Flask(__name__)

dispatchers = {}

@app.route("/test")
def test():
    options = {
        "sn" : "1",
        "camera_ip" : "172.23.48.1",
        "camera_port" : "",
        "username" : "",
        "password" : "",
        "path" : "/test",
        "resolution" : "1280x720",
        "fps" : 30,
        "model" : "yolov5",
        "algorithm" : "coco",
        "si" : 1,
        "worker_cls" : Recorder
    }
    dis = Dispatcher(**options)
    dispatchers[options.get("sn")] = dis
    dis.start()
    return "good to start"

@app.route("/stop1")
def stop():
    dispatchers["1"].stop()
    return "good to stop1"

@app.route("/start", methods=['POST'])
def start_new_proccessing_thread():
    # 海康威视摄像头url样例：'rtsp://admin:password123@192.168.1.64:554/h264/ch1/sub/av_stream'
    # {
    #     "sn": "",
    #     "camera_ip": "",
    #     "camera_port": "",
    #     "username": "admin",
    #     "password": "password",
    #     "path": "", # /h264/ch1/sub/av_stream or /test
    #     "resolution": "1280x720",
    #     "fps": 30,
    #     "moedl": "yolov5",
    #     "algorithm": "",
    #     "si" : 0.1
    # }
    request_data = request.get_json()
    camera_ip = request_data['camera_ip']
    camera_port = request_data['camera_port']
    username = request_data['username']
    password = request_data['password']
    path = request_data['path']
    resolution = request_data['resolution'].split('x')
    fps = request_data['fps']

    model = request_data['model']
    algorithm = request_data['algorithm']


    rtsp_url = "rtsp://"
    if username != "" and password != "":
        rtsp_url += "{}:{}@".format(username, password)
    if camera_ip != "":
        rtsp_url += camera_ip
    else:
        return jsonify({"message": "Please specify IP Addr of the camera!"}), 403
    if camera_port != "":
        rtsp_url += ":{}".format(camera_port)
    if path != "":
        rtsp_url += path
    else:
        rtsp_url += "/h264/ch1/sub/av_stream"

    return "TODO"
