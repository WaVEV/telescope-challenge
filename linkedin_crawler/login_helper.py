import logging
import requests
from retry import retry
from bs4 import BeautifulSoup


# Configure the logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def debug_page(response):
    with open("salida.html", "w") as f:
        f.write(response.content.decode())


class LogedSessionCreator:
    LOGIN_URL = "https://www.linkedin.com/"
    FAILED_LOGIN_URL = 'https://www.linkedin.com/uas/login-submit'

    """
    Helper class for creating logged-in sessions.
    """

    @staticmethod
    @retry(tries=5, delay=5)
    def _get_static_data_form(session: requests.Session):
        """
        Extract the hidden values that are relevant in the authentication form.

        Args:
            session (requests.Session): The session to use for making the request.

        Returns:
            dict: A dictionary containing the hidden values from the authentication form.
        """

        result = {}
        response = session.get(LogedSessionCreator.LOGIN_URL, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'})
        soup = BeautifulSoup(response.content, 'html.parser')
        for input_ in soup.find(attrs={"data-id": "sign-in-form"}).find_all("input"):
            result[input_.attrs["name"]] = input_.attrs.get("value")
        return result

    @staticmethod
    def user_successfully_loged(session: requests.Session, response: requests.Response):
        """
        Check if the user has successfully logged in.

        Args:
            session (requests.Session): The session object used for the login.
            response (requests.Response): The response received after the login request.

        Returns:
            bool: True if the user has successfully logged in, False otherwise.
        """
        return not (response.url == LogedSessionCreator.FAILED_LOGIN_URL or 'checkpoint/challenge' in response.url)

    @staticmethod
    def log_in(username=None, password=None, cookies=None):
        """
        Log in a user or initialize a session with cookies. If neither cookies nor a username and password
        are provided, it returns a fresh session.

        Args:
            username (str): The LinkedIn username.
            password (str): The password for the username.
            cookies (dict): A dictionary of cookies for an already logged-in session.

        Returns:
            requests.Session: The logged-in session.
        
        Raises:
            ValueError: If the credentials are not valid.
        """

        session = requests.Session()
        
        if cookies:
            cookies = requests.utils.cookiejar_from_dict(cookies)
            session.cookies.update(cookies)
        elif username and password:
            input_ = LogedSessionCreator._get_static_data_form(session)
            input_["session_password"] = password
            input_["session_username"] = username
            input_["session_key"] = username
            response = session.post("https://www.linkedin.com/uas/login-submit", data=input_)

            if not LogedSessionCreator.user_successfully_loged(session, response):
                raise ValueError("Credentials aren't valid")

        return session
