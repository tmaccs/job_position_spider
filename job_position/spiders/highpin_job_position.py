# -*- coding: utf-8 -*-
# Base class for highpin_job_position Spider
# Author ian.Yang
# Create date 2018-06-05

import logging
import scrapy
from scrapy.http import Request

from job_position.items import JobPositionItem
from job_position.utils import try_get_value_from_array


class HighpinJobPosition(scrapy.Spider):
    name = 'highpin_job'
    start_urls = ['http://www.highpin.cn/shanghai/ci_201100.html']
    # start_urls = ['http://www.highpin.cn/shanghai/jt_2090000.html', 'http://www.highpin.cn/shanghai/ci_201100.html']

    def parse(self, response):
        total_page = int(response.xpath(
            u'//*[@class="c-pagenext-li"]/preceding-sibling::li[1]/a/text()').extract()[0])
        current_page = int(response.xpath(
            u'//a[@class="c-pageactive sign"]/text()').extract()[0])
        logging.info('Page {}/{}'.format(current_page, total_page))

        if current_page != total_page:
            url = self.build_search_url(current_page + 1)
            page_request = Request(url)
            yield page_request

        # 获取每个职位信息
        jobs = response.xpath('//p[@class="jobname clearfix"]/a')
        for job in jobs:
            item = JobPositionItem()
            # 存储信息
            item['page_url'] = response.urljoin(job.xpath('./@href').extract()[0])
            item['position'] = job.xpath('./text()').extract()[0]
            item['source'] = 'highpin'
            job_request = Request(item['page_url'], callback=self.parse_item)
            job_request.meta['item'] = item
            yield job_request

    # 获取每个职位的信息
    def parse_item(self, response):
        item = response.meta['item']
        company_info = response.xpath(u'.')
        self.parse_company_info(company_info, item)

        basic_info = response.xpath(u'//*[text()="基本信息"]/..')
        self.parse_basic_info(basic_info, item)

        salary_info = response.xpath(u'//*[text()="薪酬信息"]/..')
        self.parse_salary_info(salary_info, item)

        job_detail_info = response.xpath(
            u'//*[text()="职位描述"]/following-sibling::div')
        self.parse_job_detail_info(job_detail_info, item)

        other_requirement_info = response.xpath(u'//*[text()="其他要求"]/..')
        self.parse_other_requirement_info(other_requirement_info, item)

        company_detail_info = response.xpath(u'//*[text()="公司介绍"]/..')
        self.parse_company_detail_info(company_detail_info, item)
        yield item

    # 获取公司的信息
    @ staticmethod
    def parse_company_info(root, item):
        list_items = root.xpath('.')
        item['company_name'] = try_get_value_from_array(list_items.xpath(
            u'.//*[text()="公司名称："]/../a/text()').extract())
        item['company_trade'] = try_get_value_from_array(list_items.xpath(
            u'//*[text()="所属行业："]/following-sibling::span/text()').extract())
        item['company_type'] = try_get_value_from_array(
            list_items.xpath(u'.//*[text()="公司性质："]/../text()').extract())
        item['company_size'] = try_get_value_from_array(
            list_items.xpath(u'.//*[text()="公司规模："]/../text()').extract())
        item['company_address'] = try_get_value_from_array(list_items.xpath(
            u'.//*[text()="公司地址："]/../span[@title]/text()').extract())

    # 获取基本信息
    @ staticmethod
    def parse_basic_info(root, item):
        list_items = root.xpath(u'./ul/li')

        item['department'] = try_get_value_from_array(list_items.xpath(u'./span[text()="所属部门："]/../text()').extract())

        item['job_type'] = try_get_value_from_array(list_items.xpath(u'./span[text()="职位类别："]/../text()').extract())

        item['subordinate'] = try_get_value_from_array(list_items.xpath(u'./span[text()="下属人数："]/../text()').extract())

        item['requirement'] = try_get_value_from_array(list_items.xpath(u'./span[text()="招聘人数："]/../text()').extract())

        item['work_place'] = try_get_value_from_array(list_items.xpath(u'./span[text()="工作地点："]/../a/text()').extract())

        item['publish_time'] = try_get_value_from_array(list_items.xpath(
            u'./span[text()="发布时间："]/../*[2]/text()').extract())

        item['supervisor'] = try_get_value_from_array(list_items.xpath(u'./span[text()="汇报对象："]/../text()').extract())

    # 获取年薪信息
    @ staticmethod
    def parse_salary_info(root, item):
        list_items = root.xpath(u'./ul/li')
        item['salary'] = try_get_value_from_array(
            list_items.xpath(u'./span[text()="年薪范围："]/../span/a/text()').extract())

    # 获取职位描述信息
    @ staticmethod
    def parse_job_detail_info(root, item):
        list_items = root.xpath('string(.)')
        item['job_detail'] = try_get_value_from_array(list_items.extract())

    # 获取其他要求信息
    @ staticmethod
    def parse_other_requirement_info(root, item):
        list_items = root.xpath('./div')
        item['experience'] = try_get_value_from_array(
            list_items.xpath(u'./ul/li/p[text()="工作经验："]/../span/text()').extract())
        item['education'] = try_get_value_from_array(
            list_items.xpath(u'./ul/li/p[text()="学历要求："]/../text()').extract())
        item['age'] = try_get_value_from_array(
            list_items.xpath(u'./ul/li/span[text()="年龄："]/../text()').extract())
        item['full_time'] = try_get_value_from_array(
            list_items.xpath(u'./ul/li/span[text()="是否统招全日制："]/../text()').extract())
        item['major'] = try_get_value_from_array(
            list_items.xpath(u'./div[text()="专业要求："]/../div/p/text()').extract())
        item['oversea'] = try_get_value_from_array(
            list_items.xpath(u'./*[text()="海外经历："]/../div/p/text()').extract())
        item['language'] = try_get_value_from_array(
            list_items.xpath(u'./div[text()="语言要求："]/../div/p/text()').extract())

    # 获取公司相关信息
    @ staticmethod
    def parse_company_detail_info(root, item):
        list_items = root.xpath('string(.)')
        item['company_detail'] = try_get_value_from_array(list_items.extract()).replace(r' ', r'')

    @ staticmethod
    def build_search_url(page, params=None):
        # 地点: 上海  职位类别: 教育/培训
        base_url = 'http://www.highpin.cn/shanghai/ci_201100.html'
        url = '{}_p_{}.html'.format(base_url, page)
        return url





