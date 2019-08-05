#!/usr/bin/env python3

import pymongo # pip3 install pymongo
from colorama import Fore, Back, Style # pip3 install colorama
from verifier.transformation_generator import *
from verifier import log_parser

class RuleChecker:
    def __init__(self):
        self.client = None
        self.db = None
        self.passed_rules = 0
        self.total_rules = 0
        print("=-=-=-=-=-=-=-=-=-=-=-=- CHECKING RULES -=-=-=-=-=-=-=-=-=-=-=-=")

    def print_rule(self, rule_text, passed=False):
        rule_fore = Fore.GREEN if passed else Fore.RED
        print(rule_fore + rule_text + Style.RESET_ALL)

    def print_summary(self):
        print("=-=-=-=-=-=-=-=-=-=-=-=-=-  SUMMARY  -=-=-=-=-=-=-=-=-=-=-=-=-=")
        print("")
        summary_fore = Fore.GREEN if self.passed_rules == self.total_rules else Fore.RED
        summary = "{} rules, {} assertions, {} failures".format(self.total_rules, self.passed_rules, self.total_rules - self.passed_rules)
        print(summary_fore + summary + Style.RESET_ALL)

    def connect_db(self):
        self.client = pymongo.MongoClient("localhost", 27017)
        self.db = self.client.concu_db
    
    def execute_transformations(self, transformations):
        concu_collection = self.db.concu_collection
        return concu_collection.aggregate([t for subt in transformations for t in subt])
    
    def check_rule(self, rule, rule_transformations, rule_between=None):
        if self.db is None:
            self.connect_db()

        rule_passed = True
        if rule_between is None:
            s = self.execute_transformations(rule_transformations)
            for x in s:
                if not x["_id"]: rule_passed = False
        else:
            rule_ctx = self.execute_transformations(rule_between)
            for ctx in rule_ctx:
                s = self.execute_transformations([ filter_between_lines(ctx["l1"], ctx["l2"]) ] + rule_transformations)

                for x in s:
                    if not x["_id"]: rule_passed = False

        if rule_passed: self.passed_rules += 1
        self.total_rules += 1
        self.print_rule(rule, rule_passed)

        

if __name__ == "__main__":
    lp = log_parser.LogParser("/vagrant/resources/pc.log", "/vagrant/resources/pc.chk")
    lp.populate_db()
    
    rc = RuleChecker()

    rule_1 = (
        "# RULE 1: Every item is produced only once\n"
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

    rule_2 = (
        "# RULE 2: Every item is consumed only once\n"
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

    rule_3 = (
        "# RULE 3: 10 items are produced\n"
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

    rule_4 = (
        "# RULE 4: 10 items are consumed\n"
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

    rule_5 = (
        "# RULE 5: Every item is produced before consumed\n"
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

    rule_6 = (
        "# RULE 6: Items are produced in order\n"
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

    rule_7 = (
        "# RULE 7: Items are consumed in order\n"
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

    rule_8 = (
        "# RULE 8: The buffer size is 5\n"
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


    rc.check_rule(rule_1, rule_1_transformations)
    rc.check_rule(rule_2, rule_2_transformations)
    rc.check_rule(rule_3, rule_3_transformations)
    rc.check_rule(rule_4, rule_4_transformations)
    rc.check_rule(rule_5, rule_5_transformations)
    rc.check_rule(rule_6, rule_6_transformations)
    rc.check_rule(rule_7, rule_7_transformations)
    rc.check_rule(rule_8, rule_8_transformations, rule_8_between)

    rc.print_summary()
    lp.db.concu_collection.drop()
