#!/usr/bin/env python3

import multiprocessing
import os
import copy

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


def _file_is_coriolis_log(filename):
    return filename.endswith(".log")


def _get_all_coriolis_logs(logs_path):
    all_logs = []
    if os.path.isfile(logs_path) and _file_is_coriolis_log(logs_path):
        all_logs.append(logs_path)
    elif os.path.isdir(logs_path):
        for dirpath, _, files in os.walk(logs_path):
            for file in files:
                this_file = os.path.join(dirpath, file)
                if _file_is_coriolis_log(this_file):
                    all_logs.append(this_file)

    if len(all_logs) == 0:
        raise Exception("Could not find any coriolis logs on {}".format(logs_path))
    return all_logs


def _full_log_has_passed(all_rules):
    return all([rule.has_passed() for rule in all_rules])


def run_verifier(args, rules):
    printer = VerifierPrinter(args.verbose)
    printer.print_checking_rules()
    try:
        logs_names = _get_all_coriolis_logs(args.log_path)
        logs_passed = [False] * len(logs_names)

        for i in range(len(logs_names)):
            all_rules = copy.deepcopy(rules)
            rc = RuleChecker(all_rules, logs_names[i], args.checkpoints)
            rules_results = rc.check_all_rules()
            printer.print_logfile_summary(rules_results, logs_names[i])
            logs_passed[i] = _full_log_has_passed(rules_results)

        printer.print_verifier_summary(logs_names, logs_passed)
    except Exception as e:
        printer.print_error("{}".format(e))
