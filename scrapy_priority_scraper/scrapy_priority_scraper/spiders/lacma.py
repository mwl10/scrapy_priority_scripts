# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Spider
import re
import json
from scrapy.http.request import Request
from scrapy_priority_scraper.items import ExhibitItem

class LacmaSpider(Spider):
    name = 'lacma'
    allowed_domains = ['lacma.org']
    start_urls = ['https://www.lacma.org/art/exhibitions/current', 'https://www.lacma.org/art/exhibitions/coming-soon', 'https://www.lacma.org/art/exhibitions/current?page=1']


    def parse(self, response):
        exhibits = response.css('.view-content').css('.views-infinite-scroll-content-wrapper.clearfix.form-group').css(
            '.views-row')
        for exhibit in exhibits:
            exhibit_url = 'https://www.lacma.org' + exhibit.css('.views-field.views-field-title').css(
                '.field-content').css('a::attr(href)').get()
            if exhibit_url == "https://www.lacma.org/athome/learn" or exhibit_url == "https://www.lacma.org/athome/watch" or exhibit_url == "https://www.lacma.org/athome/listen" or exhibit_url == "https://www.lacma.org/art/exhibition/watch" or exhibit_url == "https://www.lacma.org/art/exhibition/listen" or exhibit_url =="https://www.lacma.org/art/exhibition/learn":
                continue
            else:
                if exhibit.css('.field-content').css('img::attr(src)').get():
                    image_link = 'https://www.lacma.org' + exhibit.css('.field-content').css('img::attr(src)').get()
                start_date = exhibit.css('.views-field.views-field-field-alternative-start-date').css('.field-content::text').get() or\
                            exhibit.css('.views-field.views-field-field-start-date').css('.field-content::text').get()
                end_date = exhibit.css('.views-field.views-field-field-alternative-end-date').css('.field-content::text').get() or\
                        exhibit.css('.views-field.views-field-field-end-date').css('.field-content::text').get()
                yield Request(url=exhibit_url, callback=self.parse_exhibit, meta = {'image link': image_link, 'start date': start_date, 'end date' : end_date})


    def parse_exhibit(self, response):
        exhibit_item = ExhibitItem()
        title = response.css('.fixed-page-title::text').get()
        start_date = response.meta['start date']
        end_date = response.meta['end date']
        if not start_date and end_date:
            start_date = end_date
            end_date = ""
        image_link = response.meta['image link']
        url = response.url
        description = response.css(
            '.field.field--name-body.field--type-text-with-summary.field--label-hidden.field--item')[0].css('*::text').getall()
        description = "".join(description).strip().rstrip()
        exhibit_item['title'] = title
        exhibit_item['start_date'] = start_date
        exhibit_item['end_date'] = end_date
        exhibit_item['description'] = description
        exhibit_item['exhibit_url'] = url
        exhibit_item['image_link'] = image_link
        exhibit_item['museum'] = 'Los Angeles County Museum of Art'
        exhibit_item['exhibit_html'] = response.body
        yield exhibit_item
