import numpy as np
import pandas as pd

import requests
from bs4 import BeautifulSoup

from .ml_to_decimal import to_decimal

def fix_name(name):
    r = name
    # For Double Header games
    r = r.replace('D1 ', '')
    r = r.replace('D2 ', '')
    r = r.replace('Blue Jays', 'Toronto Blue Jays')
    r = r.replace('Nationals', 'Washington Nationals')
    r = r.replace('Cubs', 'Chicago Cubs')
    r = r.replace('Reds', 'Cincinnati Reds')
    r = r.replace('Braves', 'Atlanta Braves')
    r = r.replace('Rays', 'Tampa Bay Rays')
    r = r.replace('Brewers', 'Milwaukee Brewers')
    r = r.replace('Pirates', 'Pittsburgh Pirates')
    r = r.replace('Mariners', 'Seattle Mariners')
    r = r.replace('Astros', 'Houston Astros')
    r = r.replace('White Sox', 'Chicago White Sox')
    r = r.replace('Indians', 'Cleveland Indians')
    r = r.replace('Royals', 'Kansas City Royals')
    r = r.replace('Tigers', 'Detroit Tigers')
    r = r.replace('Mets', 'New York Mets')
    r = r.replace('Red Sox', 'Boston Red Sox')
    r = r.replace('Cardinals', 'St. Louis Cardinals')
    r = r.replace('Twins', 'Minnesota Twins')
    r = r.replace('Diamondbacks', 'Arizona Diamondbacks')
    r = r.replace('Rangers', 'Texas Rangers')
    r = r.replace('Dodgers', 'Los Angeles Dodgers')
    r = r.replace('Angels', 'Los Angeles Angels')
    r = r.replace('Rockies', 'Colorado Rockies')
    r = r.replace('Athletics', 'Oakland Athletics')
    r = r.replace('Giants', 'San Francisco Giants')
    r = r.replace('Yankees', 'New York Yankees')
    r = r.replace('Phillies', 'Philadelphia Phillies')
    r = r.replace('Padres', 'San Diego Padres')
    r = r.replace('Orioles', 'Baltimore Orioles')
    return r

def scrape():
    # URL OF THE SITE WE'RE SCRAPING
    url = 'https://www.betnow.eu/sportsbook-info/baseball/mlb'

    res = requests.get(url)
    html_soup = BeautifulSoup(res.text, 'html.parser')

    bucket = html_soup.find('div', {'id':'odds'})
    rows = bucket.find_all('div', recursive=False)

    # Initialize lists for dataframe
    first_teams = []
    first_odds = []
    second_teams = []
    second_odds = []
    game_days = []
    game_times = []

    day = ''
    time = ''
    is_first_team = True
    for row in rows:
        if row.has_attr('class'):
            # Get the date
            if row['class'][0] == 'odd-header':
                buf = ''
                for ch in row.text:
                    if ch.isdigit():
                        buf += ch
                    if len(buf) == 2:
                        break
                day = buf

            # Get the time
            if row['class'][0] == 'odd-time':
                t = row.find('span', {'class':'statusOpen'})
                # Games with Red time header have 'statusClose' class and don't have ML's
                if t is None:
                    continue
                time = parse_time_string(t.text)

            # Get the team + odds from the row
            if row['class'][0] == 'odd-info-teams':
                # the <span> tags look like '905 Rockies' so remove the number to get the team
                team_name = fix_name(row.find('span', {'class':'team-name'}).text.split(' ', 1)[1])
                
                three_odds = row.find_all('div', {'class': 'col-md-2'})
                try:
                    if 'EV' in three_odds[2].text:
                        ml = to_decimal(100)
                    else:
                        ml = to_decimal(int(three_odds[2].text))
                except:
                    continue

                if is_first_team:
                    first_teams.append(team_name)
                    first_odds.append(ml)
                    game_days.append(day)
                    game_times.append(time)
                    is_first_team = False
                else:
                    second_teams.append(team_name)
                    second_odds.append(ml)
                    is_first_team = True
                    
        else:
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
    if time[-2:] == 'PM':
        hh = str(int(hh) + 12)
    
    return hh + ':' + mm

if __name__ == '__main__':
    scrape()