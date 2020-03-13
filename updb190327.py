# -*-coding:utf-8-*-
import pymysql

# connection = pymysql.connect(host='39.105.9.20', user='root', passwd='bigdata_oil',
#                 db='cxd_data', port=3306, charset='utf8')

connection = pymysql.connect(host='39.105.9.20', user='root', passwd='bigdata_oil',
                db='cxd_test', port=3306, charset='utf8')
cursor = connection.cursor()

dic_sql = "SELECT Spmc,cate_code,type_code,path_code FROM dic_good_type_bill"
cursor.execute(dic_sql)
dic_data = cursor.fetchall()

dic = {r[0]: [r[1], r[2], r[3]]for r in dic_data}

# exchange_sql = "SELECT financial_exchange_id,exchange_good,main_id,spec_id,good_id FROM financial_exchange W" \
#                "HERE main_id IS NULL AND exchange_good IS NOT NULL"
exchange_sql = "SELECT DISTINCT exchange_good FROM financial_exchange WHERE spec_id IS NULL AND exchange_good IS NOT NULL"

cursor.execute(exchange_sql)
exchange_data = cursor.fetchall()
print(len(exchange_data))

up_sql = """UPDATE financial_exchange SET main_id ='%s',spec_id ='%s' WHERE exchange_good = "%s" and spec_id is null"""

num = 1

for r in exchange_data:
    # if num < 6985:
    #     num += 1
    #     continue
    if r[0] in dic.keys():
        print(num, r[0])
        print(up_sql % (dic[r[0]][0], dic[r[0]][1], r[0]))
        cursor.execute(up_sql % (dic[r[0]][0], dic[r[0]][1], r[0]))
        connection.commit()
        num += 1





