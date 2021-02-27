import scrapy
import json
import datetime as dt
from ..items import InstagramUser


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    graphql_url = '/graphql/query/'
    query_hash = {
        'edge_followed_by': '5aefa9893005572d237da5068082d8d5',
        'edge_follow': '3dec7e2c57367ef3da3d987d89f9dbc8',
    }

    def __init__(self, login, enc_password, start_users: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users = start_users
        self.start_users = [f'/{user}/' for user in self.users]
        self.login = login
        self.enc_password = enc_password

    @staticmethod
    def js_script(response) -> dict:
        script = response.xpath('//script[contains(text(), "window._sharedData =")]/text()').get()
        return json.loads(script.replace("window._sharedData =", '')[:-1])

    def parse(self, response, **kwargs):

        try:
            data = self.js_script(response)
            yield scrapy.FormRequest(
                self.login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.login,
                    'enc_password': self.enc_password
                },
                headers={
                    'X-CSRFToken': data['config']['csrf_token']
                }
            )
        except AttributeError:
            if response.json().get('authenticated'):
                for user in self.start_users:
                    yield response.follow(user, callback=self.user_parse)


    def user_parse(self, response):
        json_data = self.js_script(response)
        print(json_data)
        user_id = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['id']
        user_name = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['username']
        for follow in self.query_hash.keys():
            variables = {"id": user_id,
                         "include_reel": True,
                         "fetch_mutual": False,
                         "first": 100,
                         "after": ''}
            url = f'{self.graphql_url}?query_hash={self.query_hash[follow]}&variables={json.dumps(variables)}'

            yield response.follow(url, callback=self.follow_parse,
                                  meta={'user_id': user_id, 'user_name': user_name, 'follow': follow})

    def follow_parse(self, response):
        data = response.json()
        end_cursor = data['data']['user'][response.meta['follow']]['page_info']['end_cursor']
        if data['data']['user'][response.meta['follow']]['page_info']['has_next_page']:
            follow = response.meta['follow']
            variables = {"id": response.meta['user_id'],
                         "include_reel": True,
                         "fetch_mutual": False,
                         "first": 100,
                         "after": end_cursor}
            url = f'{self.graphql_url}?query_hash={self.query_hash[follow]}&variables={json.dumps(variables)}'
            yield response.follow(url, callback=self.follow_parse, meta=response.meta)
        users = data['data']['user'][response.meta['follow']]['edges']
        for user in users:
            yield InstagramUser(date_parse=dt.datetime.utcnow(),
                                list_user = response.meta['user_name'],
                                list_user_id = response.meta['user_id'],
                                status = self.get_status(response.meta['follow']),
                                data={
                                    'user_id': user['node']['id'],
                                    'username': user['node']['username'],
                                    'full_name': user['node']['full_name'],
                                    'profile_pic_url': user['node']['profile_pic_url']
                                },)

    def get_status(self, status):
        if status == 'edge_followed_by':
            status = 'subscribers'
        else: status = 'subscriptions'
        return status
