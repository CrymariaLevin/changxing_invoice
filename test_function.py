# 测试功能

import os

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

def gci_gx(filepath):
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

com_name = ''
docxlist = {}
print(gci('2020第一批/进销发票明细'))

com_name = ''
docxlist = []
print(gci_gx('购销'))
