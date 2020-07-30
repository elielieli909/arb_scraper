import numpy as np
import pandas as pd

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from .ml_to_decimal import to_decimal

def fix_name(name):
    r = name
    r = r.replace('Chi White Sox', 'Chicago White Sox')
    r = r.replace('COLORADO', 'Colorado Rockies')
    r = r.replace('OAKLAND', 'Oakland Athletics')
    r = r.replace('ARIZONA', 'Arizona Diamondbacks')
    r = r.replace('TEXAS', 'Texas Rangers')
    r = r.replace('CHI WHITE SOX', 'Chicago White Sox')
    r = r.replace('CLEVELAND', 'Cleveland Indians')
    r = r.replace('WASHINGTON', 'Washington Nationals')
    r = r.replace('TORONTO', 'Toronto Blue Jays')
    r = r.replace('CHICAGO CUBS', 'Chicago Cubs')
    r = r.replace('CINCINNATI', 'Cincinnati Reds')
    r = r.replace('MILWAUKEE', 'Milwaukee Brewers')
    r = r.replace('PITTSBURGH', 'Pittsburgh Pirates')
    r = r.replace('BOSTON', 'Boston Red Sox')
    r = r.replace('NY METS', 'New York Mets')
    r = r.replace('TAMPA BAY', 'Tampa Bay Rays')
    r = r.replace('ATLANTA', 'Atlanta Braves')
    r = r.replace('KANSAS CITY', 'Kansas City Royals')
    r = r.replace('DETROIT', 'Detroit Tigers')
    r = r.replace('ST. LOUIS', 'St. Louis Cardinals')
    r = r.replace('MINNESOTA', 'Minnesota Twins')
    r = r.replace('SAN DIEGO', 'San Diego Padres')
    r = r.replace('SAN FRANCISCO', 'San Francisco Giants')
    r = r.replace('SEATTLE', 'Seattle Mariners')
    r = r.replace('LA ANGELS', 'Los Angeles Angels')
    r = r.replace('LA DODGERS', 'Los Angeles Dodgers')
    r = r.replace('HOUSTON', 'Houston Astros')
    r = r.replace('NY YANKEES', 'New York Yankees')
    r = r.replace('BALTIMORE', 'Baltimore Orioles')

    return r

def scrape():
    # URL OF THE SITE WE'RE SCRAPING
    url = 'https://www.gtbets.eu/wagering1.asp?mode=lines'

    # Setup selenium
    options = Options()
    options.headless = True
    options.add_argument('log-level=3')
    browser = webdriver.Chrome(options=options)

    # Initialize lists for dataframe
    first_teams = []
    first_odds = []
    second_teams = []
    second_odds = []
    game_days = []

    try:
        # Get GT Bets
        browser.get(url)
        browser.implicitly_wait(5)

        # START WITH LIVE GAMES ==============================================================
        try:
            live_bucket = browser.find_element_by_class_name('events-collection-live')

            live_games = live_bucket.find_elements_by_class_name('wagering-event-main')
            for game in live_games:
                teams = game.find_elements_by_class_name('wagering-event-team')
                lines = game.find_elements_by_class_name('wagering-event-money')

                first_teams.append(fix_name(teams[0].text))
                first_odds.append(to_decimal(int(lines[0].text)))
                second_teams.append(fix_name(teams[1].text))
                second_odds.append(to_decimal(int(lines[1].text)))
                game_days.append('LIVE')
        except Exception as e:
            print('Issue getting GT Bets live games: ', e)

        # Now do next events ==================================================================
        next_bucket = browser.find_element_by_class_name('events-collection-main')
        date = next_bucket.find_element_by_class_name('wagering-event-date').text.split(' ')[1][:-1]

        next_games = next_bucket.find_elements_by_class_name('wagering-event-main')
        for game in next_games:
            teams = game.find_elements_by_class_name('wagering-event-team')
            lines = game.find_elements_by_class_name('wagering-event-money')

            first_teams.append(fix_name(teams[0].text.split('\n')[0]))
            first_odds.append(to_decimal(int(lines[0].text)))
            second_teams.append(fix_name(teams[1].text.split('\n')[0]))
            second_odds.append(to_decimal(int(lines[1].text)))
            game_days.append(date)
            


    except Exception as e:
        print('Something went wrong: ' + str(e))
        browser.quit()

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