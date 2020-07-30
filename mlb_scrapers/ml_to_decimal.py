# Accepts US Moneyline odds (-175, +225, etc.) as int and returns decimal odds (as float)
def to_decimal(odds):
    odds = max((odds / 100) + 1, (100 / -odds) + 1)
    return odds