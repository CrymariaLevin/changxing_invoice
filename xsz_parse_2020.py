# -*-coding:utf-8-*-
import pymysql
import os
import xlrd
import DB_conn as conn_db

# 序时账里只取买入的数据

# connection = pymysql.connect(host='39.105.9.20', user='root', passwd='bigdata_oil',
#                 db='cxd_data', port=3306, charset='utf8')

# connection = pymysql.connect(host='39.105.9.20', user='root', passwd='bigdata_oil',
#                 db='cxd_test', port=3306, charset='utf8')

connection = conn_db.connection
cursor = connection.cursor()

oil_key = ['油', '沥青', '92', '95', '0', '35', '燃料', '油气', '苯', '热载体', '烯', '醚', '醇', '天然气', '液化',\
           '烷', '烃', '碳', 'MTBE', '剂', '脂', '酚', '酯', '原料']
com_key = ['公司', '加油', '厂', '气站', 'LTD', 'CO']
trade_key = ['购', '销']

docxlist = {}
com_name = ''

def name_filter(com_name): # 有些特殊的记账方式对应的名字
    filter = ['单位', '往来单位', '应付账款', '客户']
    com = com_name
    for f in filter:
        if com_name.startswith(f):
            com = com_name[len(f):]
    return com


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


def read_xls(path):
    # xls文件解析
    record = []
    data = None
    try:
        data = xlrd.open_workbook(path, encoding_override="cp936")  # 打开xls文件
    except Exception as e:
        print(e)
        data = xlrd.open_workbook(path, encoding_override="cp1252")
    finally:
        if data.sheets():
            table = data.sheets()[0]  # 打开第一张表
            nrows = table.nrows  # 获取表的行数
            for i in range(nrows):  # 循环逐行打印
                if i == 0:  # 跳过第一行
                    continue
                record.append(table.row_values(i))
        return record


