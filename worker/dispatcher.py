from vidgear.gears import CamGear
import queue

from numpy import floor
from worker.reader import StreamReader
from queue import Queue
from threading import Thread
import sys
sys.path.append("..")
from detectors.yolov5_detect import yolov5_detect
from config.config import frame_buf_time_in_sec

# class Dispatcher(Thread):
#     def __init__(self, sn, stream, detector, worker_class) -> None:
#         Thread.__init__(self)
#         self.sn = sn
#         self.frame_buffer_queue = Queue(floor(stream.framerate * frame_buf_time_in_sec))
#         # pass stream to StreamReader and let it controll this
#         self.stream_reader_thread = StreamReader(stream, self.frame_buffer_queue)
#         # link reader and worker by the frame buffer
#         self.worker_thread = worker_class(stream.framerate, detector, self.frame_buffer_queue)

#     def run(self) -> None:
#         self.stream_reader_thread.start()
#         self.worker_thread.start()
    
#     def stop(self):
#         self.stream_reader_thread.stop()
#         self.worker_thread.stop()


def build_rtsp_url(camera_ip, camera_port, username, password, path):
    # 海康威视摄像头url样例：'rtsp://admin:password123@192.168.1.64:554/h264/ch1/sub/av_stream'
    rtsp_url = "rtsp://"
    if username != "" and password != "":
        rtsp_url += "{}:{}@".format(username, password)

    rtsp_url += camera_ip

    if camera_port != "":
        rtsp_url += ":{}".format(camera_port)

    if path != "":
        rtsp_url += path
    else:
        rtsp_url += "/h264/ch1/sub/av_stream"

    return rtsp_url
    
def get_camgear_stream(rtsp_url, resolution, fps):
    resolution = resolution.split('x')
    options = {
        "CAP_PROP_FRAME_WIDTH": int(resolution[0]), 
        "CAP_PROP_FRAME_HEIGHT": int(resolution[1]), 
        "CAP_PROP_FPS": int(fps)
    }
    stream = CamGear(source=rtsp_url, **options)
    return stream

# dispatcher can control this pipeline
# worker_thread is specified by user [it can be liver or recorder]
# dispatcher owned a queue that can store frames
#                            dispatcher
# stream_reader_thread => [frame1, frame2, ...] => worker_thread
#                              frame_buf
class Dispatcher(Thread):
    # options(dict)
    # sn          : serious number of the camera        string
    # camera_ip   :                                     string          
    # camera_port :                                     string        
    # username    :                                     string           
    # password    :                                     string        
    # path        : /h264/ch1/sub/av_stream or /test    string       
    # resolution  : "{}x{}".format(width, height)       string     
    # fps         :                                     int
    # model       : yolov5                              string  
    # algorithm   : choose weights under /pts/{model}/  string           
    # si          : sampling interval                   float     
    # worker_cls  : Recorder or Liver                   class

    def __init__(self, **options) -> None:
        Thread.__init__(self)
        self.dispatcher_config = {
            "sn" : options.get("sn"),
            "stream" : get_camgear_stream(
                # rtsp_url
                build_rtsp_url(
                    options.get("camera_ip"), 
                    options.get("camera_port"), 
                    options.get("username"), 
                    options.get("password"),
                    options.get("path")
                ),
                options.get("resolution"),
                options.get("fps")
            ),
            "si" : options.get("si"),
            "frame_buf" : queue.Queue(floor(1 / options.get("si") * frame_buf_time_in_sec)),
            # TODO:
            # choose detector based on {model} and {algorithm}
            "detector" : yolov5_detect()
        }
        # stream reader
        self.stream_reader_thread = StreamReader(**self.dispatcher_config)
        # worker
        worker_cls = options.get("worker_cls")
        self.worker_thread = worker_cls(**self.dispatcher_config)

    def run(self) -> None:
        self.stream_reader_thread.start()
        self.worker_thread.start()

    def stop(self):
        self.stream_reader_thread.stop()
        self.worker_thread.stop()