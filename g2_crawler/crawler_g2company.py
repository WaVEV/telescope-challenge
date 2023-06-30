import random

from functools import cached_property
import logging
import csv
from playwright.sync_api import sync_playwright
from time import sleep


# Configure the logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class G2CompranyCrawl:

    def __init__(self, csv_file):    
        self.csv_file = csv_file
        self._init_playwright()

    def _init_playwright(self):
        logger.info("creating a new browser")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch()

    def _destroy_playwright(self):
        logger.info("destroying the browser")
        self.browser.close()
        self.playwright.stop()

    def __delete__(self):
        self._destroy_playwright()
        super().__delete__()

    @cached_property
    def _page_tab(self):
        firefox_context = self.playwright.devices['Desktop Firefox']
        context = self.browser.new_context(
            **firefox_context,
        )
        page = context.new_page()
        return page

    def _goto(self, url):
        self._page_tab.goto(url)
        locator = self._page_tab.locator(
            'h2[id=challenge-running], div[itemprop=description], div.cf-error-title').inner_text()

        if locator == "Checking if the site connection is secure":
            logger.info("Captcha detected")
            logger.info("clicking the captcha")
            self._page_tab.frame_locator("iFrame").locator('input').click()
        elif locator == "Access denied\nError code 1020":
            logger.info("browser denied, creating another")
            self._destroy_playwright()
            self._init_playwright()
            del self.__dict__['_page_tab']
            return self._goto(url)

        self._page_tab.locator('div[itemprop=description]').inner_text()
        logger.info("Captcha passed")

    def extract_data(self):
        
        for company_url in self.read_csv():
            logger.info("Crawling %s", company_url)
            self._goto(company_url)
            data = self.get_company_data(company_url)
            yield data

    def read_csv(self):
        with open(self.csv_file) as file:
            csv_file = csv.reader(file)
            for company_url, in csv_file:
                logger.info("read %s company", company_url)
                yield company_url
                tts = random.randint(2, 6)
                logger.info("Sleeping %d", tts)
                sleep(tts)

    def get_company_data(self, page):
        page = self._page_tab
        title = page.query_selector("h1.l2.pb-half.inline-block")
        title = title.inner_html() if title else None
        description = page.query_selector('div[itemprop=description]')
        description = description.inner_text() if description else None
        logo = page.query_selector('a.product-head__logo__img.pjax img.detail-logo')
        logo_url = logo.get_attribute("src") if logo else None

        return {
            "title": title,
            "description": description,
            "logo_url": logo_url
        }
