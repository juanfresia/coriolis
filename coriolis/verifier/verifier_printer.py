#!/usr/bin/env python3

from common.printer import *


class VerifierPrinter(CoriolisPrinter):
    def __init__(self, using_verbosity=False):
        super().__init__(using_verbosity)

    def print_checking_rules(self):
        self._print_over_separator("CHECKING RULES")

    def print_logfile_summary(self, rules, log_file):
        self._print_left_right_aligned("Verifying log:", log_file)
        self._print_separator()
        passed_rules = 0
        for i in range(len(rules)):
            if i and self.using_verbosity:
                self._print_separator()
            self._print_rule(rules[i])
            if rules[i].has_passed():
                passed_rules += 1

        result_fore = Fore.GREEN if passed_rules == len(rules) else Fore.RED
        result_text = "{} rules, {} passed, {} failed".format(len(rules), passed_rules, len(rules) - passed_rules)
        self._print_separator()
        self._print_left_right_aligned("Result:", result_text, None, result_fore)
        self._print_separator()

    def print_verifier_summary(self, logs_names, logs_passed):
        print()
        print()
        self._print_over_separator("SUMMARY")
        failed_ones = []
        for i in range(len(logs_names)):
            if not logs_passed[i]:
                failed_ones.append(logs_names[i])

        summary_fore = Fore.GREEN if len(failed_ones) == 0 else Fore.RED
        summary_text = "{} log files verified, {} passed, {} failed".format(len(logs_names), len(logs_names) - len(failed_ones), len(failed_ones))
        print(summary_fore + summary_text + Style.RESET_ALL)

        if len(failed_ones) > 0:
            print()
            print("Failed logs:")
            for failed_log in failed_ones:
                print(failed_log)

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
        self._print_left_right_aligned("Rule {}".format(rule.rule_header), rule_status, None, rule_fore)
        if self.using_verbosity:
            print()
            print(rule_fore + rule.text.rstrip() + Style.RESET_ALL)
            print()
            if rule.has_failed():
                failed_scope = self._rule_failed_scope_string(rule)
                print("{}:".format(failed_scope))
                self._print_wrapped_text(rule.get_failed_info())
                print()
