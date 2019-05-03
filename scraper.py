from config import config

TW_SID = config["tw_sid"]
TW_TOKEN = config["tw_token"]
TW_NUMBER = config["tw_number"]
NUMBERS = config["numbers"]

import scrapy
from scrapy.crawler import CrawlerProcess

from twilio.rest import Client
client = Client(TW_SID, TW_TOKEN)

num_listings = 0

class ApartmentSpider(scrapy.Spider):
    name = "apartment_spider"
    start_urls = ["https://www.equityapartments.com/boston/central-square/church-corner-apartments##unit-availability-tile"]

    # helper method to send an alert via SMS or email
    @staticmethod
    def alert(listing):
        for number in NUMBERS:
            client.messages.create( 
                    body = "A listing at Church Corner Apartments for " + listing["Availability"] + " with rent " + listing["Price"] + " has been posted! ",
                from_ = TW_NUMBER,
                to = number
            )

    # parases the response 
    def parse(self, res):
        global num_listings
        #get the listings, which are in li elements
        SELECTOR = '#bedroom-type-2 ul li'
        
        for listing in res.css(SELECTOR):
            price = None
            ROW_SELECTOR = '.row .specs p'
            for row in listing.css(ROW_SELECTOR):
                PRICE_SELECTOR = '.pricing ::text'
                # look for price if not found yet
                if price is None:
                    price = row.css(PRICE_SELECTOR).extract_first()
                # get inner HTML text
                text = row.xpath('text()').extract()
                for keyword in text:
                    # NOTE: assumes keyword will look like "Availability month/day/year"
                    if 'Available' in keyword:
                        num_listings += 1
                        # get the date string that should be in the form month/day/year
                        date_string = keyword.strip().split()[1]
                        listing_result = {"Availability": keyword.strip().split()[1], "Price":price}
                        ApartmentSpider.alert(listing_result)
                        yield listing_result

if __name__ == "__main__":
    process = CrawlerProcess({
	'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(ApartmentSpider)
    process.start() # the script will block here until the crawling is finished
    print("Found", num_listings, "Listings")
