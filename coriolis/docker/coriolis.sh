#! /bin/bash

if [[ -z "${CORIOLIS_DIR}" ]]; then
    CORIOLIS_DIR="$(pwd)"
fi

docker run -it --rm --init -v "${CORIOLIS_DIR}":/coriolis-dir coriolis:latest $@
