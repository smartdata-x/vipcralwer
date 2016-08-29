
from get_history_data import get_member_id

files = open('User_data.txt', 'a+')
id_exist = []
files_lines = files.readlines()
for files_line in files_lines:
    id = files_line.split('\t')[0]
    id_exist.append(id)

f = open('singledata.txt', 'r')
lines = f.readlines()
for line in lines:


    account = line.split('\t')[0]
    user_name = line.split('\t')[1]
    verfied = line.split('\t')[2]
    guanzhu = line.split('\t')[3]
    fans = line.split('\t')[4]
    wenzhang = line.split('\t')[5]

    if account not in id_exist:
        print 'id not in: %s ' % account
        net = get_member_id(account)
        save_data = '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (
            account, user_name.decode('utf-8'), verfied, guanzhu, fans, wenzhang[:-1], net)
        files.write(save_data.encode('utf-8'))
    else:
        print 'all in'



files.close()
f.close()
