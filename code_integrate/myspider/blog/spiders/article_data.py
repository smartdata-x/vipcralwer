# -*- coding: utf-8 -*-
import scrapy
import datetime
import re
from blog.myconfig import UsersConfig
from blog.items import Article_InfoItem


class ArticleDataSpider(scrapy.Spider):
    name = "article_data"
    headers = {'Host': 'blog.cnfol.com',
               'Accept': "application/json, text/javascript, */*; q=0.01",
               'Accept-Language': "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
               'Accept-Encoding': "gzip, deflate",
               'Connection': "keep-alive",
               'Cache-Control': "max-age=0",
               'Cookie': "SUV=1471944245695628",
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',}

    months = []
    this_month = (datetime.datetime.now()).strftime( '%Y/%m' )
    months.append(this_month)
    last_month = (datetime.datetime.now() - datetime.timedelta(days=32)).strftime( '%Y/%m' )
    months.append(last_month)
    last_second_month = (datetime.datetime.now() - datetime.timedelta(days=64)).strftime( '%Y/%m' )
    months.append(last_second_month)
    last_thrid_month = (datetime.datetime.now() - datetime.timedelta(days=96)).strftime( '%Y/%m' )
    months.append(last_thrid_month)

    pattern_url = 'http://blog.cnfol.com/.*rticle/.*-(.*).html'
    pattern_read = '.*html(.*);.*adon.*'

    def __init__(self, data_dict):
        self.uid = data_dict['uid']

    def start_requests(self):
        for month in self.months:
            yield scrapy.Request('http://blog.cnfol.com/%s/archive/%s/1' % (self.uid, month),
                                 method='GET',
                                 headers=self.headers,
                                 callback=self.parses,
                                 # errback=self.error_back,
                                 meta={'cookiejar': 1,
                                       'uid': self.uid,
                                       'month':month,
                                       'proxy': 'http://%s' % (UsersConfig['proxy']),
                                       },
                                 )

    def parses(self, response):
        month = response.request.meta.get('month')
        try:
            pagenum = response.xpath('//*[@class="CoRed"]/text()').extract()[0].split('/')[1]
        except:
            pagenum = 1
        for i in range(1, int(pagenum) + 1):
            yield scrapy.Request('http://blog.cnfol.com/%s/archive/%s/%s' % (self.uid, month,i),
                                 method='GET',
                                 headers=self.headers,
                                 callback=self.parse_arttime,
                                 # errback=self.error_back,
                                 meta={'cookiejar': 1,
                                       'uid': self.uid,
                                       'proxy': 'http://%s' % (UsersConfig['proxy']),
                                       },
                                 )

    def parse_arttime(self, response):
        title_url = response.xpath('//h4/a/@href').extract()
        read_url = 'http://blog.cnfol.com/articleclick/art/,'
        for jj in range(len(title_url)):
            ArtTime = response.xpath('//*[@class="Date"]/text()').extract()[jj]
            title = response.xpath('//h4/a/text()').extract()[jj]
            title_id = re.findall(self.pattern_url, title_url[jj])[0]
            yield scrapy.Request(read_url+title_id,
                                 method='GET',
                                 headers=self.headers,
                                 callback=self.parse_other_data,
                                 # errback=self.error_back,
                                 meta={'cookiejar': 1,
                                       'uid': self.uid,
                                       'ArtTime':ArtTime,
                                       'title': title,
                                       'title_url':title_url[jj],
                                       'proxy': 'http://%s' % (UsersConfig['proxy']),
                                       },
                                 )

    def parse_other_data(self,response):
        ArtTime = response.request.meta.get('ArtTime')
        title = response.request.meta.get('title')
        title_url = response.request.meta.get('title_url')
        read_num = re.findall(self.pattern_read, response.body)[0].split('"')[1]

        yield scrapy.Request(title_url,
                             method='GET',
                             headers=self.headers,
                             callback=self.parse_vote_data,
                             # errback=self.error_back,
                             meta={'cookiejar': 1,
                                   'uid': self.uid,
                                   'ArtTime': ArtTime,
                                   'title': title,
                                   'title_url': title_url,
                                   'read_num':read_num,
                                   'proxy': 'http://%s' % (UsersConfig['proxy']),
                                   },
                             )

    def parse_vote_data(self, response):
        item = Article_InfoItem()

        ArtTime = response.request.meta.get('ArtTime')
        title = response.request.meta.get('title')
        title_url = response.request.meta.get('title_url')
        read_num = response.request.meta.get('read_num')
        uid = response.request.meta.get('uid')

        try:
            vote = response.xpath('//*[@id="showvotes"]/text()').extract()[0]
        except Exception, e:
            print e
            print 'vote wrong'
            vote = '0'
            pass
        try:
            zhuanzai = response.xpath('//*[@id="transshipmentnum"]/text()').extract()[0]
        except Exception, e:
            print e
            print 'zhuanzai wrong'
            zhuanzai = '0'
            pass
        try:
            comment = response.xpath('//*[@id="ArticleCommentNum"]/text()').extract()[0]
        except Exception, e:
            print e
            print 'comment wrong'
            comment = '0'
            pass

        save_data = '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (
            uid, title, vote, read_num, zhuanzai, comment, ArtTime)
        item['article_info'] = save_data
        yield item
        print  uid,title,title_url,read_num,vote, zhuanzai,comment


