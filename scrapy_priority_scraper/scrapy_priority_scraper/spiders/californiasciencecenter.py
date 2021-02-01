# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Spider
import re
import json
from scrapy_priority_scraper.items import ExhibitItem
from scrapy.http.request import Request


class CaliforniasciencecenterSpider(Spider):
    name = 'californiasciencecenter'
    allowed_domains = ['californiasciencecenter.org']
    start_urls = ['https://californiasciencecenter.org/exhibits']

    def parse(self, response):
        special_exhibits = permanent_exhibits = response.css('.index-list')[0].\
            css('.index-list__item > a::attr(href)').getall()
        for exhibit in special_exhibits:
            url = 'https://californiasciencecenter.org' + exhibit
            date = 'Ongoing'
            yield Request(url=url, callback=self.parse_exhibit, meta={'date':date})

        permanent_exhibits = response.css('.index-list')[1].\
            css('.index-list__item > a::attr(href)').getall()
        for exhibit in permanent_exhibits:
            date = 'Permanent'
            url = 'https://californiasciencecenter.org' + exhibit
            yield Request(url=url, callback = self.parse_exhibit, meta={'date':date})


    def parse_exhibit(self, response):
        exhibit_item = ExhibitItem()
        title = response.css('.main-article__header-inner > h1::text').get()
        image_link = response.css('picture > img::attr(src)').get()
        start_date = response.meta['date']
        end_date = ""
        description = response.css('.main-article__content > *::text').getall()
        description = "".join(description).rstrip().strip()
        exhibit_item['title'] = title
        exhibit_item['start_date'] = start_date
        exhibit_item['end_date'] = end_date
        exhibit_item['description'] = description
        exhibit_item['exhibit_url'] = response.url
        exhibit_item['image_link'] = image_link
        exhibit_item['museum'] = 'California Science Center'
        exhibit_item['exhibit_html'] = response.body
        yield exhibit_item


