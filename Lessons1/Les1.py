import time
import json
import requests

class StatusCodeError(Exception):
    def __init__(self, txt):
        self.txt = txt


class Parser5ka:
    _params = {
        'records_per_page': None,
    }
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }

    def __init__(self, start_url, product_url):
        self.start_url = start_url
        self.product_url = product_url

    def _get_response(self, url, **kwargs):
        while True:
            try:
                response = requests.get(url, **kwargs)
                if response.status_code != 200:
                    raise StatusCodeError(f'status {response.status_code}')
                return response
            except (requests.exceptions.ConnectTimeout,
                    StatusCodeError):
                time.sleep(0.1)

    def run(self):
        response = self._get_response(self.start_url, headers=self.headers)
        for categor in response.json():
            data = {
                "name": categor['parent_group_name'],
                'code': categor['parent_group_code'],
                "products": [],
            }

            self._params['categories'] = categor['parent_group_code']

            for products in self.parse(self.product_url):
                data["products"].extend(products)
            self.save_file(
                data,
                categor['parent_group_code']
             )


    def parse(self, url):
        params = self._params
        while url:
            response = self._get_response(url, params = params, headers=self.headers)
            data: dict = response.json()
            url = data['next']
            yield data.get('results', [])

    def save_file(self, data, name):
        with open(f'{name}.json', 'w', encoding='UTF-8') as file:
            json.dump(data, file, ensure_ascii=False)


if __name__ == '__main__':
    parser = Parser5ka('https://5ka.ru/api/v2/categories/', 'https://5ka.ru/api/v2/special_offers/')
    parser.run()