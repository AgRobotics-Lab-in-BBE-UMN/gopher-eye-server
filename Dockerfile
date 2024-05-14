FROM ubuntu:20.04
COPY app /app
COPY requirements.txt /app
WORKDIR /app
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install -r requirements.txt
EXPOSE 5000