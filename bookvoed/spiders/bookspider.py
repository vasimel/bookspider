import psycopg2
from scrapy.exceptions import DropItem
import os
from scrapy_redis.spiders import RedisSpider
import re
import logging


class BookspiderSpider(RedisSpider):
    name = "bookspider"
    #allowed_domains = ["www.bookvoed.ru"]
    #start_urls = ["https://www.bookvoed.ru/catalog"]
    redis_key = 'bookspider:start_urls'

    def __init__(self, *args, **kwargs):
        super(BookspiderSpider, self).__init__(*args, **kwargs)

        # Подключение к базе данных PostgreSQL
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),  # Хост PostgreSQL
            port="6432",  # Порт PostgreSQL
            dbname="web_crawler",  # Имя базы данных
            user="crawler_user",   # Имя пользователя
            password=os.getenv("DB_PASSWORD"),  # Пароль
        )
        self.cursor = self.conn.cursor()

        # Создание таблицы, если она не существует
        self.create_table()

    def create_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS books (
            id SERIAL PRIMARY KEY,
            name TEXT,
            author TEXT,
            price TEXT,
            error TEXT
        );
        """
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def parse(self, response):
        for book in response.css('div.product-card'):
            try:
                # Извлечение данных о книге
                name = book.css('div.product-card::attr(data-product-name)').get()
                author = book.css('span.ui-comma-separated-links__tag::text').get()
                price = book.css('span.price-info__price::text').get().replace(u'\xa0', u'')
                
                # Запись данных в базу данных
                self.save_to_db(name, author, price, error=None)
                
                # Возврат результата парсинга
                yield {
                    'name': name,
                    'author': author,
                    'price': price
                }
            except Exception as e:
                # Если произошла ошибка, записываем ошибку
                name = book.css('div.product-card::attr(data-product-name)').get()
                self.save_to_db(name, author=None, price=None, error=str(e))
                
                yield {
                    'name': name,
                    'error': "Can't parse data"
                }

        # Переход на следующую страницу
        next_page = response.css("a.base-link--active.base-link--exact-active.ui-button.ui-button--size-s.ui-button--color-secondary-blue").attrib['href']
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def save_to_db(self, name, author, price, error):
        """Функция для сохранения данных в базу данных"""
        insert_query = """
        INSERT INTO books (name, author, price, error) 
        VALUES (%s, %s, %s, %s);
        """
        self.cursor.execute(insert_query, (name, author, price, error))
        self.conn.commit()

    def closed(self, reason):
        """Закрытие соединения с базой данных после завершения работы"""
        self.cursor.close()
        self.conn.close()
        super(BookspiderSpider, self).closed(reason)
