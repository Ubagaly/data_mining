import scrapy
from urllib.parse import urljoin
from ..loaders import HHLoader
from ..items import HHJobItem, HHCompanyItem



class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']
    _xpath = {
        'pagination': '//div[@data-qa="pager-block"]//a[@data-qa="pager-page"]/@href',
        'vacancy_urls': '//a[@data-qa="vacancy-serp__vacancy-title"]/@href',
        'other_links': '//a[@data-qa="employer-page__employer-vacancies-link"]/@href'
    }
    vacancy_xpath = {
        "title": '//h1[@data-qa="vacancy-title"]/text()',
        "salary": '//p[@class="vacancy-salary"]//text()',
        "description": '//div[@data-qa="vacancy-description"]//text()',
        "skills": '//div[@class="bloko-tag-list"]//span[@data-qa="bloko-tag__text"]/text()',
        "employee_url": '//a[@data-qa="vacancy-company-name"]/@href',
    }

    company_xpath = {
        'company_name': '//h1/span[contains(@class, "company-header-title-name")]/text()',
        'company_url': '//a[contains(@data-qa, "company-site")]/@href',
        'company_desc': '//div[contains(@data-qa, "company-description")]//text()',
        'company_fields': '//div[@class="employer-sidebar-block"]/p/text()',

    }

    def parse(self, response, **kwargs):
        for pag_page in response.xpath(self._xpath['pagination']):
            yield response.follow(pag_page, callback=self.parse)

        for vacancy_page in response.xpath(self._xpath['vacancy_urls']):
            yield response.follow(vacancy_page, callback=self.vacancy_parse)

    def vacancy_parse(self, response, **kwargs):
        loader = HHLoader(item=HHJobItem(), response=response)
        employee_url = urljoin(response.url, response.xpath(self.vacancy_xpath['employee_url']).extract_first())
        loader.add_value('url', response.url)
        loader.add_value('employee_url', employee_url)
        for key, value in self.vacancy_xpath.items():
            loader.add_xpath(key, value)

        yield loader.load_item()

        yield response.follow(response.xpath(self.vacancy_xpath['employee_url']).get(), callback=self.company_parse)

    def company_parse(self, response, **kwargs):
        loader = HHLoader(item=HHCompanyItem(), response=response)
        for key, value in self.company_xpath.items():
            loader.add_xpath(key, value)

        yield loader.load_item()
        other_links = response.xpath(self._xpath['other_links']).get()
        if other_links:
             yield response.follow(other_links, callback=self.parse)





