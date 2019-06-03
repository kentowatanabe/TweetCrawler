# -*- coding: utf-8 -*-
import scrapy
import json
from urllib.parse import quote

from TweetCrawler.items import Tweet


class TweetSpider(scrapy.Spider):
    """Tweet Crawler."""

    name = 'TweetSpider'
    allowed_domains = ['twitter.com']

    def __init__(self, query='', *args, **kwargs):
        """Initialize."""
        super(TweetSpider, self).__init__(*args, **kwargs)
        self.query = query
        self.base_url = 'https://twitter.com/'
        self.url = self.base_url + 'i/profiles/show/%s/timeline/tweets?max_position=%s'

    def start_requests(self):
        """Specify URL dynamically."""
        url = self.url % (quote(self.query), '')
        yield scrapy.http.Request(url, callback=self.parse)

    def parse(self, response):
        """Parse for response."""
        data = json.loads(response.body.decode("utf-8"))
        page = scrapy.Selector(text=data['items_html'])
        items = page.xpath('//li[@data-item-type="tweet"]/div')

        for item in items:
            yield Tweet(
                name=item.xpath('.//span[@class="username u-dir u-textTruncate"]/b/text()').extract(),
                text=item.xpath('.//div[@class="js-tweet-text-container"]/p//text()').extract(),
                image_urls=item.xpath('.//div[@class="AdaptiveMedia-container"]//img/@src').extract(),
            )

        # get next scroll
        min_position = data['min_position'].replace("+", "%2B")
        url = self.url % (self.query, min_position)
        yield scrapy.http.Request(url, callback=self.parse)
