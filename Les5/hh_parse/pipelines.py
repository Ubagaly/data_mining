# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


import pymongo


class HhParsePipeline:

    def __init__(self):
        self.db = pymongo.MongoClient('mongodb://localhost:27017')['hh_parse']

    def process_item(self, item, spider):

        collection = self.db[spider.name]
        collection.insert_one(item)
        return item