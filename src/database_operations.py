import os
from pymongo import MongoClient


def get_database(database="sample_mflix"):
    user = os.environ.get("mongoUser")
    password = os.environ.get("mongoPass")
    CONNECTION_STRING = f"mongodb+srv://{user}:{password}@cluster0.yy0jlun.mongodb.net/?retryWrites=true&w=majority"

    client = MongoClient(CONNECTION_STRING)

    return client[database]


def get_collection(collection_name):
    db = get_database()
    return db[collection_name]


def get_document(collection_name, query: dict):
    collection = get_collection(collection_name)
    return collection.find_one(query)


def get_many_documents(collection_name, query: dict):
    collection = get_collection(collection_name)
    return collection.find(query)
