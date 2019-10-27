#!/usr/bin/env python3

from common.printer import *


class ParserPrinter(CoriolisPrinter):
    def __init__(self, using_verbosity=False):
        super().__init__(using_verbosity)

    def print_parser_summary(self, rules_file):
        self._print_over_separator("PARSING RULES")
        self._print_left_right_aligned("Rules file:", rules_file)
        self._print_separator()

    def print_checking_syntax(self, error_lines):
        status_fore = Fore.GREEN if len(error_lines) == 0 else Fore.RED
        status_text = "OK" if len(error_lines) == 0 else "FAILED"
        self._print_left_right_aligned("Checking syntax:", status_text, None, status_fore)
        self._print_parser_error_lines(error_lines)

    def print_parsing_rule(self, rule, caught_error=None):
        if self.using_verbosity:
            self._print_separator()
        status_fore = Fore.RED if caught_error else Fore.GREEN
        status_text = "FAILED" if caught_error else "OK"
        self._print_left_right_aligned("Parsing rule {}:".format(rule.name), status_text, None, status_fore)

        if self.using_verbosity:
            print()
            print(status_fore + rule.text.rstrip() + Style.RESET_ALL)
            print()
        if caught_error:
            self.print_error("{}".format(caught_error))

    def print_error(self, error_msg):
        error_msg = "ERROR: {}".format(error_msg)
        self._print_wrapped_text(Fore.RED + error_msg + Style.RESET_ALL)

    def _print_parser_error_lines(self, error_lines):
        for e in error_lines:
            self.print_error("At {}".format(e))