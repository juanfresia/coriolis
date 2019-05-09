#!/usr/bin/env python3

import pymongo # pip3 install pymongo
from transformation_generator import *
import log_parser

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
        for x in s:
            if(x["_id"] == False):
                print("--- RULE FAILED ---")
                return
        print("--- RULE PASSED ---")

        

if __name__ == "__main__":
    lp = log_parser.LogParser("pc.log", "pc.chk")
    lp.populate_db()
    
    rc = RuleChecker()
    # RULE 1: Every item is produced only once
    # for every i and any p:
    #   produce(p, i) must happen 1 time
    rule_1 = [ 
        match_checkpoint("produce"), 
        rename_args(["produce"], [("p", "i")]),
        group_by_arg_name("i"),
        compare_results_equal(1),
        reduce_result()
        ]
    rc.check_rule(rule_1)
    # RULE 2: 10 items are produced
    # for any p, i:
    #   produce(p, i) must happen 10 times
    rule_2 = [ 
        match_checkpoint("produce"), 
        rename_args(["produce"], [("p", "i")]),
        group_by_arg_name("null"),
        compare_results_equal(10),
        reduce_result()
        ]
    rc.check_rule(rule_2)
    # RULE 3: 10 items are consumed
    # for any c, i:
    #   consume(c, i) must happen 10 times
    rule_3 = [ 
        match_checkpoint("consume"), 
        rename_args(["consume"], [("c", "i")]),
        group_by_arg_name("null"),
        compare_results_equal(10),
        reduce_result()
        ]
    rc.check_rule(rule_3)
    # RULE 4: Every item is produced before consumed
    # for every i and any p, c:
    #   produce(p, i) must precede consume(c, i)
    rule_4 = [ 
        match_checkpoints(["produce", "consume"]), 
        rename_args(["produce", "consume"], [("p", "i"), ("c", "i")]),
        group_by_arg_name("i"),
        compare_results_precedence("produce", "consume"),
        reduce_result()
        ]
    rc.check_rule(rule_4)
    
    lp.db.concu_collection.drop()
