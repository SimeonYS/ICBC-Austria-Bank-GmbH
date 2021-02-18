import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from ..items import IcbcItem
import re
redate = r'\d+\-\d+\-\d+'

class SpiderSpider(scrapy.Spider):
    name = 'spider'

    start_urls = ['http://www.icbc-at.com/ICBC/%e6%b5%b7%e5%a4%96%e5%88%86%e8%a1%8c/%e5%b7%a5%e9%93%b6%e5%a5%a5%e5%9c%b0%e5%88%a9%e7%bd%91%e7%ab%99/en/AboutUs/ICBCNews/']

    def parse(self, response):
        links = response.xpath('//span[@class="ChannelSummaryList-insty"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//div[@align="right"]/a[contains(text(),"Next")]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        item = ItemLoader(IcbcItem())
        item.default_output_processor = TakeFirst()

        date = response.xpath('//span[@id="InfoPickFromFieldControl"]//text()').get()
        date = re.findall(redate, date)
        title = response.xpath('//div[@class="subtitleclass"]//text()').getall()
        title = ''.join([text.strip() for text in title])
        content = response.xpath('//span[@id="MyFreeTemplateUserControl"]//text()').getall()
        content = ' '.join([text.strip() for text in content if text.strip()])

        item.add_value('date', date)
        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        return item.load_item()