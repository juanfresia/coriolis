#!/usr/bin/env python3
import pymongo
from common.utils import *


class MongoClientFactory:
    def __init__(self, host=MONGO_DEFAULT_HOST, port=MONGO_DEFAULT_PORT):
        self.host = host
        self.port = port

    def new_mongo_client(self):
        return MongoClient(self.host, self.port)


class MongoClient:
    def __init__(self, host=MONGO_DEFAULT_HOST, port=MONGO_DEFAULT_PORT):
        self.client = pymongo.MongoClient(host, port)
        self.concu_collection = self.client.concu_db.concu_collection

    def aggregate(self, pipeline_steps):
        return self.concu_collection.aggregate(pipeline_steps, allowDiskUse=True)

    def insert_one(self, document):
        self.concu_collection.insert_one(document)

    def drop(self):
        self.concu_collection.drop()
