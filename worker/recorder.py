from threading import Thread
from concurrent import futures
from numpy import floor
import time
import sys
import queue
import cv2

sys.path.append("..")
from config.config import record_duration

# class VideoWriter(Thread):
#     # item 
#     # {
#     #     "hint": True | False
#     #     "im0" : processed image
#     #     "done": indicate whether thread done
#     #     "ts"  : timestamp of unprocessed frame
#     # }
#     def __init__(self, fps, item_buf) -> None:
#         Thread.__init__(self)
#         self.item_buf = item_buf
#         fps = 1
#         self.fps = int(fps)
#         self.record_duration = floor(fps * record_duration)
#         self.terminate = False

#     def run(self) -> None:
#         blank_frame_count = 0
#         save_path_format = "{}.mp4"
#         save_path = ""
#         vid_writer = None

#         while self.terminate == False:
#             # get frame
#             item = self.item_buf.get(block=True)
#             # wait 
#             while item["done"] == False:
#                 time.sleep(0.5)
#             # get info from item
#             hint, im0, ts = item["hint"], item["im0"], item["ts"]
#             if hint == False:
#                 blank_frame_count += 1
#                 if blank_frame_count == self.record_duration:
#                     blank_frame_count = 0
#                     save_path = ""
#                     vid_writer = None
#             else:
#                 blank_frame_count = 0
#                 if blank_frame_count == 0 and vid_writer == None:
#                     save_path = save_path_format.format(ts)
#                     fps, w, h = self.fps, im0.shape[1], im0.shape[0]
#                     vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
#             if vid_writer != None:
#                 vid_writer.write(im0)
#         # we need this beacuse 
#         # cv2.VideoWriter may not an atomic write
#         # self.terminate = False
    
#     def stop(self):
#         self.terminate = True
#         # until last write is done
#         # can we return
#         # while self.terminate == True:
#         #     time.sleep(0.1)
#         # return

# class detect_thread(Thread):
#     def __init__(self, detector, frame, ts, item) -> None:
#         Thread.__init__(self)
#         self.detector = detector
#         self.frame = frame
#         self.ts = ts
#         self.item = item
    
#     def run(self) -> None:
#         hint, im0 = self.detector.detect(self.frame)
#         self.item["ts"] = self.ts
#         self.item["hint"] = hint
#         self.item["im0"] = im0
#         self.item["done"] = True

# def detect_proccess(detector, frame, ts, item):
#         hint, im0 = detector.detect(frame)
#         item["ts"] = ts
#         item["hint"] = hint
#         item["im0"] = im0
#         item["done"] = True

# class Recorder(Thread):
#     def __init__(self, fps, detector, frame_buf) -> None:
#         Thread.__init__(self)
#         self.fps = int(fps)
#         self.detector = detector
#         self.frame_buf = frame_buf
#         self.record_duration = floor(fps * record_duration)
#         self.item_buf = queue.Queue(100)
#         self.writer_thread = VideoWriter(fps, self.item_buf)
#         self.terminate = False
#         self.thread_pool = futures.ThreadPoolExecutor(max_workers=self.fps)

#     def run(self) -> None:
#         #     push and run thread         
#         # item ==> [item, item, item, ..., item] ==> item  ==>
#         #            |      |     |          |               |
#         #      *detect_thread     ...    *detect_thread      |
#         #                                                    | get and wait until item.done
#         #                                                    => *VideoWriter write to mp4
#         self.writer_thread.start()
#         while self.terminate == False:
#             # get frame
#             # {
#             #     "time"  : timestamp 
#             #     "frame" : frame read from vidgear
#             # }
#             frame = self.frame_buf.get(block=True)
#             # detect
#             # hint, im0 = self.detector.detect(frame['frame'])
#             # pass to writer [q:why need queue?]
#             # [ans:because we need to ensure the order of frames]
#             item = {
#                 "hint" : False,
#                 "im0"  : frame["frame"],
#                 "done" : False,
#                 "ts"   : frame["time"]
#             }
#             self.item_buf.put(item, block=True)
#             self.thread_pool.submit(detect_proccess, self.detector, frame["frame"], frame["time"], item)
#             # detect_thread(self.detector, frame["frame"], frame["time"], item).start()
        
