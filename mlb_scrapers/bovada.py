from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

import numpy as np
import pandas as pd

from .ml_to_decimal import to_decimal

# Dynamic site, needs selenium
def scrape():
    # URL OF THE SITE WE'RE SCRAPING
    bovada_url = 'https://www.bovada.lv/sports/baseball'

    # Setup selenium
    options = Options()
    options.headless = True
    options.add_argument('log-level=3')
    browser = webdriver.Chrome(options=options)

    try:
        # Get Bovada
        browser.get(bovada_url)
        browser.implicitly_wait(5)

        # Grab by bucket to separate live and upcoming games
        next_events_bucket = browser.find_element_by_class_name('next-events-bucket')

        # Initialize lists for dataframe
        first_teams = []
        first_odds = []
        second_teams = []
        second_odds = []
        game_days = []
        game_times = []

        # START WITH LIVE GAMES ================================================================================================================

        # Grab by bucket to separate live and upcoming games
        try:
            live_bucket = browser.find_element_by_class_name('happening-now-bucket')
            all_events = live_bucket.find_elements_by_class_name('coupon-content')

            for event in all_events:
                players = event.find_elements_by_class_name('name')
                moneylines = event.find_elements_by_class_name('bet-price')

                # matchup = {}
                is_first = True
                j = 0
                for i in range(len(players)):
                    if j > i + 3:
                        j = i
                    while moneylines[j].text[0] == '(':
                        j += 1
                    if is_first:
                        first_teams.append(players[i].text)
                        if moneylines[j].text == 'EVEN':
                            first_odds.append(2.0)
                        else:
                            first_odds.append(to_decimal(int(moneylines[j].text)))
                        is_first = False
                    else:
                        second_teams.append(players[i].text)
                        if moneylines[j].text == 'EVEN':
                            second_odds.append(2.0)
                        else:
                            second_odds.append(to_decimal(int(moneylines[j].text)))
                    j += 1

                game_days.append('LIVE')
        except Exception as e:
            print('Issue getting live Bovada games: ', e)
            

        # Now Do NEXT EVENTS ================================================================================================================
        event_groups = next_events_bucket.find_elements_by_class_name('grouped-events')
        for group in event_groups:
            # Skip the Series winner bets
            group_header = group.find_element_by_class_name('league-header-collapsible__description')
            if 'Series Prices' in group_header.text:
                continue

            # Grab all the matchup boxes
            all_events = group.find_elements_by_class_name('coupon-content')

            for event in all_events:
                players = event.find_elements_by_class_name('name')
                moneylines = event.find_elements_by_xpath(".//*[@class='bet-price' or @class='empty-bet']")

                # matchup = {}
                is_first = True
                includes_empty_ml = False
                for i in range(len(players)):
                    if is_first:
                        if moneylines[2].text == 'EVEN':
                            first_odds.append(2.0)
                            first_teams.append(players[i].text)
                        elif moneylines[2].get_attribute('class') == 'empty-bet':
                            includes_empty_ml = True
                        else:
                            first_odds.append(to_decimal(int(moneylines[2].text)))
                            first_teams.append(players[i].text)
                        is_first = False
                    else:
                        if moneylines[3].text == 'EVEN':
                            second_odds.append(2.0)
                            second_teams.append(players[i].text)
                        elif moneylines[3].get_attribute('class') == 'empty-bet':
                            includes_empty_ml = True
                        else:
                            second_odds.append(to_decimal(int(moneylines[3].text)))
                            second_teams.append(players[i].text)

                if includes_empty_ml:
                    continue

                date = event.find_element_by_class_name('period')
                time = date.find_element_by_class_name('clock')

                try:
                    # Parse just the Day from the entire "7/26/20 2:00 AM" string
                    entire_date = date.get_attribute("innerText")
                    on_day = False
                    day = ''
                    for ch in entire_date:
                        if ch == '/':
                            on_day = not on_day
                            continue
                        if on_day:
                            day += ch
                    game_days.append(day)

                    # Get the time as well
                    game_times.append(parse_time_string(time.get_attribute("innerText")[1:]))

                except Exception as e:
                    print(e)
                    game_days.append('idk')

        df = pd.DataFrame({
            'Team 1': first_teams, 
            'Team 1 ML': first_odds, 
            'Team 2': second_teams,
            'Team 2 ML': second_odds,
            'Game Date': game_days,
            # 'Time' : game_times
        })

        browser.quit()
    except Exception as e:
        print('Something went wrong: ' + str(e))
        browser.quit()

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
    
    if time[-2:] == 'PM' and hh != '12':
        hh = str(int(hh) + 12)
    if time[-2:] == 'AM' and hh == '12':
        hh = '0'
    
    return hh + ':' + mm

if __name__ == '__main__':
    scrape()