# -*-coding:utf-8-*-

import pymysql
import codecs

connection = pymysql.connect(host='47.92.25.70', user='root', passwd='Wfn031641',
                db='cxd_data', port=3306, charset='utf8')
cursor = connection.cursor()

with codecs.open('./files/total190510.txt', 'rb', 'utf-8') as f:
    com = f.readlines()

sql = "SELECT Xf_id,Xfmc,LEFT(Kprq,4),ROUND(SUM(Je),1) FROM ticket_bill " \
      "WHERE Kprq IS NOT NULL GROUP BY Xfmc,LEFT(Kprq,4) ORDER BY Xfmc"
insertsql = "INSERT INTO in_total (com_name,com_id,year,gmv) VALUES('%s','%s','%s','%s')"

for r in com:
    name = r.strip()
    cursor.execute(sql % name)
    data = cursor.fetchall()
    if data:
        for k in data:
            comid = k[0]
            comname = k[1]
            year = k[2]
            gmv = k[3]
            num = cursor.execute(insertsql % (comname, comid, year, gmv))
            if num == 1:
                print(comname, year, gmv, 'success')
                connection.commit()
            else:
                print(comname, year, gmv, 'false')











