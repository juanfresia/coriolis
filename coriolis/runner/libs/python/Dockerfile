FROM python:3.6

RUN mkdir -p /logs
RUN mkdir -p /src
WORKDIR /coriolis
COPY /start_coriolis.sh .
COPY /coriolis_* /usr/local/lib/python3.6/

ENTRYPOINT ["/bin/bash", "start_coriolis.sh"]
