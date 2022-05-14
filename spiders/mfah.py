# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Spider
import re
import json
from scrapy_priority_scraper.items import ExhibitItem
from scrapy.http.request import Request

class MfahSpider(Spider):
    name = 'mfah'
    allowed_domains = ['mfah.org']
    start_urls = ['https://www.mfah.org/exhibitions/current', 'https://www.mfah.org/exhibitions/upcoming']

    def parse(self, response):
        for exhibit in response.css('.media.mb-4'):
            title = exhibit.css('.media-body').css('.my-0').css('a::text').get().rstrip().strip()
            image_link = exhibit.css('.border.mr-3').css('picture').css('img::attr(data-src)').get()
            exhibit_url = 'https://www.mfah.org' + exhibit.css('.media-body').css('a::attr(href)').get()
            date = exhibit.css('.mb-1::text').get()
            if date.find("–") != -1:
                start_date = date.split("–")[0]
                end_date = date.split("–")[1]
                if (len(start_date.split(", "))) == 1:
                    start_date = start_date + ", " + end_date.split(", ")[1]
            elif date.find("-") != -1:
                start_date = date.split("-")[0]
                end_date = date.split("-")[1]
                if (len(start_date.split(", "))) == 1:
                    start_date = start_date + ", " + end_date.split(", ")[1]
            else:
                start_date = date
                end_date = ""
            description = "".join(exhibit.css('.media-body').css('p').css('*::text').getall()).rstrip().strip()

            yield Request(url=exhibit_url, callback=self.parse_html, meta={'title':title, 'start_date':start_date, 'end_date':end_date,
                                                                     'description':description, 'image_link':image_link})


    def parse_html(self, response):
        exhibit_item = ExhibitItem()
        exhibit_item['title'] = response.meta['title']
        exhibit_item['start_date'] = response.meta['start_date']
        exhibit_item['end_date'] = response.meta['end_date']
        exhibit_item['description'] = response.meta['description']
        exhibit_item['exhibit_url'] = response.url
        exhibit_item['museum'] = 'The Museum of Fine Arts, Houston'
        exhibit_item['image_link'] = response.meta['image_link']
        exhibit_item['exhibit_html'] = response.body
        yield exhibit_item


