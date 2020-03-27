# bot.py
import csv
import os
import discord
from discord.ext import commands

TOKEN = "Njg0MDYyMTMwMzg2ODk0OTcw.XmADZQ.McCDZLUUB7smn6SjvuagzjU8eZ8"
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

    confirmed = "D:/Projects/Matlab/covid/COVID-19/csse_covid_19_data/csse_covid_19_time_series" \
                "/time_series_covid19_confirmed_global.csv "
    deaths = "D:/Projects/Matlab/covid/COVID-19/csse_covid_19_data/csse_covid_19_time_series" \
             "/time_series_covid19_deaths_global.csv "
    recovered = "D:/Projects/Matlab/covid/COVID-19/csse_covid_19_data/csse_covid_19_time_series" \
                "/time_series_covid19_recovered_global.csv "

    if len(args) > 0:
        country = args[0]
        localization = confirmed
        date_read = False
        if len(args) > 1:
            case = args[1]
            if case == "deaths":
                localization = deaths
            elif case == "recovered":
                localization = recovered
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
