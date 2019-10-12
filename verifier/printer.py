#!/usr/bin/env python3

from colorama import Fore, Back, Style # pip3 install colorama
from textwrap import wrap
from math import ceil, floor

BANNER_LENGTH = 84
BANNER = "=" * int(BANNER_LENGTH)

class VerifierPrinter:
    def __init__(self, using_verbosity=False):
        self.using_verbosity = using_verbosity

    def _print_banner(self):
        print(BANNER)

    def _print_over_banner(self, text):
        d = (BANNER_LENGTH - len(text) - 2) / 2
        print("{} {} {}".format(BANNER[:floor(d)], text, BANNER[-ceil(d):]))

    def print_verifier_summary(self, rules):
        passed_rules = 0
        self._print_over_banner("CHECKING RULES")
        for i in range(len(rules)):
            if i and self.using_verbosity: self._print_banner()
            self._print_rule(rules[i])
            if rules[i].has_passed(): passed_rules += 1
        self._print_over_banner("SUMMARY")
        if self.using_verbosity: print()
        summary_fore = Fore.GREEN if passed_rules == len(rules) else Fore.RED
        summary = "{} rules, {} assertions, {} failures".format(len(rules), passed_rules, len(rules) - passed_rules)
        print(summary_fore + summary + Style.RESET_ALL)

    def _rule_failed_scope_string(self, rule):
        l_first, l_second = rule.get_failed_scope()
        if l_second == "MAX" and l_first == "MIN": return "During the whole execution"
        if l_first == "MIN": return "Before log line {}".format(l_second)
        if l_second == "MAX": return "After log line {}".format(l_first)
        return "Between log lines {}-{}".format(l_first, l_second)

    def _print_rule(self, rule):
        rule_fore = Fore.GREEN if rule.has_passed() else Fore.RED
        rule_status = "PASSED" if rule.has_passed() else "FAILED"
        rule_header = "RULE {}".format(rule.rule_header).ljust(BANNER_LENGTH - len(rule_status))
        rule_status = rule_fore + rule_status + Style.RESET_ALL
        print("{}{}".format(rule_header, rule_status))
        if self.using_verbosity:
            print()
            print(rule_fore + rule.text + Style.RESET_ALL)
            if rule.has_failed():
                self._print_over_banner("REASON")
                print()
                failed_scope = self._rule_failed_scope_string(rule)
                print("{}:".format(failed_scope))
                info = wrap(rule.get_failed_info(), BANNER_LENGTH)
                print(*info, sep = "\n")
                print()
