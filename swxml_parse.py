# -*-coding:utf-8-*-
"""
处理xml格式财务数据
数据直接入发票表与交易表
注意在main函数里修改筛选日期
"""
import pymysql
import os
from lxml import etree
import codecs
import re
import shutil
import DB_conn as conn_db

# connection = pymysql.connect(host='39.105.9.20', user='root', passwd='bigdata_oil',
#                 db='cxd_data', port=3306, charset='utf8')

# connection = pymysql.connect(host='39.105.9.20', user='root', passwd='bigdata_oil',
#                 db='cxd_test', port=3306, charset='utf8')
# cursor = connection.cursor()

# 如果使用连接池，注意在这里对应的import库改表名
connection = conn_db.connection
cursor = connection.cursor()


def xml_parse(com, path):
    try:
        data = etree.parse(path)
    except:
        try:
            # os.system("PowerShell -Command '& {get-content %s | set-content %s -encoding utf8}'" % (path, path))
            f = codecs.open(path, 'r', 'utf-8')
            content = f.read()  # 文本方式读入
            content = re.sub("GB2312", "UTF-8", content)  # 替换encoding头
            f.close()
            f = open(path, 'w')  # 写入
            f.write(content)
            f.close()
            data = etree.parse(path)
        except:
            try:
            # os.system("PowerShell -Command '& {get-content %s | set-content %s -encoding utf8}'" % (path, path))
                f = codecs.open(path, 'r', 'gbk')
                content = f.read()  # 文本方式读入
                content = re.sub("GB2312", "UTF-8", content)  # 替换encoding头
                f.close()
                f = open(path, 'w')  # 写入
                f.write(content)
                f.close()
                data = etree.parse(path)
            except Exception as e:
                print(str(e))
                print('文件解析问题')
                try:
                    copy_file(path, com)
                    # del_files(path)
                except FileExistsError:
                    return 0
                return 0

    record = []

    row_data = data.getroot()
    for row in row_data:
        for field in row:
            row = []
            fpdm = field.get('发票代码')
            fphm = field.get('发票号码')
            gfmc = field.get('客户名称')
            gfsh = field.get('客户识别号')
            spmc = field.get('主要商品名称')
            je = field.get('合计金额')
            se = field.get('税额')
            kj_name = field.get('开票人')
            jshj = field.get('价税合计')
            kprq = field.get('开票日期')
            row.append(fpdm)
            row.append(fphm)
            row.append(gfmc)
            row.append(gfsh)
            row.append(spmc)
            row.append(je)
            row.append(se)
            row.append(kprq)
            row.append(com)
            row.append(kj_name)
            row.append(path)
            record.append(row)
    return record


def xml_parse_other(com, path):
    """
    处理有单价xml文件
    :param com:
    :param path:
    :return:
    """
    xml = etree.parse(path)
    data = xml.getroot()
    fp_data = data.xpath('/Kp/Fpxx/Fpsj/Fp')
    reocrd = []
    for fp in fp_data:
        tmp = []
        Lbdm = fp.xpath('./Lbdm')[0].text
        Fphm = fp.xpath('./Fphm')[0].text
        Gfmc = fp.xpath('./Gfmc')[0].text
        Gfsh = fp.xpath('./Gfsh')[0].text
        Gfyhzh = fp.xpath('./Gfyhzh')[0].text
        Gfdzdh = fp.xpath('./Gfdzdh')[0].text
        Xfmc = fp.xpath('./Xfmc')[0].text
        Xfsh = fp.xpath('./Xfsh')[0].text
        Xfyhzh = fp.xpath('./Xfyhzh')[0].text
        Xfdzdh = fp.xpath('./Xfdzdh')[0].text
        Kprq = fp.xpath('./Kprq')[0].text
        Kpr = fp.xpath('./Kpr')[0].text
        Spmc = fp.xpath('./Spxx/Sph/Spmc')[0].text
        Jldw = fp.xpath('./Spxx/Sph/Jldw')[0].text
        Dj = fp.xpath('./Spxx/Sph/Dj')[0].text
        Sl = fp.xpath('./Spxx/Sph/Sl')[0].text
        Je = fp.xpath('./Spxx/Sph/Je')[0].text
        Slv = fp.xpath('./Spxx/Sph/Slv')[0].text
        Se = fp.xpath('./Spxx/Sph/Se')[0].text
        tmp.append(Lbdm)
        tmp.append(Fphm)
        tmp.append(Gfmc)
        tmp.append(Gfsh)
        tmp.append(Gfyhzh)
        tmp.append(Gfdzdh)
        tmp.append(Xfmc if Xfmc else com)
        tmp.append(Kprq)
        tmp.append(Kpr)
        tmp.append(Spmc)
        tmp.append(Jldw)
        tmp.append(Dj)
        tmp.append(Sl)
        tmp.append(Je)
        tmp.append(Slv)
        tmp.append(Se)
        tmp.append(path)
        reocrd.append(tmp)
    return reocrd


docxlist = {}
com_name = ''


