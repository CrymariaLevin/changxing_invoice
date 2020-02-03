# -*-coding:utf-8-*-
"""
更新交易表企业信息
"""
import pymysql
import codecs

connection = pymysql.connect(host='39.105.9.20', user='root', passwd='bigdata_oil',
                db='cxd_data', port=3306, charset='utf8')
cursor = connection.cursor()

# 获取无id销方企业
xfsql = "SELECT DISTINCT Xf_company_name FROM financial_exchange WHERE Xf_company_id IS NULL " \
        "AND Xf_company_name IS NOT NULL"
# 获取无id购方企业
gfsql = "SELECT DISTINCT Gf_company_name FROM financial_exchange WHERE Gf_company_id IS NULL " \
        "AND Gf_company_name IS NOT NULL"
# 获取无油品类型
oilsql = "SELECT DISTINCT exchange_good FROM financial_exchange WHERE exchange_good IS NOT NULL AND main_id IS NULL"

# 记录公司字典表中无数据的公司
nfile = codecs.open('./files/nocom190510.txt', 'wb', 'utf-8')
# 记录销方更新失败公司
xfile = codecs.open('./files/xcom190510.txt', 'wb', 'utf-8')
# 记录购方更新失败公司
gfile = codecs.open('./files/gcom190510.txt', 'wb', 'utf-8')

cursor.execute(xfsql)
xfdata = cursor.fetchall()
xfcom = [i[0] for i in xfdata]
cursor.execute(gfsql)
gfdata = cursor.fetchall()
gfcom = [i[0] for i in gfdata]
cursor.execute(oilsql)
oildata = cursor.fetchall()
oil = [i[0] for i in oildata]

# 获取企业信息
comsql = "SELECT id,com_type,com_group FROM dic_company WHERE name = '%s'"
# 更新销方企业信息
updatexf = "UPDATE financial_exchange SET Xf_com_type = '%s',Xf_com_group = '%s',Xf_company_id = '%s' " \
           "WHERE Xf_company_name = '%s'"
# 更新购方企业信息
updategf = "UPDATE financial_exchange SET Gf_com_type = '%s',Gf_com_group = '%s',Gf_company_id = '%s' " \
           "WHERE Gf_company_name = '%s'"


def updatex():
    print('共%d家销方企业' % len(xfcom))
    count = 1
    for x in xfcom:
        print('查询第%d家：%s ' % (count, x))
        cursor.execute(comsql % x)
        data = cursor.fetchall()
        if data:
            print(data)
            id = data[0][0] if data[0][0] else ''
            com_type = data[0][1] if str(data[0][1]) else ''
            com_group = data[0][2] if str(data[0][2]) else ''
            print(id, com_type, com_group)
            print('更新 ', x)
            num = cursor.execute(updatexf % (com_type, com_group, id, x))
            if num != 0:
                print('%s更新成功' % x)
            else:
                xfile.write(x + '\n')
        else:
            nfile.write(x + '\n')
        count += 1
    connection.commit()


def updateg():
    print('共%d家购方企业' % len(gfcom))
    count = 1
    for g in gfcom:
        print('查询第%d家：%s ' % (count, g))
        cursor.execute(comsql % g)
        data = cursor.fetchall()
        if data:
            print(data)
            id = data[0][0] if data[0][0] else ''
            com_type = data[0][1] if str(data[0][1]) else ''
            com_group = data[0][2] if str(data[0][2]) else ''
            print(id, com_type, com_group)
            print('更新 ', g)
            num = cursor.execute(updategf % (com_type, com_group, id, g))
            if num != 0:
                print('%s更新成功' % g)
            else:
                gfile.wriet(g + '\n')
        else:
            nfile.write(g + '\n')
        count += 1
    connection.commit()


if __name__ == '__main__':
    print('开始更新销方企业')
    updatex()
    print('开始更新购方企业')
    updateg()

