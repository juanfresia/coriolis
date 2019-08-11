#!/usr/bin/env python3

from colorama import Fore, Back, Style # pip3 install colorama

class VerifierPrinter:
    def __init__(self, using_verbosity=False):
        self.using_verbosity = using_verbosity

    def print_verifier_summary(self, rules):
        passed_rules = 0
        print("=-=-=-=-=-=-=-=-=-=-=-=- CHECKING RULES -=-=-=-=-=-=-=-=-=-=-=-=")
        for i, rule in enumerate(rules):
            self.print_rule(i+1, rule.text, rule.has_passed())
            if rule.has_passed(): passed_rules += 1
        print("=-=-=-=-=-=-=-=-=-=-=-=-=-  SUMMARY  -=-=-=-=-=-=-=-=-=-=-=-=-=")
        summary_fore = Fore.GREEN if passed_rules == len(rules) else Fore.RED
        summary = "{} rules, {} assertions, {} failures".format(len(rules), passed_rules, len(rules) - passed_rules)
        print(summary_fore + summary + Style.RESET_ALL)

    def print_rule(self, rule_number, rule_text, rule_passed):
        rule_fore = Fore.GREEN if rule_passed else Fore.RED
        rule_status = "PASSED" if rule_passed else "FAILED"
        rule_status = rule_fore + rule_status + Style.RESET_ALL
        print("RULE #{}: \t{}".format(rule_number, rule_status))
        if self.using_verbosity: print(rule_fore + rule_text + Style.RESET_ALL)
