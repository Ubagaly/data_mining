import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.instagram import InstagramSpider

if __name__ == '__main__':
    dotenv.load_dotenv('.env')
    users = ['skladupakovki', 'skidki_po_krasnodary']

    crawl_settings = Settings()
    crawl_settings.setmodule('gb_parse.settings')
    crawl_proc = CrawlerProcess(settings=crawl_settings)

    crawl_proc.crawl(InstagramSpider,
                     start_users=users,
                     login=os.getenv('LOGIN'),
                     enc_password=os.getenv('ENC_PASSWORD'))
    crawl_proc.start()