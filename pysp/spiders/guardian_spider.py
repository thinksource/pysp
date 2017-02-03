import scrapy
from datetime import datetime
from pymongo import MongoClient
from string import *
import pprint
class GuardianSpider(scrapy.Spider):
    name = "guardian"
    main_url = 'https://www.theguardian.com/au'
    join_url='https://www.theguardian.com'
    urls=[]
    link_parts=["a.u-faux-block-link__overlay"]
    title_parts=[""]
    db=MongoClient('mongodb://8.43.86.84:27017/').get_database("websites")
    # cl=MongoClient('mongodb://challenge:123456@aws-eu-west-1-portal.5.dblayer.com:15271/?ssl=true')
    # db=cl
    #db=client['websites']
    collection=db.get_collection("guardian")
    #collection=db.guardian
    def start_requests(self):
        yield scrapy.Request(url=self.main_url, callback=self.main_parse)

    def main_parse(self, response):
        # for part in link_parts:
        for a in response.css("a.u-faux-block-link__overlay"):
            href=response.urljoin(a.css("::attr(href)").extract_first())
            title=strip(a.css("::text").extract_first())

            print "================"
            pprint.pprint(href)
            yield scrapy.Request(href, callback=self.detail_parse)

    def detail_parse(self, response):
        title=response.css("h1.content__headline::text").extract_first()
        author=response.css("a[rel=author]")
        author_names=author.css("span[itemprop*=name]::text").extract()
        passage=response.css("div.content__article-body")
        timestamp=response.css("time::attr(data-timestamp)").extract_first()
        creat_time=datetime.utcfromtimestamp(long(timestamp)/1000)
        aps=passage.css("p::text, a::text, p span.drop-cap::text, p span.drop-cap__inner::text").extract()
        pprint.pprint(response.url)
        pprint.pprint(author_names)
        article=""
        article=article.join(aps)
        if len(article)>0 and response.status==200:
            post={"url":response.url,
                "title":title,
                "author":author_names,
                "text": article,
                "publish_date":creat_time,
                "view_date": datetime.utcnow()}
            # pprint.pprint(post)
            if self.collection.find_one({"url":response.url}):
                self.collection.update_one(
                    {"url":response.url},
                    {"$set":{
                        "title":title,
                        "author":author_names,
                        "text":article,
                        "publish_date":creat_time,
                        "view_date":datetime.utcnow()
                        }
                    })
            else:
                self.collection.insert_one(post)

    def get_collection(self):
        return self.collection

    def parse(self, response):
        print response.url
        print "==============="
        # page = response.url.split("/")[-2]
        # print page
        filename = 'main.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
