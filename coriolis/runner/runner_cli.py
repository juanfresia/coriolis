#!/usr/bin/env python3

import os
import shutil
import time
import distutils.dir_util
import docker  # pip3 install docker
import dockerpty  # pip3 install dockerpty
from uuid import uuid4
from common.utils import *
from runner import lang_instrumenter
from runner.runner_printer import RunnerPrinter


class Runner:
    def __init__(self, language, checkpoints, verbose_mode=False):
        self.instrumenter = lang_instrumenter.get_file_instrumenter(language, checkpoints, verbose_mode)
        self.printer = RunnerPrinter(verbose_mode)
        self.language = language
        self.checkpoints = checkpoints
        self.docker_client = docker.from_env()
        self.id = str(uuid4())[-12:]

    def _get_instrumented_code_dir(self):
        return "{}/{}/".format(INSTRUMENTED_CODE_DIR, self.id)

    def instrument(self, src_dir):
        dst_dir = self._get_instrumented_code_dir()
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
                        self.printer.print_instrument_file(file[len(dst_dir):], can_instrument=True)
                        self.instrumenter.instrument_file_inline(file)
                    else:
                        self.printer.print_instrument_file(file[len(dst_dir):], can_instrument=False)
                except Exception as e:
                    self.printer.print_error("{}".format(e))

    def _run_interactive_container(self, image, docker_args, container_id):
        try:
            docker_container = self.docker_client.containers.create(image, **docker_args)
            self.printer.print_launch_container(container_id, launched_ok=True, is_interactive=True)
            dockerpty.start(self.docker_client.api, docker_container.id)
            self.printer.print_stop_container(container_id, stopped_ok=True)
        except Exception as e:
            self.printer.print_launch_container(container_id, launched_ok=False, is_interactive=True)
            self.printer.print_error("{}".format(e))
            return

    def _run_detached_container(self, image, docker_args, container_id, timeout):
        try:
            docker_container = self.docker_client.containers.run(image, **docker_args)
            self.printer.print_launch_container(container_id, launched_ok=True)
        except Exception as e:
            self.printer.print_launch_container(container_id, launched_ok=False)
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
            self.printer.print_stop_container(container_id, stopped_ok=True, timeouted=True)
        except docker.errors.NotFound:
            # If here, container was already stopped
            self.printer.print_stop_container(container_id, stopped_ok=True)
        except Exception as e:
            # If here, a real error happened
            self.printer.print_stop_container(container_id, stopped_ok=False)
            self.printer.print_error("{}".format(e))

    def run_code(self, logs_dir, n, timeout):
        self.printer.print_runner_summary(n)
        src_dir = self._get_instrumented_code_dir()
        # Check if the run_coriolis script is inside the users project
        if not coriolis_run_script_exists(src_dir):
            self.printer.print_error("{} not found on project!".format(RUN_SCRIPT))
            return

        # Launch the n containers
        image = language_to_docker_image(self.language)
        interactive_mode = (timeout <= 0)
        logs_dir = os.path.join(logs_dir, LOGS_FOLDER)
        for i in range(0, n):
            current_log_dir = os.path.join(logs_dir, "{}".format(i + 1))
            if not os.path.exists(current_log_dir):
                os.makedirs(current_log_dir)
            volumes = {src_dir: {"bind": "/src", "mode": "rw"}, current_log_dir: {"bind": "/logs", "mode": "rw"}}
            docker_args = {
                "auto_remove": True,
                "stdin_open": True,
                "tty": True,
                "init": True,
                "detach": not interactive_mode,
                "volumes": volumes
            }
            if interactive_mode:
                self._run_interactive_container(image, docker_args, i + 1)
            else:
                self._run_detached_container(image, docker_args, i + 1, timeout)
        return logs_dir

    def clean_tmp_dir(self):
        tmp_dir = self._get_instrumented_code_dir()
        shutil.rmtree(tmp_dir, ignore_errors=True)


def run_runner(args):
    coriolis_runner = Runner(args.language[0], args.checkpoints, args.verbose)
    coriolis_runner.instrument(args.source)
    logs_dir = coriolis_runner.run_code(args.destination, args.number_runs, args.timeout)
    coriolis_runner.clean_tmp_dir()
    return logs_dir
