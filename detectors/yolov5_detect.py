# import argparse
import time

import torch
import numpy as np

from yolov5.models.experimental import attempt_load
from yolov5.utils.datasets import letterbox
from yolov5.utils.general import check_img_size, non_max_suppression, apply_classifier, \
    scale_coords, set_logging
from yolov5.utils.plots import colors, plot_one_box
from yolov5.utils.torch_utils import select_device, load_classifier, time_sync

def getOpt():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--weights', nargs='+', type=str, default='../pts/yolov5/yolov5s.pt', help='model.pt path(s)')
    # parser.add_argument('--source', default="./images/bus.jpg",type=str, help='source')  # file/folder, 0 for webcam
    # parser.add_argument('--img-size', type=int, default=640, help='inference size (pixels)')
    # parser.add_argument('--conf-thres', type=float, default=0.25, help='object confidence threshold')
    # parser.add_argument('--iou-thres', type=float, default=0.45, help='IOU threshold for NMS')
    # parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    # parser.add_argument('--view-img', action='store_true', help='display results')
    # # parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    # parser.add_argument('--save-txt',default=True)
    # parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
    # parser.add_argument('--save-crop', action='store_true', default= False, help='save cropped prediction boxes')
    # parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
    # parser.add_argument('--classes', default=8, type=int, help='filter by class: --class 0, or --class 0 2 3')
    # parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    # parser.add_argument('--augment', action='store_true', help='augmented inference')
    # parser.add_argument('--update', action='store_true', help='update all models')
    # parser.add_argument('--project', default='runs/detect', help='save results to project/name')
    # parser.add_argument('--name', default='exp', help='save results to project/name')
    # parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
    # parser.add_argument('--line-thickness', default=3, type=int, help='bounding box thickness (pixels)')
    # parser.add_argument('--hide-labels', default=False, action='store_true', help='hide labels')
    # parser.add_argument('--hide-conf', default=False, action='store_true', help='hide confidences')
    # parser.add_argument('--run', default=False, action='store_true', help='hide confidences')
    # opt = parser.parse_args()   
    class opt():
        weights = '../weights/yolov5/yolov5s.pt'
        img_size = 640
        device = ''
        conf_thres = 0.25
        iou_thres = 0.45
        augment = False
        hide_labels = False
        hide_conf = False
        line_thickness = 3
    return opt()

class yolov5_detect():
    def __init__(self, weights_path) -> None:
        class opt():
            weights = weights_path
            img_size = 640
            max_detect = 1000
            device = ''
            conf_thres = 0.25
            iou_thres = 0.45
            augment = False
            hide_labels = False
            hide_conf = False
            line_thickness = 3
        self.opt = opt()
        # load models
        weights, imgsz = self.opt.weights, self.opt.img_size
        # Initialize
        set_logging()
        self.device = select_device(opt.device)
        self.half = self.device.type != 'cpu'  # half precision only supported on CUDA
        # Load model
        self.model = attempt_load(weights, map_location=self.device)  # load FP32 model
        self.stride = int(self.model.stride.max())  # model stride
        self.imgsz = check_img_size(imgsz, s=self.stride)  # check img_size
        self.names = self.model.module.names if hasattr(self.model, 'module') else self.model.names  # get class names
        if self.half:
            self.model.half()  # to FP16
        # Second-stage classifier
        self.classify = False
        if self.classify:
            self.modelc = load_classifier(name='resnet101', n=2)  # initialize
            self.modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=self.device)['model']).to(self.device).eval()
    
    def detect(self, source):
        hint = False
        # Run inference
        if self.device.type != 'cpu':
            self.model(torch.zeros(1, 3, self.imgsz, self.imgsz).to(self.device).type_as(next(self.model.parameters())))  # run once
        t0 = time.time()

        im0s = source # BGR

        # Padded resize
        img = letterbox(im0s, self.imgsz, stride=self.stride)[0]
        # Convert
        img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
        img = np.ascontiguousarray(img)

        img = torch.from_numpy(img).to(self.device)
        img = img.half() if self.half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        # if img.ndimension() == 3:
        #     img = img.unsqueeze(0)
        if len(img.shape) == 3:
            img = img[None]  # expand for batch dim

        # Inference
        t1 = time_sync()
        pred = self.model(img, augment=self.opt.augment)[0]

        # Apply NMS
        pred = non_max_suppression(pred, self.opt.conf_thres, self.opt.iou_thres, classes=None, agnostic=False, max_det=1000)
        t2 = time_sync()

        # Apply Classifier
        if self.classify:
            pred = apply_classifier(pred, self.modelc, img, im0s)

        # Process detections
        detect_result = ""
        for i, det in enumerate(pred):  # detections per image
            s, im0 = '', im0s.copy()
            s += '%gx%g ' % img.shape[2:]  # print string
            if len(det):
                hint = True
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += f"{n} {self.names[int(c)]}{'s' * (n > 1)}, "  # add to string

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    # Add bbox to image
                    c = int(cls)  # integer class
                    label = None if self.opt.hide_labels else (self.names[c] if self.opt.hide_conf else f'{self.names[c]} {conf:.2f}')
                    plot_one_box(xyxy, im0, label=label, color=colors(c, True), line_width=self.opt.line_thickness)

            # Print time (inference + NMS)
            detect_result = s[:-2]
            print(f'{s}Done. ({t2 - t1:.3f}s)')

        print(f'Done. ({time.time() - t0:.3f}s)')
        return hint, im0, time.time() - t0, detect_result

