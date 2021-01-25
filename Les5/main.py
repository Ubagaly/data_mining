from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from hh_parse.spiders.hhru import HhruSpider


if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule('hh_parse.settings')
    crawl_process = CrawlerProcess(settings=crawl_settings)
    crawl_process.crawl(HhruSpider)
    crawl_process.start()
