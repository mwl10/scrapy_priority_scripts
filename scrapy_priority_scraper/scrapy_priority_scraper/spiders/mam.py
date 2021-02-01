# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.http.request import Request
from scrapy_priority_scraper.items import ExhibitItem

class MamSpider(Spider):
    name = 'mam'
    allowed_domains = ['mam.org']
    start_urls = ['https://mam.org/exhibitions/upcoming.php','https://mam.org/exhibitions/', 'https://mam.org/exhibitions/previous.php']

    def parse(self, response):
        exhibits = response.css('.past-exhibition') + response.css('.new-exhibition') + response.css('.inner-column.pfirst.span-p6') + response.css('.inner-column.plast.span-p6')
        for exhibit in exhibits:
            exhibit_url = 'https://mam.org' + exhibit.css('a::attr(href)').get()
            image_link = 'https://mam.org' + exhibit.css('img::attr(src)').get()
            title = exhibit.css('a')[1].css('::text').get()
            date = exhibit.css('.exhibition-date::text').get()
            yield Request(url=exhibit_url, callback=self.parse_exhibit, meta={'image_link': image_link, 'date':date, 'title':title})


    def parse_exhibit(self, response):
        exhibit_item = ExhibitItem()
        title = response.meta['title']
        date = response.meta['date']
        image_link = response.meta['image_link']
        url = response.url
        description_list = response.css('.exhibition-description').css('p *::text').getall()
        if not description_list:
            description_list = response.css('.exhibition-details').css('p *::text').getall()
        if not description_list:
            description_list = response.css('#main').css('p *::text').getall()
        description = list()
        for d in description_list:
            d = d.strip().rstrip()
            if len(d) > 3:
                if d[-1] == "." or d[-2] == "." or d[-3] == ".":
                    d = d + "\n"
                    description.append(d)
                else:
                    d = d + " "
                    description.append(d)
        description = "".join(description)
        if date:
            if date.find("–") != -1:
                start_date = date.split("–")[0]
                end_date = date.split("–")[1]
            elif date.find("Until") != -1:
                start_date = ""
                end_date = date.split("Until ")[1]
            else:
                start_date = date
                end_date = ""
        else:
            start_date = ""
            end_date = ""

        exhibit_item['title'] = title
        exhibit_item['start_date'] = start_date
        exhibit_item['end_date'] = end_date
        exhibit_item['description'] = description
        exhibit_item['exhibit_url'] = url
        exhibit_item['image_link'] = image_link
        exhibit_item['museum'] = 'Milwaukee Art Museum'
        exhibit_item['exhibit_html'] = response.body
        yield exhibit_item



