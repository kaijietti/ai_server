# offer real-time object detect result
# using websocket to streaming images
from threading import Thread
import queue
from concurrent import futures
from numpy import floor
import time


class ImageStreamer(Thread):
    # item 
    # {
    #     "hint": True | False
    #     "im0" : processed image
    #     "done": indicate whether thread done
    #     "ts"  : timestamp of unprocessed frame
    # }
    def __init__(self, item_buf, live_buf) -> None:
        Thread.__init__(self)
        self.item_buf = item_buf
        self.live_buf = live_buf
        self.terminate = False

    def run(self) -> None:
        while self.terminate == False:
            # get frame
            item = self.item_buf.get(block=True)
            # wait until done
            while item["done"] == False:
                time.sleep(0.00001)
            # get info from item
            # hint, im0, ts = item["hint"], item["im0"], item["ts"]
            self.live_buf.put(item, block=True)
    
    def stop(self):
        self.terminate = True

def detect_proccess(dispatcher_config, detector, frame, ts, item):
    hint, im0, infer_time = detector.detect(frame)
    dispatcher_config["si"] = ( infer_time + dispatcher_config["si"] ) / 2
    item["ts"] = ts
    item["hint"] = hint
    item["im0"] = im0
    item["done"] = True

class Liver(Thread):
    def __init__(self, dispatcher_config) -> None:
        Thread.__init__(self)
        self.dispatcher_config = dispatcher_config
        self.si = dispatcher_config.get("si")
        self.detector = dispatcher_config.get("detector")
        self.frame_buf = dispatcher_config.get("frame_buf")
        
        self.item_buf = queue.Queue(floor(1 / self.si))
        self.writer_thread = ImageStreamer(
            self.item_buf,
            dispatcher_config.get("live_buf")
        )
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
    