def data_merge(com, original_data, path):
    # 将序时账合并为对应的一条数据
    # 样例数据
    # [['10', '*', '', '', '2019-10-31', '记-1', '购货', '140587', '库存商品 - 0号  车用柴油(IV)', '', '', '', '', '',
    # 'RMB', '', 199821.24, 199821.24, 0.0, 'Manager', '', 'Manager', '', '', '', '32.221', '6,201.58'],
    # ['10', '*', '', '', '', '', '购货', '140564', '库存商品 - 0#车用柴油 （VI）', '', '', '', '', '', 'RMB', '',
    # 635065.12, 635065.12, 0.0, 'Manager', '', 'Manager', '', '', '', '100.654', '6,309.39'],
    # ['10', '*', '', '', '', '', '购货', '22210101', '应交税费 - 应交增值税 - 进项税额', '', '', '', '', '', 'RMB', '',
    # 108535.22, 108535.22, 0.0, 'Manager', '', 'Manager', '', '', '', '', ''],
    # ['10', '*', '', '', '', '', '购货', '220240', '应付账款 - 四川中油九洲北斗科技能源有限公司', '', '', '', '', '', 'RMB',
    # '', 943421.58, 0.0, 943421.58, 'Manager', '', 'Manager', '', '', '', '', '']]
    result = []
    oil_list = []
    com_list = []
    if len(original_data[0])<28: #文件结构错误
        return -1
    if '购' in original_data[0][6]:
        flag = 0    # 0:购 1:销
    else:
        flag = 1
    for record in original_data:
        # 解析油品名称
        # if any(key in record[8] for key in oil_key) and '公司' not in record[8] and '加油' not in record[8] and '厂' not in record[8]:
        if any(key in record[8] for key in oil_key) and all(key not in record[8] for key in com_key):
            # for r in record[8].replace(' ', '').split('-'):
            # for r in record[8].replace(' -- ', ' - ').replace(' ', '').split('-'):
            r = record[8].replace('库存商品 -', '').strip()
            if any(key in r for key in oil_key):
                oil_list.append(r)
                    # com_list.append(r)
        # 解析公司名称
        # elif '公司' in record[8] or '加油站' in record[8] or '厂' in record[8]:
        elif any(key in record[8] for key in com_key):
            for r in record[8].replace(' -- ', ' - ').replace(' ', '').split('-'):
                if any(key in r for key in com_key):
                    com_list.append(r)
        # 解析特殊公司的名称（不含任何公司相关的关键字）
        # elif '账款' in record[8] and '公司' not in record[8] and '加油' not in record[8] and '厂' not in record[8]:
        elif '账款' in record[8] and all(key not in record[8] for key in com_key):
            for r in record[8].replace(' -- ', ' - ').replace(' ', '').split('-'):
                if '账款' not in r and len(r) > 1:
                    com_list.append(r)
    oil_num = len(oil_list)
    com_num = len(com_list)
    if len(oil_list) < 1 or len(com_list) < 1: # 对应解析失败
        if flag == 0:
            print('oil_num:', oil_num, oil_list)
            print('com_num:', com_num, com_list)
            print('公司名称解析失败')
            return -2
        else:
            print('此记录为卖出记录，不予统计')
            return 0
    elif oil_num == 1 and com_num == 1:   # 油品公司一对一对应，最简单的匹配
        if flag == 0:
            xf = name_filter(com_list[0])
            gf = name_filter(com)
        else:
            print('此记录为卖出记录，不予统计')
            return 0
            # xf = com
            # gf = com_list[0]
        date = original_data[0][4]
        spmc = oil_list[0]
        Je = original_data[0][16]
        Sl = original_data[0][25] if original_data[0][25] else None
        Dj = original_data[0][26] if original_data[0][26] else None
        if ',' in str(Dj):
            Dj = Dj.replace(',', '')
        result.append((xf, gf, date, spmc, Je, Sl, Dj, path))
    elif oil_num > 1 and com_num == 1:  # 一个公司多个油品：
        if flag == 0:
            # xf = com_list[0]
            # gf = com
            xf = name_filter(com_list[0])
            gf = name_filter(com)
        else:
            print('此记录为卖出记录，不予统计')
            return 0
            # xf = com
            # gf = com_list[0]
        date = original_data[0][4]
        for m in oil_list:
            oil_ori = []
            for n in original_data:
                if m in n[8] and n[8] not in oil_ori:
                    spmc = m
                    oil_ori.append(n[8])
                    Je = n[16]
                    Sl = n[25] if n[25] else None
                    Dj = n[26] if n[26] else None
                    if ',' in str(Dj):
                        Dj = Dj.replace(',', '')
                    result.append((xf, gf, date, spmc, Je, Sl, Dj, path))
    elif oil_num > 1 and com_num > 1 and oil_num == com_num:  # 数量相同一一按顺序对应
        if flag == 0:
            # xf = name_filter(com_list[0])
            gf = name_filter(com)
        else:
            print('此记录为卖出记录，不予统计')
            return 0
        date = original_data[0][4]
        price = []
        for n in original_data:
            # original_data: [['1', '*', '', '', '2019-01-31', '通用-1', '购货', '140506', '库存商品 - -10号车用柴油（VI）', '', '', '', '', '', \
            # 'RMB', '', 982758.62, 982758.62, 0.0, 'Manager', '', 'Manager', '', '', '', '200.00', '4,913.79', 2],
            # ['1', '*', '', '', '2019-01-31', '通用-1', '购货', '140506', '应付账款 - 四川中油九洲北斗科技能源有限公司', '', '', '', '', '', \
            # 'RMB', '', 982758.62, 982758.62, 0.0, 'Manager', '', 'Manager', '', '', '', '', '', 2]]
            if len(str(n[25])) > 2:
                Je = n[16]
                Sl = n[25] if n[25] else None
                Dj = n[26] if n[26] else None
                if ',' in str(Dj):
                    Dj = Dj.replace(',', '')
                price.append([Je, Sl, Dj, path])
        # print(len(price))
        title = []
        for i in range(len(com_list)):
            xf = com_list[i]
            spmc = oil_list[i]
            t = [xf, gf, date, spmc]
            title.append(t)
        for i in range(len(price)):
            row = title[i] + price[i]
            result.append(tuple(row))
    else:   # 多个油品对应多家公司，油品数目与公司数目可能不等。或者一个产品对应多个公司
        if flag == 0:
            # xf = name_filter(com_list[0])
            gf = name_filter(com)
        else:
            print('此记录为卖出记录，不予统计')
            return 0
        print('oil_num:',oil_num,oil_list)
        print('com_num:',com_num,com_list)
        print('合并记账，暂时没想到好方法,可先将此文件做记录，后续处理')
        return -2
    return result

