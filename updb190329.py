# -*-coding:utf-8-*-
import pymysql

# connection = pymysql.connect(host='39.105.9.20', user='root', passwd='bigdata_oil',
#                 db='cxd_data', port=3306, charset='utf8')

connection = pymysql.connect(host='39.105.9.20', user='root', passwd='bigdata_oil',
                db='cxd_test', port=3306, charset='utf8')
cursor = connection.cursor()

def oil_info(good):
    sql = "SELECT * FROM dic_good_type_bill WHERE spmc = '%s'"
    cursor.execute(sql % good)
    data = cursor.fetchall()
    if data:
        cate_id = data[0][2]
        type_id = data[0][3]
        spec_id = data[0][4]
        record = [cate_id,type_id,spec_id]
    else:
        record = []
    return record


dic_sql = "SELECT Spmc,cate_code,type_code FROM dic_good_type_bill"
cursor.execute(dic_sql)
dic_data = cursor.fetchall()

dic = {r[0]: [r[1], r[2]]for r in dic_data}
print(dic)
print(len(dic))


exchange_sql = "SELECT DISTINCT Spmc,type_code FROM ticket_bill WHERE type_code IS NULL"
cursor.execute(exchange_sql)
exchange_data = cursor.fetchall()
print(len(exchange_data))

up_sql = """UPDATE ticket_bill SET cate_code = '%s',type_code = '%s' WHERE Spmc = "%s" """

num = 1

for r in exchange_data:
    if r[0] in dic.keys():
        print(num, r[0])
        print(up_sql % (dic[r[0]][0], dic[r[0]][1], r[0]))
        cursor.execute(up_sql % (dic[r[0]][0], dic[r[0]][1], r[0]))
        connection.commit()
        num += 1


















