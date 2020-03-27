# bot.py
import csv
import os
import discord
from discord.ext import commands

TOKEN = "Njg0MDYyMTMwMzg2ODk0OTcw.XmADZQ.McCDZLUUB7smn6SjvuagzjU8eZ8"
GUILD = "Server Andrzeja"

bot = commands.Bot(command_prefix='/')

client = discord.Client()


@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )


@bot.command(name='create-channel', help='Creates channel, takes channel name as input')
@commands.has_role('admin')
async def create_channel(ctx, channel_name):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if existing_channel:
        await ctx.send(f'Channel {channel_name} already exists')
    else:
        await ctx.send(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)


@bot.command(name='kys')
async def kill(ctx):
    await bot.close()


@bot.command(name='cov')
async def cov(ctx, country, type):
    confirmed = "D:/Projects/Matlab/covid/COVID-19/csse_covid_19_data/csse_covid_19_time_series" \
                "/time_series_covid19_confirmed_global.csv "
    deaths = "D:/Projects/Matlab/covid/COVID-19/csse_covid_19_data/csse_covid_19_time_series" \
             "/time_series_covid19_deaths_global.csv "
    recovered = "D:/Projects/Matlab/covid/COVID-19/csse_covid_19_data/csse_covid_19_time_series" \
                "/time_series_covid19_recovered_global.csv "
    if type == "deaths":
        localization = deaths
    elif type == "recovered":
        localization = recovered
    else:
        localization = confirmed
        type = "cases"

    with open(localization) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row[1] == country:
                await ctx.send(f'There are already {row[-1]} {type} in {country}')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

bot.run(TOKEN)
