from CardBase import *
from constants import *
from User import User
from Game import Game
import os, glob, string, random, shutil, copy

role_conversions = {"Villager":Villager, "Werewolf":Werewolf, "Robber":Robber, "Mason":Mason,
                    "Troublemaker":Troublemaker, "Drunk":Drunk, "Hunter":Hunter, "Seer":Seer,
                    "Insomniac":Insomniac, "Tanner":Tanner, "Minion":Minion}



def role_to_text(card):
    return card.__name__

def char_to_text(card):
    return "[{},{},{}]".format(card.__class__.__name__, card.original_player, card.player)

def text_to_role(text):
    if text:
        return role_conversions[text.strip()]

def text_to_char(text, g):
    text = text[1:-1]
    if text:
        clss, original_player, player = text.split(",")
        clss = role_conversions[clss.strip()]
        new_card = clss(g, original_player)
        new_card.change_player(player)
    return new_card

def list_to_file(l, f):
   f.write("`".join(l)+"\n")

def roles_list_to_file(l, f):
    f.write("`".join(map(role_to_text, l))+"\n")

def dict_to_file(d, f):
   f.write("`".join(map(lambda x: "{}:{}".format(x, d[x]), d))+"\n")

def roles_dict_to_file(d, f):
    f.write("`".join(map(lambda x: "{}:{}".format(x, char_to_text(d[x])), d))+"\n")

def tuple_dict_to_file(d, f):
    a = copy.deepcopy(d)
    for key in a:
        val = a[key]
        val = "("+",".join(map(lambda x: "None" if x is None else x.strip(), val))+")"
        a[key] = val
    dict_to_file(a,f)

def text_to_tuple_dict(text):
    d = {}
    for pair in text.split("`"):
        if pair:
            key, value = pair.split(":")
            value = value[1:-1]
            value = value.split(",")
            value = list(map(lambda x: None if x.strip() == "None" else x.strip(), value))
            value = tuple(value)
            d[key] = value
    return d

def text_to_list(text):
    l = text.split("`")
    while "" in l:
        l.remove("")
    return l

def text_to_roles_list(text):
    l = list(map(lambda x: text_to_role(x), text.split("`")))
    while None in l:
        l.remove(None)
    return l


def text_to_dict(text):
   d = {}
   for pair in text.split("`"):
       if pair:
           key, value = pair.split(":")
           d[key] = value
   return d

def text_to_roles_dict(text, g):
    d = {}
    for pair in text.split("`"):
        if pair:
            key, value = pair.split(":")
            value = text_to_char(value, g)
            d[key] = value
    return d

def string_to_list(text):
    if text == "":
        #Just return the empty list
        return []

    #Remove the [] around the list
    text = text[1:-1]
    
    result = text.split(",")
    result = list(map(lambda x: x.strip(), result))
    while "" in result:
        result.remove("")
    return result


def string_to_dict(text):
    fields = {}
    lines = text.split("\n")
    for line in lines:
        result = line.split("=", 1)

        if len(result) == 2:
            name, val = result
            name = name.strip()
            val = val.strip()
            fields[name] = val
    
    return fields

def sanitise(text):
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace("'", "&apos;")
    text = text.replace('"', "&quot;")
    text = text.replace("\r\n", "\\n")
    text = text.replace("\r", "\\n")
    text = text.replace("\n", "\\n")

    return text

# Create an account and send an email for activation
def make_pending_account(parameters):
    zid = sanitise(parameters.getvalue("username", ""))

    if (not zid) or os.path.exists("{}/{}".format(DATA_DIRECTORY, zid)):
        print(zid)
        print(os.path.exists("{}/{}".format(DATA_DIRECTORY, zid)))
        #Either no zid supplied or account already exists, failure in creating account
        return False

    password = sanitise(parameters.getvalue("password", ""))

    os.mkdir("{}/{}".format(DATA_DIRECTORY, zid))
    with open("{}/{}/user.txt".format(DATA_DIRECTORY, zid), "w", encoding="UTF-8") as f:
        #Store it in a temporary folder for when it gets confirmed
        f.write("""
zid={}
password={}
""".format(zid, password))
    


    return True

def login_as(zid, password):
    if os.path.exists("{}/{}".format(DATA_DIRECTORY, zid)):
        user = User(zid, None)
    else:
        return None

    if user.password == password:
        token = []
        for i in range(256):
            token.append(random.choice(string.ascii_letters+string.digits))

        token = "".join(token)
        user.add_token(token)

        with open("tokens.txt", "a") as f:
            f.write("{}:{}\n".format(token, zid))

        user.set_me(user)
        return user
        
    else:
        return None

def token_to_user(token):
    with open("tokens.txt") as f:
        for line in f:
            actual_token, zid = line.split(":")
            zid = zid.strip()
            if actual_token == token:
                if os.path.exists("{}/{}".format(DATA_DIRECTORY, zid)):
                    user = User(zid, None)
                else:
                    return None
                user.add_token(token)
                user.set_me(user)
                return user
        return None

def join_game(parameters, me):
    if not me:
        return
    g = Game.load("curr.game")

    if me.zid not in g.players and g.stage == STAGE_BEFORE:
        g.add_players([me.zid])
        g.save("curr.game")


def leave_game(parameters, me):
    if not me:
        return

    g = Game.load("curr.game")

    if me.zid in g.players and g.stage == STAGE_BEFORE:
        g.remove_player(me.zid)
        g.save("curr.game")

def start_game(parameters, me):
    if not me:
        return

    g = Game.load("curr.game")

    if me.zid == "venergon" and g.stage == STAGE_BEFORE:
        g.assign()
        g.save("curr.game")

def change_roles(parameters, me):
    if not me:
        return

    g = Game.load("curr.game")

    if me.zid == "venergon" and g.stage == STAGE_BEFORE:
        roles = parameters.getvalue("roles", "[]")
        roles = roles.replace(",", "`")
        g.roles = text_to_roles_list(roles[1:-1])
        g.save("curr.game")

def submit_action(parameters, me):
    g = Game.load("curr.game")
    if not me or me.zid not in g.players or g.stage != STAGE_NIGHT:
        return
    
    target1 = parameters.getvalue("target1", None)
    target2 = parameters.getvalue("target2", None)
    g.add_action(me.zid, target1, target2)
    if g.actions_for_all():
        g.do_actions()
    g.save("curr.game")

def vote(parameters, me):
    g = Game.load("curr.game")
    
    if not me or me.zid not in g.players or g.stage != STAGE_DAY:
        return

    target = parameters.getvalue("target", None)

    g.add_vote(me.zid, target)

    if g.votes_for_all():
        g.count_votes()

    g.save("curr.game")

