import re
import time
import random
import pandas as pd
import undetected_chromedriver as uc

from typing import Union
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from utils import generate_sleep_times

SLEEP_TIMES = generate_sleep_times()
MOVES = [
    'https://www.flashscore.com/match/PLACE_FOR_ID/#/match-summary/match-summary',
    'https://www.flashscore.com/match/PLACE_FOR_ID/#/h2h/overall',
    'https://www.flashscore.com/match/PLACE_FOR_ID/#/standings/table/overall',
    'https://www.flashscore.com/match/PLACE_FOR_ID/#/standings/top_scorers',
    'https://www.flashscore.com/match/PLACE_FOR_ID/#/standings/form/overall/5',
    'https://www.flashscore.com/match/PLACE_FOR_ID/#/h2h/home',
    'https://www.flashscore.com/match/PLACE_FOR_ID/#/h2h/away',
    'https://www.flashscore.com',
    'https://www.flashscore.com/football/england/premier-league/',
    'https://www.flashscore.com/football/england/premier-league/archive/',
    'https://www.flashscore.com/football/england/premier-league/news/',
    'https://www.flashscore.com/football/england/premier-league/results/'
    'https://www.flashscore.com/football/france/ligue-1/',
    'https://www.flashscore.com/football/france/ligue-1/archive/',
    'https://www.flashscore.com/football/france/france/news/',
    'https://www.flashscore.com/football/france/france/results/'
    'https://www.flashscore.com/football/germany/bundesliga/',
    'https://www.flashscore.com/football/germany/bundesliga/archive/',
    'https://www.flashscore.com/football/germany/germany/news/',
    'https://www.flashscore.com/football/germany/germany/results/'
    'https://www.flashscore.com/football/italy/serie-a/',
    'https://www.flashscore.com/football/italy/serie-a/archive/',
    'https://www.flashscore.com/football/italy/italy/news/',
    'https://www.flashscore.com/football/italy/italy/results/'
    'https://www.flashscore.com/football/spain/laliga/',
    'https://www.flashscore.com/football/spain/laliga/archive/',
    'https://www.flashscore.com/football/spain/laliga/news/',
    'https://www.flashscore.com/football/spain/laliga/results/'
    'https://www.flashscore.com/football/turkey/super-lig/',
    'https://www.flashscore.com/football/turkey/super-lig/archive/',
    'https://www.flashscore.com/football/turkey/super-lig/news/',
    'https://www.flashscore.com/football/turkey/super-lig/results/'
]

class Match():
    def __init__(self, id: str, driver: uc.Chrome):
        self.id = id
        self.driver = driver
        self.match_info = {}
        self.generate_url()

    def generate_url(self) -> str:
        """Generates url to flashscore page with match summary.

        Returns:
            str: Url to match summary.
        """
        self.url = f'https://www.flashscore.com/match/{self.id}/#/match-summary/match-statistics/0'

    def get_match_info(self, as_df: bool=True) -> Union[dict, pd.DataFrame]:
        """Returns match information.

        Args:
            as_df (bool, optional): Indicates if info should be returned as dataframe or as dictionary. Defaults to True.

        Returns:
            Union[dict, pd.DataFrame]: Match information.
        """
        if as_df:
            return pd.DataFrame(self.match_info, index=[self.id])
        return self.match_info

    def generate_match_info(self):
        """Generates match information by scraping teams and match time, score, match statistics, coach information and odds.
        """
        self.driver.get(self.url)
        time.sleep(random.choice(SLEEP_TIMES))
        self.accept_cookies()

        # get page content
        page_soup = BeautifulSoup(self.driver.page_source, 'lxml')
        self.random_move()
        # get teams and match time
        self.get_teams_time(page_soup)
        # get score
        self.get_score_info(page_soup)
        # get all stats
        self.get_stats(page_soup)
        # move to lineups
        self.move_to_lineups_tab()
        # get lineups page content
        page_soup = BeautifulSoup(self.driver.page_source, 'lxml')
        self.random_move()
        # get coaches info
        self.get_coaches_info(page_soup)
        # move to odds tab
        self.move_to_odds_tab()
        # get odds page content
        page_soup = BeautifulSoup(self.driver.page_source, 'lxml')
        self.random_move()
        # get odds info
        self.get_odds(page_soup)


    def get_teams_time(self, page_soup: BeautifulSoup):
        """Scrape information about teams and match time.

        Args:
            page_soup (BeautifulSoup): HTML match statistics page content.
        """
        self.match_info['home_team'] = page_soup.find("div", {'class': 'duelParticipant__home'}).text
        self.match_info['away_team'] = page_soup.find("div", {'class': 'duelParticipant__away'}).text
        self.match_info['date_time'] = page_soup.find("div", {'class':"duelParticipant__startTime"}).text

    def get_score_info(self, page_soup: BeautifulSoup):
        """Scrape information about score.

        Args:
            page_soup (BeautifulSoup): HTML match statistics page content.
        """
        score = page_soup.find("div", {'class': 'duelParticipant__score'}).text
        home_goals, away_goals = re.findall(r'\d+', score)
        self.match_info['home_goals'] = int(home_goals)
        self.match_info['away_goals'] = int(away_goals)

    def get_stats(self, page_soup: BeautifulSoup):
        """Scrape all statistics.

        Args:
            page_soup (BeautifulSoup): HTML match statistics page content.
        """
        content = page_soup.find_all('div', {'class': '_row_rz3ch_9'})

        for i in range(len(content)):
            name = "".join(re.split("[^a-zA-Z]*", content[i].text))
            home_stat, away_stat = re.findall(r"[-+]?\d*\.?\d+|[-+]?\d+", content[i].text)
            self.match_info[name + '_home'] = float(home_stat)
            self.match_info[name + '_away'] = float(away_stat)

    def get_coaches_info(self, page_soup: BeautifulSoup):
        """Scrape information about coaches.

        Args:
            page_soup (BeautifulSoup): HTML match lineups page content.
        """
        all_sections = page_soup.find_all("div", {'class': 'section'})
        coach_section = [section for section in all_sections if 'Coaches' in section.text]
        # find coaches info
        coaches = coach_section[0].find_all('a', {'class': 'lf__participantName'})
        self.match_info['coach_home'] = coaches[0].text
        self.match_info['coach_away'] = coaches[1].text

    def get_odds(self, page_soup: BeautifulSoup):
        """Scrape information about odds.

        Args:
            page_soup (BeautifulSoup): HTML match odds page content.
        """
        odds_text = page_soup.find("div", {'class': 'ui-table__row'}).text
        self.match_info['odds_H'] = odds_text[:4]
        self.match_info['odds_X'] = odds_text[4:8]
        self.match_info['odds_A'] = odds_text[8:]

    def move_to_lineups_tab(self):
        """Moves ChromeDriver to lineups tab.
        """
        self.driver.get(f"https://www.flashscore.com/match/{self.id}/#/match-summary/lineups")
        time.sleep(random.choice(SLEEP_TIMES))

    def move_to_odds_tab(self):
        """Moves ChromeDriver to odds tab.
        """
        self.driver.get(f"https://www.flashscore.com/match/{self.id}/#/odds-comparison/1x2-odds/full-time")
        time.sleep(random.choice(SLEEP_TIMES))

    def random_move(self):
        if random.random() > 0.5:
            self.driver.get(random.choice(MOVES).replace('PLACE_FOR_ID', self.id))
            time.sleep(random.choice(SLEEP_TIMES) - 3.4)

    def accept_cookies(self):
        try:
            self.driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
            time.sleep(1)
        except NoSuchElementException:
            pass
