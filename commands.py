import json
import random


def handle_command(message_id, channel_id, message_content):
    prefix = "shodan"
    if message_content.startswith(prefix):
        command = message_content.split(prefix)[1]
        if command:
            pass
        else:
            return _get_quote()
    return None


def _get_quote():
    with open("quotes.json") as json_file:
        data = json.load(json_file)
        return random.choice(data)
