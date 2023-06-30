import re
import logging
import json
import requests
from bs4 import BeautifulSoup
from functools import cached_property
from login_helper import LogedSessionCreator
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse


# Configure the logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LinkedInNavigator:

    """
    This function uses the search bar of LinkedIn to search for companies. It uses a logged-in user to retrieve
    companies that match the provided name.
    """

    SEARCH_URL = "https://www.linkedin.com/search/results/COMPANIES/"
    _EMPLOYEES_SELECTOR = ".t-normal.t-black--light.link-without-visited-state.link-without-hover-state"

    def __init__(self, username=None, password=None, cookies=None):
        """
        Initialize the LinkedInNavigator object.

        Args:
            username (str): Valid LinkedIn username.
            password (str): Username's password.
            cookies (dict): A dict of valid logged-in user CookiesJar.

        Note:
            These arguments are optional, but either cookies or a pair of username and password must be provided.
        """
        if (not cookies) and not (username and password):
            raise ValueError("Cookie or user and password are needed")
        self.username = username
        self.password = password
        self.cookies = cookies

    @cached_property
    def _loged_session(self):
        """
        A cached property that logs in the user.
        """

        return LogedSessionCreator.log_in(self.username, self.password, self.cookies)

    def _is_company_data(self, raw_data, path=None):
        """
        Check if the provided data belongs to a company on the page.

        Args:
            raw_data (str): The raw data to check.

        Returns:
            bool: True if the data belongs to a company, False otherwise.
        """

        return '"COMPANIES"' in raw_data

    def _extract_company_url(self, dict_):
        """
        Extract the URLs of companies given relevant scraped data.

        Args:
            dict_ (dict): The relevant scraped data.

        Returns:
            list: List of company URLs.
        """

        urls = set()
        for included_data in dict_["included"]:
            if 'navigationUrl' in included_data:
                urls.add(included_data['navigationUrl'])
        return list(urls)

    def search(self, company_name):
        """
        Search for a company name in the search bar.

        Args:
            company_name (str): The name of the company to search for.

        Returns:
            list: List of company URLs that match the company name.
        """

        response = self._loged_session.get(self.SEARCH_URL, params={"keywords": company_name})
        soup = BeautifulSoup(response.content, 'html.parser')
        companies_urls = []
        for c in soup.find_all("code"):
            if self._is_company_data(c.get_text()):
                companies_urls += self._extract_company_url(json.loads(c.get_text()))
        return companies_urls

    @staticmethod
    def _adapt_cookiejar_to_playwright_cookies(cookies: dict):
        """
        Adapt the request CookieJar to the Playwright cookie format.

        Args:
            cookies (dict): Dictionary containing cookies.

        Returns:
            list: List of cookies adapted to the Playwright cookie format.
        """
        result = []
        for key, value in cookies.items():
            result.append({
                "name": key,
                "value": value,
                "domain": urlparse(LinkedInNavigator.SEARCH_URL).netloc,
                "path": "/"
            })
        return result

    def get_employees_number(self, company_url: str):
        """
        Scrape the number of employees from a LinkedIn company URL.

        Args:
            company_url (str): The URL of the company's LinkedIn page.

        Returns:
            str: The number of employees as a string, or None if not found.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            cookies = requests.utils.dict_from_cookiejar(self._loged_session.cookies)
            context.add_cookies(self._adapt_cookiejar_to_playwright_cookies(cookies))
            page = context.new_page()
            page.goto(company_url)
            handle = page.query_selector(self._EMPLOYEES_SELECTOR)
            result = re.sub('[^0-9]', '', handle.inner_html()) if handle else None

        logger.info("There are %s employees", result)
        return result
