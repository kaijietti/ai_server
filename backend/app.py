from database import db
from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO
from flask.json import jsonify
import json
import cv2
import queue
import base64
import sys
sys.path.append("..")
from config.config import SQLALCHEMY_DATABASE_URI, KEY_FORMAT, UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from views import Algorithm, Camera_Algorithm, Record
from worker.dispatcher import Dispatcher
from worker.recorder import Recorder
from worker.liver import Liver
from worker.alarmer import global_alarmer
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)
socketio = SocketIO(app)

# initialize database
with app.app_context():
    db.create_all()
    if Algorithm.query.filter(Algorithm.id > 0).count() == 0:
        # TODO:
        # config more basic algorithms
        db.session.add(Algorithm(id=1, algorithm="coco", weights_path="{}/coco.pt".format(UPLOAD_FOLDER)))
    db.session.commit()

# TODO:
# persist dispatcher
# explain:
# runtime dispatchers includes
## record_dispatchers
## live_dispatchers

# record_dispatchers
## record_dispatchers[KEY_FORMAT.format(sn, algorithm_id)] = 
## dispatcher thread that are recording for camera sn under case algorithm_id
record_dispatchers = {}
# live_dispatchers [the same as above]
live_dispatchers = {}
## live_queues[KEY_FORMAT.format(sn, algorithm_id)] = 
## image buffer used for each socketIO
live_queues = {}

@app.route("/start_record", methods=['POST'])
def start_record():
    body = request.get_json()
    sn = body['sn']
    camera_ip = body['camera_ip']
    camera_port = body['camera_port']
    username = body['username']
    password = body['password']
    path = body['path']
    resolution = body['resolution']
    fps = body['fps']
    algorithm_id = body['algorithm_id']
    si = body['si']
    alarm_interval = body['alarm_interval']

    options = {
        "sn": sn,
        "camera_ip": camera_ip,
        "camera_port": camera_port,
        "username": username,
        "password": password,
        "path": path,
        "resolution": resolution,
        "fps": fps,
        "algorithm_id": algorithm_id,
        "si": si,
        "worker_cls": Recorder
    }

    dis = Dispatcher(options)
    unique_key = KEY_FORMAT.format(sn, algorithm_id)
    if record_dispatchers.get(unique_key, None) != None:
        return jsonify(
            code=403,
            message="You have already start recording for this camera {} algorithm #{}".format(sn, algorithm_id)
        ), 403
    global_alarmer().alram_interval[unique_key] = alarm_interval
    record_dispatchers[unique_key] = dis
    dis.start()
    # add to database
    if Camera_Algorithm.query.filter(Camera_Algorithm.sn==sn, Camera_Algorithm.algorithm_id==algorithm_id).count() == 0:
        db.session.add(Camera_Algorithm(sn=sn,algorithm_id=algorithm_id))
        db.session.commit()

    return jsonify(
        code=200,
        message="Successfully start!"
    ), 200
    
@app.route("/stop_record", methods=['POST'])
def stop_record():
    body = request.get_json()
    sn = body["sn"]
    algorithm_id = body["algorithm_id"]
    key = KEY_FORMAT.format(sn, algorithm_id)
    dis = record_dispatchers.get(key, None)
    if dis == None:
        return jsonify(
            code=403,
            message="No recorder has been started for [camera {} / algorithm #{}]".format(sn, algorithm_id)
        ), 403
    else:
        dis.stop()
        # delete 
        record_dispatchers.pop(key, None)
        return  jsonify(
            code=200,
            message="Successfully stop!"
        ), 200

@app.route("/cameras")
def cameras():
    cameras = [{
        "sn": c.sn,
        "algorithm_id": c.algorithm_id
    } for c in Camera_Algorithm.query.all()]
    return jsonify(
        code=200,
        cameras=cameras
    ), 200

@app.route("/camera_status")
def camera_state():
    sn = request.args.get("sn", None)
    algorithm_id = request.args.get("algorithm_id", None)
    if sn == None or algorithm_id == None:
        return jsonify(
            code=403,
            message="Need both sn and algorithm_id"
        )
    # both recording and living 3
    # is_recording              2
    # is_living                 1
    # none                      0
    key = KEY_FORMAT.format(sn, algorithm_id)
    status = 0
    if record_dispatchers.get(key, None) != None:
        status += 2
    if live_dispatchers.get(key, None) != None:
        status += 1
    return jsonify(
        code=200,
        status=status
    ), 200

@app.route("/camera_records")
def camera_records():
    sn = request.args.get("sn", None)
    algorithm_id = request.args.get("algorithm_id", None)
    if sn == None or algorithm_id == None:
        return jsonify(
            code=403,
            message="Need both sn and algorithm_id"
        )
    records = [ {
        "sn": r.sn,
        "algorithm_id": r.algorithm_id,
        "record_date": r.record_date,
        "record_path": r.record_path
    } for r in Record.query.filter(Record.sn==sn,Record.algorithm_id==algorithm_id).all()]

    return jsonify(
        code=200,
        records=records
    ), 200

@app.route("/algorithms")
def algorithms():
    algorithms = [ {
        "algorithm_id": a.id,
        "algorithm": a.algorithm,
        "weights_path": a.weights_path
    } for a in Algorithm.query.all()]

    return jsonify(
        code=200,
        algorithms=algorithms
    ), 200

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/algorithm", methods=['POST'])
def add_algorithm():
    # TODO
    if 'file' not in request.files:
        return jsonify(
            code=403,
            message="No file part"
        ), 403
    file = request.files['file']
    if file.filename == '':
        return jsonify(
            code=403,
            message="No selected part"
        ), 403
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))

    return jsonify(
        code=200,
        message="Successfully uploaded!"
    ), 200

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
    live_queues[options.get("sn")] = lq
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
