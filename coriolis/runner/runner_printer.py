#!/usr/bin/env python3

from common.printer import *


class RunnerPrinter(CoriolisPrinter):
    def __init__(self, using_verbosity=False):
        super().__init__(using_verbosity)

    def print_instrument_summary(self, source, destination, language, checkpoints):
        self._print_over_separator("INSTRUMENTING CODE")
        self._print_left_right_aligned("Language:", language)
        self._print_left_right_aligned("Source:", source)
        self._print_left_right_aligned("Destination:", destination)
        self._print_left_right_aligned("Checkpoints:", checkpoints)
        if not self.using_verbosity:
            self._print_separator()

    def print_instrument_file(self, filename, can_instrument):
        if self.using_verbosity:
            print()
            self._print_separator()
        file_fore = Fore.GREEN if can_instrument else None
        file_text = "FINISHED" if can_instrument else "SKIPPED"
        self._print_left_right_aligned("File {}".format(filename), file_text, None, file_fore)

    def print_launch_container(self, container_id, launched_ok):
        status_fore = Fore.GREEN if launched_ok else Fore.RED
        status_text = "OK" if launched_ok else "FAILED"
        launch_text = "Starting run {}:".format(container_id)
        self._print_left_right_aligned(launch_text, status_text, None, status_fore)

    def print_stop_container(self, container_id, stopped_ok, timeouted=False):
        status_fore = Fore.GREEN if stopped_ok else Fore.RED
        status_text = "OK" if stopped_ok else "FAILED"
        timeout_msg = " (reached timeout)" if timeouted else ""
        launch_text = "Stopping run {}{}:".format(container_id, timeout_msg)
        self._print_left_right_aligned(launch_text, status_text, None, status_fore)

    def print_runner_summary(self, n):
        self._print_over_separator("RUNNING CODE")
        print("Starting {} runs for program...".format(n))

    def print_error(self, error_msg):
        error_msg = "ERROR: {}".format(error_msg)
        self._print_wrapped_text(Fore.RED + error_msg + Style.RESET_ALL)