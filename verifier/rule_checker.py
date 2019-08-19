#!/usr/bin/env python3

from common.aggregation_steps import *
from verifier.log_parser import LogParser
from verifier.mongo_client import MongoClient
from verifier.printer import VerifierPrinter
from common.jarl_rule import JARLRule, RuleScope, RuleFact

class RuleChecker:
    def __init__(self, rules_to_check, log_file, checkpoint_file):
        self.mongo_client = MongoClient()
        self.rules = rules_to_check
        self.lp = LogParser(log_file, checkpoint_file)
    
    def execute_aggregation_steps(self, aggregation_steps):
        #print("+ + + {}".format(aggregation_steps))
        return self.mongo_client.aggregate(aggregation_steps)
    
    def check_rule(self, rule):
        rule.set_passed()
        rule_scope = RuleScope.get_default_scope()
        if rule.has_scope():
            rule_scope = self.execute_aggregation_steps(rule.evaluate_scope_steps())
        for s in rule_scope:
            #print("1) Current scope: {}".format(s))
            l_first, l_second = RuleScope.parse_scope_log_lines(s)
            r = self.execute_aggregation_steps(FilterByLogLines(l_first, l_second).evaluate() + rule.evaluate_fact_steps(s))
            #print("3) Execution [lines {}-{}]:".format(l_first, l_second))
            for x in r:
                #print(x)
                if not x["_id"]: rule.set_failed(x["info"])
            #print("")

    def check_all_rules(self):
        self.lp.populate_db(self.mongo_client)
        for rule in self.rules:
            self.check_rule(rule)
        self.mongo_client.drop()
        return self.rules


if __name__ == "__main__":
    #print("Run any of the tests.verifier.rule_checker instead")
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

    rc = RuleChecker([ rule_5 ], "/vagrant/resources/prod_cons_1.log", "/vagrant/resources/prod_cons.chk")
    all_rules = rc.check_all_rules()


    VerifierPrinter(True).print_verifier_summary(all_rules)
