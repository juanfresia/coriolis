#!/usr/bin/env python3

from colorama import Fore, Back, Style # pip3 install colorama


def print_verifier_start():
    print("=-=-=-=-=-=-=-=-=-=-=-=- CHECKING RULES -=-=-=-=-=-=-=-=-=-=-=-=")

def print_verifier_summary(total_rules, passed_rules):
    print("=-=-=-=-=-=-=-=-=-=-=-=-=-  SUMMARY  -=-=-=-=-=-=-=-=-=-=-=-=-=")
    summary_fore = Fore.GREEN if passed_rules == total_rules else Fore.RED
    summary = "{} rules, {} assertions, {} failures".format(total_rules, passed_rules, total_rules - passed_rules)
    print(summary_fore + summary + Style.RESET_ALL)

def print_rule(rule_number, rule_text, rule_passed, using_verbosity=False):
    rule_fore = Fore.GREEN if rule_passed else Fore.RED
    rule_status = "PASSED" if rule_passed else "FAILED"
    rule_status = rule_fore + rule_status + Style.RESET_ALL
    print("RULE #{}: \t{}".format(rule_number, rule_status))
    if using_verbosity: print(rule_fore + rule_text + Style.RESET_ALL)
