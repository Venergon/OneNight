import random
import string
import collections
import data_modification
from CardBase import *
from CardDaybreak import *
from DotH import *
import TerribleCrypto


class Game:
    # Set up the inital roles and players
    def __init__(self, players, roles):
        self.stage = STAGE_BEFORE
        self.players = players
        self.roles = roles
        self.role_order = [Werewolf, Minion, Mason, Seer, Robber, Troublemaker,
                           Drunk, Insomniac, Villager, Tanner, Hunter]
        self.action_returns = {}
        self.actions_to_do = {}
        self.votes = {}
        self.arranged_players = []
        self.arranged_roles = []
        self.matchup = {}
        self.original = {}
        self.killed = []

    # In case you want to change players before starting the game
    def set_players(self, players):
        self.players = players

    # As above if you just want to add some players
    def add_players(self, players):
        self.players += players

    def remove_player(self, player):
        if player in self.players:
            self.players.remove(player)

    # As above if you want to change roles
    def set_roles(self, roles):
        self.roles = roles

    # As above if you just want to add some roles
    def add_roles(self, roles):
        self.roles += roles

    # Check if there is at least one player with that team.
    def team_in_play(self, death_team):
        for player in self.players:
            if self.matchup[player].deathTeam == death_team:
                return True
        return False

    # Checks if a card or card type (eg any werewolf) is owned by at least one player
    def card_in_play(self, card):
        for player in self.players:
            if isinstance(self.matchup[player], card):
                return True
        return False

    # Assign the roles to each of the players, adding in the three centre cards
    def assign(self):
        if len(self.players) != len(self.roles) - 3:
            raise ValueError('Players and Roles do not match up')
        self.arranged_players = copy.copy(self.players)
        random.shuffle(self.arranged_players)
        self.arranged_roles = copy.copy(self.roles)
        random.shuffle(self.arranged_roles)
        self.matchup = dict(zip(self.arranged_players+['left', 'centre', 'right'], self.arranged_roles))
        self.matchup["wolf"] = Wolfling
        for player in self.matchup:
            self.matchup[player] = self.matchup[player](self, player)
        self.original = copy.copy(self.matchup)
        self.giveinfo()
        self.stage = STAGE_NIGHT

    def swap(self, player1, player2):
        self.matchup[player1], self.matchup[player2] = self.matchup[player2], self.matchup[player1]
        self.matchup[player1].change_player(player1)
        self.matchup[player2].change_player(player2)

    def peek(self, player):
        return self.matchup[player]

    # Returns an order for things like circle voting
    def order(self):
        return self.arranged_players[0:-3]

    # Finds all of the roles that a card needs for its role text and gives it to the card
    def give_info(self):
        for player, role in self.matchup.items():
            things_to_find = role.need_others()
            if things_to_find is not None:
                to_return = []
                for type_to_check in things_to_find:
                    if type_to_check is None:
                        continue
                    for other_player, other_role in self.matchup.items():
                        if isinstance(other_role, type_to_check) and other_player not in centre_cards:
                            to_return.append(other_player)
                if to_return:
                    role.add_others(to_return)

    # Add the actions for one of the players onto the dict for use once all actions are in
    def add_action(self, player, person1=None, person2=None):
        if self.matchup[player].is_legal_action(person1, person2) and (person1 != person2 or person1 is None):
            self.actions_to_do[player] = (person1, person2)
        else:
            raise IsNotLegalError("That is not a legal action. Did you select the same person twice?")

    def print_role_text(self):
        for player, player_role in self.matchup.items():
            if player not in centre_cards:
                self.print_encrypted_with_key(player, player_role.init_text() + " " +
                                              self.init_win_text(player_role), self.generate_key(512))

    def player_role_text(self, player):
        role = self.matchup[player]
        return role.init_text() + " " + self.init_win_text(role)

    # Returns the win condition to add onto the end of each role text
    @staticmethod
    def init_win_text(player_role):
        if player_role.win_team == Team.Villager:
            return "You win with the village, so make sure to kill a werewolf!"
        elif player_role.win_team == Team.Werewolf:
            return "You win with the werewolves, so make sure none of the werewolves or the tanner die!"
        elif player_role.win_team == Team.Tanner:
            return "You are a tanner so you only win if you die."

    # Determines whether everyone has given in their actions
    def actions_for_all(self):
        for player in self.arranged_players:
            if player not in self.actions_to_do:
                return False
        return True

    # Simulate all of the actions happening in their proper order throughout the night then print the results
    # Again obfuscated so that the host doesn't accidentally see them
    def do_actions(self):
        if not self.actions_for_all():
                raise ValueError("Not every player has an action yet")

        original_matchup = copy.copy(self.matchup)
        for role in self.role_order:
            for player, player_role in original_matchup.items():
                if type(player_role) == role and player not in centre_cards:
                    person1, person2 = self.actions_to_do[player]
                    self.action_returns[player] = player_role.do_action(person1, person2)

        action_returns_list = list(self.action_returns.items())
        random.shuffle(action_returns_list)

        for player_role in self.matchup.values():
            player_role.any_changes()

        self.stage = STAGE_DAY

    def print_actions(self):
        action_returns_list = list(self.action_returns.items())
        random.shuffle(action_returns_list)


        for player, text in action_returns_list:
            self.print_encrypted_with_key(player, text, self.generate_key(512))

    def print_player_action(self, player):
        return self.action_returns[player]

    # Print out text obfuscated so that the host doesn't accidentally see it
    @staticmethod
    def print_encrypted_with_key(player, text, key):
        cipher = TerribleCrypto.obfuscate(text, key)

        print()
        print(player+":")
        print(cipher)
        print(key)
        print()

    # Generate a key for using in print_obfuscated_with_key
    @staticmethod
    def generate_key(length):
        to_choose_from = string.ascii_letters+string.digits
        key = []
        for i in range(length):
            key.append(random.choice(to_choose_from))

        return "".join(key)

    # Find if everyone has voted
    def votes_for_all(self):
        for player in self.arranged_players:
            if player not in self.votes:
                return False
        return True

    # Adds a vote from one of the players
    def add_vote(self, voter, votee):
        if voter == votee:
            raise SelfVoteError
        elif voter not in self.players or votee not in self.players:
            raise InvalidPlayerVoteError
        else:
            self.votes[voter] = votee

    # Count up all the votes to determine who dies
    def count_votes(self):
        votes = collections.defaultdict(int)
        for voter, votee in self.votes.items():
            votes[votee] += 1

        maximum = 0
        killed = []
        for votee, num in votes.items():
            if num == maximum:
                killed.append(votee)
            elif num > maximum:
                killed = [votee]
                maximum = num

        if maximum == 1:
            killed = []

        self.stage = STAGE_DONE
        self.killed = killed
        return killed

    def save(self, filename):
        with open(filename, "w") as f:
            f.write(str(self.stage)+"\n")
            data_modification.list_to_file(self.killed, f)
            data_modification.list_to_file(self.players, f)
            data_modification.roles_list_to_file(self.roles, f)
            data_modification.dict_to_file(self.action_returns, f)
            data_modification.tuple_dict_to_file(self.actions_to_do, f)
            data_modification.list_to_file(self.arranged_players, f)
            data_modification.roles_list_to_file(self.arranged_roles, f)
            data_modification.roles_dict_to_file(self.matchup, f)
            data_modification.roles_dict_to_file(self.original, f)
            data_modification.dict_to_file(self.votes, f)

    @staticmethod
    def load(filename):
        g = Game([], [])
        try:
            with open(filename) as f:
                g.stage = int(f.readline().strip("\n"))
                g.killed = data_modification.text_to_list(f.readline().strip("\n"))
                g.players = data_modification.text_to_list(f.readline().strip("\n"))
                g.roles = data_modification.text_to_roles_list(f.readline().strip("\n"))
                g.action_returns = data_modification.text_to_dict(f.readline().strip("\n"))
                g.actions_to_do = data_modification.text_to_tuple_dict(f.readline().strip("\n"))
                g.arranged_players = data_modification.text_to_list(f.readline().strip("\n"))
                g.arranged_roles = data_modification.text_to_roles_list(f.readline().strip("\n"))
                g.matchup = data_modification.text_to_roles_dict(f.readline().strip("\n"), g)
                g.original = data_modification.text_to_roles_dict(f.readline().strip("\n"), g)
                g.votes = data_modification.text_to_dict(f.readline().strip("\n"))
        except FileNotFoundError:
            pass
        if g.stage >= STAGE_NIGHT:
            g.give_info()
        return g
