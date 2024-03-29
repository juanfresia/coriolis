FROM ubuntu:bionic

RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && \
    apt-get install -y build-essential autoconf libtool pkg-config wget valgrind && \
    wget -qO- "https://cmake.org/files/v3.15/cmake-3.15.4-Linux-x86_64.tar.gz" | \
    tar --strip-components=1 -xz -C /usr/local

RUN mkdir -p /logs
RUN mkdir -p /src
WORKDIR /coriolis
COPY /start_coriolis.sh .
COPY /coriolis_* ./
RUN gcc -Wall -Werror -c -fPIC coriolis_lock.c -o coriolis_lock.o && \
    gcc -Wall -Werror -c -fPIC coriolis_logger.c -o coriolis_logger.o && \
    gcc -shared -o libcoriolis.so coriolis_logger.o coriolis_lock.o && \
    cp libcoriolis.so /usr/lib/ && \
    cp coriolis_lock.h /usr/include/ && \
    cp coriolis_logger.h /usr/include/

ENTRYPOINT ["/bin/bash", "start_coriolis.sh"]
