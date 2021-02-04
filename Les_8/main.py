import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.instagram_1 import Instagram1Spider


if __name__ == '__main__':
    dotenv.load_dotenv('.env')
    user_1 = ['mixail_bagaly']
    user_2 = 'skladupakovki'
    crawl_settings = Settings()
    crawl_settings.setmodule('gb_parse.settings')
    crawl_proc = CrawlerProcess(settings=crawl_settings)

    crawl_proc.crawl(Instagram1Spider,
                     start_users=user_1,
                     end_usr=user_2,
                     login=os.getenv('LOGIN1'),
                     enc_password=os.getenv('ENC_PASSWORD1'))

    crawl_proc.start()
