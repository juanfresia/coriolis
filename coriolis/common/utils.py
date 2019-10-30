#!/usr/bin/env python3

import os

MONGO_DEFAULT_HOST = "localhost"
MONGO_DEFAULT_PORT = 21592

RUN_SCRIPT = "run_coriolis.sh"
INSTRUMENTED_CODE_DIR = "/tmp/coriolis"
LOGS_FOLDER = "coriolis_logs"


def language_to_docker_image(language):
    return {
        "c": "coriolis_cpp",
        "cpp": "coriolis_cpp",
        "py": "coriolis_python",
        "rs": "coriolis_rust"
    }[language]


def language_to_language_name(language):
    return {
        "c": "C",
        "cpp": "C++",
        "py": "Python",
        "rs": "Rust"
    }[language]


def coriolis_run_script_exists(src_dir):
    run_script = os.path.join(src_dir, RUN_SCRIPT)
    return os.path.isfile(run_script)
