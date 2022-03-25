import os
from currency_symbols import CurrencySymbols


DISCORD_API_URL = os.environ["DISCORD_API_URL"]
CURRENCY = os.environ["CURRENCY"]
CURRENCY_SYMBOL = CurrencySymbols.get_symbol(CURRENCY)
PAGE_NAME = os.environ["PAGE_NAME"]
LOGO_URL = os.environ["LOGO_URL"]
ROOT_DISCORD_IDS = os.environ["ROOT_DISCORD_IDS"].split(",")
SUBSCRIPTION_RECURRENCE = os.environ["SUBSCRIPTION_RECURRENCE"]
SUBSCRIPTION_INTERVAL = int(os.environ["SUBSCRIPTION_INTERVAL"])
MONTHLY_GOAL = float(os.environ["MONTHLY_GOAL"])
MONTHLY_GOAL_PARAGRAPH = os.environ["MONTHLY_GOAL_PARAGRAPH"]
THIRD_PARTY_MODULES = os.environ["THIRD_PARTY_MODULES"].split(",")
DISCORD_HEADER = {
    "Authorization": f"Bot {os.environ['DISCORD_BOT_TOKEN']}"
}
