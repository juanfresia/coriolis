#!/usr/bin/env python3

import pymongo # pip3 install pymongo
from common.aggregation_steps import *
from verifier.log_parser import LogParser
from verifier.printer import VerifierPrinter
from common.jarl_rule import JARLRule, RuleScope, RuleFact

class RuleChecker:
    def __init__(self, rules_to_check):
        self.client = None
        self.db = None
        self.rules = rules_to_check

    def connect_db(self):
        self.client = pymongo.MongoClient("localhost", 27017)
        self.db = self.client.concu_db
    
    def execute_aggregation_steps(self, aggregation_steps):
        if self.db is None: self.connect_db()
        concu_collection = self.db.concu_collection
        return concu_collection.aggregate(aggregation_steps)
    
    def check_rule(self, rule):
        rule.set_passed()
        rule_scope = RuleScope.get_default_scope()
        if rule.has_scope():
            rule_scope = self.execute_aggregation_steps(rule.evaluate_scope_steps())
        for s in rule_scope:
            l_first, l_second = RuleScope.parse_scope_log_lines(s)
            r = self.execute_aggregation_steps(FilterByLogLines(l_first, l_second).evaluate() + rule.evaluate_fact_steps(s))
            for x in r:
                if not x["_id"]: rule.set_failed(x["info"])


    def check_all_rules(self):
        for rule in self.rules:
            self.check_rule(rule)
        return self.rules




if __name__ == "__main__":
    #print("Run any of the tests.verifier.rule_checker instead")
    lp = LogParser("/vagrant/resources/prod_cons_1.log", "/vagrant/resources/prod_cons.chk")

    rule_5_statement = (
        "# Every item is produced before consumed\n"
        "for every i1, i2=i1 and any p, c, :\n"
        "produce(p, i1) must precede consume(c, i2)\n"
    )
    rule_5_fact = RuleFact([
        MatchCheckpoints(["produce", "consume"]),
        RenameArgs(["produce", "consume"], [["p", "i1"], ["c", "i2"]]),
        CrossAndGroupByArgs(["produce", "consume"], [("i1",), ("i2",)]),
        ImposeIteratorCondition("i1", "=", "i2"),
        CompareResultsPrecedence("produce1", "consume2"),
        ReduceResult()
    ])
    rule_5 = JARLRule(rule_5_statement, rule_5_fact)
    lp.populate_db()
    rc = RuleChecker([rule_5])
    all_rules = rc.check_all_rules()
    lp.db.concu_collection.drop()

    VerifierPrinter(True).print_verifier_summary(all_rules)
