import scrapy
from bs4 import BeautifulSoup
from hashlib import md5

class IoTSpider(scrapy.Spider):
    name = "iot_spider"

    start_urls = [
        "https://gyrfalconintelliedge.com/",
        "https://www.iotm2mcouncil.org/iot-library/",
        "https://www.iot-now.com/",
        "https://iot-analytics.com/"
       
    ]

    allowed_domains = [
        "gyrfalconintelliedge.com",
        "iotm2mcouncil.org",
        "iot-now.com",
        "iot-analytics.com",
    ]
 
    custom_settings = {
        'DEPTH_LIMIT': 2,
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 2,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'LOG_FILE': 'spider_debug.log',
        'LOG_LEVEL': 'INFO',
        'FEEDS': {
            '../../data/iot_scraped.json': {
                'format': 'json',
                'encoding': 'utf8',
                'overwrite': True,
            },
        },
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'Mozilla/5.0 (compatible; IoTScraper/1.0; +https://example.com/bot)'
    }

    # Store seen hashes to prevent duplicate text
    seen_hashes = set()

    def parse(self, response):
        # Process only HTML pages
        if "text/html" not in response.headers.get("Content-Type", b"").decode().lower():
            return

        # Use BeautifulSoup to clean and extract
        soup = BeautifulSoup(response.text, "lxml")

        # Remove unwanted tags
        for tag in soup(["script", "style", "nav", "footer", "header", "form", "aside"]):
            tag.decompose()

        paragraphs = soup.find_all("p")
        for p in paragraphs:
            text = p.get_text(strip=True)
            if not text:
                continue

            # Create a hash to filter duplicates
            text_hash = md5(text.encode("utf-8")).hexdigest()
            if text_hash in self.seen_hashes:
                continue  # skip duplicate
            self.seen_hashes.add(text_hash)

            yield {"text": text}

        # Follow links
        for href in response.css("a::attr(href)").getall():
            if not href or href.startswith(("javascript:", "mailto:", "tel:", "#")):
                continue

            if href.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".pdf", ".svg", ".zip", ".docx", ".mp4", ".mp3")):
                continue

            yield response.follow(href, callback=self.parse)






# import scrapy

# class IoTSpider(scrapy.Spider):
#     name = "iot_spider"

    
#     start_urls = [
#         "https://gyrfalconintelliedge.com/",
#         "https://www.iotm2mcouncil.org/iot-library/",
#         "https://www.iot-now.com/",
#         "https://iot-analytics.com/",
#     ]

#     allowed_domains = [
#         "gyrfalconintelliedge.com",
#         "iotm2mcouncil.org",
#         "iot-now.com",
#         "iot-analytics.com",
#     ]

#     custom_settings = {
#         'DEPTH_LIMIT': 2,
#         'FEED_FORMAT': 'json',
#         'FEED_URI': '../../data/iot_scraped.json',
#         'LOG_LEVEL': 'ERROR',
#         'DOWNLOAD_DELAY': 3,
#         'RANDOMIZE_DOWNLOAD_DELAY': True,
#         'AUTOTHROTTLE_ENABLED': True,
#         'AUTOTHROTTLE_START_DELAY': 3,
#         'AUTOTHROTTLE_MAX_DELAY': 10,
#         'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
#         'DOWNLOADER_MIDDLEWARES': {
#         'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
#         }
#     }

#     def parse(self, response):
       
#         if "text/html" not in response.headers.get("Content-Type", b"").decode().lower():
#             return

        
#         for p in response.css("p::text").getall():
#             text = p.strip()
#             if text:
#                 yield {"text": text}

      
#         for href in response.css("a::attr(href)").getall():
#             if not href:
#                 continue
#             href = href.strip()

#             if href.startswith(("javascript:", "mailto:", "tel:", "#")):
#                 continue
#             if href.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".pdf", ".svg", ".zip", ".docx")):
#                 continue

#             yield response.follow(href, self.parse)
