# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime

from openpyxl import Workbook

from job_position.utils import load_job_excel_config, build_job_excel_line


class JobPositionPipeline(object):
    def process_item(self, item, spider):
        return item


# 将爬取结果存储到excel的类
class JobPositionPipelineExcel(object):

    excelFileName = None
    wb = Workbook()
    ws = wb.active
    config = load_job_excel_config()
    itemCount = 0

    def open_spider(self, spider):
        self.excelFileName = '{}_scrapy_{}.xlsx'.format(spider.name, datetime.datetime.now().strftime("%Y%m%d_%H%M"))
        excel_head = self.config['heads']
        self.ws.append(excel_head)

    def close_spider(self, spider):
        self.wb.save(self.excelFileName)

    def process_item(self, item, spider):
        line = build_job_excel_line(self.config, item)
        self.ws.append(line)

        self.itemCount += 1
        if self.itemCount == 100:
            self.wb.save(self.excelFileName)
            self.itemCount = 0

        return item


# # 将爬取结果存储到MongoDB的类
# class JobopPipelineMongoDB(object):
#     settings = get_project_settings()
#     dbhost = settings['MONGODB_HOST']
#     dbport = settings['MONGODB_PORT']
#     dbname = settings['MONGODB_DB']
#     client = pymongo.MongoClient(host=dbhost, port=dbport)
#     tdb = client[dbname]
#
#     def process_item(self, item, spider):
#         highpin_job_data = dict(item)
#         table = self.tdb[spider.name]
#         if table is None:
#             logging.info('Connected to MongoDB failed!!')
#             return item
#         else:
#             table.insert(highpin_job_data)
#         return item
