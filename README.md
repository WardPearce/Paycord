# Welcome to Paycord
Paycord allows you to charge Discord users for Discord roles, Paycord is also hackable with a custom event system. The codebase it a bit messy (mainly because I find flask messy.) Built using Docker, Stripe, Flask & Mongo.

## Setup
### Production
- On stripe dashboard, go Developers ➡️ Webhooks ➡️ Add endpoint ➡️ endpoint URL ➡️ "myUrlHere/event" ➡️ "checkout.session.completed" & "customer.subscription.deleted" events required.
- On stripe dashboard, go Settings ➡️ Customer portal ➡️ Ensure "Update subscriptions" is all disabled ➡️ then update your "Business information"
- On discord developer portal, go OAuth2 ➡️ General ➡️ Redirects ➡️ "myUrlHere/discord/authorize".
- Invite discord bot to guild.
- Download `docker-compose.yml`
- `sudo docker-compose build; sudo docker-compose up -d`
- Proxy exposed port.
- Ensure Discord roles for products is below Discord bot.
### Development
- Git clone this repo.
- `pip3 install -r requirements.txt`
- export environment variables in CLI.
- Run mongodb server.
- `python main.py` to run dev server.

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
- MONTHLY_GOAL_PARAGRAPH - optional, by default `"The goal below indicates how much our services cost a month to run.\nYou can help support our service by purchasing one of the packages below."`
- CURRENCY - optional, by default `"USD"` ([Supported currencies](https://stripe.com/docs/currencies))
- DISCORD_API_URL - optional, by default `"https://discord.com/api"`
- LOGO_URL - optional, by default `"https://i.imgur.com/d5SBQ6v.png"`
- PAGE_NAME - optional, by default `"Paycord"`
- SUBSCRIPTION_RECURRENCE - optional, by default `"month"` ([Supported recurrences](https://stripe.com/docs/api/prices/object#price_object-recurring))
- SUBSCRIPTION_INTERVAL - optional, by default `1`
- DISCORD_WEBHOOK - optional, by default disabled
    - Provide a discord webhook to push alerts for new & cancelled subscriptions.
- MONGO_IP - optional, by default `"localhost"`
- MONGO_PORT - optional, by default `27017`
- MONGO_DB - optional, by default `"paycord"`
- THIRD_PARTY_MODULES - optional, by default `"paycord.built_ins.discord"`
    - Third party modules to run on subscription events, currently look at [paycord/built_ins/discord.py](/paycord/built_ins/discord.py) for a example.
    - Separate modules with `,` e.g. `module.file,module.file`

## TODOs
- Allow one package to have multiple roles.
- Form validation for root users (Didn't think this was super important, but would be nice to implement with wtforms.)

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
