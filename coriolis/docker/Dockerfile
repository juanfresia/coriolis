FROM ubuntu:16.04

RUN apt update && apt install -y python3-pip
RUN pip3 install pyinstaller
ADD . /coriolis

WORKDIR /coriolis
RUN pip3 install -r requirements.txt

RUN pyinstaller --clean --onefile coriolis
