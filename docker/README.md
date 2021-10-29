RUN 
```
# ai_server container
$ cd /usr/local/lib/python3.8/dist-packages/yolov5
$ python detect.py --source data/images --weights yolov5s.pt --img 640
```
<!-- CHECK
```
# host
docker cp aa41ace34d05:/usr/local/lib/python3.8/dist-packages/yolov5/runs/detect/exp .
``` -->