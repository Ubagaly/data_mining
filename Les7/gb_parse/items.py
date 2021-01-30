# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GbParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class InstagramUser(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    list_user = scrapy.Field()
    list_user_id = scrapy.Field()
    status = scrapy.Field()
    data = scrapy.Field()

