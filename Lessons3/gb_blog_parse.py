import os
import time
import datetime as dt
import requests
import bs4
from urllib.parse import urljoin
from dotenv import load_dotenv

from database import Database

# todo обойти пагинацию блога
# todo обойти каждую статью
# todo Извлечь данные: Url, Заголовок, имя автора, url автора, список тегов (url, имя)
class StatusCodeError(Exception):
    def __init__(self, txt):
        self.txt = txt

class GbParse:
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }

    def __init__(self, start_url, database):
        self.start_url = start_url
        self.done_urls = set()
        self.tasks = [self.parse_task(self.start_url, self.pag_parse)]
        self.done_urls.add(self.start_url)
        self.database = database


    def _get_soup(self, *args, **kwargs):
        response = requests.get(*args, **kwargs)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        return soup

    def parse_task(self, url, callback):
        def wrap():
            soup = self._get_soup(url)
            return callback(url, soup)

        return wrap

    def run(self):
        for task in self.tasks:
            result = task()
            if result:

                self.database.create_post(result)

    def post_parse(self, url, soup: bs4.BeautifulSoup) -> dict:
        author_name_tag = soup.find('div', attrs={'itemprop': 'author'})
        data = {
            'post_data': {
                'url': url,
                'title': soup.find('h1', attrs={'class': 'blogpost-title'}).text,
                'image_url': urljoin(self.start_url, soup.find("img").attrs.get("src")),
                'data_create': self.data_from(soup.find("time").attrs.get("datetime"))},

            'author': {
                'url': urljoin(url, author_name_tag.parent.get('href')),
                'name': author_name_tag.text,
            },
            'tags': [{
                'name': tag.text,
                'url': urljoin(url, tag.get('href')),
            } for tag in soup.find_all('a', attrs={'class': 'small'})],

            'comments': self.comments_parse(soup.find("comments").attrs.get("commentable-id")),
        }

        return data

    def data_from (self, text):
        data_list = text.split("-")
        data_list[2] = int(data_list[2][0:2])
        return dt.datetime(
                     year=int(data_list[0]),
                     day=int(data_list[2]),
                     month=int(data_list[1]),
                    )

    def _get_response(self, url, **kwargs):
        while True:
            #try:         Почему то с отловом ошибок код не работает
            response = requests.get(url, **kwargs)
                # if response.status_code != 200:
                #     raise StatusCodeError(f'status {response.status_code}')
            return response
            # except (requests.exceptions.ConnectTimeout,
            #         StatusCodeError):
            #     time.sleep(0.1)

    def comments_parse(self, commentable_id):
        comment_id = commentable_id
        comment_url = f"https://geekbrains.ru/api/v2/comments?commentable_type=Post&commentable_id={comment_id}&order=desc"
        commenttable = []
        response = self._get_response(comment_url, headers=self.headers)
        for com in response.json():
            comment = {
                "number": com['comment']['id'],
                "user": f"{com['comment']['user']['first_name']} {com['comment']['user']['last_name']}",
                "text_post": com['comment']['body'],
            }
            commenttable.append(comment)
        return commenttable


    def pag_parse(self, url, soup: bs4.BeautifulSoup):
        gb_pagination = soup.find('ul', attrs={'class': 'gb__pagination'})
        a_tags = gb_pagination.find_all('a')
        for a in a_tags:
            pag_url = urljoin(url, a.get('href'))
            if pag_url not in self.done_urls:
                task = self.parse_task(pag_url, self.pag_parse)
                self.tasks.append(task)
                self.done_urls.add(pag_url)

        posts_urls = soup.find_all('a', attrs={'class': 'post-item__title'})
        for post_url in posts_urls:
            post_href = urljoin(url, post_url.get('href'))
            if post_href not in self.done_urls:
                task = self.parse_task(post_href, self.post_parse)
                self.tasks.append(task)
                self.done_urls.add(post_href)


if __name__ == '__main__':
    load_dotenv('.env')
    parser = GbParse('https://geekbrains.ru/posts',
                     Database(os.getenv('SQL_DB')))
    parser.run()