# -*- coding: utf-8 -*-

import json


def try_get_value_from_array(array, index=0):

    try:
        # 去掉由空格字符组成的数组元素，以及元素首尾的空格
        value = [i.strip() for i in array if len(i.strip()) > 0][index]
    except Exception as e:
        value = None

    return value


# 加载excel输出配置文件，json格式
def load_job_excel_config():
    d = json.loads(open('output.mapping').read())
    return d['job_position']


# 通过配置文件的映射，将爬取到的数据存进EXCEL
def build_job_excel_line(config, item):
    line = []
    for i in config['heads']:
        tv = config['line'].get(i, None)
        if tv is None or len(tv) == 0:
            value = None
        else:
            value = item.get(tv, None)
        line.append(value)

    return line

