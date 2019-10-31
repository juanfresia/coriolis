FROM rust:1.38

RUN mkdir -p /logs
RUN mkdir -p /src
WORKDIR /coriolis
COPY /start_coriolis.sh .
COPY /coriolis_logger.rs ./
RUN rustc --crate-type=rlib --crate-name=coriolis coriolis_logger.rs && \
    mv libcoriolis.rlib /usr/local/rustup/toolchains/1.38.0-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib/

ENTRYPOINT ["/bin/bash", "start_coriolis.sh"]
