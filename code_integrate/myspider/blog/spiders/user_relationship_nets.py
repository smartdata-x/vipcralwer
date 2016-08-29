# -*- coding: utf-8 -*-
import scrapy
import logging
import re
from scrapy.http import Request, FormRequest
from blog.items import BlogItem
from blog.myconfig import UsersConfig
from user_info  import UserInfoSpider
from article_data import  ArticleDataSpider

# from moer.utils import complete_url, simple_post
logger = logging.getLogger('alluser')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('test.log')
fh.setLevel(logging.DEBUG)
formatter = logging.basicConfig(format='%(levelname)s:%(message)s' + '\n', level=logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)


class UserRelationshipNetsSpider(scrapy.Spider):
    name = "user_relationship_nets"
    count_dict = {}
    maxpage_dict = {}
    focus_user_dict = {}
    save_uid = []
    single_user_uid_save = []
    single_user_uid_has_requested = []

    headers = {'Host': 'blog.cnfol.com',
               'Accept': "application/json, text/javascript, */*; q=0.01",
               'Accept-Language': "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
               'Accept-Encoding': "gzip, deflate",
               'Connection': "keep-alive",
               'Cache-Control': "max-age=0",
               'Cookie': "SUV=1471944245695628",
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',}

    def __init__(self, first_uid, runner):
        self.user_url = 'http://blog.cnfol.com/%s/myfocus/friend'
        self.first_uid = first_uid
        self.runner = runner

    def start_requests(self):
        yield scrapy.Request(self.user_url % (self.first_uid),
                             method='GET',
                             headers=self.headers,
                             callback=self.request_info,
                             meta={'cookiejar': 1,
                                   'request_id': self.first_uid,
                                   'proxy': 'http://%s' % (UsersConfig['proxy']),
                                   },
                             )

    def request_info(self, response):
        requsest_id = response.request.meta.get('request_id')
        try:
            page_num = response.xpath('//*[@class="CoRed"]/text()').extract()[0].split('/')[1]
        except:
            page_num = 1

        for j in range(1, int(page_num) + 1):
            focus_url = 'http://blog.cnfol.com/%s/myfocus/friend?type=&&p=%s' % (requsest_id, j)
            yield FormRequest(focus_url,
                              method='GET',
                              headers=self.headers,
                              callback=self.parse_page,
                              meta={
                                  'proxy': 'http://%s' % (UsersConfig['proxy']),
                                  'maxpage': page_num,
                                  'cookiejar': response.meta['cookiejar'],
                              },
                              dont_filter=True)

    def parse_page(self, response):
        page_data = response.body
        maxpage = response.request.meta.get('maxpage')
        page_data_len = len(response.xpath('//div[starts-with(@class,"MyFollowBox FirstMesg")]'))
        if page_data_len > 0:
                pattern2 = 'http://blog.cnfol.com/(.*)/myfocus/frien.*'
                key_user_id2 = re.findall(pattern2, response.url)[0]
                if key_user_id2 in self.count_dict.keys():
                    self.count_dict[key_user_id2] = self.count_dict[key_user_id2] + 1
                else:
                    self.count_dict[key_user_id2] = 1
                self.maxpage_dict[key_user_id2] = maxpage

                if int(self.count_dict[key_user_id2]) <= int(self.maxpage_dict[key_user_id2]):
                    for i in range(page_data_len):
                        try:
                            focus_link = \
                                response.xpath(
                                    '//div[starts-with(@class,"MyFollowBox FirstMesg")]/div[2]/p[2]/span[1]/a/@href')[
                                    i].extract()
                            if 'returnbolg' not in focus_link:
                                # print focus_link
                                request_id = re.findall(pattern2, focus_link)[0]
                                # print request_id
                                friends_count = response.xpath(
                                    '//div[starts-with(@class,"MyFollowBox FirstMesg")]/div[2]/p[2]/span[1]/a/em/text()')[
                                    i].extract()
                                follows_count = response.xpath(
                                    '//div[starts-with(@class,"MyFollowBox FirstMesg")]/div[2]/p[2]/span[2]/a/em/text()')[
                                    i].extract()
                                if int(friends_count) < 500:
                                    yield scrapy.Request(self.user_url % (request_id),
                                                         method='GET',
                                                         headers=self.headers,
                                                         callback=self.request_info,
                                                         # errback=self.error_back,
                                                         meta={
                                                             'proxy': 'http://%s' % (UsersConfig['proxy']),
                                                             'request_id': request_id,
                                                             'cookiejar': response.meta['cookiejar'],
                                                         },
                                                         )
                        except:
                            print 'first datalength '
                            pass

                for i in range(page_data_len):
                    try:
                        focus_link = \
                            response.xpath('//div[starts-with(@class,"MyFollowBox FirstMesg")]/div[2]/p[2]/span[1]/a/@href')[
                                i].extract()
                        if 'returnbolg' not in focus_link:
                            request_id = re.findall(pattern2, focus_link)[0]
                            friends_count = \
                                response.xpath(
                                    '//div[starts-with(@class,"MyFollowBox FirstMesg")]/div[2]/p[2]/span[1]/a/em/text()')[
                                    i].extract()
                            follows_count = \
                                response.xpath(
                                    '//div[starts-with(@class,"MyFollowBox FirstMesg")]/div[2]/p[2]/span[2]/a/em/text()')[
                                    i].extract()
                            if int(friends_count) < 500 and int(follows_count) > 5000:
                                pass_id = request_id
                                if pass_id not in self.single_user_uid_has_requested:

                                    data_dict = {
                                        'uid': pass_id
                                    }
                                    self.runner.crawl(UserInfoSpider, data_dict)
                                    self.runner.crawl(ArticleDataSpider, data_dict)

                                    # UserInfoSpider(data_dict)
                                    self.single_user_uid_has_requested.append(pass_id)
                                else:
                                    pass
                                # UserInfoSpider(data_dict)

                                if key_user_id2 in self.focus_user_dict.keys():
                                    self.focus_user_dict[key_user_id2].append('%s' % pass_id)
                                else:
                                    self.focus_user_dict[key_user_id2] = []
                                    self.focus_user_dict[key_user_id2].append('%s' % pass_id)
                    except Exception, e:
                        print 'second datalength '
                        pass

        item = BlogItem()
        if self.count_dict[key_user_id2] == self.maxpage_dict[key_user_id2]:
            self.count = 0
            if str(key_user_id2) not in self.save_uid and str(key_user_id2) in self.focus_user_dict.keys():
                save_data = '%s\t%s\n' % (key_user_id2.strip(), ','.join(self.focus_user_dict[key_user_id2]))
                item['user_relationship_nets'] = save_data
                yield item
            self.save_uid.append(key_user_id2)


