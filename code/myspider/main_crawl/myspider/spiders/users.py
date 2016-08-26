# -*- coding: utf-8 -*-
import scrapy
import os
import time
from myspider.items import UserItem
from myspider.myconfig import UsersConfig
from scrapy.http import FormRequest
import json
import logging
import re
import requests


logger = logging.getLogger('alluser')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('test.log')
fh.setLevel(logging.DEBUG)
formatter = logging.basicConfig(format='%(levelname)s:%(message)s' + '\n', level=logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)


class UsersSpider(scrapy.Spider):

    name = 'users'
    count_dict = {}
    maxpage_dict = {}
    focus_user_dict = {}
    save_uid = []
    single_user_uid_save = []
    headers = {'Host': 'blog.cnfol.com',
               'Accept': "application/json, text/javascript, */*; q=0.01",
               'Accept-Language': "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
               'Accept-Encoding': "gzip, deflate",
               'Connection': "keep-alive",
               'Cache-Control': "max-age=0",
               'Cookie': "SUV=1471944245695628",
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',}

    def __init__(self):
        self.user_url = 'http://blog.cnfol.com/%s/myfocus/friend'

    def start_requests(self, first_uid='huangjinfengbao'):
        yield scrapy.Request(self.user_url%(first_uid),
                          method='GET',
                          headers=self.headers,
                          callback=self.request_info,
                          meta={'cookiejar': 1,
                                'request_id':first_uid,
                                'proxy': 'http://%s' % (UsersConfig['proxy']),
                                },
                          )

    def request_info(self, response):
        requsest_id = response.request.meta.get('request_id')
        try:
            page_num = response.xpath('//*[@class="CoRed"]/text()').extract()[0].split('/')[1]
        except:
            page_num = 1

        for j in range(1, int(page_num)+1):
            focus_url = 'http://blog.cnfol.com/%s/myfocus/friend?type=&&p=%s'%(requsest_id,j)
            yield FormRequest(focus_url,
                              method='GET',
                              headers=self.headers,
                              callback=self.parse_page,
                              meta={
                                  # 'proxy': UsersConfig['proxy'],
                                  'maxpage': page_num,
                                  'cookiejar': response.meta['cookiejar'],
                              },
                              dont_filter=True)

    def parse_page(self, response):
        # logging.debug('item page %s:' % page + '\n')
        page_data = response.body
        maxpage = response.request.meta.get('maxpage')
        page_data_len = len(response.xpath('//div[starts-with(@class,"MyFollowBox FirstMesg")]'))
        # logging.debug('page_data_len %s:' % page_data_len + '\n')
        pattern2 = 'http://blog.cnfol.com/(.*)/myfocus/frien.*'
        key_user_id2 = re.findall(pattern2, response.url)[0]
        if key_user_id2 in self.count_dict.keys():
            self.count_dict[key_user_id2] = self.count_dict[key_user_id2] + 1
        else:
            self.count_dict[key_user_id2] = 1
        self.maxpage_dict[key_user_id2] = maxpage
        #logging.debug('self.count_dict %s:' % self.count_dict + '\n')
        #logging.debug('self.maxpage_dict %s:' % self.maxpage_dict + '\n')

        if int(self.count_dict[key_user_id2]) <= int(self.maxpage_dict[key_user_id2]):
            for i in range(page_data_len):
                try:
                    focus_link = response.xpath('//div[starts-with(@class,"MyFollowBox FirstMesg")]/div[2]/p[2]/span[1]/a/@href')[i].extract()
                    if 'returnbolg' not in focus_link:
                        #print focus_link
                        request_id = re.findall(pattern2, focus_link)[0]
                        #print request_id
                        friends_count = response.xpath('//div[starts-with(@class,"MyFollowBox FirstMesg")]/div[2]/p[2]/span[1]/a/em/text()')[i].extract()
                        follows_count = response.xpath('//div[starts-with(@class,"MyFollowBox FirstMesg")]/div[2]/p[2]/span[2]/a/em/text()')[i].extract()
                        if int(friends_count)<500 :
                            yield scrapy.Request(self.user_url%(request_id),
                                              method='GET',
                                              headers=self.headers,
                                              callback=self.request_info,
                                              # errback=self.error_back,
                                              meta={
                                                  # 'proxy': UsersConfig['proxy'],
                                                  'request_id':request_id,
                                                  'cookiejar': response.meta['cookiejar'],
                                              },
                                              )
                except:
                    pass

        for i in range(page_data_len):
            try:
                focus_link = \
                response.xpath('//div[starts-with(@class,"MyFollowBox FirstMesg")]/div[2]/p[2]/span[1]/a/@href')[
                    i].extract()
                if 'returnbolg' not in focus_link:
                    request_id = re.findall(pattern2, focus_link)[0]
                    friends_count = \
                    response.xpath('//div[starts-with(@class,"MyFollowBox FirstMesg")]/div[2]/p[2]/span[1]/a/em/text()')[
                        i].extract()
                    follows_count = \
                    response.xpath('//div[starts-with(@class,"MyFollowBox FirstMesg")]/div[2]/p[2]/span[2]/a/em/text()')[
                        i].extract()
                    if int(friends_count) < 500 and int(follows_count) > 5000:
                        # self.all_user.append('%s' % user_id)
                        if key_user_id2 in self.focus_user_dict.keys():
                            self.focus_user_dict[key_user_id2].append('%s'% request_id)
                        else:
                            self.focus_user_dict[key_user_id2] = []
                            self.focus_user_dict[key_user_id2].append('%s' % request_id)

                        yield scrapy.Request('http://blog.cnfol.com/%s' % request_id,
                                             method='GET',
                                             headers=self.headers,
                                             callback=self.parses,
                                             # errback=self.error_back,
                                             meta={'cookiejar': 1,
                                                   'key_user_id2': key_user_id2,
                                                   'proxy': 'http://%s' % (UsersConfig['proxy']),
                                                   },
                                             )
            except:
                pass

        # logging.debug('self.count_dict %s:' % self.count_dict + '\n')
        # logging.debug('self.maxpage_dict %s:' % self.maxpage_dict + '\n')
        # logging.debug('self.focus_user_dict %s:' % self.focus_user_dict + '\n')
        # logging.debug('self.user_followers_count %s:' % self.user_followers_count + '\n')

    def parses(self, response):
        item = UserItem()
        save_data = 'no data'
        key_user_id2 = response.request.meta.get('key_user_id2')
        #个人信息
        # 账户名
        uid = response.url.split('/')[-1]
        # 昵称
        single_name = response.xpath(
            '/html/body/div[1]/div[2]/div[3]/div[1]/strong/text()').extract()[0]
        # 认证
        try:
            verified_or_descripiton = response.xpath(
                '/html/body/div[1]/div[2]/div[2]/i/text()').extract()[0]
            if verified_or_descripiton == 'ApproveIco':
                verified = 'True'
        except:
            verified = 'False'
            pass
        # 文章数
        article_num = response.xpath(
            '/html/body/div[1]/div[2]/div[2]/ul/li[3]/a/p[1]/text()').extract()
        # 粉丝数
        fans_num = response.xpath('/html/body/div[1]/div[2]/div[2]/ul/li[2]/a/p[1]/text()').extract()[0]
        # 关注数
        guanzhu = response.xpath(
            '/html/body/div[1]/div[2]/div[2]/ul/li[1]/a/p[1]/text()').extract()[0]

        # 具体文章内容信息
        single_info = '%s\t%s\t%s\t%s\t%s\t%s' % (
            uid, single_name, verified, fans_num, guanzhu, article_num[0])
        logging.debug('single_info %s:' % single_info + '\n')
        if self.count_dict[key_user_id2] == self.maxpage_dict[key_user_id2]:
            # logger.info('self.all_user %s' % list(set(self.all_user)) + '\n')
            self.count = 0
            #logging.debug('key_user_id2 %s:' % key_user_id2 + '\n')
            # logging.debug('self.save_uid %s:' % self.save_uid + '\n')
            if str(key_user_id2) not in self.save_uid:
                save_data = '%s\t%s\n' % (key_user_id2.strip(), ','.join(self.focus_user_dict[key_user_id2]))
            self.save_uid.append(key_user_id2)

        if uid not in self.single_user_uid_save:
            single_info = single_info
            self.single_user_uid_save.append(uid)
        else:
            single_info = 'do not save'
        item['name'] = save_data
        item['info'] = single_info
        yield item
