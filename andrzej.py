# andrzej.py
import os

import discord

# from dotenv import load_dotenv
#       wyskakuje mi error przez to, ale w sumie nie jest to kompletnie potrzebne
# load_dotenv()

token = "Njg0MDYyMTMwMzg2ODk0OTcw.XmADZQ.McCDZLUUB7smn6SjvuagzjU8eZ8"   # os.getenv('DISCORD_TOKEN')

client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

client.run(token)
