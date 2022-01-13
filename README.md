# Welcome to Paycord
Paid roles for discord using Stripe, Python, Flask & Docker.

## Setup
### Production
- On stripe dashboard, go Developers ➡️ Webhooks ➡️ Add endpoint ➡️ endpoint URL ➡️ "myUrlHere/event" ➡️ "checkout.session.completed" & "customer.subscription.deleted" events required.
- On stripe dashboard, go Settings ➡️ Customer portal ➡️ Ensure "Update subscriptions" is all disabled ➡️ then update your "Business information"
- On discord developer portal, go OAuth2 ➡️ General ➡️ Redirects ➡️ "myUrlHere/discord/authorize".
- Invite discord bot to guild.
- `sudo docker pull wardpearce/paycord`
- `sudo docker run -d -p 56733:80 --name paycord -v $PWD:/app -e DISCORD_CLIENT_ID="..." -e DISCORD_CLIENT_SECRET="..." -e DISCORD_BOT_TOKEN="..." -e DISCORD_GUILD_ID="..." -e ROOT_DISCORD_IDS="...,..." -e STRIPE_WEBHOOK_SECRET="..." -e STRIPE_API_KEY="..." wardpearce/paycord`
- Proxy exposed port.
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
- `python app.py` to run.

## Docker parameters
- DISCORD_CLIENT_ID - required
- DISCORD_CLIENT_SECRET - required
- DISCORD_BOT_TOKEN - required
- DISCORD_GUILD_ID - required
- ROOT_DISCORD_IDS - required
- STRIPE_WEBHOOK_SECRET - required
- STRIPE_API_KEY - required
- CURRENCY - optional, by default "USD" [Supported currencies](https://stripe.com/docs/currencies)
- DISCORD_API_URL - optional, by default "https://discord.com/api"

## TODOs
- Allow one package to have multiple roles.
- Form validation for root users (Didn't think this was super important, but would be nice to implement with wtforms.)
- Allow upgrading of packages.
- Maybe move away from `tinydb` to `mongodb`.

## Screenshots
![screenshot 1](https://cdn.discordapp.com/attachments/927646781670576259/931081467956719676/unknown.png)
![screenshot 2](https://cdn.discordapp.com/attachments/927646781670576259/931081556905312276/unknown.png)
![screenshot 3](https://cdn.discordapp.com/attachments/927646781670576259/931081819548450826/unknown.png)