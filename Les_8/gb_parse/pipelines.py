# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import pymongo


class GbParsePipeline:

    def __init__(self):
        self.db_client = pymongo.MongoClient('mongodb://localhost:27017')

    def process_item(self, item, spider):
        db = self.db_client['instagramm_users_parse']
        collection = db[type(item).__name__]
        collection.insert_one(item)
        return item