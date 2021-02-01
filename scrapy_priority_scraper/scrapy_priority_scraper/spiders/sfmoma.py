# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Spider
import re
import json
from scrapy.http.request import Request
from scrapy_priority_scraper.items import ExhibitItem

class SfmomaSpider(Spider):
    name = 'sfmoma'
    allowed_domains = ['sfmoma.org']
    start_urls = ['https://www.sfmoma.org/exhibitions/','https://www.sfmoma.org/upcoming-exhibitions/']

    def parse(self, response):
        exhibit_item = ExhibitItem()
        exhibits = response.css('.exhibitionsgrid-wrapper-grid').css('.exhibitionsgrid-wrapper-grid-item.item-with-border')
        for exhibit in exhibits:
            title = exhibit.css('::attr(title)').get()
            date = exhibit.css('.exhibitionsgrid-wrapper-grid-item-text-date::text').get().strip().rstrip()
            url = exhibit.css('::attr(href)').get()
            image_link = exhibit.css('.exhibitionsgrid-wrapper-grid-item-image::attr(src)').get()
            yield Request(url=url, callback = self.parse_description, meta={'title':title, 'date':date, 'image link':image_link})

    def parse_description(self, response):
        title = response.meta['title']
        date = str(response.meta['date'])
        print(len(date.split("-")), "bbb", date)
        if len(date.split("-")) > 1:
            start_date = date.split("-")[0]
            end_date = date.split("-")[1]
            # no year provided for start date
            if (len(start_date.split(", "))) == 1:
                start_date = start_date + ", " + end_date.split(", ")[1]
        elif len(date.split("–")) > 1:
            start_date = date.split("–")[0]
            end_date = date.split("–")[1]
            if (len(start_date.split(", "))) == 1:
                start_date = start_date + ", " + end_date.split(", ")[1]
        else:
            start_date = date
            end_date = ""
        image_link = response.meta['image link']
        url = response.url
        description = "".join(response.css('.exhibitioncard-wrapper-copy').css('*::text').getall()).strip().rstrip()
        description = "".join(description).rstrip().strip()
        exhibit_item = ExhibitItem()
        exhibit_item['title'] = title
        exhibit_item['start_date'] = start_date
        exhibit_item['end_date'] = end_date
        exhibit_item['description'] = description
        exhibit_item['exhibit_url'] = url
        exhibit_item['image_link'] = image_link
        exhibit_item['museum'] = "San Francisco Museum of Modern Art"
        exhibit_item['exhibit_html'] = response.body
        yield exhibit_item

