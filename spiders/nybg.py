# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import re
import json
from scrapy_priority_scraper.items import ExhibitItem
from scrapy.http.request import Request

class DenverartmuseumSpider(CrawlSpider):
    name = 'nybg'
    allowed_domains = ['nybg.org']
    start_urls = ['https://www.nybg.org/whats-on/']

    def parse(self, response):
        long_term_ex = response.css('.flex_container')[0].css('a')
        for exhibit in long_term_ex:
            url = exhibit.css('::attr(href)').get()
            image_link = response.css('.flex_container')[0].css('a')[0].css('img::attr(srcset)').get().split(" ")[0]
            yield Request(url=url, callback=self.parse_exhibit, meta={'image_link':image_link})

    def parse_exhibit(self, response):
        self.logger.info("Visting {}".format(response.url))
        exhibit_item = ExhibitItem()
        title = response.css('.page_title > h1::text').get()
        description_list = response.css('.module.wysiwyg.row > .col-xs-12 > p > *::text').getall()
        print(description_list, "jjj")
        description = list()
        months = "september|october|november|december|january|february|march|april|may|june|july|august"
        for d in description_list:

            if (re.search(months, d.lower())) and (d.find("–") != -1):
                start_date = d.split("–")[0]
                end_date = d.split("–")[1]
            if d == "Year-round":
                start_date = d
                end_date = ""
            description.append(d.rstrip().strip() + "\n")

        image_link = response.meta['image_link']
        description = "".join(description)
        exhibit_item['title'] = title
        exhibit_item['start_date'] = start_date
        exhibit_item['end_date'] = end_date
        exhibit_item['description'] = description
        exhibit_item['exhibit_url'] = response.url
        exhibit_item['image_link'] = image_link
        exhibit_item['museum'] = 'New York Botanical Gardens'
        #exhibit_item['exhibit_html'] = response.body
        yield exhibit_item


