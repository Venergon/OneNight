import random
import string
import collections
from CardBase import *
from DotH import *
import TerribleCrypto


class Game:
    def __init__(self, players, roles):
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

    def set_players(self, players):
        self.players = players

    def add_players(self, players):
        self.players += players

    def set_roles(self, roles):
        self.roles = roles

    def add_roles(self, roles):
        self.roles += roles

    def team_in_play(self, death_team):
        for player in self.players:
            if self.matchup[player].deathTeam == death_team:
                return True
        return False

    def card_in_play(self, card):
        for player in self.players:
            if isinstance(self.matchup[player], card):
                return True
        return False

    def assign(self):
        if len(self.players) != len(self.roles) - 3:
            raise ValueError('Players and Roles do not match up')
        self.arranged_players = copy.copy(self.players)
        random.shuffle(self.arranged_players)
        self.arranged_roles = copy.copy(self.roles)
        random.shuffle(self.arranged_roles)
        self.matchup = dict(zip(self.arranged_players+['left', 'centre', 'right'], self.arranged_roles))
        for player in self.matchup:
            self.matchup[player] = self.matchup[player](self, player)
        self.original = copy.copy(self.matchup)

    def swap(self, player1, player2):
        self.matchup[player1], self.matchup[player2] = self.matchup[player2], self.matchup[player1]
        self.matchup[player1].change_player(player1)
        self.matchup[player2].change_player(player2)

    def peek(self, player):
        return self.matchup[player]

    def order(self):
        return self.arranged_players[0:-3]

    def give_info(self):
        for player, role in self.matchup.items():
            things_to_find = role.need_others()
            if things_to_find is not None:
                to_return = []
                for type_to_check in things_to_find:
                    for other_player, other_role in self.matchup.items():
                        if isinstance(other_role, type_to_check) and other_player not in centre_cards:
                            to_return.append(other_player)
                if to_return:
                    role.add_others(to_return)

    def add_action(self, player, person1=None, person2=None):
        if self.matchup[player].is_legal_action(person1, person2):
            self.actions_to_do[player] = (person1, person2)
        else:
            raise IsNotLegalError

    def print_role_text(self):
        for player, player_role in self.matchup.items():
            if player not in centre_cards:
                self.print_encrypted_with_key(player, player_role.init_text() + " " +
                                              self.init_win_text(player_role), self.generate_key(512))

    @staticmethod
    def init_win_text(player_role):
        if player_role.win_team == Team.Villager:
            return "You win with the village, so make sure to kill a werewolf!"
        elif player_role.win_team == Team.Werewolf:
            return "You win with the werewolves, so make sure none of the werewolves or the tanner die!"
        elif player_role.win_team == Team.Tanner:
            return "You are a tanner so you only win if you die."

    def actions_for_all(self):
        for player in self.arranged_players:
            if player not in self.actions_to_do:
                return False
        return True

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

        for player, text in action_returns_list:
            self.print_encrypted_with_key(player, text, self.generate_key(512))

    @staticmethod
    def print_encrypted_with_key(player, text, key):
        cipher = TerribleCrypto.obfuscate(text, key)

        print()
        print(player+":")
        print(cipher)
        print(key)
        print()

    @staticmethod
    def generate_key(length):
        to_choose_from = string.ascii_letters+string.digits
        key = []
        for i in range(length):
            key.append(random.choice(to_choose_from))

        return "".join(key)

    def votes_for_all(self):
        for player in self.arranged_players:
            if player not in self.votes:
                return False
        return True

    def add_vote(self, voter, votee):
        if voter == votee:
            raise SelfVoteError
        elif voter not in self.players or votee not in self.players:
            raise InvalidPlayerVoteError
        else:
            self.votes[voter] = votee

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
            killed = None

        return killed