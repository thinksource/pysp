import scrapy
from string import *

class BbcSpider(scrapy.Spider):
    name = "bbc"
    main_url = 'http://www.bbc.com'
    urls=[]
    link_parts=["a.top-list-item__link", "a.media__link"]
    title_parts=[""]
    def start_requests(self):
        scrapy.Request(url=self.main_url, callback=self.parse)

    def main_parse(self, response):
        for part in link_parts:
            for a in response.css("a.block-link__overlay-link"):
                href=response.urljoin(a.css("::attr(href)").extract_first())
                title=strip(a.css("::text").extract_first())
                yield scrapy.Request(href, callback=self,detail_parse)

    def detail_parse(self, response):
        title=response.css("h1::text").extract_first()
        author=response.css("a")

    def parse(self, response):
        print response.url
        print "==============="
        # page = response.url.split("/")[-2]
        # print page
        filename = 'main.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
