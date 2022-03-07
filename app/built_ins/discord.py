import os
import requests

from discord_webhook import DiscordWebhook, DiscordEmbed
from typing import Any


from ..env import (
    DISCORD_HEADER, DISCORD_API_URL,
    CURRENCY, CURRENCY_SYMBOL,
    PAGE_NAME, LOGO_URL
)

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", None)
MESSAGE_ON_COMPLETE = os.getenv(
    "MESSAGE_ON_COMPLETE",
    "Thank you {username} for subscribing to {name} for {currency_symbol}{price}"  # noqa: E501
)


def run_on_complete(product: dict, subscription: Any) -> None:
    metadata = subscription.metadata

    if MESSAGE_ON_COMPLETE:
        channel = requests.post(
            f"{DISCORD_API_URL}/users/@me/channels",
            json={"recipient_id": metadata["discord_id"]},
            headers=DISCORD_HEADER
        )
        if channel.status_code == 200:
            channel_data = channel.json()
            requests.post(
                (f"{DISCORD_API_URL}/channels/{channel_data['id']}"
                    "/messages"),
                json={
                    "content": MESSAGE_ON_COMPLETE.format_map(
                        {
                            **channel_data["recipients"][0],
                            **product,
                            "currency": CURRENCY,
                            "currency_symbol": CURRENCY_SYMBOL
                        }
                    )
                },
                headers=DISCORD_HEADER
            )

    if DISCORD_WEBHOOK:
        price_in_dollars = subscription["amount_total"] * 0.01

        embed = DiscordEmbed(
            title=f"New subscription for {PAGE_NAME}",
            description=(f"<@{metadata['discord_id']}> subscribed to"
                         f" **{product.get('name', '**Deleted**')}**"
                         f" *({metadata['product_id']})*"
                         f" for **{CURRENCY_SYMBOL}{price_in_dollars}**"
                         f"\n\nRole <@&{metadata['role_id']}> added"),
            color="4ee51b"
        )
        embed.set_author(name=PAGE_NAME)
        embed.set_thumbnail(url=LOGO_URL)
        embed.set_timestamp()

        webhook = DiscordWebhook(url=DISCORD_WEBHOOK)
        webhook.add_embed(embed)
        webhook.execute()


def run_on_delete(product: dict, subscription: Any) -> None:
    if DISCORD_WEBHOOK:
        embed = DiscordEmbed(
            title=f"Subscription cancelled for {PAGE_NAME}",
            description=(f"<@{subscription['discord_id']}> unsubscribed to"
                         f" **{product.get('name', '**Deleted**')}**"
                         f" *({product.get('product_id', '**Deleted**')})*"
                         f"\n\nRole <@&{subscription['role_id']}> removed"
                         ),
            color="e5301b"
        )
        embed.set_author(name=PAGE_NAME)
        embed.set_thumbnail(url=LOGO_URL)
        embed.set_timestamp()

        webhook = DiscordWebhook(url=DISCORD_WEBHOOK)
        webhook.add_embed(embed)
        webhook.execute()
