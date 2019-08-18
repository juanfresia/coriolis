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
        rule.set_passed_status(True)
        rule_scope = RuleScope.get_default_scope()
        if rule.has_scope():
            rule_scope = self.execute_aggregation_steps(rule.evaluate_scope_steps())
        for s in rule_scope:
            l_first, l_second = RuleScope.parse_scope_log_lines(s)
            r = self.execute_aggregation_steps(FilterByLogLines(l_first, l_second).evaluate() + rule.evaluate_fact_steps(s))
            for x in r:
                if not x["_id"]: rule.set_passed_status(False)


    def check_all_rules(self):
        for rule in self.rules:
            self.check_rule(rule)
        return self.rules




if __name__ == "__main__":
    #print("Run any of the tests.verifier.rule_checker instead")
    lp = LogParser("/vagrant/resources/readers_writers_2.log", "/vagrant/resources/readers_writers.chk")

    rule_1_statement = (
        "# While there are writers, readers cannot enter\n"
        "for every w1, w2=w1, r1, r2=r1:\n"
        "between every writer_enter(w1, r1) and next writer_exit(w2, r2)\n"
        "  for every room=r1 and any r:\n"
        "  reader_enter(r, room) must not happen\n"
    )
    rule_1_scope = RuleScope([
        MatchCheckpoints(["writer_enter", "writer_exit"]),
        RenameArgs(["writer_enter", "writer_exit"], [ ["w1", "r1"], ["w2", "r2"] ]),
        CrossAndGroupByArgs(["writer_enter", "writer_exit"], [ ["w1", "r1"], ["w2", "r2"] ]),
        ImposeIteratorCondition("w1", "=", "w2"),
        ImposeIteratorCondition("r1", "=", "r2"),
        ScopeBetween("writer_enter1", "writer_exit2")
    ])
    rule_1_fact = RuleFact([
        MatchCheckpoints(["reader_enter"]),
        RenameArgs(["reader_enter"], [ ["r", "room"] ]),
        CrossAndGroupByArgs(["reader_enter"], [ ["room"] ]),
        ImposeIteratorCondition("room", "=", "#r1", True),
        CompareResultsQuantity("=", 0),
        ReduceResult()
    ])
    rule_1 = JARLRule(rule_1_statement, rule_1_fact, rule_1_scope)
    rule_1.set_dynamic_scope_arg("r1", True)
    lp.populate_db()
    rc = RuleChecker([rule_1])
    all_rules = rc.check_all_rules()
    lp.db.concu_collection.drop()

    VerifierPrinter(True).print_verifier_summary(all_rules)
