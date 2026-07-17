import os
import sys
from pathlib import Path
import logging
import traceback

from scrapy.crawler import CrawlerRunner
from scrapy.settings import Settings
from crochet import setup, wait_for

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend4.settings')
os.environ.setdefault('TWISTED_REACTOR', 'twisted.internet.asyncioreactor.AsyncioSelectorReactor')

from twisted.internet import asyncioreactor
asyncioreactor.install()

import django
django.setup()

from twisted.internet import reactor
from backend4app.courses_spider import CoursesSpider

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Setup crochet (for running Twisted reactor in blocking manner)
setup()

def main():
    logger.info("=== Script STARTED: run_courses_spider_script ===")
    
    scrapy_settings = Settings()
    scrapy_settings.set('BOT_NAME', 'backend4app')
    scrapy_settings.set('SPIDER_MODULES', ['backend4app.courses_spider'])
    scrapy_settings.set('NEWSPIDER_MODULE', 'backend4app.courses_spider')
    scrapy_settings.set('LOG_LEVEL', 'INFO')
    scrapy_settings.set('ROBOTSTXT_OBEY', True)
    scrapy_settings.set('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0')
    scrapy_settings.set('CONCURRENT_REQUESTS', 1) #set to 1 to avoid botting
    scrapy_settings.set('CONCURRENT_REQUESTS_PER_DOMAIN', 1)  
    scrapy_settings.set('DOWNLOAD_DELAY', 7)  
    scrapy_settings.set('AUTOTHROTTLE_ENABLED', True)
    scrapy_settings.set('DOWNLOAD_TIMEOUT', 240)
    scrapy_settings.set('RETRY_TIMES', 3)
    scrapy_settings.set('COOKIES_ENABLED', True)
    scrapy_settings.set('DEFAULT_REQUEST_HEADERS', {                                         
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',   
        'Accept-Encoding': 'gzip, deflate, br, zstd',                                        
        'Accept-Language': 'en-US,en;q=0.9',                                                 
        'Cache-Control': 'max-age=0',                                                        
        'Connection': 'keep-alive',                                                          
        'Host': 'www.mblseminars.com',                                                       
        'Pragma': 'no-cache',                                                                
        'Sec-Ch-Ua': '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',     
        'Sec-Ch-Ua-Mobile': '?0',                                                            
        'Sec-Ch-Ua-Platform': '"Windows"',                                                   
        'Sec-Fetch-Dest': 'document',                                                        
        'Sec-Fetch-Mode': 'navigate',                                                        
        'Sec-Fetch-Site': 'none',                                                            
        'Sec-Fetch-User': '?1',                                                              
        'Upgrade-Insecure-Requests': '1',                                                    
    })                                                                                       
    
    runner = CrawlerRunner(scrapy_settings)

    @wait_for(timeout=600)
    def crawl():
        logger.info("About to call runner.crawl(CoursesSpider)")
        deferred = runner.crawl(CoursesSpider)
        return deferred

    try:
        crawl()
        logger.info("=== Script FINISHED successfully ===")
    except Exception:
        logger.error("=== Script FAILED ===")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()