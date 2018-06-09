# -*- coding: utf-8 -*-
# Base class for liepin_job_position Spider
# Author ian.Yang
# Create date 2018-06-05

import logging
from urlparse import urljoin

import scrapy
from scrapy.http import Request

from job_position.items import JobPositionItem
from job_position.utils import try_get_value_from_array


class LiepinJobPosition(scrapy.Spider):
    name = 'liepin_job'
    allowed_domains = ['www.liepin.com']
    base_url = 'https://www.liepin.com'
    start_url = 'https://www.liepin.com/zhaopin/?d_sfrom=search_fp_nvbar&init=1'
    params = [{u'城市': u'上海'}, {u'行业': u'教育培训'}]
    i = 0
    new_url = ''
    total_page = 0

    def start_requests(self):
        return [Request(self.start_url, callback=self.parse_params_to_url)]

    # 根据参数生成url
    def parse_params_to_url(self, response):
        root_node = response.xpath(".//div[@class='search-conditions']")
        if self.i < len(self.params):
            for k, v in self.params[self.i].items():
                param_type = root_node.xpath(
                    u".//*[@class='search-title'][contains(text(), '{}')]/following-sibling::dd".format(k))
                url = try_get_value_from_array(param_type.xpath(u".//a[contains(text(), '{}')]/@href".format(v)).extract())
                self.i += 1
                self.new_url = urljoin(self.base_url, url)
                # self.new_url = response.urljoin(url)
                # print self.new_url, 'self.new_url'
            return Request(self.new_url, callback=self.parse_params_to_url)

        else:
            return Request(self.new_url, callback=self.go_last_page, dont_filter=True)

    # 获取总页数
    def go_last_page(self, response):
        last_page_url = try_get_value_from_array(response.xpath("//a[@class='last']/@href").extract())
        return Request(urljoin(self.base_url, last_page_url), callback=self.get_total_page, dont_filter=True)

    def get_total_page(self, response):
        self.total_page = int(response.xpath(u'//a[@class="current"]/text()').extract()[0])
        return Request(self.new_url, dont_filter=True)

    def parse(self, response):
        current_page = int(response.xpath(
            u'//a[@class="current"]/text()').extract()[0])
        # logging.info(u'total_page ' + str(self.total_page))
        logging.info('Page {}/{}'.format(current_page, self.total_page))

        # 第一页会不会被爬取？？
        if current_page != self.total_page:
            # url = self.build_search_url(current_page+1)
            url = self.get_next_page_url(response)
            page_request = Request(url, dont_filter=True)
            yield page_request

        # 获取每个职位信息
        jobs = response.xpath("//ul[@class='sojob-list']/li")
        for job in jobs:
            item = JobPositionItem()
            # 存储信息
            item['page_url'] = job.xpath(".//div[@class='job-info']//h3/a/@href").extract()[0]
            item['position'] = job.xpath(".//div[@class='job-info']//h3/a/text()").extract()[0].strip()
            item['company_name'] = job.xpath(".//p[@class='company-name']/a/text()").extract()[0]
            item['source'] = 'liepin'
            # print item['page_url'], item['position']
            job_request = Request(item['page_url'], callback=self.parse_item)
            job_request.meta['item'] = item
            yield job_request

    # 获取每个职位的信息
    def parse_item(self, response):
        item = response.meta['item']
        company_info = response.xpath(u'.')
        self.parse_company_info(company_info, item)

        basic_require = response.xpath('.')
        self.parse_basic_require(basic_require, item)

        job_detail_info = response.xpath(
            u'//*[contains(text(), "职位描述")]/following-sibling::div')
        self.parse_job_detail_info(job_detail_info, item)

        other_info = response.xpath(u'//*[contains(text(), "其他信息")]/following-sibling::div')
        self.parse_other_info(other_info, item)

        company_detail_info = response.xpath(u"//*[contains(text(), '企业介绍')]")
        self.parse_company_detail_info(company_detail_info, item)

        yield item

    # 获取公司的信息
    @staticmethod
    def parse_company_info(root, item):
        list_items = root.xpath('.')
        # item['company_name'] = try_get_value_from_array(list_items.xpath(
        #     '//div[@class="title-info "]/h3/a/text()').extract())
        item['company_trade'] = try_get_value_from_array(list_items.xpath(
            u".//*[contains(text(), '行业：')]/a/text()").extract())
        item['company_size'] = try_get_value_from_array(
            list_items.xpath(u'.//*[contains(text(), "公司规模：")]//text()').extract())
        item['company_address'] = try_get_value_from_array(list_items.xpath(
            u'.//*[contains(text(), "公司地址：")]/../text()').extract())

    # 获取基本要求
    @ staticmethod
    def parse_basic_require(root, item):
        list_items = root.xpath("//div[@class='job-title-left']")
        item['work_place'] = try_get_value_from_array(list_items.xpath('.//a/text()').extract())
        item['salary'] = try_get_value_from_array(list_items.xpath('./p/text()').extract())
        # 判断span数量
        item['education'] = try_get_value_from_array(
            list_items.xpath(u'.//span[1]/text()').extract())
        item['experience'] = try_get_value_from_array(
            list_items.xpath(u'.//span[2]/text()').extract())
        item['language'] = try_get_value_from_array(
            list_items.xpath(u'.//span[3]/text()').extract())
        item['age'] = try_get_value_from_array(
            list_items.xpath(u'.//span[4]/text()').extract())

    # 获取职位描述信息
    @staticmethod
    def parse_job_detail_info(root, item):
        list_items = root.xpath('string(.)')
        item['job_detail'] = try_get_value_from_array(list_items.extract())

    # 获取其他信息
    @ staticmethod
    def parse_other_info(root, item):
        list_items = root.xpath("./ul")
        item['department'] = try_get_value_from_array(
            list_items.xpath(u'.//span[text()="所属部门："]/../label/text()').extract())
        item['major'] = try_get_value_from_array(
            list_items.xpath(u'.//span[text()="专业要求："]/../label/text()').extract())
        item['supervisor'] = try_get_value_from_array(
            list_items.xpath(u'.//span[text()="汇报对象："]/../label/text()').extract())
        item['subordinate'] = try_get_value_from_array(
            list_items.xpath(u'.//span[text()="下属人数："]/../label/text()').extract())

    # 公司介绍
    @ staticmethod
    def parse_company_detail_info(root, item):
        list_items = root.xpath("./following-sibling::div/div[@class='info-word']/text()")
        company_detail = try_get_value_from_array(list_items.extract())
        if company_detail is not None:
            company_detail = company_detail.replace(r' ', r'')
        item['company_detail'] = company_detail

    def build_search_url(self, page, params=None):
        if page == 1:
            url = self.new_url
        else:
            base_url = self.new_url[:-1]
            url = '{}{}&curPage={}'.format(base_url, int(page)-2, int(page)-1)

        return url

    def get_next_page_url(self, response):
        next_page_url = try_get_value_from_array(response.xpath(u"//a[contains(text(), '下一页')]/@href").extract())
        return urljoin(self.base_url, next_page_url)
