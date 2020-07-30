from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

import numpy as np
import pandas as pd

import time
from datetime import date, timedelta

# from .ml_to_decimal import to_decimal

def fix_name(name):
    r = name
    r = r.replace('Nippon Ham', 'Nippon-Ham')
    r = r.replace('KT Wiz Suwon', 'KT Wiz')
    r = r.replace('Kia Tigers', 'KIA Tigers')
    r = r.replace('Yokohama Bay Stars', 'Yokohama Dena Baystars')
    return r

def scrape():
    # URL OF THE SITE WE'RE SCRAPING
    url = 'https://www.pinnacle.com/en/baseball/matchups/'
    # TODO: DO for live
    live_url = 'https://www.pinnacle.com/en/baseball/matchups/live'


    # Setup selenium
    options = Options()
    options.headless = True
    options.add_argument('log-level=3')
    browser = webdriver.Chrome(options=options)

    try:
        # START WITH NON LIVE GAMES =============================================================================================
        browser.get(url)
        browser.implicitly_wait(9)

        # Grab by bucket to separate live and upcoming games
        all_content = browser.find_element_by_class_name('style_vertical__28Lr3')

        divs = all_content.find_elements_by_xpath('div/*')
        
        # Initialize lists for dataframe
        first_teams = []
        first_odds = []
        second_teams = []
        second_odds = []
        game_days = []
        game_times = []

        day = ''
        for div in divs:
            # The style bar showing the date of the subsequent games ('today', 'tomorrow', etc.)
            if div.get_attribute('class') == 'style_dateBar__2qa4C':
                if div.find_element_by_xpath('div/span/span').text == 'TODAY':
                    today = date.today()
                    day = today.strftime("%d")
                elif div.find_element_by_xpath('div/span/span').text == 'TOMORROW':
                    tomorrow = date.today() + timedelta(days=1)
                    day = tomorrow.strftime("%d")

            # Get the teams and odds
            if 'style_row__3duhx style_taller__22DGF' in div.get_attribute('class'):
                teams = div.find_elements_by_class_name('style_participantName__vRjBw')
                odds = div.find_elements_by_class_name('price')
                time = div.find_element_by_class_name('style_time__24Qcs')

                try:
                    first_odds.append(float(odds[0].text))
                    second_odds.append(float(odds[1].text))
                    first_teams.append(fix_name(teams[0].text))
                    second_teams.append(fix_name(teams[1].text))
                except:
                    print('Something went wrong. Prolly closed odds on this match')
                    continue

                game_days.append(day)
                game_times.append(time.text)

        # NOW DO LIVE GAMES ===================================================================================================
        browser.get(live_url)
        browser.implicitly_wait(15)

        # Grab by bucket to separate live and upcoming games
        all_games = browser.find_elements_by_class_name('style_row__3duhx')

        # divs = all_content.find_elements_by_xpath('div/*')
        for game in all_games:
            names = game.find_elements_by_class_name('style_participantName__vRjBw')
            prices = game.find_elements_by_class_name('price')
            
            if len(prices) != 2:
                continue

            first_teams.append(names[0].text)
            first_odds.append(float(prices[0].text))
            second_teams.append(names[1].text)
            second_odds.append(float(prices[1].text))
            game_days.append('LIVE')

        
        browser.quit()
    except Exception as e:
        print('Something went wrong: ' + str(e))
        browser.quit()


    df = pd.DataFrame({
        'Team 1': first_teams, 
        'Team 1 ML': first_odds, 
        'Team 2': second_teams,
        'Team 2 ML': second_odds,
        'Game Date': game_days,
        # 'Time' : game_times
    })
    # print(df)

    return df

if __name__ == '__main__':
    scrape()