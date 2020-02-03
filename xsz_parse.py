# -*-coding:utf-8-*-
import pymysql
import os
import xlrd
# import pretty_errors

# 注意改main函数里的日期

connection = pymysql.connect(host='39.105.9.20', user='root', passwd='bigdata_oil',
                db='cxd_data', port=3306, charset='utf8')
cursor = connection.cursor()

oil_key = ['油', '沥青', '92', '95', '0', '35', '10']
trade_key = ['购', '销']

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


def data_merge(com, original_data):
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
    if '购' in original_data[0][6]:
        flag = 0    # 0:购 1:销
    else:
        flag = 1
    for record in original_data:
        if any(key in record[8] for key in oil_key) and '公司' not in record[8]:
            for r in record[8].replace(' ', '').split('-'):
                if any(key in r for key in oil_key):
                    oil_list.append(r)
        elif '公司' in record[8]:
            for r in record[8].replace(' ', '').split('-'):
                if '公司' in r:
                    com_list.append(r)
    oil_num = len(oil_list)
    com_num = len(com_list)
    if oil_num == 1 and com_num == 1:   # 油品公司一一对应，最简单的匹配
        if flag == 0:
            xf = com_list[0]
            gf = com
        else:
            xf = com
            gf = com_list[0]
        date = original_data[0][4]
        spmc = oil_list[0]
        Je = original_data[0][16]
        Sl = original_data[0][25] if original_data[0][25] else None
        Dj = original_data[0][26] if original_data[0][26] else None
        if ',' in str(Dj):
            Dj = Dj.replace(',', '')
        result.append((xf, gf, date, spmc, Je, Sl, Dj))
    elif oil_num > 1 and com_num == 1:  # 一个公司多个油品：
        if flag == 0:
            xf = com_list[0]
            gf = com
        else:
            xf = com
            gf = com_list[0]
        date = original_data[0][4]
        for m in oil_list:
            for n in original_data:
                if m in n:
                    spmc = oil_list[0]
                    Je = n[16]
                    Sl = n[25] if n[25] else None
                    Dj = n[26] if n[26] else None
                    if ',' in str(Dj):
                        Dj = Dj.replace(',', '')
                    result.append((xf, gf, date, spmc, Je, Sl, Dj))
    else:   # 多个油品对应多家公司，油品数目与公司数目可能不等
        print('暂时没想到好方法,可先将此文件做记录，后续处理')
        return -1
    return result

def main():
    """
        序时账表头
        ['0期间', '1过账', '2审核', '3作废', '4日期', '5凭证字号', '6摘要', '7科目代码', '8科目名称',
        '9往来单位', '10部门', '11职员', '12自定义项目', '13业务编号', '14币别', '15汇率', '16原币金额',
        '17借方金额', '18贷方金额', '19制单人', '20审核人', '21过账人', '22结算方式', '23结算号',
         '24结算日期', '25数量', '26单价', '27附件数']
        """
    path_list = gci('XSZ')
    error_list = []
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
                if '2019' in str(file_data[0][4]):
                    temp = []
                    temp_data = []
                    for r in file_data:
                        if temp and r[4]:  # 判断是否是新账目
                            if any(key in temp[0][6] for key in trade_key):  # 判断是否是购销
                                if any(key in temp[0][8] for key in oil_key) and '公司' not in temp[0][8]:  # 是否包含油品
                                    temp_data.append(temp)
                            temp = []
                        temp.append(r)
                    for r in temp_data:
                        try:
                            middle_data = data_merge(k, r)
                            if middle_data == -1:
                                match_error_list.append(file_path)  # 添加没想到好方法文件的路径信息
                                continue
                            if middle_data:
                                for j in middle_data:
                                    final_data.append(j)
                        except:
                            print('有问题公司：', file_path)
                            error_list.append(file_path)  # 添加解析文件出错的路径信息
            # print(final_data)
            update_list.extend(final_data)
    # print('err:',error_list)
    # print('update:',update_list)

    # 上传到数据库
    # 交易表入库sql
    trade_sql = "INSERT INTO financial_exchange (Xf_company_name,Gf_company_name,exchange_date,exchange_good,Je,Sl,Dj" \
                ") VALUES (%s,%s,%s,%s,%s,%s,%s)"
    cursor.executemany(trade_sql, update_list)
    connection.commit()

def test(k,file_path):
    file_data = read_xls(file_path)
    final_data =[]
    if file_data:
        # 跳过无关公司的序时账
        if len(file_data[0]) < 27:
            print('格式有误')
        if '2019' in str(file_data[0][4]):
            temp = []
            temp_data = []
            for r in file_data:
                if temp and r[4]:  # 判断是否是新账目
                    if any(key in temp[0][6] for key in trade_key):  # 判断是否是购销
                        if any(key in temp[0][8] for key in oil_key) and '公司' not in temp[0][8]:  # 是否包含油品
                            temp_data.append(temp)
                    temp = []
                temp.append(r)
            for r in temp_data:
                try:
                    middle_data = data_merge(k, r)
                    if middle_data == -1:
                        print('middle_data == -1')
                        continue
                    if middle_data:
                        for j in middle_data:
                            final_data.append(j)
                except:
                    print('有问题公司：', file_path)
    print(final_data)


if __name__ == "__main__":
    main()
    # test('大连国和诚宇石油化工有限公司',r'D:\Selvaria\scripts\company\changxing_invoice\XSZ\2019-11-25\大连国和诚宇石油化工有限公司\85801509-cf84-40d7-be8f-2b6494e6fa8d_大连国和诚宇石油化工有限公司序时账.xls')




















