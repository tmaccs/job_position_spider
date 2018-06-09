# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JobPositionItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    session = scrapy.Field()  # 搜索词典的session名字
    keyword = scrapy.Field()  # 搜索的关键字
    position = scrapy.Field()  # 职位
    source = scrapy.Field()  # 职位来源
    page_url = scrapy.Field()  # 职位链接

    # 公司信息
    company_name = scrapy.Field()  # 公司名
    company_trade = scrapy.Field()  # 公司所属行业
    company_type = scrapy.Field()  # 公司类型
    company_size = scrapy.Field()  # 公司规模
    company_address = scrapy.Field()  # 公司地址

    # 职位基本信息
    department = scrapy.Field()  # 部门
    job_type = scrapy.Field()  # 职位类别
    subordinate = scrapy.Field()  # 下属人数
    requirement = scrapy.Field()  # 招聘人数
    work_place = scrapy.Field()  # 工作地点
    publish_time = scrapy.Field()  # 发布时间
    supervisor = scrapy.Field()  # 汇报对象

    # 薪酬信息
    salary = scrapy.Field()  # 年薪范畴

    # 职位描述
    job_detail = scrapy.Field()  # 职位描述

    # 其他要求
    experience = scrapy.Field()  # 工作经验
    education = scrapy.Field()  # 学历要求
    age = scrapy.Field()  # 年龄要求
    full_time = scrapy.Field()  # 是否统招全日制
    major = scrapy.Field()  # 专业要求
    oversea = scrapy.Field()  # 海外经历
    language = scrapy.Field()  # 语言要求

    # 公司介绍
    company_detail = scrapy.Field()  # 公司介绍

