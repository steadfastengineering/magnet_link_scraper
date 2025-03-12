
import scrapy
import argparse
import re
from scrapy.crawler import CrawlerProcess
import datetime
from bs4 import BeautifulSoup

class MagnetSpider(scrapy.Spider):
    name = "magnet_spider"
    
    def __init__(self, start_url, *args, **kwargs):
        super(MagnetSpider, self).__init__(*args, **kwargs)
        # Set the start_urls list to the provided start_url.
        self.start_urls = [start_url]
    
    def parse(self, response):
        # Clean all HTML elements such as <wbr> or others that might breakup link text, we only care about the inner text without the HTML tags
        soup = BeautifulSoup(response.text, 'html.parser')
        clean_text = soup.get_text()   
        
        # The regex looks for strings starting with "magnet:?" and collects characters until a terminator (space, quote, or angle bracket)
        magnet_links = re.findall(r'magnet:\?[^\s"\'<>]+', clean_text)
         
        for link in set(magnet_links):  # using set() to avoid duplicates
            yield {"magnet": link} 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape torrent magnet links starting from the given URL.")
    parser.add_argument("start_url", help="The root URL for the spider to start crawling.")
    args = parser.parse_args()

    # Configure feed export to save the yielded items (magnet links) to a JSON file.
    time_stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    settings = {
        "FEEDS": {
            f"./links/{time_stamp}-magnet_links.json": {"format": "json", "overwrite": True}
        }
    }
    
    process = CrawlerProcess(settings=settings)
    process.crawl(MagnetSpider, start_url=args.start_url)
    process.start()
