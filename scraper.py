import scrapy
from scrapy.crawler import CrawlerProcess

num_listings = 0

class ApartmentSpider(scrapy.Spider):
    name = "apartment_spider"
    start_urls = ["https://www.equityapartments.com/boston/central-square/church-corner-apartments##unit-availability-tile"]
    # parases the response 
    def parse(self, res):
        global num_listings
        #use CSS selector
        SELECTOR = '#bedroom-type-2 ul li'
        
        for listing in res.css(SELECTOR):
            price = None
            ROW_SELECTOR = '.row .specs p'
            for row in listing.css(ROW_SELECTOR):
                PRICE_SELECTOR = '.pricing ::text'
                if price is None:
                    price = row.css(PRICE_SELECTOR).extract_first()
                text = row.xpath('text()').extract()
                for keyword in text:
                    # NOTE: assumes keyword will look like "Availability month/day/year"
                    if 'Available' in keyword:
                        num_listings += 1
                        # get the date string that should be in the form month/day/year
                        date_string = keyword.strip().split()[1]
                        yield {"Availability": keyword.strip().split()[1], "Price":price}

if __name__ == "__main__":
    process = CrawlerProcess({
	'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(ApartmentSpider)
    process.start() # the script will block here until the crawling is finished
    print("Found", num_listings, "Listings")
