#!/usr/bin/env python3

import os
import distutils.dir_util
import docker  # pip3 install docker
from uuid import uuid4
from runner import lang_instrumenter
from runner.runner_printer import RunnerPrinter

TMP_DIR = "/tmp/coriolis"


class Runner:
    def __init__(self, language, checkpoints, verbose_mode=False):
        self.instrumenter = lang_instrumenter.get_file_instrumenter(language, checkpoints, verbose_mode)
        self.printer = RunnerPrinter(verbose_mode)
        self.language = language
        self.checkpoints = checkpoints
        self.docker_client = docker.from_env()
        self.id = str(uuid4())[-12:]

    def _get_image(self):
        # TODO: Build images as "coriolis_{self.language}" ?
        return {
            "c": "coriolis_cpp",
            "cpp": "coriolis_cpp",
            "py": "coriolis_python",
            "rs": "coriolis_rust"
        }[self.language]

    def _get_tmp_dir(self):
        return "{}/{}/".format(TMP_DIR, self.id)

    def instrument(self, src_dir):
        dst_dir = self._get_tmp_dir()
        self.printer.print_instrument_summary(src_dir, dst_dir, self.language, self.checkpoints)
        try:
            distutils.dir_util.copy_tree(src_dir, dst_dir)
        except Exception as err:
            print("Error copying files:")
            print("\t", err)
            return

        for dirpath, _, files in os.walk(dst_dir):
            for file in files:
                file = os.path.join(dirpath, file)

                if self.instrumenter.can_instrument(file):
                    self.instrumenter.instrument_file_inline(file)
                    self.printer.print_instrument_file(file[len(dst_dir):], True)
                else:
                    self.printer.print_instrument_file(file[len(dst_dir):], False)

    def run_code(self, logs_dir):
        image = self._get_image()
        src_dir = self._get_tmp_dir()
        volumes = {src_dir: {"bind": "/src", "mode": "rw"}, logs_dir: {"bind": "/logs", "mode": "rw"}}
        docker_args = {
            "remove": True,
            "stdin_open": True,
            "tty": True,
            "init": True,
            "detach": True,
            "volumes": volumes
        }
        self.docker_client.containers.run(image, **docker_args)


def run_runner(args):
    coriolis_runner = Runner(args.language[0], args.checkpoints, args.verbose)
    coriolis_runner.instrument(args.source)
    coriolis_runner.run_code(args.destination)
