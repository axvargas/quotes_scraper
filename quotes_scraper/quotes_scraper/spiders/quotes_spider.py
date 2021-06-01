from scrapy import Spider

# title = //h1/a/text()
# quotes = //span[@class="text" and @itemprop="text"]/text()
# authors = //small[@class="author" and @itemprop="author"]/text()
# top_tags = //h2/following-sibling::span/a/text()
# next_page_btn = //ul[@class="pager"]/li[@class="next"]/a/@href


class QuotesSpider(Spider):
    name = "quotes_spider"
    start_urls = [
        'https://quotes.toscrape.com'
    ]
    custom_settings = {
        'FEEDS': {
            'quotes.json': {
                'format': 'json',
                'encoding': 'utf8',
                'fields': ['title', 'quotes', 'top_tags'],
                'overwrite': True
            }
        },
        'MEMUSAGE_LIMIT_MB': 2048,
        'MEMUSAGE_NOTIFY_MAIL': 'axvargas@fiec.espol.edu.ec',
        'CONCURRENT_REQUESTS': 24,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'
    }

    def parseQuotes(self, response, **kwargs):
        if kwargs:
            quotes = kwargs['quotes']
            authors = kwargs['authors']
        quotes.extend(response.xpath(
            '//span[@class="text" and @itemprop="text"]/text()').getall())
        authors.extend(response.xpath(
            '//small[@class="author" and @itemprop="author"]/text()').getall())
        next_page_btn_link = response.xpath(
            '//li[@class="next"]/a/@href').get()

        if next_page_btn_link:
            yield response.follow(
                next_page_btn_link,
                callback=self.parseQuotes,
                cb_kwargs={'quotes': quotes, 'authors': authors}
            )
        else:
            yield {
                'quotes': list(zip(quotes, authors))
            }

    def parse(self, response):
        title = response.xpath('//h1/a/text()').get()
        quotes = response.xpath(
            '//span[@class="text" and @itemprop="text"]/text()').getall()
        authors = response.xpath(
            '//small[@class="author" and @itemprop="author"]/text()').getall()
        top_tags = response.xpath(
            '//h2/following-sibling::span/a/text()').getall()

        # Ask for an attr named top in the execution(via console)
        top = getattr(self, 'top', None)
        if top:
            try:
                top = int(top)
                top_tags = top_tags[:top]
            except:
                print('The argument must be a number')

        yield {
            'title': title,
            'top_tags': top_tags
        }

        next_page_btn_link = response.xpath(
            '//li[@class="next"]/a/@href').get()
        if next_page_btn_link:
            yield response.follow(
                next_page_btn_link,
                callback=self.parseQuotes,
                cb_kwargs={'quotes': quotes, 'authors': authors}
            )
