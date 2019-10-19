#!/usr/bin/env python3

import multiprocessing

from verifier.log_parser import LogParser
from verifier.mongo_client import MongoClient
from verifier.verifier_printer import VerifierPrinter
from common.jarl_rule import JARLRule, RuleScope, RuleFact
from common.aggregation_steps import *


class RuleChecker:
    def __init__(self, rules_to_check, log_file, checkpoint_file):
        self.rules = rules_to_check
        self.lp = LogParser(log_file, checkpoint_file)
        self.workers = multiprocessing.Pool(processes=2)  # TODO: Decide if this should be a constant or the default CPU amount
        self.mongo_client = MongoClient()

    @staticmethod
    def check_rule(rule):
        client = MongoClient()
        rule.set_passed()
        rule_scope = RuleScope.get_default_scope()
        if rule.has_scope():
            rule_scope = client.aggregate(rule.evaluate_scope_steps())
        for s in rule_scope:
            r = client.aggregate(rule.evaluate_fact_steps(s))
            found_no_results = True  # Have to do this because pymongo cursor has no "len" method
            for x in r:
                found_no_results = False
                if not x["_id"]:
                    rule.set_failed(failed_scope=s, failed_info=x["info"])
            if found_no_results:
                rule.set_default(scope=s, info="No matching checkpoints found!")
        return rule

    def check_all_rules(self):
        self.lp.populate_db(MongoClient())  # TODO: Make populate_db parallel too
        all_rules = self.workers.map(RuleChecker.check_rule, self.rules)
        self.mongo_client.drop()
        return all_rules


def run_verifier(args):
    try:
        exec(open(args.rules).read())
        rc = RuleChecker(locals()['all_rules'], args.log_file, args.checkpoints)
        rules_results = rc.check_all_rules()
        VerifierPrinter(args.verbose).print_verifier_summary(rules_results)
    except NameError as e:
        print("FATAL: The {} file seems to be corrupt:".format(args.rules))
        print(str(e))
