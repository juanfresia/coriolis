#!/usr/bin/env python3

import argparse
import os

from common.aggregation_steps import *
from verifier.log_parser import LogParser
from verifier.mongo_client import MongoClient
from verifier.printer import VerifierPrinter
from common.jarl_rule import JARLRule, RuleScope, RuleFact

class FullPaths(argparse.Action):
    """Expand user- and relative-paths"""
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest,
                os.path.abspath(os.path.expanduser(values[0])))

class RuleChecker:
    def __init__(self, rules_to_check, log_file, checkpoint_file):
        self.mongo_client = MongoClient()
        self.rules = rules_to_check
        self.lp = LogParser(log_file, checkpoint_file)
    
    def execute_aggregation_steps(self, aggregation_steps):
        return self.mongo_client.aggregate(aggregation_steps)
    
    def check_rule(self, rule):
        rule.set_passed()
        rule_scope = RuleScope.get_default_scope()
        if rule.has_scope():
            rule_scope = self.execute_aggregation_steps(rule.evaluate_scope_steps())
        for s in rule_scope:
            r = self.execute_aggregation_steps(rule.evaluate_fact_steps(s))
            for x in r:
                if not x["_id"]: rule.set_failed(failed_info=x["info"])

    def check_all_rules(self):
        self.lp.populate_db(self.mongo_client)
        for rule in self.rules:
            self.check_rule(rule)
        self.mongo_client.drop()
        return self.rules


if __name__ == "__main__":
    # Set arguments
    CURDIR = os.getcwd()
    parser = argparse.ArgumentParser(description='Verifies concurrent rules based on log file.')
    parser.add_argument('-l', '--log-file', metavar='logfile', nargs=1,
                        action=FullPaths, help='Log file',
                        default='{}/coriolis_run.log'.format(CURDIR))
    parser.add_argument('-c', '--checkpoints', metavar='checkpoints', nargs=1,
                        action=FullPaths, help='Checkpoint list file',
                        default='{}/rules.chk'.format(CURDIR))
    parser.add_argument('-r', '--rules', metavar='rules', nargs=1,
                        action=FullPaths, help='Rules parsed .py file',
                        default='{}/rules.py'.format(CURDIR))
    parser.add_argument('-v', '--verbose',action='store_true', help="Enables verbosity")
    # Parse arguments
    args = parser.parse_args()
    try:
        exec(open(args.rules).read())
        rc = RuleChecker(all_rules, args.log_file, args.checkpoints)
        all_rules = rc.check_all_rules()
        VerifierPrinter(args.verbose).print_verifier_summary(all_rules)
    except NameError as e:
        print("FATAL: The {} file seems to be corrupt:".format(args.rules))
        print(str(e))
