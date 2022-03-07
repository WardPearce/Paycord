import stripe
import os

stripe.api_key = os.environ["STRIPE_API_KEY"]


__all__ = ["stripe"]
