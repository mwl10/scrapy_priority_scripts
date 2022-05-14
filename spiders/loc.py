# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Spider
import re
import json
from scrapy_priority_scraper.items import ExhibitItem
from scrapy.http.request import Request

class LocSpider(Spider):
    name = 'loc'
    allowed_domains = ['loc.gov']
    start_urls = ['https://www.loc.gov/exhibits/current/']

    def parse(self, response):
        exhibits = response.css('.item')
        for exhibit in exhibits:
            url = exhibit.css('h4 > a::attr(href)').get() or ""
            if url:
                url = 'https://www.loc.gov' + url
            print(url, "fff")
            title = exhibit.css('h4 > a::text').get()
            if not title:
                continue
            else:
                title.rstrip().strip()
            date = exhibit.css('p::text').getall()[1].rstrip().strip()
            description = "".join(exhibit.css('p')[1].css('*::text').getall())
            image_link = 'https://www.loc.gov/exhibits' + exhibit.css('img::attr(src)').get()
            image_link = image_link.replace("..", "")
            yield Request(url=url, callback=self.parse_exhibit, meta={'title':title,'date':date,'description':description,'image_link':image_link})

    def parse_exhibit(self, response):
        exhibit_item = ExhibitItem()
        title = response.meta['title']
        description = response.meta['description']
        image_link = response.meta['image_link']
        date = response.meta['date']
        if date.find("–") != -1:
            start_date = date.split("–")[0]
            end_date = date.split("–")[1]
        else:
            start_date = date
            end_date = ""

        exhibit_item['title'] = title
        exhibit_item['start_date'] = start_date
        exhibit_item['end_date'] = end_date
        exhibit_item['description'] = description
        exhibit_item['exhibit_url'] = response.url
        exhibit_item['image_link'] = image_link
        exhibit_item['museum'] = 'The Library of Congress'
        exhibit_item['exhibit_html'] = response.body
        yield exhibit_item



