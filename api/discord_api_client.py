import json
import requests


class DiscordApiClient:
    BASE_URL = "https://discord.com/api"

    def __init__(self, BOT_TOKEN):
        self.token = BOT_TOKEN
        self.headers = {"Authorization": f"Bot {self.token}"}

    def get_bot_id(self):
        url = f"{self.BASE_URL}/users/@me"
        r = requests.get(url, headers=self.headers)
        response = r.json()
        bot_id = response["id"]
        return bot_id

    def send_message(self, channel_id, message):
        payload = {
            "content": str(message),
            "tts": False,
        }
        url = f"{self.BASE_URL}/channels/{channel_id}/messages"
        r = requests.post(
            url,
            headers=self.headers,
            json=payload,
        )

    def get_channels(self, guild_id):
        url = f"{self.BASE_URL}/guilds/{guild_id}/channels"
        r = requests.get(
            f"{self.BASE_URL}/guilds/{guild_id}/channels", headers=self.headers
        )
        response = r.json()

        # "Default" channel
        self.channel_id = response[0]["id"]

    def get_message(self, message_id):
        r = requests.get(
            f"{self.BASE_URL}/channels/{self.channel_id}/messages/{message_id}",
            headers=self.headers,
        )
        response = r.json()
        return response
