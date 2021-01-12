#!/usr/bin/python3

# written by Alex Rowell
# A cgi script to run One Night Ultimate Werewolf
# Based off matelook.cgi

import cgi, cgitb, glob, os, sys, codecs, copy
import data_modification
from User import User
from constants import *
from Game import Game
from DotH import *
from CardBase import *

role_conversions = {"villager":Villager, "werewolf":Werewolf, "robber":Robber, "mason":Mason,
                    "troublemaker":Troublemaker, "drunk":Drunk, "hunter":Hunter, "seer":Seer,
                    "insomniac":Insomniac, "tanner":Tanner, "minion":Minion,
                    'paranormal':ParanormalInvestigator}



def main():
    debug = False

    # http://stackoverflow.com/questions/14860034/python-cgi-utf-8-doesnt-work said that this was 
    # how to get utf-8 printing to work
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

    parameters = cgi.FieldStorage()


    if debug:
        # So that the header is printed before anything that could go wrong happens,
        # Not the case when not debugging since the header needs the cookie
        print(page_header(parameters, None))
        cgitb.enable()

    post_action = parameters.getvalue('post_action', '')
    if post_action == 'log_out':
        me = None
    else:
        me = check_login(parameters)

    if not debug:
        print(page_header(parameters, me))

        cgitb.enable()

    if post_action == "join_game":
        data_modification.join_game(parameters, me)
    elif post_action == "start_game":
        data_modification.start_game(parameters, me)
    elif post_action == "change_roles":
        data_modification.change_roles(parameters, me)
    elif post_action == "leave_game":
        data_modification.leave_game(parameters, me)
    elif post_action == "submit_action":
        data_modification.submit_action(parameters, me)
    elif post_action == "vote":
        data_modification.vote(parameters, me)

    # If an action has been submitted through a form, find out what it is and do it
    page = parameters.getvalue('page', 'home_page')

    print(body_start(parameters, me))

    # Find which page to display
    if post_action == 'login' and me is None:
        # Tried to login but failed
        print(login_fail())
    elif post_action == "make_account":
        if data_modification.make_pending_account(parameters):
            print(account_creation_successful())
        else:
            print(account_creation_failed())
    elif page == 'home_page':
        print(home_page(parameters, me))
    elif page == 'activate_account':
        if data_modification.confirm_account(parameters):
            print(account_confirmation_successful())
        else:
            print(account_confirmation_failed())
    else:
        raise NotImplementedError("{} does not exist".format(page))

    print(page_trailer(parameters))



#
# HTML placed at the top of every page
#
# Using a teeny amount of bootstrap (getbootstrap.com) because why not
def page_header(parameters, me):
    if me is None or parameters.getvalue("post_action", "") == "log_out":
        token = ""
    else:
        token = me.token

    return """Content-Type: text/html;charset=utf-8;
Set-Cookie: token={}; httponly; Path=/

<!DOCTYPE html>
<html lang="en">
<head>
<title>One Night Ultimate Werewolf</title>
</head>""".format(token)


# The top of the body
# Contains login/out and searching
# Separated from the header so that error handling can start before this gets printed
def body_start(parameters, me):
    if me:
        login = """
Welcome {}
<form method="POST" action="">
    <input type="hidden" name="post_action" value="log_out">
    <input type="submit" value="Log Out">
</form>""".format(me.zid)
    else:
        token = ""
        login = """
<form method="POST" action="">
    <input type="text" name="username" placeholder="zid">
    <input type="password" name="password" placeholder="password">
    <input type="hidden" name="post_action" value="login">
    <input type="submit" value="login">
</form>"""

    return login


# Check if the person is validly logged in
def check_login(parameters):
    # Code from http://stackoverflow.com/questions/20898394/how-to-read-cookie-in-python?rq=1 to get cookies
    # Since cgi doesn't seem to have an inbuilt way
    handler = {}
    if 'HTTP_COOKIE' in os.environ:
        cookies = os.environ['HTTP_COOKIE']
        cookies = cookies.split('; ')

        for cookie in cookies:
            cookie = cookie.split('=')
            handler[cookie[0]] = cookie[1]

    token = handler.get("token", None)

    zid = parameters.getvalue("username", None)
    password = parameters.getvalue("password", None)

    if zid is not None and password is not None:
        return data_modification.login_as(zid, password)
    elif token:
        return data_modification.token_to_user(token)
    else:
        return None

# If logged in, show your feed
# Else show a sign in page

def home_page(parameters, me):
    if me is None:
        return """
<div class="matelook_box"><h1>Welcome to One Night Ultimate Werewolf!</h1></div>
<div class="matelook_box">
    <h2>Create Your Account Today!</h2>
    <form method="post" action="">
        <input type="hidden" name="post_action" value="make_account">
        <input type="text" name="username" placeholder="zid">
        <p>zid</p>
        <input type="password" name="password" placeholder="Password">
        <p>Password</p>
        <input type="submit" value="Create!">
    </form>
</div>
        """;
    else:
        g = Game.load("curr.game")

        if g.stage == STAGE_BEFORE:
            return game_before(g, me)
        elif g.stage == STAGE_NIGHT:
            return game_night(g, me)
        elif g.stage == STAGE_DAY:
            return game_day(g, me)
        elif g.stage == STAGE_DONE:
            return game_done(g, me)

