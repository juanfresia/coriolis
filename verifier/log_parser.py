#!/usr/bin/env python3

import pymongo # pip3 install pymongo
import checkpoint_table

class LogParser:
    def __init__(self, log_file, checkpoint_file):
        self.checkpoint_table = checkpoint_table.CheckpointTable(checkpoint_file)
        self.log_file = log_file
        self.client = None
        self.db = None
        
    def connect_db(self):
        self.client = pymongo.MongoClient("localhost", 27017)
        self.db = self.client.concu_db
    
    def cast_arg_with_type(self, arg, type):
        if type == "int": return int(arg)
        if type == "string": return "{}".format(arg)
        if type == "float": return float(arg)
        raise Exception("Cannot convert {} to type {}".format(arg, type))
    
    def create_checkpoint_json(self, log_line, checkpoint_name, args):
        json = {"checkpoint": checkpoint_name, "log_line": log_line}
        for i in range(0, len(args)): json["arg_{}".format(i + 1)] = args[i]
        return json
    
    def populate_db(self):
        if self.db is None: self.connect_db()
        concu_collection = self.db.concu_collection

        with open(self.log_file) as lf:
            for i, line in enumerate(lf):
                args = line.split()
                arg_types = self.checkpoint_table.get_checkpoint(args[0]).get_arg_types()
                for j in range(0, len(arg_types)):
                    args[j + 1] = self.cast_arg_with_type(args[j + 1], arg_types[j])
                checkpoint_json = self.create_checkpoint_json(i+1, args[0], args[1:])
                concu_collection.insert_one(checkpoint_json)

if __name__ == "__main__":
    log_parser = LogParser("pc.log", "pc.chk")
    log_parser.populate_db()
