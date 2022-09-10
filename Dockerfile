FROM python:3.8-slim

RUN apt-get update && apt-get upgrade -y

RUN mkdir /application
COPY . /application
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r /application/requirements.txt
