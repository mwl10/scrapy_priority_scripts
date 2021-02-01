# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Spider
import re
import json
from scrapy_priority_scraper.items import ExhibitItem
from scrapy.http.request import Request


class AgoSpider(Spider):
    name = 'ago'
    start_urls = ['https://ago.ca/exhibitions']

    def parse(self, response):
        current_exhibits = response.css('#standard-current-exhibitions').css('div.views-row')
        also_on_view_ex = response.css('#also-on-view').css('div.views-row')
        upcoming_exhibits = response.css('#upcoming-exhibitions').css('div.views-row')
        exhibits = current_exhibits + also_on_view_ex + upcoming_exhibits
        for exhibit in exhibits:
            url = 'https://ago.ca' + exhibit.css('a::attr(href)').get()
            title = exhibit.css(".field.field--name-title.field--type-string.field--label-hidden::text").get()
            date = exhibit.css(".field.field--name-field-date-time-description.field--type-string.field--label-hidden.field__item::text").get()
            image_link = 'https://ago.ca' + exhibits[0].css('img::attr(src)').get()
            yield Request(url=url, callback=self.parse_exhibit, meta={'title':title,'date':date,'image_link':image_link})

    def parse_exhibit(self, response):
            exhibit_item = ExhibitItem()
            title = response.meta['title']
            image_link = response.meta['image_link']
            date = response.meta['date']
            if date.find("-") != -1:
                start_date = date.split("-")[0]
                end_date = date.split("-")[1]
            elif date.find(" to ") != -1:
                start_date = date.split(" to ")[0]
                end_date = date.split(" to ")[1]
            elif date.find("–") != -1:
                start_date = date.split("–")[0]
                end_date = date.split("–")[1]
            else:
                start_date = date
                end_date = ""
            description_list = response.css(".clearfix.text-formatted.field.field--name-body.field--type-text-with-summary"
                                            ".field--label-hidden.field__item").css("*::text").getall()
            description = "".join(description_list)

            if description.find("\n\n\n\n\n") != -1:
                description = description.split("\n\n\n\n\n")[0]
            exhibit_item['title'] = title
            exhibit_item['start_date'] = start_date
            exhibit_item['end_date'] = end_date
            exhibit_item['description'] = description
            exhibit_item['exhibit_url'] = response.url
            exhibit_item['image_link'] = image_link
            exhibit_item['museum'] = 'Art Gallery of Ontario'
            exhibit_item['exhibit_html'] = response.body
            yield exhibit_item

