# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import re
import json
from scrapy_priority_scraper.items import ExhibitItem
from scrapy.http.request import Request

class SeattleartmuseumSpider(CrawlSpider):
    name = 'seattleartmuseum'
    start_urls = ['http://www.seattleartmuseum.org/exhibitions/upcoming-exhibitions', 'http://www.seattleartmuseum.org/exhibitions/now-on-view']

    def parse(self, response):
        exhibits = response.css('.item')
        for exhibit in exhibits:
            url = 'http://www.seattleartmuseum.org' + exhibit.css('a::attr(href)').get()
            title = exhibit.css('.bi-eventTitle::text').get()
            date = exhibit.css('.bi-eventDate::text').get()
            image_link = 'http://www.seattleartmuseum.org' + exhibit.css('.bi-eventImageWrapper > img::attr(src)').get()
            yield Request(url=url, callback=self.parse_exhibit, meta={'title':title,'date':date,'image_link':image_link})

    def parse_exhibit(self, response):
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
        description_list = response.css('.entry-content > *').css('::text').getall()
        if not description_list:
            description_list = response.css('.sam-event-description > *').css('::text').getall()
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
        exhibit_item['museum'] = 'Seattle Art Museum'
        exhibit_item['exhibit_html'] = response.body
        yield exhibit_item


