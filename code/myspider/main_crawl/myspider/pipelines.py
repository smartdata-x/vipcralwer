# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class UserPipeline(object):
    def __init__(self):
        self.file = open('data.txt', 'a+')
        self.file2 = open('singledata.txt', 'a+')
    def process_item(self, item, spider):
        # name = item['name'].encode('utf-8')
       if item['name'] != 'no data' :
            name = item['name'].encode('utf-8')
            self.file.write(name)
       if item['info'] != 'do not save':
            info = item['info'].encode('utf-8') + '\n'
            self.file2.write(info)