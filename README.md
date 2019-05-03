## Scraper to get available listings on Church Corner apartments website and send SMS/Email alerts

This script should be called with scrapy's scraper shell and will look for new listings. Once it finds a new listing within a specified time range it will use Twilio's API to send a text alert. All sensitive configuration should be done in `config.py` with the form:

    # config.py
    config = {
        twilio_sid = xxxxxxx,
        sensitive_info = zzzzzzz,
        ...
    }

The script can be called periodically as a cron job or something similar.


