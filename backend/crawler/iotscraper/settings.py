BOT_NAME = "iotscraper"
SPIDER_MODULES = ["iotscraper.spiders"]
NEWSPIDER_MODULE = "iotscraper.spiders"
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
DEPTH_LIMIT = 2
LOG_LEVEL = "ERROR"
FEED_FORMAT = 'json'
FEED_URI = '../../data/iot_scraped.json'
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Log settings
LOG_FILE = "spider_debug.log"
FEEDS = {
    "../../data/iot_scraped.json": {
        "format": "json",
        "encoding": "utf8",
        "store_empty": False,
        "overwrite": True,
    },
}

# User agent to identify the scraper
USER_AGENT = "Mozilla/5.0 (compatible; IoTScraper/1.0; +https://example.com/bot)"