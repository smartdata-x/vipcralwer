#coding:utf-8
from get_article_info import get_page_num_and_article_id

filess = open('article.txt', 'a+')
files = open('article_ids_has_saved.txt','r+')
id_exist = []
files_lines = files.readlines()
for files_line in files_lines:
    id = files_line[:-1]
    id_exist.append(id)

f = open('singledata.txt', 'r')
lines = f.readlines()
try:   
    for line in lines:
        account = line.split('\t')[0]    
        if account not in id_exist:
            print 'id not in: %s ' % account
            nets = get_page_num_and_article_id(account)
            for net in nets:
                net = net.decode('utf-8')
                filess.write(net.encode('utf-8'))
            id_exist.append(account)
            files.write(account+'\n')
        else:           
            print 'all in'
except:
    pass
finally:
    filess.close()
    f.close()
    files.close()