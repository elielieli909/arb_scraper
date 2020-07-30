Program structure:

All scrapers working in parallel, saving data in mutex-locked databases.  Main script will constantly look at these databases to try and find arb opportunities. 

Scraper:
    Goes to specific site, (i.e. MLB baseball), scrapes, saves (Team1, Team2, ML1, ML2) in the table.  Games like soccer can have (Team1, Team2, Draw, ML1, ML2, ML3).  Can be extended to any n outcomes with n ML's.  Repeat every 15 seconds or so.

    RETURNS: A List of PACKET's.  Each PACKET represents a matchup on the page

Matcher:
    Go through tables, look for identical games, make an algorithm to find best odds and determine if its an arbitrage opportunity, as well as optimal bet sizes.  Can be threaded (think of them scanning DB's like a ribbon).  If an arb opportunity is found, use telnet to send a text to 4152794558 with the teams, odds, bet amounts, books, and links to the books (maybe can be automated eventually)


Data will look like:

PACKET:

    TEAM 1      MONEYLINE
    TEAM 2      MONEYLINE

MAIN STATE:

    TEAM 1      BEST MONEYLINE
    TEAM 2      BEST MONEYLINE

    TEAM 3      BEST MONEYLINE
    TEAM 4      BEST MONEYLINE

    ...         ...

For every packet that comes in, check if that matchup is already in the main state.  If it is, update the best moneyline. 




