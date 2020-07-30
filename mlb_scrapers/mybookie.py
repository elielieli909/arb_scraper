# from selenium import webdriver
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options

import numpy as np
import pandas as pd

import cloudscraper
import requests
from bs4 import BeautifulSoup

from .ml_to_decimal import to_decimal

# TODO: Might need to use selenium instead

def fix_name(team_name):
    r = team_name
    r = r.replace('La ', 'Los Angeles ')
    r = r.replace('Sfo ', 'San Francisco ')
    r = r.replace('Oak ', 'Oakland ')
    r = r.replace('Was ', 'Washington ')
    r = r.replace('Tor ', 'Toronto ')
    r = r.replace('Cin ', 'Cincinnati ')
    r = r.replace('Chi ', 'Chicago ')
    r = r.replace('Tam ', 'Tampa Bay ')
    r = r.replace('Atl ', 'Atlanta ')
    r = r.replace('Phi ', 'Philadelphia ')
    r = r.replace('Ny ', 'New York ')
    r = r.replace('Pit ', 'Pittsburgh ')
    r = r.replace('Mil ', 'Milwaukee ')
    r = r.replace('Mia ', 'Miami ')
    r = r.replace('Bal ', 'Baltimore ')
    r = r.replace('Hou ', 'Houston ')
    r = r.replace('Cle ', 'Cleveland ')
    r = r.replace('Sea ', 'Seattle ')
    r = r.replace('Det ', 'Detroit ')
    r = r.replace('Kan ', 'Kansas City ')
    r = r.replace('Ari ', 'Arizona ')
    r = r.replace('Tex ', 'Texas ')
    r = r.replace('Stl ', 'St. Louis ')
    r = r.replace('Bos ', 'Boston ')
    r = r.replace('Min ', 'Minnesota ')
    r = r.replace('Col ', 'Colorado ')
    r = r.replace('Sdg ', 'San Diego ')



    return r

def scrape():
    # URL OF THE SITE WE'RE SCRAPING
    url = 'https://mybookie.ag/sportsbook/mlb/'

    # To bypass Cloudflare anti-DDOS protection, use cloudscraper
    # scraper = cloudscraper.create_scraper()
    res = requests.get(url, cookies={'sp_lit': 'jwah9qSIW0FCBldf4xr/Dg==', 'spcsrf':'e43fa88ce5d8a0dcf561d0c1f4050fd6', 'SPSI':'835bc3750082f7f9ea67285d926233f9'})
    html_soup = BeautifulSoup(res.text, 'html.parser')
    # print(html_soup)

    # Initialize lists for dataframe
    first_teams = []
    first_odds = []
    second_teams = []
    second_odds = []
    game_days = []

    all_games = html_soup.find_all('div', {'class': 'game-line'})
    # print(all_games)
    day = ''
    for game in all_games:
        # Get game banner (Includes date and whether or not its live)
        try:
            banner = game.find('p', {'class':'game-line__banner'}).text

            if 'LIVE BETTING' in banner:
                day = 'LIVE'
            elif banner[-2].isdigit() and banner[-1].isdigit():
                day = banner[-2:]
        except:
            pass

        # Get teams (sometimes they aren't in the game element so use try catch)
        try:
            team2 = fix_name(game.find('p', {'class': 'game-line__home-team__name'})['title'])
            team1 = fix_name(game.find('p', {'class': 'game-line__visitor-team__name'})['title'])
        except:
            continue

        # time = game.find('span', {'class':'game-line__time__date__hour dynamic_date change__timer'}).text
        # print(time)

        # Get Moneyline Odds
        all_odds = game.find_all('button', {'class':'lines-odds'})
        try:
            ml1 = int(all_odds[1].text)
            ml2 = int(all_odds[4].text)
            ml1 = to_decimal(ml1)
            ml2 = to_decimal(ml2)
        except:
            # In case Int conversion fails (odds = ' - ')
            continue

        first_odds.append(ml1)
        second_odds.append(ml2)
        first_teams.append(team1)
        second_teams.append(team2)
        game_days.append(day)

    df = pd.DataFrame({
        'Team 1': first_teams, 
        'Team 1 ML': first_odds, 
        'Team 2': second_teams,
        'Team 2 ML': second_odds,
        'Game Date': game_days
    })

    return df

if __name__ == '__main__':
    print(scrape())