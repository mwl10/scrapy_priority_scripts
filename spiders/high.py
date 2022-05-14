
from scrapy.spiders import Spider
from scrapy_priority_scraper.items import ExhibitItem
from scrapy.http.request import Request
import imgkit

class HighSpider(Spider):
    name = 'high'
    start_urls = ['https://high.org/exhibitions//tab/Current']

    def parse(self, response):
        exhibits = response.css('.bottom-spacer.new-media.case-lower.col-4.not-on-view')
        for exhibit in exhibits:
            url = exhibit.css('a::attr(href)').get()
            title = exhibit.css('.bottom-spacer.text-medium.text-left.details.col-2 > h2::text').get().strip()
            date = exhibit.css('.brand2.date::text').get()
            image_link = exhibit.css('img::attr(srcset)').get().split(" ")[0]
            yield Request(url=url, callback=self.parse_exhibit, meta={'title':title,'date':date,'image_link':image_link})

    def parse_exhibit(self, response):
        exhibit_item = ExhibitItem()
        title = response.meta['title']
        image_link = response.meta['image_link']
        date = response.meta['date']
        if date:
            if date.find("–") != -1:
                start_date = date.split("–")[0]
                end_date = date.split("–")[1]
            elif date.find("Through") != -1:
                start_date = ""
                end_date = date.split("Through ")[1]
            else:
                start_date = date
                end_date = ""
        else:
            start_date = ""
            end_date = ""
        description_list = response.css('.two-columns > .one-column > p').css("*::text").getall()
        if not description_list:
            description_list = response.css('.two-columns > .overview')[1].css('*::text').getall()
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
        imgkit.from_url(response.url, './screenshots/{}.jpg'.format(title))
        description = "".join(description)
        exhibit_item['title'] = title
        exhibit_item['start_date'] = start_date
        exhibit_item['end_date'] = end_date
        exhibit_item['description'] = description
        exhibit_item['exhibit_url'] = response.url
        exhibit_item['image_link'] = image_link
        exhibit_item['museum'] = 'High Museum of Art'
        exhibit_item['exhibit_html'] = response.body
        yield exhibit_item



