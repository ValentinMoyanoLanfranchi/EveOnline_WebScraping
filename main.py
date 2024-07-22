import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
import requests
import json
import csv

data = {
    'Item_ID': [],
    'Name': [],
    'Volume': [],
    'Jita_Price': [],
    'Amarr_Price': [],
    'Rens_Price': [],
    'Dodixie_Price': [],
    'Hek_Price': [],
}

def price_check(id_region, server, order_type, page, type_id, id_solar):
            x = 0
            price_avg = 0
            total_price = 0
            request = requests.get(f'https://esi.evetech.net/latest/markets/{id_region}/orders/?datasource={server}&order_type={order_type}&page={page}&type_id={type_id} ')
            data = request.json()
            for i in data:
                if x == 5:
                    break
                if i['system_id'] == id_solar:
                    total_price += i['price']
                    x += 1
            if x != 0:
                price_avg = total_price/x
            return price_avg
          
class Spider(scrapy.Spider):
    
    name = "EveSpider"
    def start_requests(self):
        urls = ["https://everef.net/market/837", "https://everef.net/market/131", "https://everef.net/market/542"]
        for url in urls:
            yield scrapy.Request( url = url, callback = self.parse_front)
            
    def parse_front(self, response):
        links_to_follow = response.xpath('//a[@class="item-row"]/@href').extract()
        for url in links_to_follow:
            yield response.follow(url = url, callback = self.parse_page)

    def parse_page(self, response):
        item_id = response.css('div.masonry-item:nth-child(5) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(3)::text').extract_first()
        item_name = response.css('div.row:nth-child(6) > div:nth-child(1) > h1:nth-child(2)::text').extract_first()
        item_volume = response.css('div.masonry-item:nth-child(5) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(5) > td:nth-child(3)::text').extract_first()
        jita_price = price_check(10000002, "tranquility", "sell", 1, item_id, 30000142)
        amarr_price = price_check(10000043, "tranquility", "sell", 1, item_id, 30002187)
        rens_price = price_check(10000030, "tranquility", "sell", 1, item_id, 30002510)
        dodixie_price = price_check(10000032, "tranquility", "sell", 1, item_id, 30002659)
        hek_price = price_check(10000042, "tranquility", "sell", 1, item_id, 30002053)
        data['Item_ID'].append(item_id)
        data['Name'].append(item_name)
        data['Volume'].append(item_volume)
        data['Jita_Price'].append(jita_price)
        data['Amarr_Price'].append(amarr_price)
        data['Rens_Price'].append(rens_price)
        data['Dodixie_Price'].append(dodixie_price)
        data['Hek_Price'].append(hek_price) 

process = CrawlerProcess()
process.crawl(Spider)
process.start()

print(data)
data_frame = pd.DataFrame(data)
csv = 'data.csv'
data_frame.to_csv(csv, index=False)

