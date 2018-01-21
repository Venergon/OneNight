import discord
import asyncio
import pickle
import re
import time

from DotH import *
from CardBase import *
from CardDaybreak import *
from discord.ext import commands
from Game import Game

description = '''!help: display help message

To do in the server:
!new: start a new game
!start: start the game once everyone has joined
!end: end the current game
!status: display the status of the game
!join: join the current game
!leave: leave the current game
!role `card`: add a copy of `card` to the game

To do in PM:
!target `gameId` [`player1`] [`player2`]: use your role action from the game with id `gameId` on players 1 and 2. Leave the players blank if you don't/can't target multiple people
!vote `gameId` `player`: vote for `player` to die in the game with id `gameId`'''
bot = commands.Bot(command_prefix='!', description=description)

def save_game(game, server):
    with open("games/"+server.id, 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(game, f, pickle.HIGHEST_PROTOCOL)


def load_game(server):
    try:
        with open("games/"+server.id, 'rb') as f:
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            return pickle.load(f)
    except FileNotFoundError:
        return None

@bot.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command(pass_context=True)
@asyncio.coroutine
def new(ctx):
    g = load_game(ctx.message.server)
    if g is None:
        g = Game([], [])
        g.channel = ctx.message.channel
        save_game(g, ctx.message.server)
        yield from bot.say("New game created")
    else:
        yield from bot.say("Game already running")

@bot.command(pass_context=True)
@asyncio.coroutine
def end(ctx):
    save_game(None, ctx.message.server)
    yield from bot.say("Game ended")

@bot.command(pass_context=True)
@asyncio.coroutine
def status(ctx):
    g = load_game(ctx.message.server)
    if g is None:
        yield from bot.say("No active game")
    else:
        yield from bot.say("There is a current game at stage " + str(g.stage) + " running with players " + ", ".join(map(lambda x: x.mention, g.players)) + " and roles " + ", ".join(map(lambda x: str(x), g.roles)))
        yield from bot.say("The game's id is " + ctx.message.server.id)


@bot.command(pass_context=True)
@asyncio.coroutine
def join(ctx):
    g = load_game(ctx.message.server)
    if g is None:
        yield from bot.say("There is no game to join")
    elif g.stage == STAGE_BEFORE:
        if ctx.message.author in g.players:
            yield from bot.say("You are already in this game")
        else:
            g.add_players([ctx.message.author])
            save_game(g, ctx.message.server)
            yield from bot.say("Added " + ctx.message.author.mention + " to the current game")
    else:
        yield from bot.say("Sorry, the game has already started")

@bot.command(pass_context=True)
@asyncio.coroutine
def leave(ctx):
    g = load_game(ctx.message.server)
    if g is None:
        yield from bot.say("There is no game to join")
    elif g.stage == STAGE_BEFORE:
        if ctx.message.author not in g.players:
            yield from bot.say("You aren't in this game")
        else:
            g.remove_player(ctx.message.author)
            save_game(g, ctx.message.server)
            yield from bot.say("Removed " + ctx.message.author.mention + " from the current game")
    else:
        yield from bot.say("Sorry, the game has already started")
   

@bot.command(pass_context=True)
@asyncio.coroutine
def role(ctx, role: str):
    g = load_game(ctx.message.server)
    if g is None:
        yield from bot.say("There is no game to add roles to")

    else:
        if role.lower() in role_conversions:
            g.add_roles([role_conversions[role.lower()]])
            save_game(g, ctx.message.server)
            yield from bot.say("Added a " + role.lower() + " to the game")


@bot.command(pass_context=True)
@asyncio.coroutine
def target(ctx, server_id: str, *args):
    # Find the server matching the id
    server = bot.get_server(server_id)
    
    if server:
        g = load_game(server)
    else:
        g = None

    if g is None or ctx.message.author not in g.players:
        yield from bot.say("There is no game on that server or you are not in that game")
    elif g.stage != STAGE_NIGHT:
        yield from bot.say("It is not night time, you can't target anyone")
    elif len(args) > 2:
        yield from bot.say("Too many targets")
    else:
        # Check if the action is legal
        players_to_use = []

        valid = True

        for arg in args:
            found = False
            if arg in centre_cards:
                players_to_use.append(arg)
                found = True

            for player in g.players:
                if player.name == arg:
                    players_to_use.append(player)
                    found = True
                    break

            if not found:
                valid = False
        
        if not valid:
            yield from bot.say("At least one of those targets was not a player in this game")
        else:

            if len(players_to_use) < 2:
                arg2 = None
            else:
                arg2 = players_to_use[1]

            if len(players_to_use) < 1:
                arg1 = None
            else:
                arg1 = players_to_use[0]

            try:
                g.add_action(ctx.message.author, arg1, arg2) 
                save_game(g, server)
                yield from bot.say("Targetting successful")

            except IsNotLegalError:
                yield from bot.say("That action is not legal, try again")


            if g.actions_for_all():
                g.do_actions()
                save_game(g, server)
                yield from bot.send_message(g.channel, "Game has progressed to day")
                yield from bot.send_message(g.channel, "Send in votes via person message whenever you want to")
                yield from bot.send_message(g.channel, "vote with `!vote {} <player>`".format(server_id))

                for player in g.players:
                    yield from bot.send_message(player, g.print_player_action(player))


@bot.command(pass_context=True)
@asyncio.coroutine
def vote(ctx, server_id: str, votee: str):
    # Find the server matching the id
    server = bot.get_server(server_id)
    
    if server:
        g = load_game(server)
    else:
        g = None

    if g is None or ctx.message.author not in g.players:
        yield from bot.say("There is no game on that server or you are not in that game")
    elif g.stage != STAGE_DAY:
        yield from bot.say("It is not day time, you can't vote")
    else:
        # Check if the action is legal
        player_to_use = None

        found = False
        if votee in centre_cards:
            player_to_use = votee
            found = True

        for player in g.players:
            if player.name == votee:
                player_to_use = player
                found = True
                break

        if not found:
            yield from bot.say("That person is not part of the game")
        else:
            try:
                g.add_vote(ctx.message.author, player_to_use)
                save_game(g, server)
                yield from bot.say("Vote successful")

            except SelfVoteError:
                yield from bot.say("You can't vote for yourself, try again")
            except InvalidPlayerVoteError:
                yield from bot.say("Invalid vote, try again")


            if g.votes_for_all():
                killed = g.count_votes()
                

                winning_teams = []
                if not killed:
                    # Circle vote, if a werewolf is alive then werewolves win otherwise villagers win
                    if g.card_in_play(Werewolf):
                        yield from bot.send_message(g.channel, "After all was said and done, the villagers were far too conflicted to kill anyone. What a shame "
                              "too, as there was still a werewolf.")
                        winning_teams = [Team.Werewolf]
                    else:
                        yield from bot.send_message(g.channel, "Eventually, the villagers realised there was not a werewolf in their midst and did not kill anyone.")
                        winning_teams = [Team.Villager]
                else:
                    total_killed = []

                    also_killed = []
                    dying_teams = []
                    for player in killed:
                        role = g.matchup[player]
                        if role.death_team == Team.Hunter:
                            also_killed.append(g.votes[player])

                        if role.death_team not in dying_teams:
                            dying_teams.append(role.death_team)
                        total_killed.append(player)

                    killed = copy.deepcopy(also_killed)
                    # Find all of the teams that died, repeat if more die due to hunter
                    while killed:
                        also_killed = []
                        for player in killed:
                            role = g.matchup[player]
                            if role.death_team == Team.Hunter:
                                # Kill whoever the hunter voted for
                                also_killed.append(g.votes[player])

                            if role.death_team not in dying_teams:
                                # Add all of the teams that died, mainly just for werewolf but also tanner
                                # (currently used for whether Tanner wins while there are no roles that can create multiple tanners,
                                # will later be used for apprentice tanner)
                                dying_teams.append(role.death_team)
                            total_killed.append(player)

                        killed = copy.deepcopy(also_killed)

                    if Team.Werewolf in dying_teams:
                        # Villagers win as they killed a werewolf
                        winning_teams = [Team.Villager]
                        yield from bot.send_message(g.channel, ("After some reasoned arguments, the villagers finally chose to kill {}. As the blood spurted, a "
                            "deathly howl was heard. It appeared the villagers had chosen "
                            "wisely.").format(" and ".join(map(lambda x: x.mention, total_killed))))



                    else:
                        winning_teams = [Team.Werewolf]


                        yield from bot.send_message(g.channel, "The villagers finally decided on who must be the werewolf. They prepared the nooses and hung {}. "
                                "Unfortunately, the villagers were not the best at judging character and did not get a werewolf. "
                                "Looks like it's feeding time...".format(" and ".join(map(lambda x: x.mention, total_killed))))

                        if Team.Tanner in dying_teams:
                            # Tanner wins. This does not affect the villagers
                            if Team.Werewolf in winning_teams:
                                # Werewolves lose because they must not let the tanner die
                                winning_teams.remove(Team.Werewolf)
                                yield from bot.send_message(g.channel, "However, a horrible stench filled the air. It turned out that the Tanner had been hung. This "
                                        "sent the werewolves into a blind raging, leading them to decimate the whole town but also "
                                        "ruining their appetite. Looks like everyone was unfortunate, except for the tanner.")
                            else:
                                yield from bot.send_message(g.channel, "But along with the werewolf, the villagers had also hung up the Tanner. The villagers moved as "
                                        "fast as possible to bury the Tanner. And thus the villagers survived, with little more problems "
                                        "than an irritated nose. And for once in their life the Tanner achieved what they wanted. Looks "
                                        "like all the humans live happily ever after...")

                winners = []
                losers = []

                # Print out the end of game summary with everyone's current roles
                for player, role in g.matchup.items():
                    if player in g.players:
                        
                        if role.win_team == Team.Tanner:
                            # Tanner only wins if they die
                            if player in total_killed:
                                winners.append(player.mention + " " + str(role))
                            else:
                                losers.append(player.mention + " " + str(role))

                        elif role.win_team in winning_teams:
                            winners.append(player.mention+" "+str(role))
                        else:
                            losers.append(player.mention+" "+str(role))

                # Show who won and lost
                yield from bot.send_message(g.channel, "The winners were: {}".format(", ".join(winners)))
                yield from bot.send_message(g.channel, "The losers were: {}".format(", ".join(losers)))

                # Print out everyone's original roles
                origins = []
                for player, role in g.original.items():
                    if isinstance(player, str):
                        origins.append(player+" "+str(role))
                    else:
                        origins.append(player.mention+" "+str(role))
                yield from bot.send_message(g.channel, "The original roles were: {}".format(", ".join(origins)))




@bot.command(pass_context=True)
@asyncio.coroutine
def start(ctx):
    g = load_game(ctx.message.server)
    if g is None:
        yield from bot.say("There is no game to start")
    elif g.stage != STAGE_BEFORE:
        yield from bot.say("Game has already started")
    else:
        try:
            g.assign()
            yield from bot.say("Game started, check your PMs")
            save_game(g, ctx.message.server)
            for player in g.players:
                yield from bot.send_message(player, g.player_role_text(player))
                yield from bot.send_message(player, "Do your action with `!target {} <player1> <player2>` (without the anglebrackets)".format(ctx.message.server.id))
                yield from bot.send_message(player, "You can target the centre cards as 'left', 'right' and 'centre' and you should leave players blank if your role tells you to target fewer than 2 people")
                yield from bot.send_message(player, "the players are {}".format(", ".join(map(lambda x: x.name, g.players))))

        except ValueError:
            yield from bot.say("There aren't the right number of roles for players (there should be players+3 roles)")

@bot.command(pass_context=True)
@asyncio.coroutine
def clear(ctx):
    while True:
        yield from bot.change_nickname(ctx.message.author, None)
        print("{} cleared".format(ctx.message.author))
        time.sleep(0.5)

@bot.command(pass_context=True)
@asyncio.coroutine
def away(ctx):
    server = ctx.message.server
    # Find afk role
    desired_role = None
    for role in server.roles:
        if "afk" in role.name.lower():
            desired_role = role
            break

    while True:
        for user in server.members:
            if user.status != discord.Status.online and user.status != discord.Status.offline:
                try:
                    yield from bot.add_roles(user, desired_role)
                except discord.errors.Forbidden:
                    print("Cannot change {}".format(user))

            else:
                try:
                    yield from bot.remove_roles(user, desired_role)
                except discord.errors.Forbidden:
                    print("Cannot change {}".format(user))
        print("Set AFK Status")
        yield from asyncio.sleep(60)

    

@bot.command()
@asyncio.coroutine
def self_awareness():
    yield from bot.say("It's alive!")

bot.run(open("secret.txt", "r").read().strip())
