# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HhParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class HHJobItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    employee_url = scrapy.Field()

class HHCompanyItem(scrapy.Item):
    _id = scrapy.Field()
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    company_desc = scrapy.Field()
    company_fields = scrapy.Field()


