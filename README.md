# Welcome to Paycord
Paid roles for discord using Stripe, Python, Flask & Docker.

## Setup
### Production
- On stripe dashboard, go Developers ➡️ Webhooks ➡️ Add endpoint ➡️ endpoint URL ➡️ "myUrlHere/event" ➡️ "checkout.session.completed" & "customer.subscription.deleted" events required.
- On stripe dashboard, go Settings ➡️ Customer portal ➡️ Ensure "Update subscriptions" is all disabled ➡️ then update your "Business information"
- On discord developer portal, go OAuth2 ➡️ General ➡️ Redirects ➡️ "myUrlHere/discord/authorize".
- Invite discord bot to guild.
- Git clone this repo
- sudo docker-compose build; sudo docker-compose up -d
- Proxy exposed port.
- Ensure Discord roles for products is below Discord bot.
### Development
- Git clone this repo.
- `pip3 install -r requirements.txt`
- export environment variables in CLI.
```
export DISCORD_CLIENT_ID="..."
export DISCORD_CLIENT_SECRET="..."
export DISCORD_BOT_TOKEN="..."
export DISCORD_GUILD_ID="..."
export ROOT_DISCORD_IDS="...,..."
export STRIPE_WEBHOOK_SECRET="..."
export STRIPE_API_KEY="..."
```
- Run mongodb server.
- `python app.py` to run.

## Environment variables
- DISCORD_CLIENT_ID - required
    - Client ID of OAuth2 from Discord developer portal
- DISCORD_CLIENT_SECRET - required
    - Client Secret of OAuth2 from Discord developer portal
- DISCORD_BOT_TOKEN - required
    - Bot token from Discord developer portal
- DISCORD_GUILD_ID - required
    - Enable developer mode & provide the ID for the guild.
- ROOT_DISCORD_IDS - required
    - Comma separated list of Discord user IDs who can add & remove products.
- STRIPE_WEBHOOK_SECRET - required
- STRIPE_API_KEY - required
- MESSAGE_ON_COMPLETE - optional, by default `"Thank you {username} for subscribing to {name} for {currency_symbol}{price}"`
    - Leave as blank ("") to disable.
    - **Supported parameters**
        - id
            - User's discord snowflake ID.
        - username
            - User's discord username.
        - avatar
            - User's avatar hash.
        - discriminator
            - User's discriminator.
        - public_flags
            - User's pubic flags.
        - product_id
            - ID of product brought
        - name
            - Name of product brought.
        - price
            - Price of product brought.
        - description
            - Description of product brought.
        - role_id
            - Role ID of product brought.
        - currency
            - Currency of product.
        - currency_symbol
            - Symbol of currency.
- MONTHLY_GOAL - optional, by default `0.0` (Disabled)
- CURRENCY - optional, by default `"USD"` ([Supported currencies](https://stripe.com/docs/currencies))
- DISCORD_API_URL - optional, by default `"https://discord.com/api"`
- LOGO_URL - optional, by default `"https://i.imgur.com/d5SBQ6v.png"`
- PAGE_NAME - optional, by default `"Paycord"`
- SUBSCRIPTION_RECURRENCE - optional, by default `"month"` ([Supported recurrences](https://stripe.com/docs/api/prices/object#price_object-recurring))
- SUBSCRIPTION_INTERVAL - optional, by default `1`
- MONGO_IP - optional, by default `"localhost"`
- MONGO_PORT - optional, by default `27017`
- MONGO_DB - optional, by default `"paycord"`

## TODOs
- Allow one package to have multiple roles.
- Form validation for root users (Didn't think this was super important, but would be nice to implement with wtforms.)
- Allow upgrading of packages.

## Screenshots
![Screenshot 1](https://i.imgur.com/brlMepv.png)
![Screenshot 2](https://i.imgur.com/vVxEAp2.png)
![Screenshot 3](https://i.imgur.com/qY8AGHQ.png)

## Thanks to
- [Flask](https://pypi.org/project/Flask/) by Armin Ronacher
- [Werkzeug](https://pypi.org/project/Werkzeug/) by Armin Ronacher
- [Jinja](https://pypi.org/project/Jinja/) by Armin Ronacher
- [itsdangerous](https://pypi.org/project/itsdangerous/) by Armin Ronacher
- [click](https://pypi.org/project/click/) by Armin Ronacher
- [stripe](https://pypi.org/project/stripe/) by Stripe
- [Authlib](https://pypi.org/project/Authlib/) by Hsiaoming Yang
- [cryptography](https://pypi.org/project/cryptography/) by The Python Cryptographic Authority and individual contributors
- [requests](https://pypi.org/project/requests/) by Kenneth Reitz
- [certifi](https://pypi.org/project/certifi/) by Kenneth Reitz
- [currency-symbols](https://pypi.org/project/currency-symbols/) by Arshad Kazmi
- [pymongo](https://pypi.org/project/pymongo/) by The MongoDB Python Team
