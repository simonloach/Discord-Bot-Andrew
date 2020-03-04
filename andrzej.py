# andrzej.py
import os

import discord

# from dotenv import load_dotenv
#       wyskakuje mi error przez to, ale w sumie nie jest to kompletnie potrzebne
# load_dotenv()

token = "Njg0MDYyMTMwMzg2ODk0OTcw.XmADZQ.McCDZLUUB7smn6SjvuagzjU8eZ8"   # os.getenv('DISCORD_TOKEN')
my_guild = "Server Andrzeja"

client = discord.Client()


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == my_guild:
            break
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

client.run(token)
