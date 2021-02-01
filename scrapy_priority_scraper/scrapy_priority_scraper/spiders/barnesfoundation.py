
from scrapy.spiders import Spider
from scrapy_priority_scraper.items import ExhibitItem
from scrapy.http.request import Request

class BarnesfoundationSpider(Spider):
    name = 'barnesfoundation'
    start_urls = ['https://www.barnesfoundation.org/whats-on/exhibitions']

    def parse(self, response):
        exhibits = response.css('.m-card-event.vevent')
        for exhibit in exhibits:
            url = exhibit.css('.m-card-event__media-link::attr(href)').get()
            title = exhibit.css('.font-delta.m-card-event__title > a::text').get()
            date = exhibit.css('.dtstart.font-delta.m-card-event__date::text').get()
            image_link = exhibit.css('img::attr(src)').get()
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
            elif date.find("Until") != -1:
                start_date = ""
                end_date = date.split("Until ")[1]
            else:
                start_date = date
                end_date = ""
        else:
            start_date = ""
            end_date = ""
        description = list()
        description_list = response.css('.m-block__column').css('p *::text').getall()
        for d in description_list:
            d = d.strip() + "\n"
            description.append(d)
        description = "".join(description)
        exhibit_item['title'] = title
        exhibit_item['start_date'] = start_date
        exhibit_item['end_date'] = end_date
        exhibit_item['description'] = description
        exhibit_item['exhibit_url'] = response.url
        exhibit_item['image_link'] = image_link
        exhibit_item['museum'] = 'The Barnes Foundation'
        exhibit_item['exhibit_html'] = response.body
        yield exhibit_item
