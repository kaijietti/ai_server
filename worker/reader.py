from os import dup
from threading import Thread
import time

from numpy import ceil

# class StreamReader(Thread):

#     def __init__(self, stream, frame_buf, duration=1) -> None:
#         Thread.__init__(self)
#         self.stream = stream
#         self.terminate = False
#         self.frame_buf = frame_buf
#         self.duration = duration

#     # 阻塞添加 frame
#     def run(self) -> None:
#         self.stream.start()
#         count = 0
#         while self.terminate == False:
#             frame = self.stream.read()
#             if count % floor(self.duration * self.stream.framerate) == 0:
#                 count = 0
#                 self.frame_buf.put({
#                     "time" : int(time.time()),
#                     "frame": frame
#                 }, block=True)
#             count += 1

#     def stop(self):
#         self.terminate = True
#         self.stream.stop()

#     # 阻塞获取 frame
#     def get(self):
#         return self.frame_buf.get(block=True)

class StreamReader(Thread):

    def __init__(self, dispatcher_config) -> None:
        Thread.__init__(self)
        self.dispatcher_config = dispatcher_config
        self.stream = dispatcher_config.get("stream")
        self.frame_buf = dispatcher_config.get("frame_buf")
        # self.si = dispatcher_config.get("si")
        ## self.si / ( 1 / self.stream.framerate)
        # self.duration_count = floor(self.si * self.stream.framerate)
        self.terminate = False

    # 阻塞添加 frame
    def run(self) -> None:
        self.stream.start()
        count = 0
        while self.terminate == False:
            frame = self.stream.read()
            if count >= ceil(self.dispatcher_config.get("si") * self.stream.framerate):
                count = 0
                frame = {
                    "time" : int(time.time()),
                    "frame": frame
                }
                self.frame_buf.put(frame, block=True)
            count += 1

    def stop(self):
        self.terminate = True
        self.stream.stop()

    # 阻塞获取 frame
    def get(self):
        return self.frame_buf.get(block=True)