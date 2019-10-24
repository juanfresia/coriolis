FROM python:3.6

RUN mkdir -p /logs
WORKDIR /src
COPY /coriolis_* /usr/lib/python3.6/

ENTRYPOINT ["/bin/bash", "run_coriolis.sh"]
