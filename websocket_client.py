import asyncio
import json
import logging
import random
import requests
import websockets

from dataclasses import dataclass
from types import SimpleNamespace

from bot_secrets import BOT_TOKEN


@dataclass
class GatewayResponse:
    url: str


class WebsocketClient:
    BASE_URL = "https://discord.com/api"

    def __init__(self, version=None, bot=None):
        self.gateway_url = self.BASE_URL + "/v" + version + "/gateway"
        self.version = version
        self.bot = bot

        if not self.bot:
            return

    def get_websocket_url(self):
        response = requests.get(self.gateway_url)
        gw_response = GatewayResponse(**response.json())
        if gw_response and self.version:
            ws_url = gw_response.url + "?v=" + self.version + "&encoding=json"
            return ws_url
        return None

    async def connect(self):
        ws_url = self.get_websocket_url()

        if not ws_url:
            logging.error("Error. Websocket URL not defined.")
            return

        self.connection = await websockets.connect(ws_url)

        if self.connection.open:
            logging.info("Connection established.")
            return self.connection

    async def identify(self, connection):
        identify_payload = {
            "op": 2,
            "d": {
                "token": BOT_TOKEN,
                "intents": 513,
                "properties": {
                    "$os": "linux",
                    "$browser": "my_library",
                    "$device": "my_library",
                },
            },
        }
        logging.debug("Sending identify payload")
        await self.send_message(json.dumps(identify_payload))

    async def resume(self, connection):
        resume = {
            "op": 6,
            "d": {
                "token": BOT_TOKEN,
                "session_id": self.session_id,
                "seq": self.seq,
            },
        }
        logging.debug("Sending resume payload")
        await self.send_message(json.dumps(resume))

    async def send_message(self, message):
        await self.connection.send(message)

    async def handle_message(self, message, connection):
        response = json.loads(message, object_hook=lambda d: SimpleNamespace(**d))
        t = getattr(response, "t", None)
        seq = getattr(response, "s", None)

        if seq:
            self.seq = seq
            logging.debug("Sequence num set")

        if t == "READY" and hasattr(response.d, "session_id"):
            self.session_id = response.d.session_id
            logging.debug("Session id set")

        if response.op == 11 and not hasattr(self, "session_id"):
            await self.identify(connection)

        if t == "GUILD_CREATE":
            logging.debug("Received GUILD_CREATE")
            guild_details = getattr(response, "d", None)
            if guild_details:
                self.guild_id = guild_details.id
                self.bot.get_channels(self.guild_id)
                self.bot_id = self.bot.get_bot_id()

        if t == "MESSAGE_CREATE":
            logging.debug("Received MESSAGE_CREATE")
            message_details = getattr(response, "d", None)
            message_id = message_details.id
            message_content = message_details.content
            author = message_details.author
            channel_id = message_details.channel_id

            is_bot = getattr(author, "bot", None)
            if not is_bot:
                self.bot.get_message(message_id, channel_id, message_content)

        # if connection_lost:
        #     await self.resume(connection)

        if not hasattr(self, "interval"):
            logging.debug("Setting interval")
            self.interval = response.d.heartbeat_interval / 1000
            await asyncio.sleep(self.interval * random.random())

    async def receive_message(self, connection):
        # TODO: Handle reconnecting
        while True:
            try:
                message = await connection.recv()
                logging.debug("Message received")
                await self.handle_message(message, connection)

            except websockets.exceptions.ConnectionClosed:
                logging.exception("Connection with server closed.")
                pass

    async def heartbeat(self, connection):
        while True:
            try:
                heartbeat = {
                    "op": 1,
                    "d": None,
                }
                heartbeat = json.dumps(heartbeat)
                await connection.send(heartbeat)

                if getattr(self, "interval", None):
                    await asyncio.sleep(self.interval)
                else:
                    await asyncio.sleep(45)

            except websockets.exceptions.ConnectionClosed:
                logging.exception("Connection with server closed.")
                pass
            except websockets.exceptions.ConnectionClosedOk:
                logging.exception("Connection with server closed.")
                pass
