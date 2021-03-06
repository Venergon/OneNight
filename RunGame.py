from Game import *
from CardBase import *
import TerribleCrypto

def setup_game():
    # Get all of the player names, comma separated
    players_string = input("Choose the players: ")
    players = players_string.split(",")

    # Get all of the roles, comma separated
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
    # Keep getting the actions for each player until everyone has submitted an action
    while not g.actions_for_all():
        # Get username as well as cipher to ensure that there was no problem decrypting or anything
        user = input("Enter player making action: ")
        cipher = input("Enter obfuscated action: ")
        key = input("Enter key: ")
        try:
            plain = TerribleCrypto.deobfuscate(cipher, key)
        except:
            # The message wasn't properly obfuscated
            print("Error in message")
            continue
        plain_split = plain.split(",")
        if len(plain_split) < 1 or len(plain_split) > 3:
            # They did not put in the right number of players
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
                # Either they were trying to give an action for another player (shame on you) or the key is wrong
                print("User in text does not match sending user")
            elif user not in g.players:
                # They gave the name incorrectly formatted both times
                print("User does not exist")
            else:
                # Add the action to the list of things to do
                try:
                    g.add_action(user, person1, person2)
                except IsNotLegalError:
                    print("That Action is illegal!")

    # Do all the actions
    g.do_actions()
    return g


def voting(g):
    while not g.votes_for_all():
        # Get username as well as cipher to ensure that there was no problem decrypting or anything
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
            # Did not specify both a voter and a votee
            print("Invalid number of inputs")
        else:
            voter, votee = plain_split
            voter = voter.strip(chr(0))
            votee = votee.strip(chr(0))
            if voter != user:
                # Tried to vote for someone else or decrypting screwed up
                print("User in text does not match sending user")
            elif user not in g.players:
                # Tried to vote for someone that doesn't exist
                print("User does not exist")
            else:
                try:
                    g.add_vote(voter, votee)
                except SelfVoteError:
                    # Tried to vote for themselves, cannot do that
                    print("Invalid vote")
                except InvalidPlayerVoteError:
                    # Tried to vote for someone that doesn't exist
                    print("Invalid vote")

    # Find the people with the most votes to kill
    killed = g.count_votes()

    winning_teams = []
    if not killed:
        # Circle vote, if a werewolf is alive then werewolves win otherwise villagers win
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
            print(("After some reasoned arguments, the villagers finally chose to kill {}. As the blood spurted, a "
                   "deathly howl was heard. It appeared the villagers had chosen "
                   "wisely.").format(" and ".join(total_killed)))

        else:
            winning_teams = [Team.Werewolf]
            print("The villagers finally decided on who must be the werewolf. They prepared the nooses and hung {}. "
                  "Unfortunately, the villagers were not the best at judging character and did not get a werewolf. "
                  "Looks like it's feeding time...".format(" and ".join(total_killed)))

        if Team.Tanner in dying_teams:
            # Tanner wins. This does not affect the villagers
            # Tanner is not added to winning teams because each tanner dies individually
            if Team.Werewolf in winning_teams:
                # Werewolves lose because they must not let the tanner die
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

    # Print out the end of game summary with everyone's current roles
    for player, role in g.matchup.items():
        if player in g.players:
            if role.win_team in winning_teams:
                winners.append(player+" "+str(role))
            elif role.win_team == Team.Tanner and player in total_killed:
                winners.append(player+" "+str(role))
            else:
                losers.append(player+" "+str(role))

    # Show who won and lost
    print("The winners were: {}".format(", ".join(winners)))
    print("The losers were: {}".format(", ".join(losers)))

    # Print out everyone's original roles
    origins = []
    for player, role in g.original.items():
        origins.append(player+" "+str(role))
    print("The original roles were: {}".format(", ".join(origins)))


def run_game():
    g = setup_game()
    g.save("test1.txt")
    g = Game.load("test1.txt")
    g = night_phase(g)
    g.save("test2.txt")
    g = Game.load("test2.txt")
    voting(g)
    g.save("test3.txt")
    g = Game.load("test3.txt")

run_game()
