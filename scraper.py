import pickle

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

    @staticmethod
    def alert(listing, message):
        '''
        Helper method to send an alert via SMS or email
        listing: dictionary of availability date and price of listing
        message: string, either "added" or "removed" to tell if the listing was added or removed
        '''
        for number in NUMBERS:
            client.messages.create( 
                body = "A listing at Church Corner Apartments for " + listing["Availability"] + " with rent " + listing["Price"] + " has been " + message + "!",
                from_ = TW_NUMBER,
                to = number
            )

    def parse(self, res):
        '''
        Parses the response
        res: a scrapy response object
        '''
        global num_listings
        all_listings = []
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
                        all_listings.append(listing_result)
                        yield listing_result

        ApartmentSpider.check_diff_listings(all_listings)

    # check difference between newest listings seen and previous listings
    @staticmethod
    def check_diff_listings(new_listings):
        '''
        Check difference between newest listings seen and previous listings.
        Previous listings are stored in "listings.p"
        new_listings: list of dictionaries of listings, where each dictionary has
                      availability date and price of listing
        '''

        # get previous listings if any
        try:
            previous_listings = pickle.load(open('listings.p', 'rb'))
        except:
            previous_listings = []

        # look for listings that were removed
        for previous_listing in previous_listings:
            if previous_listing not in new_listings:
                ApartmentSpider.alert(previous_listing, "removed")

        # look for listings that were added
        for new_listing in new_listings:
            if new_listing not in previous_listings:
                ApartmentSpider.alert(new_listing, "added")

        # overwrite listings file
        pickle.dump(new_listings, open('listings.p', 'wb')) 


if __name__ == "__main__":
    process = CrawlerProcess({
	'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(ApartmentSpider)
    process.start() # the script will block here until the crawling is finished
    print("Found", num_listings, "Listings")