def copy_file(path_ori, com):  # 将有问题的文件复制到另一个位置
    # base_dir = r'D:\Selvaria\scripts\company\changxing_invoice\有问题公司文件\SWXML\2019-11-25'
    if 'SWXML' in path_ori:
        new_path = './有问题公司文件' + path_ori[1:19]
    elif 'SWEXCEL' in path_ori:
        new_path = './有问题公司文件' + path_ori[1:21]
    elif 'XSZ' in path_ori:
        new_path = './有问题公司文件' + path_ori[1:17]
    #     elif '购销' in path_ori:
    #         new_path = './有问题公司文件'+path_ori[1:16]
    else:  # XSZXLS
        new_path = './有问题公司文件' + path_ori[1:20]
    print(new_path,"#",com)
    if os.path.isdir(new_path):
        os.mkdir(os.path.join(new_path, com))
    else:
        print('建立文件夹的路径不存在')
    shutil.copy(path_ori, './有问题公司文件' + path_ori[1:])  # 复制前后的位置
    print('复制完成:%s' % com)


def del_files(path):
    if os.path.exists(path):  # 如果文件存在
        os.remove(path)
        print('已删除：', path)
    else:
        print('no such file:' % path)


def gci(filepath):
    # 遍历filepath下所有文件，包括子目录
    global com_name
    files = os.listdir(filepath)
    for fi in files:
        if fi == '.DS_Store':
            continue
        fi_d = os.path.join(filepath, fi)
        if os.path.isdir(fi_d):
            if '公司' in fi:
                com_name = fi
                docxlist[com_name] = []
            gci(fi_d)
        else:
            docxlist[com_name].append(fi_d)
    return docxlist


if __name__ == "__main__":
    path_list = gci('./SWEXCEL')
    # path_list = gci('./SWXML')
    # path_list = gci('./二次导入')
    # print(path_list)
    xml = []
    # excel = []
    for k, v in path_list.items():
        if not v:
            continue
        for path in v:
            if 'xml' in path:
                xml.append([k, path])
            else:
                path = path.replace('.xls', '.xml')
                # excel.append([k, path])
                xml.append([k, path])

    # 发票表入库sql
    bill_sql = "INSERT INTO ticket_bill (Lbdm,Fphm,Gfmc,Gfsh,Spmc,Je,Se,Kprq,Xfmc,kj_name,Source) " \
               "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    bill_sql_other = "INSERT INTO ticket_bill (Lbdm,Fphm,Gfmc,Gfsh,Gfyhzh,Gfdzdh,Xfmc,Kprq,kj_name,Spmc," \
                     "Jldw,Dj,Sl,Je,Slv,Se,Source) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    # 交易表入库sql
    trade_sql = "INSERT INTO financial_exchange (Gf_company_name,exchange_good,Je,exchange_date,Xf_company_name,source) " \
                "VALUES (%s,%s,%s,%s,%s,%s)"
    trade_sql_other = "INSERT INTO financial_exchange (Gf_company_name,Xf_company_name,exchange_date,exchange_good," \
                      "Jldw,Dj,Sl,Je,source) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    for r in xml:
        print(r[0])
        print(r[1])
        res = xml_parse(r[0], r[1])
        if res == 0:  # 无法解析文件
            continue
        if res[0][0] is None:
            res = xml_parse_other(r[0], r[1])

            # try:
            #     check_time = int(res[0][7].translate(str.maketrans('', '', '-')))
            #     if check_time > 20190501:  # 按需要筛选时间
            #         cursor.executemany(bill_sql_other, res)
            #     else:
            #         continue
            # except:
            #     try:
            #         check_time = int(res[0][7][:8])
            #         if check_time > 20190501:  # 按需要筛选时间
            #             cursor.executemany(bill_sql_other, res)
            #         else:
            #             continue
            #     except:
            #         pass

            # 处理入交易表数据
            trade_data = []
            for info in res:
                # try:
                #     check_time = int(res[0][7].translate(str.maketrans('', '', '-')))
                # except:
                #     check_time = int(res[0][7][:8])
                # if check_time < 20190501:  # 按需要筛选时间
                #     continue

                tmp = [info[2], info[6], info[7], info[9], info[10], info[11], info[12], info[13], r[1]]
                trade_data.append(tmp)
            cursor.executemany(trade_sql_other, trade_data)
        else:
            bill_data=[]
            for info in res:
                # check_time = int(info[7].translate(str.maketrans('', '', '-')))
                # if check_time < 20190501:
                #     continue# 按需要筛选时间
                bill_data.append(info)
            cursor.executemany(bill_sql, bill_data)

            # 处理入交易表数据
            trade_data = []
            for info in res:

                # check_time = int(info[7].translate(str.maketrans('', '', '-')))
                # if check_time < 20190501:  # 按需要筛选时间
                #     continue

                tmp = [info[2], info[4], info[5], info[7], info[8], r[1]]
                trade_data.append(tmp)
            cursor.executemany(trade_sql, trade_data)
        connection.commit()

        del_files(r[1])
























