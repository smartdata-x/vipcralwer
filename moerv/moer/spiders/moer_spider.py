#!/bin/usr/env python
# -*- coding: utf-8 -*-

from scrapy.spiders import Spider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest
from moer.items import MoerItem
from moer.utils import complete_url, simple_post
from article_spider import ArticleSpider


class MoerSpider(Spider):
    name = 'moer'

    def __init__(self, runner, user_set):
        super(MoerSpider, self).__init__()
        self.base_url = 'http://moer.jiemian.com/investment_findPageList.htm?'
        self.post_data = {
            'onColumns': 'all',
            'industrys': 'all',
            'fieldColumn': 'all',
            'price': 'all',
            'authorType': '1',
            'sortType': 'time'
        }
        self.runner = runner
        self.user_set = user_set

    def start_requests(self):
        return [FormRequest(url=self.base_url, formdata=self.post_data, callback=self.parse)]

    def parse(self, response):
        selector = HtmlXPathSelector(response)
        links = selector.select(u'//a[@class="moerUsercard"]/@href').extract()
        for link in links:
            link = complete_url(self.base_url, link)
            user_id = int(link[-9:])

            if user_id not in self.user_set:
                self.user_set.add(user_id)
                yield Request(url=link, callback=self.parse_person)
            else:
                continue

        crawler_page_num = 1500
        for crawler_page in xrange(2, crawler_page_num):
            self.post_data['page'] = str(crawler_page)
            yield FormRequest(url=self.base_url, formdata=self.post_data, callback=self.parse)

    def parse_person(self, response):
        person_item = MoerItem()
        selector = HtmlXPathSelector(response)

        person_item['name'] = selector.select(u'//div[@class="author-msg"]/h4/span/text()').extract()[0].encode(
            'utf-8').strip()
        person_item['id'] = int(response.url[-9:])

        if len(selector.select(u'//i[@class="moerv-red"]').extract()) > 0:
            person_item['type'] = 1
        else:
            person_item['type'] = 0

        person_item['concern_num'] = simple_post('concern', person_item['id'])
        person_item['followers_num'] = simple_post('follower', person_item['id'])

        extracted_article_num = selector.select(u'//input[@id="totalNum"]/@value').extract()[0]
        person_item['article_num'] = int(extracted_article_num.encode('utf-8').strip())

        data_dict = {
            'url': response.url,
            'article_num': person_item['article_num'],
            'user_id': person_item['id']
        }
        self.runner.crawl(ArticleSpider, data_dict)

        yield person_item
