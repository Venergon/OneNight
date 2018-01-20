import Game
import copy
from DotH import *
from CardBase import *
from CardDaybreak import *

class MockGame(Game.Game):
    def assign(self):
        self.arranged_players = copy.copy(self.players)
        self.arranged_roles = copy.copy(self.roles) + [Hunter, Werewolf, Seer, Wolfling]
        self.matchup = dict(zip(self.arranged_players + ['left', 'centre', 'right', 'wolf'], self.arranged_roles))

        for player in self.matchup:
            self.matchup[player] = self.matchup[player](self, player)

        self.original = copy.copy(self.matchup)

        self.give_info()

        self.stage = STAGE_NIGHT
