# Welcome to Paycord
Paycord allows you to charge Discord users for Discord roles, Paycord is also hackable with a custom event system. The codebase it a bit messy (mainly because I find flask messy.) Built using Docker, Stripe, Flask & Mongo.

## Previews
![Screenshot 1](https://i.imgur.com/brlMepv.png)
![Screenshot 2](https://i.imgur.com/vVxEAp2.png)
![Screenshot 3](https://i.imgur.com/qY8AGHQ.png)

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

## Third-party modules
(Submit a PR to add your third-party module)
- TBD

## Environment variables
- DISCORD_CLIENT_ID
    - Client ID of OAuth2 from Discord developer portal
- DISCORD_CLIENT_SECRET
    - Client Secret of OAuth2 from Discord developer portal
- DISCORD_BOT_TOKEN
    - Bot token from Discord developer portal
- DISCORD_GUILD_ID
    - Enable developer mode & provide the ID for the guild.
- ROOT_DISCORD_IDS
    - Comma separated list of Discord user IDs who can add & remove products.
- STRIPE_WEBHOOK_SECRET
- STRIPE_API_KEY
- MESSAGE_ON_COMPLETE
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
- MONTHLY_GOAL
- MONTHLY_GOAL_PARAGRAPH
- CURRENCY - ([Supported currencies](https://stripe.com/docs/currencies))
- DISCORD_API_URL
- LOGO_URL
- PAGE_NAME
- SUBSCRIPTION_RECURRENCE - ([Supported recurrences](https://stripe.com/docs/api/prices/object#price_object-recurring))
- SUBSCRIPTION_INTERVAL
- DISCORD_WEBHOOK
    - Provide a discord webhook to push alerts for new & cancelled subscriptions.
- MONGO_IP
- MONGO_PORT
- MONGO_DB
- THIRD_PARTY_MODULES
    - Third party modules to run on subscription events, currently look at [paycord/built_ins/discord.py](/paycord/built_ins/discord.py) for a example.
    - Separate modules with `,` e.g. `module.file,module.file`

## TODOs
- Allow one package to have multiple roles.
- Form validation for root users (Didn't think this was super important, but would be nice to implement with wtforms.)

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
