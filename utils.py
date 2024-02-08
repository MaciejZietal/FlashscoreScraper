import requests
import random
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

def get_proxies() -> list:
    """Reads proxies from sslproxies.org and returns them as a list.

    Returns:
        list: List of free proxies.
    """
    response = requests.get('https://www.sslproxies.org/')
    soup = BeautifulSoup(response.text,"html.parser")
    proxies = []

    for item in soup.select("table.table tbody tr"):
        if not item.select_one("td"):
            break

        ip = item.select_one("td").text
        port = item.select_one("td:nth-of-type(2)").text
        proxies.append(f"{ip}:{port}")

    return proxies

def get_random_proxy(proxies: list) -> str:
    """Gets random proxy.

    Args:
        proxies (list): List with proxies.

    Returns:
        str: Selected proxy.
    """
    return random.choice(proxies)

def create_driver(proxies: list) -> uc.Chrome:
    """Creates undetected ChromeDriver with selected proxy.

    Args:
        proxies (list): List of proxies.

    Returns:
        uc.Chrome: Created ChromeDriver.
    """
    proxy = get_random_proxy(proxies)
    
    chrome_options = uc.ChromeOptions()
    chrome_options.headless = False
    seleniumwire_options = {'proxy': {'https': f'type://{proxy}',}}

    driver = uc.Chrome(options=chrome_options, seleniumwire_options=seleniumwire_options)
    driver.maximize_window()

    return driver
