# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.http.request import Request
from scrapy_priority_scraper.items import ExhibitItem

class ClevelandartSpider(Spider):
    name = 'clevelandart'
    allowed_domains = ['clevelandart.org']
    start_urls = ['https://www.clevelandart.org/exhibitions/upcoming','https://www.clevelandart.org/exhibitions/current']

    def parse(self, response):
        exhibits = response.css('.views-row.view-mode-clevelandart-card')
        for exhibit in exhibits:
            exhibit_url = 'https://www.clevelandart.org' + exhibit.css('.field-card-title').css('a::attr(href)').get()
            image_link = exhibit.css('.views-field-image').css('img::attr(src)').get()
            yield Request(url=exhibit_url, callback=self.parse_exhibit,
                          meta={'image link': image_link})


    def parse_exhibit(self, response):
        exhibit_item = ExhibitItem()
        title = response.css('.panel-pane.pane-node-content').css('.pane-title::text').get().rstrip().strip()
        image_link = response.meta['image link']
        url = response.url
        description_list = response.css('.entity.entity-field-collection-item.field-collection-item-field-event.clearfix').css('.field-item.even').css('p')[0].css('::text').getall()
        # in one instance, the body of the text is in the third paragraph tag.. so handle that
        if len(description_list) == 0:
            description_list = response.css('.entity.entity-field-collection-item.field-collection-item-field-event.clearfix').css('.field-item.even').css('p')[2].css('::text').getall()
        description = list()
        for d in description_list:
            if len(d) >= 2:
                if (d[-1] == ".") or (d[-2] == "."):
                    d = d +'\n'
                    description.append(d)
                else:
                    description.append(d)
        description = "".join(description)
        # idk they all have dates so
        start_date = response.css('.date-display-range').css('*::text').getall()[0].split(", ")[1]
        end_date = response.css('.date-display-range').css('*::text').getall()[2].split(", ")[1]
        exhibit_item['title'] = title
        exhibit_item['start_date'] = start_date
        exhibit_item['end_date'] = end_date
        exhibit_item['description'] = description
        exhibit_item['exhibit_url'] = url
        exhibit_item['image_link'] = image_link
        exhibit_item['museum'] = 'The Cleveland Museum of Art'
        exhibit_item['exhibit_html'] = response.body
        yield exhibit_item


