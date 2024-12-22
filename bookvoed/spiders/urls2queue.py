import scrapy
import re
import logging
import redis

class Urls2queueSpider(scrapy.Spider):
    name = "urls2queue"
    allowed_domains = ["www.bookvoed.ru"]
    start_urls = ["https://www.bookvoed.ru/catalog"]

    def parse(self, response):
        last_page = 0
        for page in response.css('a.base-link--active.base-link--exact-active.app-pagination__item.base-link'):
            result = re.search(r'\d+$', page.attrib['href'])
            if result is not None:
                num = int(result.group(0))
                if num > last_page:
                        last_page = num
        
        redisClient = redis.from_url('redis://127.0.0.1:6379')

        #for i in range(last_page):
        for i in range(100):
             redisClient.lpush('bookspider:start_urls', 'https://www.bookvoed.ru/catalog?page=' + str(i+1))
