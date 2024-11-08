import json
import logging
import os.path
import time
import re
import jsonlines

from scrapy.spiders import SitemapSpider
from scrapy.utils.reactor import install_reactor

install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")

from LeuphanaScraper.definitions import ROOT_DIR
from LeuphanaScraper.definitions import JSON_DIR
from LeuphanaScraper.definitions import HTML_DIR

from LeuphanaScraper.items import NewsItem

from LeuphanaScraper.email import send_email

html_tag_pattern = re.compile(r'<.*?>')

class NewsSpider(SitemapSpider):
    counter = 0
    news_list = []

    name = "news"
    allowed_domains = ["www.leuphana.de"]
    #start_urls = ["https://www.leuphana.de"]
    sitemap_urls = [
        "https://www.leuphana.de/sitemap.xml?sitemap=news&cHash=9981f62ffc78ae8a79e5b448302db0c0"
    ]
    sitemap_rules = [
        ('/', 'parse_news')
    ]

    def parse_news(self, response):

        if response.css('.news'):
            title = ""
            subtitle = ""
            content = ""
            topic = ""
            if response.xpath('//h1[@class="c-headline"]'):
                title = response.xpath('//h1[@class="c-headline"]/text()').get()
            if response.xpath('//h2[@class="c-headline"]'):
                subtitle = response.xpath('//h2[@class="c-headline"]/text()').get()
            if response.xpath('//div[@class="row"]'):
                for ll in response.xpath('//div[@class="row"]//p'):
                    content += ll.get().strip()
                content = content.replace("\n", "")
                content = html_tag_pattern.sub("", content)

            date_reg = re.compile("(\d+/\d+/\d+)")
            if date_reg.findall(response.url):
                date = date_reg.findall(response.url)[0]
                year = date.split("/")[0]
                mon = date.split("/")[1]
                day = date.split("/")[2]
            else:
                year = ""
                mon = ""
                day = ""

            self.counter += 1
            newsItem = NewsItem(
                no=self.counter,
                title=title,
                subtitle=subtitle,
                pub_year=year,
                pub_month=mon,
                pub_day=day,
                url=response.url,
                content=content,
                topic=topic
            )

            self.news_list.append({"no": self.counter,"title":title, "subtitle":subtitle, "pub_year": year, "pub_month": mon, "pub_day": day, "url": response.url, "content": content, "topic": topic})

            print("Crawling :", self.counter)

            yield newsItem

    def closed(self, reason):

        with jsonlines.open(os.path.join(JSON_DIR, "news.jsonl"), 'w') as writer:
            writer.write_all(self.news_list)

        subject = f"Spider has stopped, reason:{reason}.\n"
        content = f"Spider has stopped at {time.asctime()}, reason:{reason}.\n"
        send_email(subject, content)


from scrapy.crawler import CrawlerProcess
c = CrawlerProcess(
    settings={
        'USER_AGENT': 'Mozilla/5.0',
        # save in file as CSV, JSON or XML
        'FEED_FORMAT': 'csv',     # csv, json, xml
        'FEED_URI': 'output.csv', #
        "TWISTED_REACTOR" : 'asyncio'
    }
)
c.crawl(NewsSpider)
c.start()