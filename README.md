使用本地摄像头进行测试的时候可以参考：
https://blog.csdn.net/weixin_40448140/article/details/113180796
本地推流完成后得到一个 rtsp 地址，可以用于下面的实验（注意自己改 app.py 内配置的摄像头 ip 等等）
使用 /docker 文件夹构造镜像（请测试一下hhh）
工程目录如下（项目中sqlite地址是 hard code 的，暂时保持一样的目录结构 /root/ai_server/*）：
```
root@aa41ace34d05:~/ai_server# tree -L 2 
.
├── README.md
├── backend
│   ├── __ini__.py
│   ├── __pycache__
│   ├── app.py
│   ├── database.py
│   ├── templates
│   └── views.py
├── config
│   ├── __ini__.py
│   ├── __pycache__
│   ├── config.py
│   ├── schema.sql
│   └── test.db
├── detectors
│   ├── README.md
│   ├── __ini__.py
│   ├── __pycache__
│   └── yolov5_detect.py
├── docker
│   ├── Arial.ttf
│   ├── Dockerfile
│   ├── README.md
│   ├── requirements.txt
│   └── yolov5s.pt
├── pts
│   ├── README.md
│   ├── config.json
│   └── yolov5
└── worker
    ├── __ini__.py
    ├── __pycache__
    ├── dispatcher.py
    ├── liver.py
    ├── reader.py
    └── recorder.py

12 directories, 24 files
```
```
$ cd backend/
$ export FLASK_APP=app.py
$ flask run
```