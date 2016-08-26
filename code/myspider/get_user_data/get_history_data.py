#coding:utf-8
import requests
import json
import time
import lxml.html as H
import re
session = requests.Session()
pattern = '(\d+)'

headers = {'Host': 'blog.cnfol.com',
            'Accept': "text/html, */*; q=0.01",
            'Accept-Language': "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            'Accept-Encoding': "gzip, deflate, br",
            'Connection': "keep-alive",
            'Cache-Control': "max-age=0",
            'Cookie': 'SUV=1471944245695628; cookie[passport][tmpuser]=CE-8418252; PHPSESSID=a31c3ead76d0b3641621ef004d183248',
            #'Referer':"https://xueqiu.com/6611504859",
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',}

def get_member_id(user_account):
    url = 'http://blog.cnfol.com/index.php/article/blogarticlelist/%s?page=1'%user_account
    content = session.get(url,headers=headers)
    
    pattern_member_id = '.*memberid = (.*)'
    member_id = re.findall(pattern_member_id,content.content)[0][:-2] 
    
    request_url = 'http://blog.cnfol.com/ajaxgetblogstat/%s'%member_id

    content = session.get(request_url,headers=headers)
    doc = H.document_fromstring(content.text)
    total_click = doc.xpath('//*[@id="s_mtclick"]/text()')[0]
    today_click = doc.xpath('//*[@id="s_mdclick"]/text()')[0]
    article_nums = doc.xpath('/html/body/ul/li[3]/text()')[0]
    article_num = re.findall(pattern, article_nums)[0]
    comment_nums = doc.xpath('/html/body/ul/li[4]/text()')[0]
    comment_num = re.findall(pattern, comment_nums)[0]

    sava_data = '%s\t%s\t%s\t%s' % ( total_click, today_click, article_num, comment_num)
    #print sava_data
    return sava_data

#get_member_id('toujishaoye')