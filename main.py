import asyncio
import logging
import logging.config

from api.discord_api_client import DiscordApiClient
from bot_secrets import BOT_TOKEN
from websocket_client import WebsocketClient


GATEWAY_VERSION = "9"


def main():
    logging.config.fileConfig("logging.conf")

    discord_api_client = DiscordApiClient(BOT_TOKEN)
    ws_client = WebsocketClient(GATEWAY_VERSION, discord_api_client)

    loop = asyncio.get_event_loop()
    connection = loop.run_until_complete(ws_client.connect())

    asyncio.ensure_future(ws_client.heartbeat(connection)),
    asyncio.ensure_future(ws_client.receive_message(connection)),
    loop.run_forever()


if __name__ == "__main__":
    main()
