import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException

from utils import create_driver, get_proxies

PROXIES  = get_proxies()

class Scraper():
    def __init__(self, country: str, division: str, season: str):
        self.country = country
        self.division = division
        self.season = season
        
    def get_all_results(self):
        url = self.generate_league_url()
        id_list = self.get_all_matches_ids(url)
        
        
    def generate_league_url(self) -> str:
        """Generate link to league results.
        
        Arguments:
            url (str): Link to flashscore page with results.
        
        Returns:
            str: Url to page with league results.
        """
        return f"https://www.flashscore.com/football/{self.country.lower()}/{self.division.replace(' ', '-').lower()}-{self.season}/results/"
    
    def get_all_matches_ids(self, url: str) -> list:
        """Gets list of IDs corresponding to matches that are available in url link.
    
        Returns:
            list: List with matches IDs.
        """
        # creates web driver
        driver = create_driver(PROXIES)

        # get url
        driver.get(url)

        # expand page by clicking "show more matches" until possible
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'event__more')))
        more_button = driver.find_element(By.CLASS_NAME, 'event__more')
        more_matches = more_button is not None
        while more_matches:
            try:
                driver.execute_script('arguments[0].click();', more_button)
                time.sleep(3)
            except StaleElementReferenceException as exc:
                more_matches = False

        # get ids
        id_list = []
        for id in WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[id^=g_1_]'))):
            single_id = id.get_attribute("id").strip("g_1_")
            id_list.append(single_id)

        return id_list