import time
import random

import pandas as pd

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

from utils import create_driver, get_proxies
from match import Match

PROXIES  = get_proxies()

class Scraper():
    def __init__(self, country: str, division: str, season: str):
        self.country = country
        self.division = division
        self.season = season
        self.matches_stats = []
        self.matches_with_errors = []
        
    def get_all_matches(self):
        url = self.generate_league_url()
        id_list = self.get_all_matches_ids(url)
        random.shuffle(id_list)
        driver = create_driver(PROXIES)
        for id in random.choices(id_list, k=20):
            single_match = Match(id, driver)
            try:
                single_match.generate_match_info()
            except:
                self.matches_with_errors.append(id)
            self.matches_stats.append(single_match.get_match_info())
            
            # change driver if generated number is greater than 0.75
            if random.random() > 0.75:
                driver.quit()
                driver = create_driver(PROXIES)
                time.sleep(1)
                
        driver.quit()
        
        return pd.concat(self.matches_stats)
        
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
            single_id = id.get_attribute("id").split('g_1_')[1]
            id_list.append(single_id)
            
        driver.quit()

        return id_list