#     def stop(self):
#         self.terminate = True
#         self.writer_thread.stop()
#         self.writer_thread.join()
    


# class Recorder(Thread):
#     def __init__(self, fps, detector, frame_buf) -> None:
#         Thread.__init__(self)
#         self.fps = int(fps)
#         self.detector = detector
#         self.frame_buf = frame_buf
#         self.record_duration = floor(fps * record_duration)
#         self.terminate = False

#     def run(self) -> None:
#         blank_frame_count = 0
#         save_path_format = "{}.mp4"
#         save_path = ""
#         vid_writer = None

#         while self.terminate == False:
#             # get frame
#             item = self.frame_buf.get(block=True)
#             # detect
#             hint, im0 = self.detector.detect(item['frame'])
#             if hint == False:
#                 blank_frame_count += 1
#                 if blank_frame_count == 100:
#                     blank_frame_count = 0
#                     save_path = ""
#                     vid_writer = None
#             else:
#                 blank_frame_count = 0
#                 if blank_frame_count == 0 and vid_writer == None:
#                     save_path = save_path_format.format(item['time'])
#                     fps, w, h = self.fps, im0.shape[1], im0.shape[0]
#                     vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
#             cv2.imwrite("haha.jpg", im0)
#             if vid_writer != None:
#                 vid_writer.write(im0)
        

#     def stop(self):
#         self.terminate = True

class VideoWriter(Thread):
    # item 
    # {
    #     "hint": True | False
    #     "im0" : processed image
    #     "done": indicate whether thread done
    #     "ts"  : timestamp of unprocessed frame
    # }
    def __init__(self, si, item_buf) -> None:
        Thread.__init__(self)
        self.item_buf = item_buf
        self.fps = floor(1 / si)
        self.record_duration = floor(self.fps * record_duration)
        self.terminate = False

    def run(self) -> None:
        blank_frame_count = 0
        save_path_format = "{}.mp4"
        save_path = ""
        vid_writer = None

        while self.terminate == False:
            # get frame
            item = self.item_buf.get(block=True)
            # wait 
            while item["done"] == False:
                time.sleep(0.00001)
            # get info from item
            hint, im0, ts = item["hint"], item["im0"], item["ts"]
            if hint == False:
                blank_frame_count += 1
                if blank_frame_count == self.record_duration:
                    blank_frame_count = 0
                    save_path = ""
                    vid_writer = None
            else:
                blank_frame_count = 0
                if blank_frame_count == 0 and vid_writer == None:
                    save_path = save_path_format.format(ts)
                    fps, w, h = self.fps, im0.shape[1], im0.shape[0]
                    vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
            if vid_writer != None:
                vid_writer.write(im0)
    
    def stop(self):
        self.terminate = True

def detect_proccess(detector, frame, ts, item):
    hint, im0 = detector.detect(frame)
    item["ts"] = ts
    item["hint"] = hint
    item["im0"] = im0
    item["done"] = True


class Recorder(Thread):
    def __init__(self, **dispatcher_config) -> None:
        Thread.__init__(self)
        self.si = dispatcher_config.get("si")
        self.detector = dispatcher_config.get("detector")
        self.frame_buf = dispatcher_config.get("frame_buf")
        
        self.item_buf = queue.Queue(floor(1 / self.si))
        self.writer_thread = VideoWriter(self.si, self.item_buf)
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
            self.thread_pool.submit(detect_proccess, self.detector, frame["frame"], frame["time"], item)
        
    def stop(self):
        self.terminate = True
        self.writer_thread.stop()
        self.writer_thread.join()
    
