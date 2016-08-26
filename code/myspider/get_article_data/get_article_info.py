#coding:utf-8
import requests
import json
import time
import lxml.html as H
import datetime
import re

session = requests.Session()
article_file = open('article.txt','a+')
def get_page_num_and_article_id(user_account ):
    months = []
    sava_data = []
    pattern_url = 'http://blog.cnfol.com/.*rticle/.*-(.*).html'    
    pattern_read = '.*html(.*);.*adon.*' 
    
    this_month = (datetime.datetime.now()).strftime( '%Y/%m' )
    months.append(this_month)
    last_month = (datetime.datetime.now() - datetime.timedelta(days=32)).strftime( '%Y/%m' )
    months.append(last_month)
    last_second_month = (datetime.datetime.now() - datetime.timedelta(days=64)).strftime( '%Y/%m' )
    months.append(last_second_month)
    last_thrid_month = (datetime.datetime.now() - datetime.timedelta(days=96)).strftime( '%Y/%m' )
    months.append(last_thrid_month)
    
    headers = {'Host': 'blog.cnfol.com',
                'Accept': "text/html, */*; q=0.01",
                'Accept-Language': "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                'Accept-Encoding': "gzip, deflate, br",
                'Connection': "keep-alive",
                'Cache-Control': "max-age=0",
                'Cookie': 'SUV=1471944245695628; cookie[passport][tmpuser]=CE-8418252; PHPSESSID=a31c3ead76d0b3641621ef004d183248',
                #'Referer':"https://xueqiu.com/6611504859",
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',}
    
    request_url = 'http://blog.cnfol.com/%s/archive/%s/%s'
    
    for month in months:

        first_url = 'http://blog.cnfol.com/%s/archive/%s/1'%(user_account,month)
        
        content = session.get(first_url,headers=headers)
        doc = H.document_fromstring(content.text)
        try:
            pagenum = doc.xpath('//*[@class="CoRed"]/text()')[0].split('/')[1]
        except:
            pagenum = 1
        for i in range(1,int(pagenum)+1):
            content_each_page = session.get(request_url%(user_account,month,i),headers=headers)
            doc_each_page = H.document_fromstring(content_each_page.text)
            ArtTime = doc_each_page.xpath('//*[@class="Date"]/text()')
            title = doc_each_page.xpath('//h4/a/text()')
            title_url = doc_each_page.xpath('//h4/a')
            arti_num = len(doc_each_page.xpath('//*[@class="Date"]'))
            print i, arti_num
            for j in range(0,int(arti_num)):
                # 发布时间
                #print ArtTime[j],title[j], title_url[j].get('href')
                title_id = re.findall(pattern_url,title_url[j].get('href'))[0]
                # 获取阅读数
                read_url = 'http://blog.cnfol.com/articleclick/art/,'
                content_read_num = session.get(read_url+title_id,headers=headers)
                read_num = re.findall(pattern_read,content_read_num.content)[0].split('"')[1]
                # 获取点赞，转载，评论数
                comment_url = title_url[j].get('href')
                content_comment_url = session.get(comment_url,headers=headers)
                doc_comment = H.document_fromstring(content_comment_url.text)
                try:
                    vote = doc_comment.xpath('//*[@id="showvotes"]/text()')[0]
                except Exception,e:
                    print e
                    print 'vote wrong'
                    vote = '0'
                    pass
                try:
                    zhuanzai = doc_comment.xpath('//*[@id="transshipmentnum"]/text()')[0]
                except Exception,e:
                    print e
                    print 'zhuanzai wrong'
                    zhuanzai = '0'
                    pass
                try:
                    comment = doc_comment.xpath('//*[@id="ArticleCommentNum"]/text()')[0]
                except Exception,e:
                    print e
                    print 'comment wrong'
                    comment = '0'
                    pass
                
                save_data = '%s\t%s\t%s\t%s\t%s\t%s\t%s\n'%(user_account, title[j].encode('utf-8'),vote,read_num , zhuanzai, comment, ArtTime[j])
                sava_data.append(save_data)
    return sava_data
                       
                #article_file.write(save_data)
                
                
#f=open('singledata.txt','r')
#for line in f.readlines():
    #account = line.split('\t')[0]
    #print account
    #get_page_num_and_article_id(account)
    
#f.close()
#article_file.close()