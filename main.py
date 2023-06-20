import discord
from decouple import config
import requests

intents = discord.Intents(messages=True, guilds=True, reactions=True, message_content=True)
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print("Joined")
    print(discord.__version__)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user.mention not in message.content:
        return

    array = message.content.split(" ")
    url = f"http://127.0.0.1:8000/get_url_report?url={array[1]}"

    response = requests.get(url)

    await message.channel.send(f"Status code: {response.status_code}\n{response.text}")


client.run(config('BOT_KEY'))
