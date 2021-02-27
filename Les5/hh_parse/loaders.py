from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, Join, MapCompose
from .items import HHCompanyItem, HHJobItem

# def get_salary(salary, **kwargs):
#     salary = str(salary)
#     salary = salary.replace("\xa", "")
#     return salary

class HHLoader(ItemLoader):
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_in = ''.join
    #salary_in = MapCompose(get_salary)
    salary_out = TakeFirst()
    description_in = ''.join
    description_out = TakeFirst()
    skills_out = TakeFirst()
    employee_url_out = TakeFirst()
    company_name_out = TakeFirst()
    company_url_out = TakeFirst()
    company_desc_out = TakeFirst()
    company_fields = TakeFirst()

