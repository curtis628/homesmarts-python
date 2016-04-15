#!/usr/bin/env python

"""
homesmarts.publish
~~~~~~~~~~~~~

This module is helpful for publishing test messages to the RabbitMQ exchange
(to simulate a Dash button being pushed).

Usage: ./homesmarts/publish.py Dash-LivingRoom "Button pushed"
"""

import argparse

from config import init
from messaging import publish_message

if __name__ == "__main__":
    config = init()

    parser = argparse.ArgumentParser(description="Publishes a provided 'message' from the provided 'dash_id'")
    parser.add_argument("dash_id", help="the Dash button's identifier", choices=config.dash_ids)
    parser.add_argument("message", help="the content of the message to publish")
    args = parser.parse_args()

    publish_message(args.dash_id, args.message)