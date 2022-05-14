# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Spider
import re
import json
from scrapy_priority_scraper.items import ExhibitItem
from scrapy.http.request import Request

class VmfaSpider(Spider):
    name = 'vmfa'
    start_urls = ['https://www.vmfa.museum/exhibitions/at-the-museum/', 'https://www.vmfa.museum/exhibitions/upcoming-exhibitions/', 'https://www.vmfa.museum/exhibitions/traveling-exhibitions/']

    def parse(self, response):
        exhibits = response.css('main.site-main > div.row > #isotope-container > div')
        for exhibit in exhibits:
            url = exhibit.css('.mb-image > a::attr(href)').get()
            title = exhibit.css('.mb-image > a::attr(title)').get()
            date = exhibit.css('.date.details::text').get()
            image_link = exhibit.css('.mb-image > a > img::attr(src)').get()
            yield Request(url=url, callback=self.parse_exhibit, meta={'title':title,'date':date,'image_link':image_link})

    def parse_exhibit(self, response):
        if response.url != 'https://www.vmfa.museum/exhibitions/exhibitions/fellowship-exhibitions/':
            exhibit_item = ExhibitItem()
            title = response.meta['title']
            image_link = response.meta['image_link']
            date = response.meta['date']
            if date.find("–") != -1:
                start_date = date.split("–")[0]
                end_date = date.split("–")[1]
            else:
                start_date = date
                end_date = ""
            description_list = response.css('.tab.tab_content > p::text').getall()
            description = list()
            for d in description_list:
                d = d.strip().rstrip()
                if len(d) > 3:
                    if d[-1] == "." or d[-2] == "." or d[-3] == ".":
                        d = d + "\n"
                        description.append(d)
                    else:
                        description.append(d)
            description = "".join(description)
            exhibit_item['title'] = title
            exhibit_item['start_date'] = start_date
            exhibit_item['end_date'] = end_date
            exhibit_item['description'] = description
            exhibit_item['exhibit_url'] = response.url
            exhibit_item['image_link'] = image_link
            exhibit_item['museum'] = 'Virgina Museum of Fine Arts'
            exhibit_item['exhibit_html'] = response.body
            yield exhibit_item

