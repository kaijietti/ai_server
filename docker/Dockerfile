FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8

RUN sed -i s@/archive.ubuntu.com/@/mirrors.ustc.edu.cn/@g /etc/apt/sources.list
RUN apt-get clean
RUN apt-get update

RUN apt-get install -y libmysqlclient-dev
RUN apt-get install -y tzdata
RUN apt-get install -y python3
RUN apt-get install -y python3-dev
# RUN apt-get install -y python3.8-venv
RUN apt-get install -y python3-pip
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get clean

COPY requirements.txt /tmp
WORKDIR /tmp

RUN apt-get autoclean
# RUN ln -sf /usr/bin/pip3 /usr/bin/pip
RUN ln -sf /usr/bin/python3 /usr/bin/python
RUN pip3 install -r requirements.txt -i https://mirrors.ustc.edu.cn/pypi/web/simple
RUN rm -rf /var/lib/apt/lists/*
RUN rm /tmp/requirements.txt
# yolov5 need this font
COPY Arial.ttf /usr/share/fonts/truetype
# for testing
# you can go to /usr/local/lib/python3.8/dist-packages/ 
# and RUN python detect.py --source data/images --weights yolov5s.pt --img 640
COPY yolov5s.pt /usr/local/lib/python3.8/dist-packages/yolov5
CMD ["bash"]