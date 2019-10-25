FROM rust:1.38

RUN mkdir -p /logs
WORKDIR /src
COPY /coriolis_logger.rs ./
RUN rustc --crate-type=rlib --crate-name=coriolis coriolis_logger.rs && \
    mv libcoriolis.rlib /usr/local/rustup/toolchains/1.38.0-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib/

ENTRYPOINT ["/bin/bash", "run_coriolis.sh"]