def game_before(g, me):
    return_list = ["<h1>New Game</h1>"] 
    return_list.append("""
<p>The current players are: {}</p>""".format(g.players))
    return_list.append("""
<p>The current roles are: {}</p>""".format(list(map(lambda x: x.__name__, g.roles))))
    if me.zid in g.players:
        return_list.append("""<p>You will be part of this game</p>
<p>
<form method="POST" action="">
    <input type="hidden" name="post_action" value="leave_game">
    <input type="Submit" value="Click Here">
</form> 
to leave it.</p>""")
    else:
        return_list.append("""<p>You are not currently part of this game</p>
<p>
<form method="POST" action="">
    <input type='hidden' name='post_action' value='join_game'>
    <input type='Submit' value='Click Here'>
</form>
to join it.</p>""")

    if me.zid == "venergon":
        return_list.append("""
<form method="POST" action="">
    <input type="hidden" name="post_action" value="start_game">
    <input type="Submit" value="Click Here">
</form>
to start the game
<form method="POST" action="">
    <input type="hidden" name="post_action" value="change_roles">
    <input type="text" name="roles" value="{}">
    <input type="Submit" value="change roles">
</form>""".format("["+",".join(list(map(lambda x: x.__name__, g.roles)))+"]"))

    return "\n".join(return_list)

def game_night(g, me):
    if me.zid not in g.players:
        return """
<h1>Game in Progress</h1>
<p>Sorry, the game has already started without you :'(</p>
<p>Hopefully you can get in earlier next time</p>"""
    else:
        return ("""
<h1>Night Phase</h1>
<h2>You are {}</h2>
<p>{}</p>
<p>The roles are: {}</p>
{}
""").format(str(g.original[me.zid]), g.player_role_text(me.zid), list(map(lambda x: x.__name__, g.roles)), actions_form(g, me))

def game_day(g, me):
    if me.zid not in g.players:
        return """
<h1>Game in Progress</h1>
<p>Sorry, the game has already started without you :'(</p>
<p>Hopefully you can get in earlier next time</p>"""
    else:
        return ("""
<h1>Day Phase</h1>
<h2>You are {}</h2>
<p>{}</p>
<p>The roles are: {}</p>
{}
""").format(str(g.original[me.zid]), g.print_player_action(me.zid), list(map(lambda x: x.__name__, g.roles)), actions_form(g,me))

def game_done(g, me):
    return_list = []
    killed = g.count_votes()


    return_list.append("""
<h1>Aftermath</h1>""")

    winning_teams = []
    if not killed:
        if g.card_in_play(Wolf):
            return_list.append("<p>After all was said and done, the villagers were far too conflicted to kill anyone. What a shame "
                  "too, as there was still a werewolf.</p>")
            winning_teams = [Team.Werewolf]
        else:
            return_list.append("<p>Eventually, the villagers realised there was not a werewolf in their midst and did not kill anyone.</p>")
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
        while killed:
            also_killed = []
            for player in killed:
                role = g.matchup[player]
                if role.death_team == Team.Hunter:
                    also_killed.append(g.votes[player])

                if role.death_team not in dying_teams:
                    dying_teams.append(role.death_team)
                total_killed.append(player)

            killed = copy.deepcopy(also_killed)

        if Team.Werewolf in dying_teams:
            winning_teams = [Team.Villager]
            return_list.append(("<p>After some reasoned arguments, the villagers finally chose to kill {}. As the blood spurted, a "
                  "deathly howl was heard. It appeared the villagers had chosen "
                  "wisely.</p>").format(" and ".join(total_killed)))


        else:
            winning_teams = [Team.Werewolf]
            return_list.append("<p>The villagers finally decided on who must be the werewolf. They prepared the nooses and hung {}. "
                  "Unfortunately, the villagers were not the best at judging character and did not get a werewolf. "
                  "Looks like it's feeding time...</p>".format(" and ".join(total_killed)))
            
        if Team.Tanner in dying_teams:
            winning_teams.append(Team.Tanner)
            if Team.Werewolf in winning_teams:
                winning_teams.remove(Team.Werewolf)
                return_list.append("<p>However, a horrible stench filled the air. It turned out that the Tanner had been hung. This "
                      "sent the werewolves into a blind raging, leading them to decimate the whole town but also "
                      "ruining their appetite. Looks like everyone was unfortunate, except for the tanner.</p>")
            else:
                return_list.append("<p>But along with the werewolf, the villagers had also hung up the Tanner. The villagers moved as "
                      "fast as possible to bury the Tanner. And thus the villagers survived, with little more problems "
                      "than an irritated nose. And for once in their life the Tanner achieved what they wanted. Looks "
                      "like all the humans live happily ever after...<p>")

    winners = []
    losers = []
    for player, role in g.matchup.items():
        if player in g.players:
            if role.win_team in winning_teams:
                winners.append(player+" "+str(role))
            else:
                losers.append(player+" "+str(role))

    return_list.append("<p>The winners were: {}</p>".format(", ".join(winners)))
    return_list.append("<p>The losers were: {}</p>".format(", ".join(losers)))

    origins = []
    for player, role in g.original.items():
        origins.append(player+" "+str(role))
    return_list.append("<p>The original roles were: {}</p>".format(", ".join(origins)))
    return "\n".join(return_list)

