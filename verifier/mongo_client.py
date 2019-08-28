#!/usr/bin/env python3
import pymongo

class MongoClient:
    def __init__(self, host="localhost", port=27017):
        self.client = pymongo.MongoClient(host, port)
        self.concu_collection = self.client.concu_db.concu_collection

    def aggregate(self, pipeline_steps):
        return self.concu_collection.aggregate(pipeline_steps, allowDiskUse=True)

    def insert_one(self, document):
        self.concu_collection.insert_one(document)

    def drop(self):
        self.concu_collection.drop()