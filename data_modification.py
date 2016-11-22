from CardBase import *

role_conversions = {"Villager":Villager, "Werewolf":Werewolf, "Robber":Robber, "Mason":Mason,
                    "Troublemaker":Troublemaker, "Drunk":Drunk, "Hunter":Hunter, "Seer":Seer,
                    "Insomniac":Insomniac, "Tanner":Tanner, "Minion":Minion}



def role_to_text(card):
    return card.__name__

def char_to_text(card):
    return "[{},{},{}]".format(card.__class__.__name__, card.original_player, card.player)

def text_to_role(text):
    return role_conversions[text]

def text_to_char(text, g):
    text = text[1:-1]
    if text:
        clss, original_player, player = text.split(",")
        clss = role_conversions[clss]
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

def text_to_list(text):
    return text.split("`")

def text_to_roles_list(text):
    return list(map(lambda x: text_to_role(x), text.split("`")))


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

