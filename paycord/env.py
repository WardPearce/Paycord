import os
from currency_symbols import CurrencySymbols


DISCORD_API_URL = os.getenv("DISCORD_API_URL", "https://discord.com/api")
CURRENCY = os.getenv("CURRENCY", "USD")
CURRENCY_SYMBOL = CurrencySymbols.get_symbol(CURRENCY)
PAGE_NAME = os.getenv("PAGE_NAME", "Paycord")
LOGO_URL = os.getenv("LOGO_URL", "https://i.imgur.com/d5SBQ6v.png")
ROOT_DISCORD_IDS = os.environ["ROOT_DISCORD_IDS"].split(",")
SUBSCRIPTION_RECURRENCE = os.getenv("SUBSCRIPTION_RECURRENCE", "month")
SUBSCRIPTION_INTERVAL = int(os.getenv("SUBSCRIPTION_INTERVAL", 1))
MONTHLY_GOAL = float(os.getenv("MONTHLY_GOAL", 0.0))
MONTHLY_GOAL_PARAGRAPH = os.getenv(
    "MONTHLY_GOAL_PARAGRAPH",
    ("The goal below indicates how much our services cost a month to run.\nYou "  # noqa: E501
     "can help support our service by purchasing one of the packages below.")
)
THIRD_PARTY_MODULES = os.getenv(
    "THIRD_PARTY_MODULES", "app.built_ins.discord"
).split(",")
DISCORD_HEADER = {
    "Authorization": f"Bot {os.environ['DISCORD_BOT_TOKEN']}"
}
