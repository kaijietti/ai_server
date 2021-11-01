from database import db
from flask import Flask, request, render_template
from flask_socketio import SocketIO
from flask.json import jsonify
import json
import cv2
import queue
import base64
import sys
sys.path.append("..")
from config.config import SQLALCHEMY_DATABASE_URI
from views import Algorithm
from worker.dispatcher import Dispatcher
from worker.recorder import Recorder
from worker.liver import Liver
from worker.alarmer import global_alarmer

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)
socketio = SocketIO(app)

# ini database
with app.app_context():
    db.create_all()
    if Algorithm.query.filter(Algorithm.id > 0).count() == 0:
        db.session.add(Algorithm(id=1, algorithm="coco", weights_path=".."))
    db.session.commit()

dispatchers = {}
live_dispatchers = {}
live_queue = {}

@app.route("/db")
def dbtestfunc():
    return json.dumps(1)


@app.route("/test")
def test():
    options = {
        "sn" : "1",
        "camera_ip" : "172.24.208.1",
        "camera_port" : "",
        "username" : "",
        "password" : "",
        "path" : "/test",
        "resolution" : "1280x720",
        "fps" : 30,
        "model" : "yolov5",
        "algorithm_id" : 1,
        "si" : 1,
        "worker_cls" : Recorder,
        "alarm_interval" : 10
    }
    dis = Dispatcher(options)
    global_alarmer().alram_interval[
        "{}{}".format(options.get("sn"), options.get("algorithm_id"))
    ] = options.get("alarm_interval")
    dispatchers[options.get("sn")] = dis
    dis.start()
    return "good to start"

@app.route("/stop1")
def stop():
    dispatchers["1"].stop()
    return "good to stop1"

@app.route("/")
def index():
    return render_template('index.html')

@socketio.on("live")
def live():
    lq = queue.Queue(100)
    options = {
        "sn" : "2",
        "camera_ip" : "172.24.208.1",
        "camera_port" : "",
        "username" : "",
        "password" : "",
        "path" : "/test",
        "resolution" : "1280x720",
        "fps" : 30,
        "model" : "yolov5",
        "algorithm" : "coco",
        "si" : 1,
        "worker_cls" : Liver,
        "live_buf" : lq
    }
    dis = Dispatcher(options)
    live_dispatchers[options.get("sn")] = dis
    live_queue[options.get("sn")] = lq
    dis.start()
    while True:
        item = lq.get(block=True)
        frame = cv2.imencode('.jpg', item["im0"])[1].tobytes()
        frame= base64.encodebytes(frame).decode("utf-8")
        try:
            socketio.emit('image', frame)
        except KeyError:
            break
    
    live_dispatchers[options.get("sn")].stop()
    live_dispatchers[options.get("sn")].join()

@socketio.on("leave_live")
def leave_live():
    live_dispatchers["2"].stop()
    live_dispatchers["2"].join()

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
