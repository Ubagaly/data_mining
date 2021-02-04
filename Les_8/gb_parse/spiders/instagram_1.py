import scrapy
import json
from anytree import Node, RenderTree
from collections import defaultdict, deque
from scrapy.exceptions import CloseSpider



class Instagram1Spider(scrapy.Spider):
    name = 'instagram_1'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    graphql_url = '/graphql/query/'
    query_hash = {
        'edge_followed_by': '5aefa9893005572d237da5068082d8d5',
        'edge_follow': '3dec7e2c57367ef3da3d987d89f9dbc8',
    }

    user_list = defaultdict(lambda: defaultdict(list))
    tree_dict = {}


    def __init__(self, login, enc_password, end_usr, start_users: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users = start_users
        self.end_user = end_usr
        self.tree_dict[self.users[0]] = Node(self.users[0])
        self.scan_que = deque()
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

    def user_parse(self, response, **kwargs):

        json_data = self.js_script(response)
        user_id = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['id']
        user_name = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['username']
        followed_by_count = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_followed_by']['count']
        follow_count = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_follow']['count']
        for follow in self.query_hash.keys():
            variables = {"id": user_id,
                         "include_reel": True,
                         "fetch_mutual": False,
                         "first": 100,
                         "after": ''}
            url = f'{self.graphql_url}?query_hash={self.query_hash[follow]}&variables={json.dumps(variables)}'

            yield response.follow(url, callback=self.follow_parse,
                                  meta={'user_id': user_id,
                                        'user_name': user_name,
                                        'follow': follow,
                                        'followed_by_count': followed_by_count,
                                        'follow_count': follow_count,
                                        'parent': response.meta.get('parent')})

    def follow_parse(self, response, **kwargs):
        data = response.json()
        end_cursor = data['data']['user'][response.meta['follow']]['page_info']['end_cursor']
        user_name = response.meta["user_name"]
        if data['data']['user'][response.meta['follow']]['page_info']['has_next_page']:
            follow = response.meta['follow']
            variables = {"id": response.meta['user_id'],
                         "include_reel": True,
                         "fetch_mutual": False,
                         "first": 100,
                         "after": end_cursor}
            url = f'{self.graphql_url}?query_hash={self.query_hash[follow]}&variables={json.dumps(variables)}'
            yield response.follow(url, callback=self.follow_parse, meta=response.meta)

        for edge in data['data']['user'][response.meta['follow']]['edges']:
            if response.meta['follow'] == 'edge_follow':
                self.user_list[user_name]['follows'].append(edge['node']['username'])
            else:
                self.user_list[user_name]['followed_by'].append(edge['node']['username'])

        a = response.meta['followed_by_count']-1

        if (len(self.user_list[user_name]["follows"]) == response.meta['follow_count']) and \
                (len(self.user_list[user_name]["followed_by"]) >= a):
            followed_list = []
            for user in self.user_list[user_name]["followed_by"]:
                if user in self.user_list[user_name]["follows"]:
                    followed_list.append(user)
                    if user not in self.tree_dict.keys():
                        self.tree_dict[user] = Node(user, parent=self.tree_dict[user_name])

            for user in followed_list:
                if user == self.end_user:
                    print('Path')
                    print(' -> '.join([node.name for node in self.tree_dict[self.end_user].iter_path_reverse()]))
                    raise CloseSpider('Users found!')


            for user in followed_list:
                yield response.follow(f'/{user}/', callback=self.user_parse,
                                          meta={'parent': user_name})


















