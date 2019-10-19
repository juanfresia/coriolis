#!/usr/bin/env python3

from common.printer import CoriolisPrinter


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
