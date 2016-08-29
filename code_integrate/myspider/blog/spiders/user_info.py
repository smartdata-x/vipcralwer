# -*- coding: utf-8 -*-
import scrapy
from blog.myconfig import UsersConfig
from blog.items import  User_InfoItem
import logging
import re

class UserInfoSpider(scrapy.Spider):
    name = "user_info"
    single_user_uid_save = []
    headers = {'Host': 'blog.cnfol.com',
               'Accept': "application/json, text/javascript, */*; q=0.01",
               'Accept-Language': "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
               'Accept-Encoding': "gzip, deflate",
               'Connection': "keep-alive",
               'Cache-Control': "max-age=0",
               'Cookie': "SUV=1471944245695628",
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',}

    def __init__(self, data_dict):
        self.user_url = 'http://blog.cnfol.com/%s'
        self.uid = data_dict['uid']
        # self.start_requests()

    def start_requests(self):
        yield scrapy.Request('http://blog.cnfol.com/%s' % self.uid,
                             method='GET',
                             headers=self.headers,
                             callback=self.parses,
                             # errback=self.error_back,
                             meta={'cookiejar': 1,
                                   'uid': self.uid,
                                   'proxy': 'http://%s' % (UsersConfig['proxy']),
                                   },
                             )

    def parses(self, response):
        uid = response.url.split('/')[-1]
        # 昵称
        single_name = response.xpath(
            '/html/body/div[1]/div[2]/div[3]/div[1]/strong/text()').extract()[0]
        # 认证
        try:
            verified_or_descripiton = response.xpath(
                '/html/body/div[1]/div[2]/div[2]/i/@class').extract()[0]
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

        single_info = '%s\t%s\t%s\t%s\t%s\t%s' % (
            uid, single_name, verified, fans_num, guanzhu, article_num[0])
        logging.debug('single_info %s:' % single_info + '\n')

        yield scrapy.Request('http://blog.cnfol.com/index.php/article/blogarticlelist/%s?page=1' % self.uid,
                             method='GET',
                             headers=self.headers,
                             callback=self.get_member_id,
                             meta={'cookiejar': 1,
                                   'single_info': single_info,
                                   'proxy': 'http://%s' % (UsersConfig['proxy']),
                                   },
                             )

    def get_member_id(self, response):
        content = response.body
        pattern_member_id = '.*memberid = (.*)'
        single_info = response.request.meta.get('single_info')
        try:
            member_id = re.findall(pattern_member_id, content)[0][:-2]

            yield scrapy.Request('http://blog.cnfol.com/ajaxgetblogstat/%s' % member_id,
                             method='GET',
                             headers=self.headers,
                             callback=self.parse_request_data,
                             meta={'cookiejar': 1,
                                   'single_info': single_info,
                                   'proxy': 'http://%s' % (UsersConfig['proxy']),
                                   },
                             )
        except IndexError:
            print 'no member id'

    def parse_request_data(self, response):
        item = User_InfoItem()
        pattern = '(\d+)'
        single_info = response.request.meta.get('single_info')
        total_click = response.xpath('//*[@id="s_mtclick"]/text()').extract()[0]
        today_click = response.xpath('//*[@id="s_mdclick"]/text()').extract()[0]
        article_nums = response.xpath('/html/body/ul/li[3]/text()').extract()[0]
        article_num = re.findall(pattern, article_nums)[0]
        comment_nums = response.xpath('/html/body/ul/li[4]/text()').extract()[0]
        comment_num = re.findall(pattern, comment_nums)[0]
        save_data = '\t%s\t%s\t%s\t%s\n' % (total_click, today_click, article_num, comment_num)
        user_info = single_info + save_data
        item['user_info'] = user_info
        yield item
