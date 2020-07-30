import numpy as np
import pandas as pd
from requests import get
import cloudscraper
from bs4 import BeautifulSoup

from .ml_to_decimal import to_decimal

def scrape():
    # URL OF THE SITE WE'RE SCRAPING
    betonline_url = 'https://www.betonline.ag/sportsbook/baseball/mlb'

    # To bypass Cloudflare anti-DDOS protection, use cloudscraper
    scraper = cloudscraper.create_scraper()
    res = scraper.get(betonline_url)
    html_soup = BeautifulSoup(res.text, 'html.parser')

    # Initialize lists for dataframe
    first_teams = []
    first_odds = []
    second_teams = []
    second_odds = []
    game_days = []


    events_table = html_soup.find('table', {'id': 'contestDetailTable'}).find_all('tbody')
    day = ''
    for tbody in events_table:
        # A 'date' class <tbody> should come before an 'event' class <tbody>, so we should know the day of all games
        if tbody['class'][0] == 'date':
            date = tbody.find('td').text

            day = ''
            got_day_char = False
            # date = 'Saturday, Jul 25, 2020 - MLB Baseball Game' we just want the 25
            for ch in date:
                if ch.isdigit():
                    got_day_char = True
                    day += ch

                if got_day_char and ch == ',': 
                    break
        elif tbody['class'][0] == 'event':
            # Should be 2 teams and 2 lines
            team_elems = tbody.findChildren('td', {'class': 'col_teamname bdevtt'})
            line_elems = tbody.findChildren('td', {'class': 'odds bdevtt moneylineodds displayOdds'})

            if len(team_elems) == 0:
                continue

            is_first = True
            for i in range(len(team_elems)):
                if is_first:
                    first_teams.append(team_elems[i].text[:-1]) # On this site teams are like 'SF Giants ' so we remove the space at the end w [:-1]
                    first_odds.append(to_decimal(int(line_elems[i].text)))
                    is_first = False
                else:
                    second_teams.append(team_elems[i].text[:-1]) # On this site teams are like 'SF Giants ' so we remove the space at the end w [:-1]
                    second_odds.append(to_decimal(int(line_elems[i].text)))
                    is_first = False
                # Add date here\
            game_days.append(day)

        # data.append(matchup)

    df = pd.DataFrame({
        'Team 1': first_teams, 
        'Team 1 ML': first_odds, 
        'Team 2': second_teams,
        'Team 2 ML': second_odds,
        'Game Date': game_days
    })

    return df