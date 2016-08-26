files = open('Relationship_Data.txt', 'a+')
rela_lines = files.readlines()
id_exist = []
for rela_line in rela_lines:
    rela_id = rela_line.split('\t')[0]
    id_exist.append(rela_id)

with open('data.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        id = line.split('\t')[0]
        follow_ids = line.split('\t')[1]
        if id not in id_exist:
            print '%s not in ' % id
            files.write(id + '\t' + follow_ids)
        else:
            print 'in'
files.close()
