FROM ubuntu:20.04
COPY app /app
COPY requirements.txt /app
COPY spike1n-seg.pt /app
WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3 python3-pip
RUN apt-get install -y ffmpeg libsm6 libxext6
RUN pip3 install -r requirements.txt
EXPOSE 5000
