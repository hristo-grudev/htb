import scrapy

from scrapy.loader import ItemLoader

from ..items import HtbItem
from itemloaders.processors import TakeFirst


class HtbSpider(scrapy.Spider):
	name = 'htb'
	start_urls = ['https://htb.com/news-community/']

	def parse(self, response):
		post_links = response.xpath('//a[@class="ht-latest-more"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//div[@class="nav-previous"]/a/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response):
		title = response.xpath('//article//h1/text()').get()
		description = response.xpath('//div[@class="entry-content"]//text()[normalize-space() and not(ancestor::div[@class="social-sharing ss-social-sharing"])]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		date = response.xpath('//meta[@property="og:updated_time"]/@content').get()

		item = ItemLoader(item=HtbItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
