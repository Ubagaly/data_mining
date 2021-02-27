import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.instagram import InstagramSpider

if __name__ == '__main__':
    dotenv.load_dotenv('.env')
    hash_tags = ['python', 'dataanalysis', 'програм']

    crawl_settings = Settings()
    crawl_settings.setmodule('gb_parse.settings')
    crawl_proc = CrawlerProcess(settings=crawl_settings)

    crawl_proc.crawl(InstagramSpider,
                     start_tags=hash_tags,
                     login=os.getenv('LOGIN'),
                     enc_password=os.getenv('ENC_PASSWORD'))
    crawl_proc.start()