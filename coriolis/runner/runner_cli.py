#!/usr/bin/env python3

import os
import time
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

    def _run_script_exists(self, src_dir):
        run_script = os.path.join(src_dir, "run_coriolis.sh")
        return os.path.isfile(run_script)

    def instrument(self, src_dir):
        dst_dir = self._get_tmp_dir()
        self.printer.print_instrument_summary(src_dir, dst_dir, self.language, self.checkpoints)
        try:
            distutils.dir_util.copy_tree(src_dir, dst_dir)
        except Exception as e:
            self.printer.print_error("{}".format(e))

        for dirpath, _, files in os.walk(dst_dir):
            for file in files:
                try:
                    file = os.path.join(dirpath, file)
                    if self.instrumenter.can_instrument(file):
                        self.printer.print_instrument_file(file[len(dst_dir):], True)
                        self.instrumenter.instrument_file_inline(file)
                    else:
                        self.printer.print_instrument_file(file[len(dst_dir):], False)
                except Exception as e:
                    self.printer.print_error("{}".format(e))

    def _run_container(self, image, docker_args, container_id, timeout):
        try:
            docker_container = self.docker_client.containers.run(image, **docker_args)
            self.printer.print_launch_container(container_id, True)
        except Exception as e:
            self.printer.print_launch_container(container_id, False)
            self.printer.print_error("{}".format(e))
            return

        delta_t = 1.0
        time_elapsed = 0.0
        try:
            while time_elapsed < timeout:
                # We monitor the container querying the API for its status
                docker_container.reload()
                time.sleep(delta_t)
                time_elapsed += delta_t

            docker_container.stop()
            self.printer.print_stop_container(container_id, True, True)
        except docker.errors.NotFound:
            # If here, container was already stopped
            self.printer.print_stop_container(container_id, True)
        except Exception as e:
            # If here, a real error happened
            self.printer.print_stop_container(container_id, False)
            self.printer.print_error("{}".format(e))

    def run_code(self, logs_dir, n, timeout):
        self.printer.print_runner_summary(n)
        src_dir = self._get_tmp_dir()
        # Check if the run_coriolis script is inside the users project
        if not self._run_script_exists(src_dir):
            self.printer.print_error("run_script.sh not found on project!")
            return

        # Launch the n containers
        image = self._get_image()
        for i in range(0, n):
            current_logs_dir = os.path.join(logs_dir, "coriolis_logs/{}".format(i + 1))
            if not os.path.exists(current_logs_dir):
                os.makedirs(current_logs_dir)
            volumes = {src_dir: {"bind": "/src", "mode": "rw"}, current_logs_dir: {"bind": "/logs", "mode": "rw"}}
            docker_args = {
                "remove": True,
                "auto_remove": True,
                "stdin_open": True,
                "tty": True,
                "init": True,
                "detach": True,
                "volumes": volumes
            }
            self._run_container(image, docker_args, i + 1, timeout)


def run_runner(args):
    coriolis_runner = Runner(args.language[0], args.checkpoints, args.verbose)
    coriolis_runner.instrument(args.source)
    coriolis_runner.run_code(args.destination, args.number_runs, args.timeout)
