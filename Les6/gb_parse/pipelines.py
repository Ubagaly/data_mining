# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
import pymongo


class GbParsePipeline:

    def __init__(self):
        self.db_client = pymongo.MongoClient('mongodb://localhost:27017')

    def process_item(self, item, spider):
        db = self.db_client['insta_parse']
        collection = db[type(item).__name__]
        collection.insert_one(item)
        return item


class GbImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        image = item.get('image', '')
        yield Request(image)

    def item_completed(self, results, item, info):
        item['image'] = [itm[1] for itm in results]
        return item

