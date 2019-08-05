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
            printer.print_rule(i + 1, rule.text, rule.has_passed(), using_verbosity=False)
            if rule.has_passed(): passed_rules += 1
        printer.print_verifier_summary(len(self.rules), passed_rules)


        

if __name__ == "__main__":
    lp = log_parser.LogParser("/vagrant/resources/pc.log", "/vagrant/resources/pc.chk")
    lp.populate_db()
    
    rc = RuleChecker()

    rule_1_text = (
        "# Every item is produced only once\n"
        "for every i and any p:\n"
        "produce(p, i) must happen 1 time\n"
    )
    rule_1_transformations = [
        match_checkpoints(["produce"]),
        rename_args(["produce"], [("p", "i")]),
        cross_group_arg_names(["produce"], ["i"]),
        compare_results_quantity("=", 1),
        reduce_result()
    ]

    rule_2_text = (
        "# Every item is consumed only once\n"
        "for every i and any c:\n"
        "consume(c, i) must happen 1 time\n"
    )
    rule_2_transformations = [
        match_checkpoints(["consume"]),
        rename_args(["consume"], [("c", "i")]),
        cross_group_arg_names(["consume"], ["i"]),
        compare_results_quantity("=", 1),
        reduce_result()
    ]

    rule_3_text = (
        "# 10 items are produced\n"
        "for any p, i:\n"
        "produce(p, i) must happen 10 times\n"
    )
    rule_3_transformations = [
        match_checkpoints(["produce"]),
        rename_args(["produce"], [("p", "i")]),
        cross_group_arg_names(["produce"], ["null"]),
        compare_results_quantity("=", 10),
        reduce_result()
    ]

    rule_4_text = (
        "# 10 items are consumed\n"
        "for any c, i:\n"
        "consume(c, i) must happen 10 times\n"
    )
    rule_4_transformations = [
        match_checkpoints(["consume"]),
        rename_args(["consume"], [("c", "i")]),
        cross_group_arg_names(["consume"], ["null"]),
        compare_results_quantity("=", 10),
        reduce_result()
    ]

    rule_5_text = (
        "# Every item is produced before consumed\n"
        "for every i and any p, c:\n"
        "produce(p, i) must precede consume(c, i)\n"
    )
    rule_5_transformations = [
        match_checkpoints(["produce", "consume"]),
        rename_args(["produce", "consume"], [("p", "i1"), ("c", "i2")]),
        cross_group_arg_names(["produce", "consume"], ["i1", "i2"]),
        having_iterators("i1", "=", "i2"),
        compare_results_precedence("produce1", "consume2"),
        reduce_result()
    ]

    rule_6_text = (
        "# Items are produced in order\n"
        "for every i, j>i and any p:\n"
        "produce(p, i) must precede produce(p, j)\n"
    )
    rule_6_transformations = [
        match_checkpoints(["produce"]),
        rename_args(["produce", "produce"], [("p", "i"), ("p", "j")]),
        cross_group_arg_names(["produce", "produce"], ["i", "j"]),
        having_iterators("j", ">", "i"),
        compare_results_precedence("produce1", "produce2"),
        reduce_result()
        ]

    rule_7_text = (
        "# Items are consumed in order\n"
        "for every i, j>i and any c:\n"
        "consume(c, i) must precede consume(c, j)\n"
    )
    rule_7_transformations = [
        match_checkpoints(["consume"]),
        rename_args(["consume", "consume"], [("c", "i"), ("c", "j")]),
        cross_group_arg_names(["consume", "consume"], ["i", "j"]),
        having_iterators("j", ">", "i"),
        compare_results_precedence("consume1", "consume2"),
        reduce_result()
        ]

    rule_8_text = (
        "# The buffer size is 5\n"
        "between produce and next consume:\n"
        "for any p, i:\n"
        "produce(p, i) must happen at most 5 times\n"
    )
    rule_8_between = make_between_clause("produce", "consume", True)
    rule_8_transformations = [
        match_checkpoints(["produce"]),
        rename_args(["produce"], [("p", "i")]),
        cross_group_arg_names(["produce"], ["null"]),
        compare_results_quantity("<=", 5),
        reduce_result()
    ]

    rc.add_rule(JARLRule(rule_1_text, rule_1_transformations))
    rc.add_rule(JARLRule(rule_2_text, rule_2_transformations))
    rc.add_rule(JARLRule(rule_3_text, rule_3_transformations))
    rc.add_rule(JARLRule(rule_4_text, rule_4_transformations))
    rc.add_rule(JARLRule(rule_5_text, rule_5_transformations))
    rc.add_rule(JARLRule(rule_6_text, rule_6_transformations))
    rc.add_rule(JARLRule(rule_7_text, rule_7_transformations))
    rc.add_rule(JARLRule(rule_8_text, rule_8_transformations, rule_8_between))

    rc.check_all_rules()
    lp.db.concu_collection.drop()
