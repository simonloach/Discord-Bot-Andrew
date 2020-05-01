# bot.py
import csv
import os
import discord
import logging
from discord.ext import commands

# Setting up discord loggers
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


# Reading variables from file
with open("variables.csv") as var_csv:
    variables = csv.DictReader(var_csv, delimiter=',')
    for row in variables:
        TOKEN = row['token']
        confirmed_localization = row['confirmed']
        deaths_localization = row['deaths']
        recovered_localization = row['recovered']


bot = commands.Bot(command_prefix='/')


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


@bot.command(name='cov', help='Shows how many COVID-19 cases there are now in given country')
async def cov(ctx, *args):

    if len(args) > 0:
        country = args[0]
        localization = confirmed_localization
        date_read = False
        if len(args) > 1:
            case = args[1]
            if case == "deaths":
                localization = deaths_localization
            elif case == "recovered":
                localization = recovered_localization
            else:
                case = "cases"
            if len(args) > 2:
                date = args[2]
                date_read = True
        else:
            case = "cases"

        with open(localization) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            update = list(next(csv_reader).keys())[-1]
            if not date_read:
                date = update
            success = False

            if country == "date":
                await ctx.send(f'Last update: {update}')
                success = True
            else:
                for row in csv_reader:
                    if country.lower() in row['Country/Region'].lower():
                        if date_read:
                            await ctx.send(f'There were {row[date]} {case} in {row["Province/State"]} {country} in {date}')
                        else:
                            await ctx.send(f'There are already {row[date]} {case} in {row["Province/State"]} {country}')
                        success = True

            if not success:
                await ctx.send(f'Something went wrong')

    else:
        await ctx.send(f'Usage:')
        await ctx.send(f'date - get the last update date')
        await ctx.send(f'<country name> - type a name of country which statistics you would like to know')



@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

bot.run(TOKEN)
