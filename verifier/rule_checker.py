#!/usr/bin/env python3

import pymongo # pip3 install pymongo
from common.transformation_generator import *
from verifier.log_parser import LogParser
from verifier.printer import VerifierPrinter
from common.jarl_rule import JARLRule

class RuleChecker:
    def __init__(self, rules_to_check):
        self.client = None
        self.db = None
        self.rules = rules_to_check

    def connect_db(self):
        self.client = pymongo.MongoClient("localhost", 27017)
        self.db = self.client.concu_db
    
    def execute_transformations(self, transformations):
        concu_collection = self.db.concu_collection
        return concu_collection.aggregate(transformations)
    
    def check_rule(self, rule):
        if self.db is None: self.connect_db()
        # TODO: Think how to do this better
        rule.set_passed_status(True)
        if not rule.has_scope():
            s = self.execute_transformations(rule.transformations)
            for x in s:
                #print(x)
                if not x["_id"]: rule.set_passed_status(False)
        else:
            rule_ctx = self.execute_transformations(rule.scope)
            for ctx in rule_ctx:
                s = self.execute_transformations(filter_between_lines(ctx["l1"], ctx["l2"]) + rule.transformations)

                for x in s:
                    if not x["_id"]: rule.set_passed_status(False)

    def check_all_rules(self):
        for rule in self.rules:
            self.check_rule(rule)
        return self.rules


if __name__ == "__main__":
    print("Run any of the tests.verifier.rule_checker instead")
