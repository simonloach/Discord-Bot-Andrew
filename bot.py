# bot.py

import discord
from discord.ext import commands
import csv
import logging
import requests
import praw
import sys
import random
import traceback
from datetime import date

stderr = sys.stderr
sys.stderr = open('files/discord.log', 'w')

# Setting up discord loggers
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='files/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


# Reading variables from file
with open("files/variables.csv") as var_csv:
    variables = csv.DictReader(var_csv, delimiter=',')
    for row in variables:
        TOKEN = row['token']
        confirmed_localization = row['confirmed']
        deaths_localization = row['deaths']
        recovered_localization = row['recovered']
        client_id = row['client_id']
        client_secret = row['client_secret']
        user_agent = row['user_agent']
        reddit_username = row['reddit_username']
        reddit_password = row['reddit_password']


bot = commands.Bot(command_prefix='/')


def update_covid_database():
    c_req = requests.get(
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
    d_req = requests.get(
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
    r_req = requests.get(
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
    c_file = open(confirmed_localization, "w")
    d_file = open(deaths_localization, "w")
    r_file = open(recovered_localization, "w")
    c_file.write(c_req.text)
    d_file.write(d_req.text)
    r_file.write(r_req.text)
    c_file.close()
    d_file.close()
    r_file.close()


@bot.event
async def on_ready():
    with open(confirmed_localization) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        update = list(next(csv_reader).keys())[-1].split('/')
        today = date.today().strftime("%m/%d/%Y").split('/')
        if not ((int(today[1])-int(update[1])) <= 1 and int(update[0]) == int(today[0])):
            update_covid_database()
        close(csv_file)


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


@bot.command(name='kys', help='Closes bot, for debug purposes only')
@commands.has_role('admin')
async def kill(ctx):
    await bot.close()


@bot.group()
async def poll(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("You can start or stop a poll")

@poll.command(name='start', help='creates a simple pool')
async def _start(ctx, *args):
    numbers = [':one:', ':two:', ':three:', ':four:', ':five:', ':six:', ':seven:', ':eight:', ':nine:', ]

    if len(args) < 3:
        await ctx.send("You have to specify a title, and at least two option")
    elif len(args) > 10:
        await ctx.send("There are up to 9 options supported")
    else:
        text = '>>> ' + args[0] + '\n'
        n = 1
        for num in numbers:
            if n == len(args):
                break
            text += num + ' ' + args[n] + '\n'
            n += 1
        msg = await ctx.send(text)
    await ctx.send('Id of the poll: ' + msg.id)

@poll.command(name='end', help='Type a poll id to end it')
async def _end(ctx, id: int):
    try:
        msg = await ctx.fetch_message(id)
        await ctx.send(msg.id)
    except:
        await ctx.send('Poll not found')

@bot.command(name='meme', help='Shows random meme from reddit')
async def meme(ctx, *args):
    if len(args) > 0:
        subred = args[0]
    else:
        subred = random.choice(['dankmemes', 'memes', 'funny'])

    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent, username=reddit_username, password=reddit_password)

    try:
        submission = reddit.subreddit(subred).random()
    except:
        await ctx.send('Subreddit not found')

    await ctx.send(submission.title)
    if submission.is_self:
        await ctx.send(submission.selftext)
    else:
        await ctx.send(submission.url)
    # await ctx.send('https://i.redd.it/dmggzptio3w41.jpg')


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
            if country == "update":
                update_covid_database()
                await ctx.send(f'Update completed')
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
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

bot.run(TOKEN)