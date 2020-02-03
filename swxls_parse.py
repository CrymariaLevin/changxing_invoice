# -*-coding:utf-8-*-
"""
处理excel财务数据
数据直接入发票表与交易表
注意在main函数里有时间筛选
"""
import pymysql
import os
import xlrd
from decimal import Decimal

connection = pymysql.connect(host='39.105.9.20', user='root', passwd='bigdata_oil',
                db='cxd_data', port=3306, charset='utf8')
cursor = connection.cursor()


def read_xls(path, flag=0):
    record = []
    data = xlrd.open_workbook(path, encoding_override="cp1252")  # 打开xls文件
    table = data.sheets()[0]  # 打开第一张表
    nrows = table.nrows  # 获取表的行数
    # print(nrows)
    if flag == 0:
        for i in range(nrows):
            if i < 4:  # 跳过前4行
                continue
            record.append(table.row_values(i))
    else:
        for i in range(nrows-1):
            if i < 6:  # 跳过前6行
                continue
            record.append(table.row_values(i))
    return record


docxlist = {}
com_name = ''


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


def parse_data(com, info_data):
    """
    发票1：
    ['0发票代码', '1发票号码', '2购方企业名称', '3购方税号', '4银行帐号', '5地址电话', '6开票日期',
    '7商品编码版本号', '8单据号', '9商品名称', '10规格',
    '11单位', '12数量', '13单价', '14金额', '15税率', '16税额', '17税收分类编码']
    发票2：
    ['0发票代码', '1发票号码', '2购方企业名称', '3购方税号', '4银行帐号', '5地址电话', '6开票日期',
    '7单据号', '8备注', '9商品名称', '10规格', '11单位', '12数量', '13单价', '14金额', '15税率', '16税额', '17发票状态']
    :param com:
    :param info_data:
    :return:
    """
    record = []
    Xfmc = com

    for fp_info in info_data:
        if '小计' in fp_info or '份数' in fp_info[0]:
            continue
        if fp_info[0] != '':
            Lbdm = fp_info[0]
            Fphm = fp_info[1]
            Gfmc = fp_info[2]
            Gfsh = fp_info[3]
            Gfyhzh = fp_info[4]
            Gfdzdh = fp_info[5]
            Kprq = fp_info[6][:10]
            Spmc = fp_info[9]
            Ggxh = fp_info[10]
            Jldw = fp_info[11]
            Sl = fp_info[12]
            Dj = fp_info[13]
            Je = fp_info[14]
            Slv = fp_info[15]
            Se = fp_info[16]
        else:
            Spmc = fp_info[9]
            Ggxh = fp_info[10]
            Jldw = fp_info[11]
            # Sl_t = Decimal(fp_info[12]).quantize(Decimal('0.00'))  # Decimal('5.000').quantize(Decimal('0.00'))
            # Sl = float(str(Sl_t))
            Sl = fp_info[12]
            Dj = fp_info[13]
            Je = fp_info[14]
            Slv = fp_info[15]
            Se = fp_info[16]
        record.append([Lbdm, Fphm, Gfmc, Gfsh, Gfyhzh, Gfdzdh,
                       Kprq, Spmc, Ggxh, Jldw, Sl, Dj, Je, Slv, Se, Xfmc])
    return record

def del_files(path):
    if os.path.exists(path):  # 如果文件存在
        os.remove(path)
        print('已删除：',path)
    else:
        print('no such file:'%path)


if __name__ == "__main__":
    path_list = gci('./SWEXCEL')
    # path_list = gci('./有问题的xls')
    xml = []
    excel = []
    excel_other = []
    for k, v in path_list.items():
        # print(k, v)
        if not v:
            continue
        for path in v:
            if '序时' in path or '余额' in path:
                continue
            if 'xml' in path:
                xml.append([k, path])
            else:
                if 'xls' not in path and 'xlsx' not in path:
                    continue
                if 'xlsx' in path or '明细' in path:
                    excel_other.append([k, path])
                else:
                    excel.append([k, path])

    # 发票表入库sql
    bill_sql = "INSERT INTO ticket_bill (Lbdm,Fphm,Gfmc,Gfsh,Gfyhzh,Gfdzdh,Kprq,Spmc,Ggxh,Jldw,Sl,Dj,Je,Slv,Se,Xfmc) " \
               "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    
    # 交易表入库sql
    trade_sql = "INSERT INTO financial_exchange (Gf_company_name,exchange_date,exchange_good,Jldw,Sl,Dj,Je," \
                "Xf_company_name) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"

    # for r in excel:
    #     print(r[1])
    #     fp_data = read_xls(r[1])
    #     fp = parse_data(r[0], fp_data)
    #     try:
    #         fp = parse_data(r[0], fp_data)
    #     except Exception as e:
    #         print(str(e))
    #         print('问题文件：',r[1])
    #         break
    #     cursor.executemany(bill_sql, fp)

        #处理入交易表数据
        trade_data = []
        for info in fp:
            check_time = int(info[6].translate(str.maketrans('', '', '-')))
            if check_time < 20190501: # 按需要筛选时间
                continue
            tmp = [info[2], info[6], info[7], info[9], info[10], info[11], info[12], info[15]]
            trade_data.append(tmp)
        print(trade_data)
        cursor.executemany(trade_sql, trade_data)

        connection.commit()
        del_files(r[1])

    for r in excel_other:
        print(r[1])
        fp_data = read_xls(r[1], 1)
        #print(r[1])
        fp = parse_data(r[0], fp_data)
        try:
            fp = parse_data(r[0], fp_data)
        except Exception as e:
            print(str(e))
            print('问题文件：',r[1])
            break
        cursor.executemany(bill_sql, fp)

        #处理入交易表数据
        trade_data = []
        for info in fp:
            # print(info)
            check_time = int(info[6].translate(str.maketrans('', '', '-')))
            if check_time < 20190501:  # 按需要筛选时间
                continue
            tmp = [info[2], info[6], info[7], info[9], info[10], info[11], info[12], info[15]]
            trade_data.append(tmp)
        print(trade_data)
        cursor.executemany(trade_sql, trade_data)

        connection.commit()
        del_files(r[1])
