def actions_form(g, me):
    if g.stage == STAGE_NIGHT:
        role = g.original[me.zid]
        return_list = []

        if me.zid in g.actions_to_do:
            return_list.append("<p>You have chosen an action</p>")
            return_list.append("<p>You have chosen to interact with {}</p>".format(g.actions_to_do[me.zid]))
        else:
            return_list.append("<p>You have <b>NOT</b> chosen an action</p>")
        
        options = role.actions_wanted()

        return_list.append("""
<h2>You have {} options of actions:</h2>""".format(len(options)))

        for option in options:
            if option is None:
                return_list.append("""
<h3>Do Nothing</h3>
<p>You can just do nothing for tonight</p>
<form method="POST" action="">
    <input type="hidden" name="post_action" value="submit_action">
    <input type="Submit" value="Do Nothing">
</form>""")
            else:
                phrase_mapping = {"centre":"a centre card", "other":"another player", "player":"any player", "non_wolf": "Anyone who isn't a werewolf", None:"Nothing", "direction":"Left or Right"}
                if len(option) == 1:
                    return_list.append("""
<h3>Interact with {}</h3>
<p>You can interact with {}</h3>
<form method="POST" action="">
    <input type="hidden" name="post_action" value="submit_action">
    <select name="target1">
        {}
    </select>
    <input type="Submit" value="Do This">
</form>""".format(phrase_mapping[option[0]], phrase_mapping[option[0]], phrase_to_targets(option[0], g, me)))
                else:
                    return_list.append("""
<h3>Interact with {} and {}</h3>
<p>You can interact with {} and {}</h3>
<form method="POST" action="">
    <input type="hidden" name="post_action" value="submit_action">
    <select name="target1">
        {}
    </select>
    <select name="target2">
        {}
    </select>
    <input type="Submit" value="Do This">
</form>""".format(phrase_mapping[option[0]], phrase_mapping[option[1]], phrase_mapping[option[0]], phrase_mapping[option[1]], phrase_to_targets(option[0], g, me), phrase_to_targets(option[1], g, me)))
        return "\n".join(return_list)
    elif g.stage == STAGE_DAY:
        players = phrase_to_targets("other", g, me)
        if me.zid in g.votes:
            voted = "voted for {}".format(g.votes[me.zid])
        else:
            voted = "<b>NOT voted</b> "
        return """
<h1>Vote</h1>
<p>You must vote for one other person to be lynched</p>
<p>You have {}</p>
<form method="POST" action="">
    <input type="hidden" name="post_action" value="vote">
    <select name="target">
        {}
    </select>
    <input type="Submit" value="VOTE">
</form>""".format(voted, players)

def phrase_to_targets(phrase, g, me):
    if phrase == "centre":
        return """
        <option value="left">Left</option>
        <option value="centre">Centre</option>
        <option value="right">Right</option>
        <option value="wolf">Wolfling</option>"""
    elif phrase == "direction":
        return """
        <option value="left">Left</option>
        <option value="right">Right</option>"""
    elif phrase == "other":
        players = copy.copy(g.players)
        players.remove(me.zid)
        players = map(lambda x: '<option value="{}">{}</option>'.format(x,x), players)
        return "\n".join(list(players))
    elif phrase == "player":
        players = copy.copy(g.players)
        players = map(lambda x: '<option value="{}">{}</option>'.format(x,x), players)
        return "\n".join(list(players))
    elif phrase == "non_wolf":
        players = copy.copy(g.players)
        players.remove(me.zid)
        for player in players:
            if isinstance(g.original[player], Wolf):
                players.remove(player)

        players = map(lambda x: '<option value="{}">{}</option>'.format(x, x), players)
        return "\n".join(list(players))

#
# HTML placed at the bottom of every page
# It includes all supplied parameter values as a HTML comment
# if global variable debug is set
#
def page_trailer(parameters):
    html = ""
    if debug:
        html += "".join("<!-- {}={} -->\n".format(p, parameters.getvalue(p)) for p in parameters)
    html += "</div></body>\n</html>"
    return html

def login_fail():
    return "<div class='matelook_box'>Sorry, your username or password is incorrect, please try again</div>"

def account_creation_successful():
    return """<h1>Success!</h1>
<p>Your account has been created</p>
<p>Log in to start playing</p>"""

def account_creation_failed():
    return """<h1>Account Creation Error</h1>
<p>Oops! It appears something has gone wrong with your account creation</p>
<p>It's possible that the zid you've used already exists, or that you may
have not put in a zid and password</p>
<p>Please try again</p>"""


if __name__ == '__main__':
    debug = 1
    main()