def main():
    """
        序时账表头
        ['0期间', '1过账', '2审核', '3作废', '4日期', '5凭证字号', '6摘要', '7科目代码', '8科目名称',
        '9往来单位', '10部门', '11职员', '12自定义项目', '13业务编号', '14币别', '15汇率', '16原币金额',
        '17借方金额', '18贷方金额', '19制单人', '20审核人', '21过账人', '22结算方式', '23结算号',
         '24结算日期', '25数量', '26单价', '27附件数']
        """
    path_list = gci('./XSZ')
    error_list = []
    error_data = []
    update_list = []
    match_error_list = []
    for k, v in path_list.items():
        for file_path in v:
            final_data = []
            if '序时' not in file_path:
                continue
            print(file_path)
            file_data = read_xls(file_path)

            if file_data:
                # 跳过无关公司的序时账
                if len(file_data[0]) < 27:
                    continue
                if '2019' in str(file_data[0][4]) or '2020' in str(file_data[0][4]):
                    temp = []
                    temp_data = []
                    index = 1
                    for r in file_data:
                        index += 1
                        r = r + [index, ]
                        if temp and r[4]:  # 判断是否是新账目(按日期）
                            if any(key in temp[0][6] for key in trade_key):  # 判断是否是购销
                                # if any(key in temp[0][8] for key in oil_key) and '公司' not in temp[0][8] and '加油' not in temp[0][8] \
                                #         and '厂' not in temp[0][8]:  # 是否包含油品
                                if any(key in temp[0][8] for key in oil_key) and all(key not in temp[0][8] for key in com_key):
                                    temp_data.append(temp)
                            temp = []
                        temp.append(r)
                    for r in temp_data:
                        try:
                            middle_data = data_merge(k, r, file_path)
                            if middle_data == -2:
                                error_data.append([r, file_path])
                                match_error_list.append(file_path)  # 添加没想到好方法文件的路径信息(合并记账）
                                continue
                            elif middle_data == -1: # 解析失败企业
                                error_list.append(file_path)
                                continue
                            elif middle_data == 0: # 该记录为卖出记录
                                continue
                            if middle_data:
                                for j in middle_data:
                                    final_data.append(j)
                        except Exception as e:
                            print('有问题公司：', file_path)
                            print(str(e))
                            error_list.append(file_path)  # 添加解析文件出错的路径信息
            # print(final_data)
            update_list.extend(final_data)
    # print('err:',error_list)
    # print('update:',update_list)

    # 上传到数据库, 单独取录入错误的数据条数时要注释掉
    # 交易表入库sql
    trade_sql = "INSERT INTO financial_exchange (Xf_company_name,Gf_company_name,exchange_date,exchange_good,Je,Sl,Dj,source" \
                ") VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.executemany(trade_sql, update_list)
    connection.commit()

    no_match_list = {}
    for com in match_error_list:
        if com not in no_match_list.keys():
            no_match_list[com]=match_error_list.count(com)

    print('合并记账企业：\n', no_match_list)
    return error_list, error_data


if __name__ == "__main__":
    e1, e2 = main()
    with open('./files/序时账解析错误公司.txt', 'w', encoding='utf-8') as w:
        for l in e1:
            w.write(l+'\n')
    # print('error_data: \n', e2[0][0])
    with open('./files/序时账合并记账详细企业记录.txt', 'w', encoding='utf-8') as w:
        for l in e2:
            for err in l[0]:
                # for e in err:
                error_row_index = ' index: ' + str(err[-1])
                w.write(l[1] + error_row_index + '\n')




















