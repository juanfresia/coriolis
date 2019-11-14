FROM ubuntu:16.04

ARG VERSION

RUN apt-get update && apt-get install -y python3-pip
RUN pip3 install pyinstaller

# Install fpm to generate .deb
RUN apt-get install -y ruby ruby-dev rubygems build-essential
RUN gem install --no-ri --no-rdoc fpm

ADD . /coriolis

WORKDIR /coriolis
RUN pip3 install -r requirements.txt

RUN pyinstaller --clean --onefile coriolis
RUN ./docker/generate-package.sh
