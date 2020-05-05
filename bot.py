# bot.py
import math
import discord
from discord.ext import commands
import csv
import logging
import praw
import sys
import random
import traceback
import youtube_dl
import asyncio

from functions import update_covid_database, write_json, contains_banned_words, open_json

stderr = sys.stderr
sys.stderr = open('files/discord.log', 'w')

DATA = open_json()
LEVELS = [int(math.pow(x, 1.5) * 20) for x in range(100)]
BANNED_WORDS = (open('files/swearWords.txt', 'r').read().replace(" ", "").split(",") +
                open('files/swearWordsPL.txt', 'r').read().replace("'", "").replace("\n", "").replace(" ", "").split(
                    ","))
CURSE_PHRASES = [
    "Watch your mouth son!",
    "Yo yooo chill out!",
    "How about we take our time and try to rephrase that?",
    "Bad words, you use - rephrase you should ~ Yoda Master",
    "You mad bruh?",
    "I mean, that ain't goin' through brother..."
]

# Setting up discord loggers
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='files/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Reading variables from file
with open("files/variables.csv", 'r') as var_csv:
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

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {'options': '-vn'}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume_=0.5):
        super().__init__(source, volume_)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        print(url)
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


bot = commands.Bot(command_prefix='/')


@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))


@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f'Siemano kolano {member.name}')


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


@bot.command(name='kys', help='Closes bot, for debug purposes only', category='asd')
@commands.has_role('admin')
async def kill(ctx):
    await bot.close()


@bot.group()
async def poll(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("You can use:\n ```/pool start '<question>' "
                       "<1st option> <2nd option> ...\n /pool result <pool ID>```")


@poll.command(name='start', help='Creates a simple pool, for more info say "/pool"')
async def _start(ctx, *args):
    numbers = ["1\u20e3", "2\u20e3", "3\u20e3", "4\u20e3", "5\u20e3", "6\u20e3", "7\u20e3", "8\u20e3", "9\u20e3", ]

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
        await ctx.send('Id of the poll: ' + str(msg.id))
        n = 1
        for num in numbers:
            if n == len(args):
                break
            await msg.add_reaction(num)
            n += 1


@poll.command(name='result', help='Type a poll id to end it')
async def _result(ctx, poll_id: int):
    try:
        msg = await ctx.fetch_message(poll_id)
        reactions = msg.reactions
        # numbers = {':one:': 0, ':two:': 0, ':three:': 0, ':four:': 0, ':five:': 0, ':six:': 0, ':seven:': 0,
        # ':eight:': 0, ':nine:': 0}
        numbers = dict()
        winner = discord.reaction
        for react in reactions:
            numbers[react] = react.count
            winner = react
        ties = list()
        for num in numbers:
            if numbers[num] == numbers[winner]:
                ties.append(str(num))
            elif numbers[num] > numbers[winner]:
                winner = num
                ties.clear()
                ties.append(str(num))
        if len(ties) > 1:
            text = "There was a tie between: "
            for t in ties:
                text += t + ' '
        else:
            text = "And the winner is: " + str(winner)
        await ctx.send(text)
    except:
        await ctx.send('Poll not found')


@bot.command(name='meme', help='Shows random meme from reddit')
async def meme(ctx, *args):
    if len(args) > 0:
        subreddit = args[0]
    else:
        subreddit = random.choice(['dankmemes', 'memes', 'funny'])

    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         user_agent=user_agent,
                         username=reddit_username,
                         password=reddit_password)

    try:
        submission = reddit.subreddit(subreddit).random()
        await ctx.send(submission.title)
        if submission.is_self:
            await ctx.send(submission.selftext)
        else:
            await ctx.send(submission.url)
    except:
        await ctx.send('Subreddit not found')

    # await ctx.send('https://i.redd.it/dmggzptio3w41.jpg')


@bot.command(name='cov', help='Shows how many COVID-19 cases there are now in given country')
async def cov(ctx, *args):
    if len(args) > 0:
        print(args)
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
                date_ = args[2]
                date_read = True
        else:
            case = "cases"

        with open(localization) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            update = list(next(csv_reader).keys())[-1]
            if not date_read:
                date_ = update
            success = False

            if country == "date":
                await ctx.send(f'Last update: {update}')
                success = True
            if country == "update":
                update_covid_database(confirmed_localization, deaths_localization, recovered_localization)
                await ctx.send(f'Update completed')
                success = True
            else:
                for row_ in csv_reader:
                    if country.lower() in row_['Country/Region'].lower():
                        if date_read:
                            await ctx.send(
                                f'There were {row_[date_]} {case} in {row_["Province/State"]} {country} in {date_}')
                        else:
                            await ctx.send(
                                f'There are already {row_[date_]} {case} in {row_["Province/State"]} {country}')
                        success = True

            if not success:
                await ctx.send(f'Something went wrong')

    else:
        await ctx.send(f'``` Usage:\n '
                       f'date - get the last update date \n '
                       f'<country name> - type a name of country which statistics you would like to know```')


@bot.command(name='leaderboard', help='Shows the most active users.')
async def leaderboard(ctx, *args):
    for user in DATA['people']:
        print(user)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    else:
        if not contains_banned_words(message):
            for user in DATA['people']:
                if user['userID'] == message.author.id:
                    unique = False
                    user['xp'] += len(message.content.split(" "))
                    level_before = user['level']
                    for x in range(len(LEVELS)):
                        if user['xp'] > LEVELS[x]:
                            user['level'] = x + 1
                    if level_before != user['level']:
                        await message.channel.send(
                            f"Congratulations {message.author.mention}, you have just hit level {user['level']}!"
                        )
                        write_json(DATA)
                    break
                else:
                    unique = True
            if unique:
                DATA['people'].append({
                    'userID': message.author.id,
                    'xp': len(message.content),
                    'level': 1
                })
                write_json(DATA)
        else:
            await message.delete()
            await message.channel.send(random.choice(CURSE_PHRASES))
    await bot.process_commands(message)


@bot.command(name='join', help='Joins to your channel')
async def join(ctx):
    for channel in ctx.guild.voice_channels:
        print(channel.name)
        for member in channel.members:
            print(member.nick)
            if member == ctx.author:
                if ctx.voice_client is not None:
                    return await ctx.voice_client.move_to(channel)

                await channel.connect()


@bot.command(name='play', help='Plays music, from yt url')
async def play(ctx, url):
    for channel in ctx.guild.voice_channels:
        print(channel.name)
        for member in channel.members:
            print(member.nick)
            if member == ctx.author:
                if ctx.voice_client is not None:
                    await ctx.voice_client.move_to(channel)
                else:
                    await channel.connect()
    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=bot.loop, stream=False)
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('Now playing: {}'.format(player.title))


@bot.command(name='volume', help='Changes the playback volume')
async def volume(ctx, volume_: int):
    if ctx.voice_client is None:
        return await ctx.send("Not connected to a voice channel.")

    ctx.voice_client.source.volume = volume_ / 100
    await ctx.send("Changed volume to {}%".format(volume_))


@bot.command(name='stop', help='Stop the player, and leaves the channel')
async def stop(ctx):
    await ctx.voice_client.disconnect()


@play.before_invoke
async def ensure_voice(ctx):
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("You are not connected to a voice channel.")
            raise commands.CommandError("Author not connected to a voice channel.")
    elif ctx.voice_client.is_playing():
        ctx.voice_client.stop()


async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


bot.run(TOKEN)
