# -*- coding: utf-8 -*-

from Model.neo_models import Neo4j
from Model.mongo_model import Mongo

neo_con = Neo4j()  # 预加载neo4j
neo_con.connectDB()
print('neo4j connected!')

# 预加载mongodb
mongo = Mongo()
mongo.makeConnection()
print("mongodb connected")
# 连接数据库
mongodb = mongo.getDatabase("agriknow")
print("connect to agriknow")
# 得到collection
collection = mongo.getCollection("train_data")
print("get connection train_data")

testDataCollection = mongo.getCollection("test_data")
print("get connection test_data")
