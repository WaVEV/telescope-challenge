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
    """
    G2CompanyCrawl is a class that enables crawling relevant data from companies' websites listed in a CSV file.

    Args:
        csv_file (str): The filename of the CSV file containing the URLs of the companies.

    Methods:
        extract_data(): Main process that requests the URLs and extracts the data from each company.
        read_csv(): Reads the company URLs from the CSV file.
        get_company_data(page): Scrapes relevant data (title, description, and logo URL) from a company page.

    Usage Example:
        crawler = G2CompanyCrawl('companies.csv')
        for data in crawler.extract_data():
            print(data)
    """

    def __init__(self, csv_file: str):
        """
        G2crwod crawler, given a csv filename with the url of the companies it crawl some relevant data from there
        """
        self.csv_file = csv_file
        self._init_playwright()

    def _init_playwright(self):
        """
        Create the playwright resources
        """
        logger.info("creating a new browser")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch()

    def _destroy_playwright(self):
        """
        Destrois the playwright resources
        """
        logger.info("destroying the browser")
        self.browser.close()
        self.playwright.stop()

    def __delete__(self):
        """
        Free the playwright resources
        """
        self._destroy_playwright()
        super().__delete__()

    @cached_property
    def _page_tab(self):
        """
        Creates a new browser page tab with firefox context.
        """
        firefox_context = self.playwright.devices['Desktop Firefox']
        context = self.browser.new_context(
            **firefox_context,
        )
        page = context.new_page()
        return page

    def _goto(self, url: str):
        """
        Move the page to a certain direction. if a captcha is detected, it pass the validation.
        if the browser session is banned, it creates a new one
        """
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
        """
        Main process of the G2CompanyCrawl class. It requests the URLs from the CSV file and extracts the data 
        from each company's website.

        Yields:
            dict: A dictionary containing the extracted data for each company, including the title, description,
            and logo URL.
                - title (str): The title of the company.
                - description (str): The description of the company.
                - logo_url (str): The URL of the company's logo.

        Note:
            - The method uses the 'read_csv' method to retrieve the company URLs from the CSV file.
            - For each company URL, it logs the crawling process, moves the page to the URL using the '_goto' method, and then calls the 'get_company_data' method to extract the relevant data.
            - The extracted data for each company is yielded as a dictionary.
            - The method uses a generator (yield) to provide the data one company at a time, which allows for efficient memory usage when processing a large number of companies.

        Example:
            crawler = G2CompanyCrawl('companies.csv')
            for data in crawler.extract_data():
                print(data)  # {'title': 'Company ABC', 'description': '...', 'logo_url': 'https://...'}
        """
        
        for company_url in self.read_csv():
            logger.info("Crawling %s", company_url)
            self._goto(company_url)
            data = self.get_company_data(company_url)
            yield data

    def read_csv(self):
        """
        Read the companies url from the csv.
        """
        with open(self.csv_file) as file:
            csv_file = csv.reader(file)
            for company_url, in csv_file:
                logger.info("read %s company", company_url)
                yield company_url
                tts = random.randint(2, 6)
                logger.info("Sleeping %d", tts)
                sleep(tts)

    def get_company_data(self, page):
        """
        Scrapes the relevant data from a company page.

        Args:
            page: The company page to scrape data from.

        Returns:
            dict: A dictionary containing the scraped data, including the title, description, and logo URL.
                - title (str): The title of the company.
                - description (str): The description of the company.
                - logo_url (str): The URL of the company's logo.

        Note:
            - If the data is not found on the page, the corresponding value in the dictionary will be None.

        Example:
            page = self._page_tab
            data = self.get_company_data(page)
            print(data)  # {'title': 'Company ABC', 'description': '...', 'logo_url': 'https://...'}
        """
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
