import asyncio
import logging
import logging.config

from api_client.apiclient import ApiClient
from bot_secrets import BOT_TOKEN
from websocket_client import WebsocketClient


GATEWAY_VERSION = "9"


def main():
    logging.config.fileConfig("logging.conf")

    api_client = ApiClient(BOT_TOKEN)
    ws_client = WebsocketClient(GATEWAY_VERSION, api_client)

    loop = asyncio.get_event_loop()
    connection = loop.run_until_complete(ws_client.connect())

    asyncio.ensure_future(ws_client.heartbeat(connection)),
    asyncio.ensure_future(ws_client.receive_message(connection)),
    loop.run_forever()


if __name__ == "__main__":
    main()
