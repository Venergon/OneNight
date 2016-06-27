from Game import *
from CardBase import *
import TerribleCrypto

role_conversions = {"Villager":Villager, "Werewolf":Werewolf, "Robber":Robber, "Mason":Mason,
                    "Troublemaker":Troublemaker, "Drunk":Drunk, "Hunter":Hunter, "Seer":Seer,
                    "Insomniac":Insomniac, "Tanner":Tanner, "Minion":Minion}


def setup_game():
    players_string = input("Choose the players: ")
    players = players_string.split(",")

    if len(players) > len(set(players)):
        raise ValueError("All players must be unique")

    roles_string = input("Choose the roles: ")
    roles_part_converted = roles_string.split(",")
    roles = []
    for role in roles_part_converted:
        roles.append(role_conversions[role])
    g = Game(players, roles)
    g.assign()
    g.give_info()
    g.print_role_text()

    return g


def night_phase(g):
    while not g.actions_for_all():
        user = input("Enter player making action: ")
        cipher = input("Enter obfuscated action: ")
        key = input("Enter key: ")
        try:
            plain = TerribleCrypto.deobfuscate(cipher, key)
        except:
            print("Error in message")
            continue
        plain_split = plain.split(",")
        if len(plain_split) < 1 or len(plain_split) > 3:
            print("That's not the right amount of players for any input")
        else:
            text_user = plain_split[0].strip(chr(0))
            if len(plain_split) > 1:
                person1 = plain_split[1].strip(chr(0))
            else:
                person1 = None

            if len(plain_split) > 2:
                person2 = plain_split[2].strip(chr(0))
            else:
                person2 = None

            if text_user != user:
                print("User in text does not match sending user")
            elif user not in g.players:
                print("User does not exist")
            else:
                try:
                    g.add_action(user, person1, person2)
                except IsNotLegalError:
                    print("That Action is illegal!")

    g.do_actions()
    return g


def voting(g):
    while not g.votes_for_all():
        user = input("Enter player making vote: ")
        cipher = input("Enter obfuscated vote: ")
        key = input("Enter key: ")
        try:
            plain = TerribleCrypto.deobfuscate(cipher, key)
        except:
            print("Error in message")
            continue
        plain_split = plain.split(",")
        if len(plain_split) != 2:
            print("Invalid number of inputs")
        else:
            voter, votee = plain_split
            voter = voter.strip(chr(0))
            votee = votee.strip(chr(0))
            if voter != user:
                print("User in text does not match sending user")
            elif user not in g.players:
                print("User does not exist")
            else:
                try:
                    g.add_vote(voter, votee)
                except SelfVoteError:
                    print("Invalid vote")
                except InvalidPlayerVoteError:
                    print("Invalid vote")


    killed = g.count_votes()

    winning_teams = []
    if killed is None:
        if g.card_in_play(Werewolf):
            print("After all was said and done, the villagers were far too conflicted to kill anyone. What a shame "
                  "too, as there was still a werewolf.")
            winning_teams = [Team.Werewolf]
        else:
            print("Eventually, the villagers realised there was not a werewolf in their midst and did not kill anyone.")
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
            print(("After some reasoned arguments, the villagers finally chose to kill {}. As the blood spurted, a "
                  "deathly howl was heard. It appeared the villagers had chosen "
                  "wisely.").format(" and ".join(total_killed)))


        else:
            winning_teams = [Team.Werewolf]
            print("The villagers finally decided on who must be the werewolf. They prepared the nooses and hung {}. "
                  "Unfortunately, the villagers were not the best at judging character and did not get a werewolf. "
                  "Looks like it's feeding time...".format(" and ".join(total_killed)))
            
        if Team.Tanner in dying_teams:
            winning_teams.append(Team.Tanner)
            if Team.Werewolf in winning_teams:
                winning_teams.remove(Team.Werewolf)
                print("However, a horrible stench filled the air. It turned out that the Tanner had been hung. This "
                      "sent the werewolves into a blind raging, leading them to decimate the whole town but also "
                      "ruining their appetite. Looks like everyone was unfortunate, except for the tanner.")
            else:
                print("But along with the werewolf, the villagers had also hung up the Tanner. The villagers moved as "
                      "fast as possible to bury the Tanner. And thus the villagers survived, with little more problems "
                      "than an irritated nose. And for once in their life the Tanner achieved what they wanted. Looks "
                      "like all the humans live happily ever after...")

    winners = []
    losers = []
    for player, role in g.matchup.items():
        if player in g.players:
            if role.win_team in winning_teams:
                winners.append(player+" "+str(role))
            else:
                losers.append(player+" "+str(role))

    print("The winners were: {}".format(", ".join(winners)))
    print("The losers were: {}".format(", ".join(losers)))

    origins = []
    for player, role in g.original.items():
        origins.append(player+" "+str(role))
    print("The original roles were: {}".format(", ".join(origins)))


def run_game():
    g = setup_game()
    g = night_phase(g)
    voting(g)

run_game()
