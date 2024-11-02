import scrapy


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["www.bookvoed.ru"]
    start_urls = ["https://www.bookvoed.ru/catalog"]

    def parse(self, response):
        for book in response.css('div.product-card'):
            try:
                yield {
                    'name': book.css('div.product-card::attr(data-product-name)').get(),
                    'author': book.css('span.ui-comma-separated-links__tag::text').get(),
                    'price': book.css('span.price-info__price::text').get().replace(u'\xa0', u'')
                }
            except:
                yield {
                    'name': book.css('div.product-card::attr(data-product-name)').get(),
                    'error': "Can't parse data"
                }

        next_page = response.css("a.base-link--active.base-link--exact-active.ui-button.ui-button--size-s.ui-button--color-secondary-blue").attrib['href']
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)