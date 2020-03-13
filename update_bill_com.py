# -*-coding:utf-8-*-
"""
更新发票表企业信息
"""
import pymysql
import codecs
import DB_conn as conn_db


# 注意在这里改表名
connection = conn_db.connection
cursor = connection.cursor()


# 记录公司字典表中无数据的公司
nfile = codecs.open('./files/billnocom191203.txt', 'wb', 'utf-8')
# 记录销方更新失败公司
xfile = codecs.open('./files/billxcom191203.txt', 'wb', 'utf-8')
# 记录购方更新失败公司
gfile = codecs.open('./files/billgcom191203.txt', 'wb', 'utf-8')


# 获取无id购方企业
gfsql = "SELECT DISTINCT Gfmc FROM ticket_bill WHERE Gf_id IS NULL AND Kprq >= '2019-01-01' AND Gfmc IS NOT NULL" # LIMIT 1000" #数据太多加限制，多更几次
# gfsql = "SELECT Gfmc FROM ticket_bill WHERE Gf_id IS NULL AND Gfmc ='大连海益石油化工有限公司'"
cursor.execute(gfsql)
gfdata = cursor.fetchall()
print(len(gfdata))
gfcom = [i[0] for i in gfdata]
# 获取无id销方企业
xfsql = "SELECT DISTINCT Xfmc FROM ticket_bill WHERE Xf_id IS NULL AND Kprq >= '2019-01-01' AND Xfmc IS NOT NULL" #  LIMIT 1000"
# xfsql = "SELECT Xfmc FROM ticket_bill WHERE Xf_id IS NULL AND Xfmc ='大连海益石油化工有限公司'"
cursor.execute(xfsql)
xfdata = cursor.fetchall()
xfcom = [i[0] for i in xfdata]

# 获取企业信息
comsql = "SELECT id,company_provinceId FROM dic_company WHERE name = '%s'"
# 更新销方企业信息
updatexf = "UPDATE ticket_bill SET Xf_id = %s,Xf_province_id = %s " \
           "WHERE Xfmc = %s"
# 更新购方企业信息
updategf = "UPDATE ticket_bill SET Gf_id = %s,Gf_province_id = %s " \
           "WHERE Gfmc = %s"


def updatex():
    print('共%d家销方企业' % len(xfcom))
    count = 1
    # record = []
    for x in xfcom:
        print('查询第%d家：%s ' % (count, x))
        cursor.execute(comsql % x)
        data = cursor.fetchall()
        if data:
            print(data)
            id = data[0][0] if data[0][0] else ''
            provinceid = data[0][1] if str(data[0][1]) else ''
            print(id, provinceid)
            print('更新 ', x)
            # record.append((id, provinceid, x))
            record = (id, provinceid, x)
            cursor.execute(updatexf, record)
            # connection.commit()
            # num = cursor.execute(updatexf % (id, provinceid, x))
            # if num != 0:
            #     print('%s更新成功' % x)
            #     connection.commit()
            # else:
            #     xfile.write(x + '\n')
        else:
            nfile.write(x + '\n')
        count += 1
    # cursor.executemany(updatexf, record)
    connection.commit()
    connection.close()


def updateg():
    print('共%d家购方企业' % len(gfcom))
    count = 1
    # record = []
    for g in gfcom:
        print('查询第%d家：%s ' % (count, g))
        cursor.execute(comsql % g)
        data = cursor.fetchall()
        if data:
            print(data)
            id = data[0][0] if data[0][0] else ''
            provinceid = data[0][1] if str(data[0][1]) else ''
            print(id, provinceid)
            print('更新 ', g)
            # record.append((id, provinceid, g))
            record = (id, provinceid, g)
            cursor.execute(updategf, record)
            # connection.commit()
            # num = cursor.execute(updategf % (id, provinceid, g))
            # if num != 0:
            #     print('%s更新成功' % g)
            #     connection.commit()
            # else:
            #     gfile.wriet(g + '\n')
        else:
            try:
                nfile.write(g + '\n')
            except TypeError:
                print('无效企业')
                continue
        count += 1
    # cursor.executemany(updategf, record)
    connection.commit()
    connection.close()


if __name__ == '__main__':
    # print('开始更新销方企业')
    # updatex()
    print('开始更新购方企业')
    updateg()


