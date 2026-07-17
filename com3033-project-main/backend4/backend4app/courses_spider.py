import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from scrapy.selector import Selector
from backend4app.models import Course
from datetime import datetime
from django.utils import timezone
from decimal import Decimal
import re
import logging
from selenium.webdriver.chrome.options import Options
from asgiref.sync import async_to_sync, sync_to_async
import time

# ===== Logger setup =====
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BASE_URL = "https://www.mblseminars.com"

class CoursesSpider(scrapy.Spider):
    name = 'courses_mbl'
    url = 'https://www.mblseminars.com/courses?parentPracticeareaId=58'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger.info(">>> CoursesSpider __init__ called <<<")
        print(">>> CoursesSpider __init__ called <<<")
    
    async def start(self):
        yield scrapy.Request(self.url, callback=self.parse_selenium, dont_filter=True)

    async def parse_selenium(self, response):
        self.logger.info(f"=== Starting start_requests with URLs: {self.url}")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless") 
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")  
        chrome_options.add_argument("--disable-dev-shm-usage")  
        chrome_options.add_argument("--remote-debugging-port=9222")  
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0")
        chrome_options.page_load_strategy = 'eager'
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.set_page_load_timeout(240)
        
        self.logger.info(f"Fetching: {self.url}")
        driver.get(self.url)
        # Wait for page to load dynamically 
        driver.implicitly_wait(10)
        # Scroll down to load more content dynamically
        self.scroll_page(driver)
        # Get the page source after JS is rendered
        page_source = driver.page_source
        driver.quit()  
        sel = Selector(text=page_source)
        return await self.parse(sel)

    def scroll_page(self, driver, scroll_pause_time=9):
        """Scroll the page until no new content loads."""
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # Scroll to the bottom
            driver.execute_script("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")
           
            time.sleep(scroll_pause_time)  # Wait for content to load

            # Calculate new page height and compare with last height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # No more content loaded
            last_height = new_height
            
    @sync_to_async
    def save_course(self, title, date, date_special, final_link, cpd_hours, course_type):
        obj, created = Course.objects.update_or_create(
            link=final_link,  
            defaults={
                'title': title,
                'date': date,
                'date_special': date_special,
                'cpd_hours': cpd_hours,
                'course_type': course_type,
            }
        )
        return obj, created
      
      
    async def parse(self, response):
        self.logger.info("=== Starting parse of MBL seminars page ===")
        course_count = 0

        # Each course container
        for course in response.css("div.css-1v7eko8 div.css-j10bqz"):
            
            link = course.css("a.css-17xitbz::attr(href)").get()
            title = course.css("a.css-17xitbz::text").get(default="").strip()

            self.logger.info(f"Found course card: title='{title}', link='{link}'")

            course_type = course.css("div.css-v2udjc span.css-1mld7v6::text").get(default=None)
            course_type = course_type.strip() if course_type else None

            cpd_hours = course.css("div.css-v2udjc span.css-1k0bxjb::text").get(default=None)
            if cpd_hours:
                match = re.search(r"([\d\.]+)", cpd_hours)
                if match:
                    try:
                        cpd_hours = Decimal(match.group(1))
                    except Exception:
                        cpd_hours = None

            date_special = course.css("div.css-ctgra::text").get(default="").strip()

            try:
                date = datetime.strptime(date_special, "%d %B %Y")
            except ValueError:
                date = None          
                
            if date is not None and timezone.is_naive(date):
                date = timezone.make_aware(date, timezone.get_current_timezone())

            if link and not link.startswith('http'):
                final_link = BASE_URL + link
            else:
                final_link = link
          
            obj, created = await self.save_course(title, date, date_special, final_link, cpd_hours, course_type)
            action = "Created" if created else "Updated"
            self.logger.info(f"{action} course: '{title}' on {date}")
            course_count += 1

        self.logger.info(f"=== Finished parse. Total saved/updated: {course_count} ===")