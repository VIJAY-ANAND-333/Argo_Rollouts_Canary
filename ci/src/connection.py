from pymongo import MongoClient
client = MongoClient('mongo URI')
db = client['batman-car-mods']
add_datas = db['add_datas']
