# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Spider
import re
import json
from scrapy_priority_scraper.items import ExhibitItem
from scrapy.http.request import Request

class DenverartmuseumSpider(Spider):
    name = 'denverartmuseum'
    allowed_domains = ['denverartmuseum.org']
    start_urls = ['https://www.denverartmuseum.org/en/exhibitions/']

    def parse(self, response):
        exhibit_links = list()
        all_links = response.css('a::attr(href)').getall()
        for link in all_links:
            if link.find('en/exhibitions/') != -1:
                exhibit_links.append(link)
        exhibit_links.remove('/en/exhibitions/past')
        print(len(exhibit_links), "ggg")
        exhibit_links = set(exhibit_links)
        print(len(exhibit_links), "hhh")
        for exhibit in exhibit_links:
            url = 'https://www.denverartmuseum.org' + exhibit
            yield Request(url=url, callback=self.parse_exhibit)



    def parse_exhibit(self, response):
        self.logger.info("Visting {}".format(response.url))
        exhibit_item = ExhibitItem()
        if response.css('.exhibition'):
            title = response.css('.title.knockout').css('h1::text').get().rstrip().strip()
            # subtitle?
            if response.css('.subtitle::text').get():
                subtitle = response.css('.subtitle::text').get().rstrip().strip()
                title = title + ": " + subtitle
            else:
                subtitle = ""
            if response.css('.date-recur-date'):
                start_date = response.css('.date-recur-date').css("*::text").getall()[0]
                end_date = response.css('.date-recur-date').css("*::text").getall()[2]
            else:
                start_date = response.css('.dateline::text').get().rstrip().strip()
                end_date = ""
            if response.xpath('/html/body/div[1]/div[1]/main/div/header/div[1]/div[1]/div[1]/picture/img/@data-src').get():
                image_link = response.xpath('/html/body/div[1]/div[1]/main/div/header/div[1]/div[1]/div[1]/picture/img/@data-src').get()
            else:
                image_link = response.xpath('//*[@id="header-video"]/source//@src').get()

            description = ("".join(response.css(".overview").css("*::text").getall())).rstrip().strip()

            exhibit_item['title'] = title
            exhibit_item['start_date'] = start_date
            exhibit_item['end_date'] = end_date
            exhibit_item['description'] = description
            exhibit_item['exhibit_url'] = response.url
            exhibit_item['image_link'] = image_link
            exhibit_item['museum'] = 'Denver Art Museum'
            exhibit_item['exhibit_html'] = response.body
            yield exhibit_item
        else:
            print(response.url)
