#!/usr/bin/env python3

import pymongo # pip3 install pymongo
from verifier.transformation_generator import *
from verifier import log_parser, printer
from common.jarl_rule import *

class RuleChecker:
    def __init__(self):
        self.client = None
        self.db = None
        self.rules = []

    def add_rule(self, rule):
        self.rules.append(rule)

    def connect_db(self):
        self.client = pymongo.MongoClient("localhost", 27017)
        self.db = self.client.concu_db
    
    def execute_transformations(self, transformations):
        concu_collection = self.db.concu_collection
        return concu_collection.aggregate([t for subt in transformations for t in subt])
    
    def check_rule(self, rule):
        if self.db is None:
            self.connect_db()
        # TODO: Think how to do this better
        rule.set_passed_status(True)
        if not rule.has_between_clause():
            s = self.execute_transformations(rule.transformations)
            for x in s:
                if not x["_id"]: rule.set_passed_status(False)
        else:
            rule_ctx = self.execute_transformations(rule.between_clause)
            for ctx in rule_ctx:
                s = self.execute_transformations([ filter_between_lines(ctx["l1"], ctx["l2"]) ] + rule.transformations)

                for x in s:
                    if not x["_id"]: rule.set_passed_status(False)

    def check_all_rules(self):
        printer.print_verifier_start()
        passed_rules = 0
        for i, rule in enumerate(self.rules):
            self.check_rule(rule)
            printer.print_rule(i + 1, rule.text, rule.has_passed(), using_verbosity=True)
            if rule.has_passed(): passed_rules += 1
        printer.print_verifier_summary(len(self.rules), passed_rules)


        

if __name__ == "__main__":
    lp = log_parser.LogParser("/vagrant/examples/smokers/smokers.log", "/vagrant/examples/smokers/smokers.chk")
    lp.populate_db()
    
    rc = RuleChecker()

    rule_1_text = (
            "Only one smoker smokes at a time\n"
            "between agent_wake and next agent_wake:\n"
            "    for any s:\n"
            "        smoker_smoke(s) must happen 1 time\n"
    )
    rule_1_between = make_between_clause("agent_wake", "agent_wake", True)
    rule_1_transformations = [
        match_checkpoints(["smoker_smoke"]),
        rename_args(["smoker_smoke"], [("s")]),
        cross_group_arg_names(["smoker_smoke"], ["null"]),
        compare_results_quantity("=", 1),
        reduce_result()
    ]

    rule_2_text = (
            "Smoker that smoked could really smoke\n"
            "between agent_wake and next smoker_smoke:\n"
            "    for any s, e:\n"
            "        smoker_take_element(s, e) must happen 2 times\n"
    )
    rule_2_between = make_between_clause("agent_wake", "smoker_smoke", True)
    rule_2_transformations = [
        match_checkpoints(["smoker_take_element"]),
        rename_args(["smoker_take_element"], [("s", "e")]),
        cross_group_arg_names(["smoker_take_element"], ["null"]),
        #having_iterators("s", "=", "e"),
        compare_results_quantity("=", 2),
        reduce_result()
    ]

    rc.add_rule(JARLRule(rule_1_text, rule_1_transformations, rule_1_between))
    rc.add_rule(JARLRule(rule_2_text, rule_2_transformations, rule_2_between))

    rc.check_all_rules()
    lp.db.concu_collection.drop()
