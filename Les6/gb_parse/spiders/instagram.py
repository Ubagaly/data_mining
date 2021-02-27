import scrapy
import json
import datetime as dt
from ..items import InstagramPost, InstagramTag



class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    graphql_url = '/graphql/query/'
    start_urls = ['https://www.instagram.com/']
    tags_names = []
    query = {
        'posts': '56a7068fea504063273cc2120ffd54f3',
        'tags': "9b498c08113f1e09617a1703c22b2f32",
    }

    def __init__(self, login, enc_password, start_tags: list, *args, **kwargs):
        self.start_tags = start_tags
        self.tag_urls = [f'/explore/tags/{tag}/?__a=1' for tag in self.start_tags]
        self.login = login
        self.enc_password = enc_password
        super().__init__(*args, **kwargs)

    @staticmethod
    def script_data(response) -> dict:
        script = response.xpath('//script[contains(text(), "window._sharedData =")]/text()').get()
        return json.loads(script.replace("window._sharedData =", '')[:-1])


    def parse(self, response, **kwargs):

        try:
            data = self.script_data(response)
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
                for tag in self.tag_urls:
                    yield response.follow(tag, callback=self.tag_parse)

    def tag_parse(self, response):
        js_data = response.json()
        end_cursor = js_data['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']

        tag = js_data["graphql"]["hashtag"]
        tag_name = tag['name']
        if tag_name not in self.tags_names:
            self.tags_names.append(tag_name)
            yield InstagramTag(
                date_parse=dt.datetime.utcnow(),
                data={
                    'id': tag['id'],
                    'name': tag['name'],
                    'post_count': tag['edge_hashtag_to_media']['count']
                },
                image=tag['profile_pic_url'])

        if js_data['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page']:
            yield response.follow(f'https://www.instagram.com/explore/tags/{tag["name"]}/?__a=1&max_id={end_cursor}',
                                  callback=self.tag_parse)

        for edge in js_data['graphql']['hashtag']['edge_hashtag_to_media']['edges']:
            yield InstagramPost(date_parse=dt.datetime.utcnow(), data=edge['node'], image=edge['node']['display_url'])