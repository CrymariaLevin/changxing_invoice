# -*-coding:utf-8-*-
"""
处理购销数据
数据直接入发票表与交易表
"""
import pymysql
import os
import xlrd

connection = pymysql.connect(host='39.105.9.20', user='root', passwd='bigdata_oil',
                db='cxd_data', port=3306, charset='utf8')
cursor = connection.cursor()


def read_xls(path):
    record = []
    data = xlrd.open_workbook(path,encoding_override="cp1252")  # 打开xls文件
    table = data.sheets()[0]  # 打开第一张表
    nrows = table.nrows  # 获取表的行数
    for i in range(nrows):  # 循环逐行打印
        if i == 0:  # 跳过第一行
            continue
        record.append(table.row_values(i))
    return record


def parse_data(com, info_data):
    """
    ['0序号', '1发票类型', '2发票代码', '3发票号码', '4作废标志', '5发票状态', '6开票日期', '7销方纳税人名称',
     '8销方社会信用代码（纳税人识别号）', '9销方主管税务机关', '10购方纳税人名称',
     '11购方社会信用代码（纳税人识别号）', '12购方主管税务机关', '13货物或应税劳务、服务名称', '14规格型号',
     '15计量单位', '16数量', '17单价', '18金额', '19税率', '20税额']
    :param com:
    :param info_data:
    :return:
    """
    record = []
    for info in info_data:
        tmp = []
        Lbdm = info[2]
        Fphm = info[3]
        Gfmc = info[10]
        Gfsh = info[11]
        Xfmc = info[7]
        Kprq = info[6]
        Spmc = info[13]
        Ggxh = info[14]
        Jldw = info[15]
        # Dj = round(float(info[17]), 4) if info[17] else info[17]
        Dj = info[17]
        # Sl = round(float(info[16]), 4) if info[16] else info[16]
        Sl = info[16]
        Je = info[18]
        Slv = info[19]
        Se = info[20]
        tmp.append(Lbdm)
        tmp.append(Fphm)
        tmp.append(Gfmc)
        tmp.append(Gfsh)
        tmp.append(Xfmc if Xfmc else com)
        tmp.append(Kprq)
        tmp.append(Spmc)
        tmp.append(Ggxh)
        tmp.append(Jldw)
        tmp.append(Dj)
        tmp.append(Sl)
        tmp.append(Je)
        tmp.append(Slv)
        tmp.append(Se)
        record.append(tmp)
    return record


docxlist = []
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
            gci(fi_d)
        else:
            info = [fi_d]
            tmp = fi.split('.')[0]
            com = tmp.split(' ')[0]
            if '销项' in tmp:  # 1为销项，入发票表
                flag = 1
            else:
                flag = 0
            info.extend([com, flag])
            docxlist.append(info)
    return docxlist


if __name__ == "__main__":
    path_list = gci('购销')
    # print(path_list)

    # bill_sql = "INSERT INTO ticket_bill (Lbdm,Fphm,Gfmc,Gfsh,Xfmc,Kprq,Spmc,Ggxh,Jldw,Dj,Sl,Je,Slv,Se) " \
    #            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    trade_sql = "INSERT INTO financial_exchange (Gf_company_name,Xf_company_name,exchange_date,exchange_good,Jldw,Dj," \
                "Sl,Je) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"

    for r in path_list:
        # if r[2] == 0:  # 若只入发票表，运行此行代码
        #     continue
        print(r[1], r[0])
        fp_data = read_xls(r[0])
        fp = parse_data(r[1], fp_data)
        print(fp)
        # cursor.executemany(bill_sql, fp)
        # 处理入交易表数据
        trade_data = []
        for info in fp:
            check_time = int(info[5].translate(str.maketrans('', '', '-')))
            if check_time < 20190501:  # 按需要筛选时间
                continue
            tmp = [info[2], info[4], info[5], info[6], info[8], info[9], info[10], info[11]]
            trade_data.append(tmp)
        print(trade_data)
        try:
            cursor.executemany(trade_sql, trade_data)
        except Exception as e:
            print(str(r))
            print(str(e))
        connection.commit()




















