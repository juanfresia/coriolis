#!/usr/bin/env python3

import pymongo # pip3 install pymongo
from verifier.transformation_generator import *
from verifier import log_parser

class RuleChecker:
    def __init__(self):
        self.client = None
        self.db = None
        
    def connect_db(self):
        self.client = pymongo.MongoClient("localhost", 27017)
        self.db = self.client.concu_db
    
    def make_rule_transformations(self, transformations):
        concu_collection = self.db.concu_collection
        return concu_collection.aggregate([t for subt in transformations for t in subt])
    
    def check_rule(self, rule_transformations):
        if self.db is None:
            self.connect_db()
        s = self.make_rule_transformations(rule_transformations)
        print("-+-+-+-+-+-+ Checking rule +-+-+-+-+-+-")
        for x in s:
            print(x)

        

if __name__ == "__main__":
    lp = log_parser.LogParser("/vagrant/resources/pc.log", "/vagrant/resources/pc.chk")
    lp.populate_db()
    
    rc = RuleChecker()

    # RULE 1: Every item is produced only once
    # for every i and any p:
    #   produce(p, i) must happen 1 time
    rule_1 = [
        match_checkpoints(["produce"]),
        rename_args(["produce"], [("p", "i")]),
        cross_group_arg_names(["produce"], ["i"]),
        compare_results_quantity("=", 1),
        #reduce_result()
    ]
    
    # RULE 2: Every item is consumed only once
    # for every i and any c:
    #   consume(c, i) must happen 1 time
    rule_2 = [
        match_checkpoints(["consume"]),
        rename_args(["consume"], [("c", "i")]),
        cross_group_arg_names(["consume"], ["i"]),
        compare_results_quantity("=", 1),
        #reduce_result()
    ]

    # RULE 3: 5 items are produced
    # for any p, i:
    #   produce(p, i) must happen 5 times
    rule_3 = [
        match_checkpoints(["produce"]),
        rename_args(["produce"], [("p", "i")]),
        cross_group_arg_names(["produce"], ["null"]),
        compare_results_quantity("=", 5),
        #reduce_result()
    ]

    # RULE 4: 5 items are consumed
    # for any c, i:
    #   consume(c, i) must happen 5 times
    rule_4 = [
        match_checkpoints(["consume"]),
        rename_args(["consume"], [("c", "i")]),
        cross_group_arg_names(["consume"], ["null"]),
        compare_results_quantity("=", 5),
        #reduce_result()
    ]

    # RULE 5: Every item is produced before consumed
    # for every i and any p, c:
    #   produce(p, i) must precede consume(c, i)
    rule_5 = [
        match_checkpoints(["produce", "consume"]),
        rename_args(["produce", "consume"], [("p", "i1"), ("c", "i2")]),
        cross_group_arg_names(["produce", "consume"], ["i1", "i2"]),
        having_iterators("i1", "=", "i2"),
        compare_results_precedence("produce1", "consume2"),
        #reduce_result()
    ]

    # RULE 6: Items are produced in order
    # for every i, j>i and any p:
    # produce(p, i) must precede produce(p, j)
    rule_6 = [
        match_checkpoints(["produce"]),
        rename_args(["produce", "produce"], [("p", "i"), ("p", "j")]),
        cross_group_arg_names(["produce", "produce"], ["i", "j"]),
        having_iterators("j", ">", "i"),
        compare_results_precedence("produce1", "produce2"),
        #reduce_result()
        ]

    # RULE 7: Items are consumed in order
    # for every i, j>i and any c:
    # consume(c, i) must precede consume(c, j)
    rule_7 = [
        match_checkpoints(["consume"]),
        rename_args(["consume", "consume"], [("c", "i"), ("c", "j")]),
        cross_group_arg_names(["consume", "consume"], ["i", "j"]),
        having_iterators("j", ">", "i"),
        compare_results_precedence("consume1", "consume2"),
        #reduce_result()
        ]


    rc.check_rule(rule_1)
    rc.check_rule(rule_2)
    rc.check_rule(rule_3)
    rc.check_rule(rule_4)
    rc.check_rule(rule_5)
    rc.check_rule(rule_6)
    rc.check_rule(rule_7)

    lp.db.concu_collection.drop()
