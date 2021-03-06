from threading import Thread
from concurrent import futures
from numpy import floor, ceil
import time
import sys
import queue
import cv2
import os
from worker.alarmer import global_alarmer

sys.path.append("..")
from config.config import record_duration, RECORDS_FOLDER
from backend.views import Record
from backend.database import db

class VideoWriter(Thread):
    # item 
    # {
    #     "hint": True | False
    #     "im0" : processed image
    #     "done": indicate whether thread done
    #     "ts"  : timestamp of unprocessed frame
    # }
    def __init__(self, dispatcher_config, item_buf) -> None:
        Thread.__init__(self)
        self.dispatcher_config = dispatcher_config
        self.item_buf = item_buf
        # self.fps = floor(1 / si)
        # self.record_duration = floor(self.fps * record_duration)
        self.terminate = False

    def run(self) -> None:
        # to use context
        from backend.app import app
        blank_frame_count = 0
        save_dir = RECORDS_FOLDER + "/sn-{}/algo-{}".format(
            self.dispatcher_config["sn"],
            self.dispatcher_config["algorithm_id"]
        )
        os.makedirs(save_dir, exist_ok=True)
        save_path_format = save_dir + "/{}.mp4"
        save_path = ""
        vid_writer = None

        while self.terminate == False:
            # get frame
            try:
                item = self.item_buf.get(block=True, timeout=5)
            except queue.Empty:
                continue
            # wait 
            while item["done"] == False:
                time.sleep(0.00001)

            # get info from item
            hint, im0, ts = item["hint"], item["im0"], item["ts"]
            if hint == False:
                blank_frame_count += 1
                # if blank_frame_count == self.record_duration:
                #     blank_frame_count = 0
                #     save_path = ""
                #     vid_writer = None
                if blank_frame_count >= ceil(record_duration / self.dispatcher_config["si"]):
                    blank_frame_count = 0
                    save_path = ""
                    vid_writer = None
            else:
                blank_frame_count = 0
                if blank_frame_count == 0 and vid_writer == None:
                    save_path = save_path_format.format(ts)
                    # fps, w, h = self.fps, im0.shape[1], im0.shape[0]
                    fps, w, h = 1 / self.dispatcher_config["si"], im0.shape[1], im0.shape[0]
                    vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))

                    # add to database
                    if save_path != "" and vid_writer != None:
                        with app.app_context():
                            db.session.add(Record(
                                sn=self.dispatcher_config["sn"],
                                algorithm_id=self.dispatcher_config["algorithm_id"],
                                record_path=save_path
                            ))
                            db.session.commit()
            if vid_writer != None:
                vid_writer.write(im0)
    
    def stop(self):
        self.terminate = True

# need detect result
def detect_proccess(dispatcher_config, detector, frame, ts, item):
    hint, im0, infer_time, detect_result = detector.detect(frame)
    dispatcher_config["si"] = ( infer_time + dispatcher_config["si"] ) / 2
    item["ts"] = ts
    item["hint"] = hint
    item["im0"] = im0
    item["done"] = True
    message = {
        "sn": dispatcher_config["sn"],
        "algorithm_id": dispatcher_config["algorithm_id"],
        "timestamp": item["ts"],
        "image": item["im0"],
        "detect_result": detect_result
    }
    global_alarmer().put(**message)

class Recorder(Thread):
    def __init__(self, dispatcher_config) -> None:
        Thread.__init__(self)
        self.dispatcher_config = dispatcher_config
        self.si = dispatcher_config.get("si")
        self.detector = dispatcher_config.get("detector")
        self.frame_buf = dispatcher_config.get("frame_buf")
        
        self.item_buf = queue.Queue(floor(1 / self.si))
        self.writer_thread = VideoWriter(dispatcher_config, self.item_buf)
        self.thread_pool = futures.ThreadPoolExecutor(max_workers=floor(3 / self.si))
        self.terminate = False

    def run(self) -> None:
        #     push and run thread         
        # item ==> [item, item, item, ..., item] ==> item  ==>
        #            |      |     |          |               |
        #      *detect_thread     ...    *detect_thread      |
        #                                                    | get and wait until item.done
        #                                                    => *VideoWriter write to mp4
        self.writer_thread.start()
        while self.terminate == False:
            # get frame
            # {
            #     "time"  : timestamp 
            #     "frame" : frame read from vidgear
            # }
            frame = self.frame_buf.get(block=True)
            # detect
            # hint, im0 = self.detector.detect(frame['frame'])
            # item = {
            #     "hint" : hint,
            #     "im0"  : im0,
            #     "done" : True,
            #     "ts"   : frame["time"]
            # }
            item = {
                "hint" : False,
                "im0"  : frame["frame"],
                "done" : False,
                "ts"   : frame["time"]
            }
            # pass to writer [q:why need queue?]
            # [ans:because we need to ensure the order of frames]
            self.item_buf.put(item, block=True)
            self.thread_pool.submit(detect_proccess, self.dispatcher_config, self.detector, frame["frame"], frame["time"], item)
        
    def stop(self):
        self.terminate = True
        self.writer_thread.stop()
        self.writer_thread.join()
    
