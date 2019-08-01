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
            print(x)

        

if __name__ == "__main__":
    lp = log_parser.LogParser("pc.log", "pc.chk")
    lp.populate_db()
    
    rc = RuleChecker()
    # RULE 6: Items are produced in order
    # for every i, j>i and any p:
    # produce(p, i) must precede produce(p, j)
    rule_6 = [
        match_checkpoint("produce"),
        rename_args(["produce", "produce"], [("p", "i"), ("p", "j")]),
        cross_group_arg_names(["produce", "produce"], ["i", "j"]),
        having_greater_iterator("i", "j"),
        compare_results_precedence("produce1", "produce2"),
        ]
    rc.check_rule(rule_6)
    # RULE 4: Every item is produced before consumed
    # for every i and any p, c:
    #   produce(p, i) must precede consume(c, i)
    rule_4 = [
        match_checkpoints(["produce", "consume"]),
        rename_args(["produce", "consume"], [("p", "i"), ("c", "i")]),
        group_by_arg_names(["i"]),
        #compare_results_precedence("produce", "consume"),
        #reduce_result()
        ]
    #rc.check_rule(rule_4)

    lp.db.concu_collection.drop()
