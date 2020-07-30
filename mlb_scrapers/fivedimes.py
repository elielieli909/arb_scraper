import numpy as np
import pandas as pd

import requests
from bs4 import BeautifulSoup

from .ml_to_decimal import to_decimal

def scrape():
    # URL OF THE SITE WE'RE SCRAPING
    url = 'https://odds.5dimes.mobi/Baseball/MLB/'
    live_url = 'https://odds.5dimes.mobi/Baseball/Live-In__Play/'

    # Initialize lists for dataframe
    first_teams = []
    first_odds = []
    second_teams = []
    second_odds = []
    game_days = []
    game_times = []

    # START WITH NOT LIVE GAMES ===================================================================================
    res = requests.get(url)
    html_soup = BeautifulSoup(res.text, 'html.parser')

    all_dates = html_soup.find_all('div', {'class': 'timeline'})    # TIME, 07/27/2020, etc. 
    all_teams = html_soup.find_all('div', {'class': 'teamline'})    # TEAM, Los Angeles Angels, Oakland Athletics, etc.
    all_odds = html_soup.find_all('div', {'class':'mlline'})
    game_titles = html_soup.find_all('b')

    for i in range(len(game_titles)):
        # titles look like Los Angeles Angels at Oakland Athletics - Game or - 1st 5 Innings
        if '1st 5 Innings' in game_titles[i].text:
            first_team = '1h ' + all_teams[1 + 2*i].text[:-1]
            second_team = '1h ' + all_teams[2 + 2*i].text
            first_odd = all_odds[1 + 2*i].text
            second_odd = all_odds[2 + 2*i].text
            date = all_dates[1 + 2*i].text[3:5]
            time = parse_time_string(all_dates[2+2*i].text)
            try:
                odds1 = to_decimal(int(first_odd))
                odds2 = to_decimal(int(second_odd))

                game_days.append(date)
                game_times.append(time)
                first_teams.append(first_team)
                second_teams.append(second_team)
                first_odds.append(odds1)
                second_odds.append(odds2)
            except:
                continue
        elif 'Game' in game_titles[i].text:
            first_team = all_teams[1 + 2*i].text[:-1]
            second_team = all_teams[2 + 2*i].text
            first_odd = all_odds[1 + 2*i].text
            second_odd = all_odds[2 + 2*i].text
            date = all_dates[1 + 2*i].text[3:5]
            time = parse_time_string(all_dates[2+2*i].text)
            
            try:
                odds1 = to_decimal(int(first_odd))
                odds2 = to_decimal(int(second_odd))

                game_days.append(date)
                game_times.append(time)
                first_teams.append(first_team)
                second_teams.append(second_team)
                first_odds.append(odds1)
                second_odds.append(odds2)
            except:
                continue

    # Now do LIVE GAMES ================================================================================
    res = requests.get(live_url)
    html_soup = BeautifulSoup(res.text, 'html.parser')

    all_dates = html_soup.find_all('div', {'class': 'timeline'})    # TIME, 07/27/2020, etc. 
    all_teams = html_soup.find_all('div', {'class': 'teamline'})    # TEAM, Los Angeles Angels, Oakland Athletics, etc.
    all_odds = html_soup.find_all('div', {'class':'mlline'})

    for i in range(1, len(all_dates), 2):
        date = 'LIVE'
        team1 = all_teams[i].text[:-1]
        team2 = all_teams[i+1].text
        first_odd = all_odds[i].text
        second_odd = all_odds[i+1].text
        # Games which haven't started yet but will be live later that day have this odds
        if '9999' in first_odd:
            continue
        try:
            odds1 = to_decimal(int(first_odd))
            odds2 = to_decimal(int(second_odd))
            game_days.append(date)
            game_times.append(time)
            first_teams.append(team1)
            second_teams.append(team2)
            first_odds.append(odds1)
            second_odds.append(odds2)
        except:
            continue





    df = pd.DataFrame({
        'Team 1': first_teams, 
        'Team 1 ML': first_odds, 
        'Team 2': second_teams,
        'Team 2 ML': second_odds,
        'Game Date': game_days,
        # 'Time' : game_times
    })

    return df

def parse_time_string(time):
    hh = ''
    mm = ''
    flip = True
    for ch in time:
        if flip and ch.isdigit():
            hh += (ch)
        if ch == ':':
            flip = False
        if not flip and ch.isdigit():
            mm += (ch)
        if ch == ' ':
            break
    
    hh = str(int(hh) - 3)
    return hh + ':' + mm

if __name__ == '__main__':
    print(scrape())