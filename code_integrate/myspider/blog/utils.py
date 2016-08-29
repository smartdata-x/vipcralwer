#!/usr/bin/env python
# coding: utf-8
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: 一些工具类
Desc :
"""
import re
import sys
import os.path

def init_rule():

        artile_rule1 = {
            'name': 'huxiu',
            'allow_domains': 'huxiu.com',
            'start_urls': 'http://www.huxiu.com/',
            'next_page': '',
            'allow_url': '/article/\d+/\d+\.html',
            'extract_from': '//div[@class="mod-info-flow"]',
            'title_xpath': '//div[@class="article-wrap"]/h1/text()',
            'body_xpath': '//div[@id="article_content"]/p//text()',
            'publish_time_xpath': '//span[@class="article-time"]/text()',
            'source_site': '虎嗅网',
            'enable': 1
        }





