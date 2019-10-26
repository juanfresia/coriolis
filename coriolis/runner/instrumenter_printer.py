#!/usr/bin/env python3

from common.printer import *


class InstrumenterPrinter(CoriolisPrinter):
    def __init__(self, using_verbosity=False):
        super().__init__(using_verbosity)

    def print_error(self, error_msg):
        error_msg = "ERROR: {}".format(error_msg)
        self._print_wrapped_text(Fore.RED + error_msg + Style.RESET_ALL)

    def print_matched_line(self, line):
        if self.using_verbosity:
            print(Fore.GREEN + line.lstrip().rstrip() + Style.RESET_ALL)