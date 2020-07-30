import pandas as pd
import numpy as np
from datetime import datetime

import keyboard

from twilio.rest import Client # To Send me texts when there's an arb

from mlb_scrapers import betonline, bovada, mybookie, pinnacle, fivedimes, betnow, gtbets


def update_odds(db, scraped_row, source_site):
    # row['Team 1'], row['Team 1 ML'], row['Team 2'], row['Team 2 ML'], row['Game Date'],
    not_there = True
    for index, db_row in db.iterrows():
        # print(row['Team 1'], row['Team 1 ML'], row['Team 2'], row['Team 2 ML'], row['Game Date'])
        # Matchup exists in DB
        if db_row['Game Date'] == scraped_row['Game Date']:
            if db_row['Team 1'] == scraped_row['Team 1'] and db_row['Team 2'] == scraped_row['Team 2']:
                not_there = False
                # Update the odds
                if scraped_row['Team 1 ML'] > db_row['Team 1 ML']:
                    db.at[index, 'Team 1 ML'] = scraped_row['Team 1 ML']
                    db.at[index, 'Source 1'] = source_site

                if scraped_row['Team 2 ML'] > db_row['Team 2 ML']:
                    db.at[index, 'Team 2 ML'] = scraped_row['Team 2 ML']
                    db.at[index, 'Source 2'] = source_site

            elif db_row['Team 1'] == scraped_row['Team 2'] and db_row['Team 2'] == scraped_row['Team 1']:
                not_there = False
                # Update the odds
                if scraped_row['Team 1 ML'] > db_row['Team 2 ML']:
                    db.at[index, 'Team 2 ML'] = scraped_row['Team 1 ML']
                    db.at[index, 'Source 2'] = source_site

                if scraped_row['Team 2 ML'] > db_row['Team 1 ML']:
                    db.at[index, 'Team 1 ML'] = scraped_row['Team 2 ML']
                    db.at[index, 'Source 1'] = source_site

    # Matchup doesn't exist yet in DB; add it
    if not_there:
        # Credit the sportsbook and add to db
        scraped_row['Source 1'] = source_site
        scraped_row['Source 2'] = source_site
        db = db.append(scraped_row)
        # Clear the indexes of each row and give them new ones (scraped_row has index from scraped_table)
        db.reset_index()
        db.index = range(0,len(db))

    return db

def decimal_to_american(odds):
    if odds < 2:
        return (-100 / (odds - 1))
    else:
        return 100 * (odds - 1)

# Dollars
BETSIZE = 100
def check_for_arbs(db):
    for index, row in db.iterrows():
        implied_odds = (1/row['Team 1 ML']) + (1/row['Team 2 ML'])
        # print(implied_odds)
        if implied_odds < 1:
            print(row)
            team_1_bet = ( row['Team 2 ML'] * BETSIZE ) / (row['Team 1 ML'] + row['Team 2 ML'])
            team_2_bet = 100 - team_1_bet
            pct_return = (row['Team 1 ML'] * team_1_bet) - BETSIZE
            print('Bet {0} on team 1, {1} on team 2, for a return of {2}', team_1_bet, team_2_bet, pct_return)

            # Text me!
            message = """
Bet 1:
{} @ {} 
vs. 
{} @ {}
Game Day: {}
{}: ${} on {}
{}: ${} on {}
Percent Return: {}
            """.format(row['Team 1'].split(' ')[0], decimal_to_american(row['Team 1 ML']),
                        row['Team 2'].split(' ')[0], decimal_to_american(row['Team 2 ML']), 
                        row['Game Date'],
                        row['Source 1'], str(team_1_bet)[:5], row['Team 1'].split(' ')[0],
                        row['Source 2'], str(team_2_bet)[:5], row['Team 2'].split(' ')[0],
                        str(pct_return)[:4])
            client = Client("AC180fd60368653033809f04f22c6876bf", "2100f6d0b582768c7e83205950281dc4")
            client.messages.create(to="+14152794558", 
                        from_="+12568263331", 
                        body=message)

if __name__ == "__main__":
    print('ELI!!! ARE YOU USING A VPN??????????\n\nIf you are, press \'b\'.')
    while True:
        a = keyboard.read_key()
        if a == 'b':
            break

    print('Starting...')


    while True:
        db = pd.DataFrame(columns=['Team 1', 'Team 1 ML', 'Source 1', 'Team 2', 'Team 2 ML', 'Source 2', 'Game Date'])

        # Scrape the sites
        scraped_data = betonline.scrape()  # same form as above
        # Add the scraped odds to the tables
        for index, row in scraped_data.iterrows():
            # db = db.append(row)
            db = update_odds(db, row, 'BetOnline')

        scraped_data = mybookie.scrape()  # same form as above
        # Add the scraped odds to the tables
        for index, row in scraped_data.iterrows():
            # db = db.append(row)
            db = update_odds(db, row, 'MyBookie')

        scraped_data = fivedimes.scrape()  # same form as above
        # Add the scraped odds to the tables
        for index, row in scraped_data.iterrows():
            # db = db.append(row)
            db = update_odds(db, row, '5dimes')

        scraped_data = betnow.scrape()  # same form as above
        # Add the scraped odds to the tables
        for index, row in scraped_data.iterrows():
            # db = db.append(row)
            db = update_odds(db, row, 'BetNow')

        try:
            scraped_data = bovada.scrape()  # same form as above
            # Add the scraped odds to the tables
            for index, row in scraped_data.iterrows():
                # db = db.append(row)
                db = update_odds(db, row, 'Bovada')
        except:
            # TODO: Except whatever exceptions there are.  I guess sometimes the best way might be just reload the page.
            print('Bovada fucked up.')

        try:
            scraped_data = gtbets.scrape()  # same form as above
            # Add the scraped odds to the tables
            for index, row in scraped_data.iterrows():
                # db = db.append(row)
                db = update_odds(db, row, 'GT Bets')
        except:
            # TODO: Except whatever exceptions there are.  I guess sometimes the best way might be just reload the page.
            print('GT Bets fucked up.')


        # PINNACLE NOT AVAILABLE IN THE US :(
        # try:
        #     scraped_data = pinnacle.scrape()  # same form as above
        #     # Add the scraped odds to the tables
        #     for index, row in scraped_data.iterrows():
        #         # db = db.append(row)
        #         db = update_odds(db, row, 'Pinnacle')
        # except:
        #     # TODO: Except whatever exceptions there are.  I guess sometimes the best way might be just reload the page.
        #     print('Pinnacle fucked up.')

        with pd.option_context('display.max_rows', None):  # more options can be specified also
            print(db)
            print("""
                \nDATABASE LAST UPDATED @: %s
            """ % datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

        check_for_arbs(db)


