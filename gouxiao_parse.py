# -*-coding:utf-8-*-
"""
处理购销数据
数据直接入发票表与交易表
注意个别企业由于数据问题,需要单独处理,在read_xls函数和main函数中要注意
"""
import pymysql
import os
import xlrd

# 测试录入
connection = pymysql.connect(host='39.105.9.20', user='root', passwd='bigdata_oil', db='cxd_test', port=3306, charset='utf8')

# connection = pymysql.connect(host='39.105.9.20', user='root', passwd='bigdata_oil', db='cxd_data', port=3306, charset='utf8')

cursor = connection.cursor()


def read_xls(path):
    record = []
    data = xlrd.open_workbook(path,encoding_override="cp1252")  # 打开xls文件
    table = data.sheets()[0]  # 打开第一张表
    nrows = table.nrows  # 获取表的行数
    ncols = table.ncols
    if ncols < 21 and '汇通天下' not in path:
        return 0
    for i in range(nrows):  # 循环逐行打印
        if i == 0:  # 跳过第一行
            continue
        record.append(table.row_values(i))
    return record


def parse_data(com, info_data, path):
    """
    ['0序号', '1发票类型', '2发票代码', '3发票号码', '4作废标志', '5发票状态', '6开票日期', '7销方纳税人名称',
     '8销方社会信用代码（纳税人识别号）', '9销方主管税务机关', '10购方纳税人名称',
     '11购方社会信用代码（纳税人识别号）', '12购方主管税务机关',
     '13货物或应税劳务、服务名称', '14规格型号', '15计量单位', '16数量', '17单价', '18金额', '19税率', '20税额']
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
        tmp.append(path)
        record.append(tmp)
    return record

def parse_data_large(com, info_data, path): #特殊企业数据太多
    """
    ['0序号', '1购方企业名称', '2购方企业税号', '3发票代码', '4发票号码', '5开票日期',
    '6货物名称', '7型号', '8单位', '9单价', '10数量', '11金额', '12税额']
    :param com:
    :param info_data:
    :return:
    """
    record = []
    for info in info_data:
        tmp = []
        Lbdm = info[3]
        Fphm = info[4]
        Gfmc = info[1]
        Gfsh = info[2]
        Xfmc = com
        Kprq = info[5]
        Spmc = info[6]
        Ggxh = info[7]
        Jldw = info[8]
        # Dj = round(float(info[17]), 4) if info[17] else info[17]
        Dj = info[9]
        # Sl = round(float(info[16]), 4) if info[16] else info[16]
        Sl = info[10]
        Je = info[11]
        Se = info[12]
        Slv = str(int(float(Se)/float(Je)*100))+'%'
        tmp.append(Lbdm)
        tmp.append(Fphm)
        tmp.append(Gfmc)
        tmp.append(Gfsh)
        tmp.append(Xfmc)
        tmp.append(Kprq)
        tmp.append(Spmc)
        tmp.append(Ggxh)
        tmp.append(Jldw)
        tmp.append(Dj)
        tmp.append(Sl)
        tmp.append(Je)
        tmp.append(Slv)
        tmp.append(Se)
        tmp.append(path)
        record.append(tmp)
    return record


docxlist = {}
com_name = ''


# def gci(filepath):
#     # 遍历filepath下所有文件，包括子目录
#     global com_name
#     files = os.listdir(filepath)
#     for fi in files:
#         if fi == '.DS_Store':
#             continue
#         fi_d = os.path.join(filepath, fi)
#         if os.path.isdir(fi_d):
#             gci(fi_d)
#         else:
#             info = [fi_d]
#             tmp = fi.split('.')[0]
#             com = tmp.split(' ')[0]
#             if '销项' in tmp:  # 1为销项，入发票表
#                 flag = 1
#             else:
#                 flag = 0
#             info.extend([com, flag])
#             docxlist.append(info)
#     return docxlist

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
                com_name = fi.split('-')[0]
                docxlist[com_name] = []
            gci(fi_d)
        else:
            docxlist[com_name].append(fi_d)
    return docxlist



if __name__ == "__main__":
    # path_list = gci('2020第一批/国税发票明细')
    path_list = gci('2020第一批/剩余发票明细')
    error_list = []
    # print(path_list)

    bill_sql = "INSERT INTO ticket_bill (Lbdm,Fphm,Gfmc,Gfsh,Xfmc,Kprq,Spmc,Ggxh,Jldw,Dj,Sl,Je,Slv,Se,Source) " \
               "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    trade_sql = "INSERT INTO financial_exchange (Gf_company_name,Xf_company_name,exchange_date,exchange_good,Jldw,Dj," \
                "Sl,Je,source) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    for com, p in path_list.items():
        # print(com)
        for path in p:
            print('开始录入文件：', path)
            fp_data = read_xls(path)
            if fp_data == 0:
                # error_list.append(path)
                error_list.append(com)
                continue
            if '汇通天下' in com and '销' in path:
                fp = parse_data_large(com, fp_data, path)
            else:
                fp = parse_data(com, fp_data, path)
            # print(fp)
            if '销' in path: # 销项还要单独入到发票表
                cursor.executemany(bill_sql, fp)
            # 处理入交易表数据
            trade_data = []
            for info in fp:
                # check_time = int(info[5].translate(str.maketrans('', '', '-')))
                # if check_time < 20190501:  # 按需要筛选时间
                #     continue
                tmp = [info[2], info[4], info[5], info[6], info[8], info[9], info[10], info[11], path]
                trade_data.append(tmp)
            # print(trade_data)
        try:
            cursor.executemany(trade_sql, trade_data)
        except Exception as e:
            print(str(e))
        connection.commit()

    reload_list = []
    for com in error_list:
        if com not in reload_list:
            reload_list.append(com)
    print('结构错误企业：\n', reload_list)




















