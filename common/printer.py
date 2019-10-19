#!/usr/bin/env python3

from colorama import Fore, Back, Style  # pip3 install colorama
from textwrap import wrap
from math import ceil, floor

SEPARATOR_LENGTH = 96
SEPARATOR = "=" * int(SEPARATOR_LENGTH)


class CoriolisPrinter:
    def __init__(self, using_verbosity=False):
        self.using_verbosity = using_verbosity

    def _print_separator(self):
        print(SEPARATOR)

    def _print_over_separator(self, text):
        d = (SEPARATOR_LENGTH - len(text) - 2) / 2
        print("{} {} {}".format(SEPARATOR[:floor(d)], text, SEPARATOR[-ceil(d):]))

    def _print_left_right_aligned(self, left_text, right_text, left_fore=None, right_fore=None):
        left_text = "{}".format(left_text).ljust(SEPARATOR_LENGTH - len(right_text))
        left_text = left_fore + left_text + Style.RESET_ALL if left_fore else left_text
        right_text = right_fore + right_text + Style.RESET_ALL if right_fore else right_text
        print("{}{}".format(left_text, right_text))

    def _print_wrapped_text(self, text):
        s = wrap(text, SEPARATOR_LENGTH)
        print(*s, sep="\n")


class InstrumenterPrinter(CoriolisPrinter):
    def __init__(self, using_verbosity=False):
        super().__init__(using_verbosity)

    def print_instrument_summary(self, source, destination, language, checkpoints):
        self._print_over_separator("INSTRUMENTING CODE")
        self._print_left_right_aligned("Source:", source)
        self._print_left_right_aligned("Destination:", destination)
        self._print_left_right_aligned("Language:", language)
        self._print_left_right_aligned("Checkpoints:", checkpoints)


class VerifierPrinter(CoriolisPrinter):
    def __init__(self, using_verbosity=False):
        super().__init__(using_verbosity)

    def print_verifier_summary(self, rules):
        passed_rules = 0
        self._print_over_separator("CHECKING RULES")
        for i in range(len(rules)):
            if i and self.using_verbosity:
                self._print_separator()
            self._print_rule(rules[i])
            if rules[i].has_passed():
                passed_rules += 1
        self._print_over_separator("SUMMARY")
        if self.using_verbosity:
            print()
        summary_fore = Fore.GREEN if passed_rules == len(rules) else Fore.RED
        summary = "{} rules, {} assertions, {} failures".format(len(rules), passed_rules, len(rules) - passed_rules)
        print(summary_fore + summary + Style.RESET_ALL)

    def _rule_failed_scope_string(self, rule):
        l_first, l_second = rule.get_failed_scope()
        if l_second == "MAX" and l_first == "MIN":
            return "During the whole execution"
        if l_first == "MIN":
            return "Before log line {}".format(l_second)
        if l_second == "MAX":
            return "After log line {}".format(l_first)
        return "Between log lines {}-{}".format(l_first, l_second)

    def _print_rule(self, rule):
        rule_fore = Fore.GREEN if rule.has_passed() else Fore.RED
        rule_status = "PASSED" if rule.has_passed() else "FAILED"
        self._print_left_right_aligned("RULE {}".format(rule.rule_header), rule_status, None, rule_fore)
        if self.using_verbosity:
            print()
            print(rule_fore + rule.text + Style.RESET_ALL)
            if rule.has_failed():
                self._print_over_separator("REASON")
                print()
                failed_scope = self._rule_failed_scope_string(rule)
                print("{}:".format(failed_scope))
                self._print_wrapped_text(rule.get_failed_info())
                print()
