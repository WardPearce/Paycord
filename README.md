# Setup
- On stripe dashboard, go Developers ➡️ Webhooks ➡️ Add endpoint ➡️ endpoint URL ➡️ "myUrlHere/event" ➡️ "checkout.session.completed" & "customer.subscription.deleted" events required.
- On stripe dashboard, go Settings ➡️ Customer portal ➡️ Ensure "Update subscriptions" is all disabled ➡️ then update your "Business information"
- On discord developer portal, go OAuth2 ➡️ General ➡️ Redirects ➡️ "myUrlHere/discord/authorize".
- Invite discord bot to guild.
- `docker pull wardpearce/paycord`
- `sudo docker run -d -p 56733:80 --name paycord -v $PWD:/app -e DISCORD_CLIENT_ID="..." -e DISCORD_CLIENT_SECRET="..." -e DISCORD_BOT_TOKEN="..." -e DISCORD_GUILD_ID="..." -e ROOT_DISCORD_IDS="...,..." -e STRIPE_WEBHOOK_SECRET="..." -e STRIPE_API_KEY="..." wardpearce/paycord`
- Proxy exposed port.
