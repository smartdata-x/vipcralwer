# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class BlogPipeline(object):

    def __init__(self):
        self.f = open('../User_Relationship_data.txt','a+')

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        self.f.close()

    def process_item(self, item, spider):
        if spider.name == 'user_relationship_nets':
            user_relationship_nets = item['user_relationship_nets'].encode('utf-8')
            self.f.write(user_relationship_nets)

        return item


class UserInfoPipeline(object):

    def __init__(self):
        self.ff = open('../User_Info_Data.txt','a+')

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        self.ff.close()

    def process_item(self, item, spider):
        if spider.name == 'user_info':
            user_info = item['user_info'].encode('utf-8')
            self.ff.write(user_info)

        return item


class ArticleInfoPipeline(object):

    def __init__(self):
        self.fff = open('../Article.txt','a+')

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        self.fff.close()

    def process_item(self, item, spider):
        if spider.name == 'article_data':
            article_info = item['article_info'].encode('utf-8')
            self.fff.write(article_info)

        return item