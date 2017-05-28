import discord
import asyncio
from discord.ext import commands
import Game

description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''
bot = commands.Bot(command_prefix='?', description=description)


@bot.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    curr_game = None

@bot.command()
@asyncio.coroutine
def new():
    if curr_game is None:
        curr_game = Game()
        yield from bot.say("New game created")
    else:
        yield from bot.say("Game already running")

@bot.command()
@asyncio.coroutine
def end():
    curr_game = None
    yield from bot.say("Game ended")

@bot.command()
@asyncio.coroutine
def add(left : int, right : int):
    """Adds two numbers together."""
    yield from bot.say(left + right)

bot.run('')
