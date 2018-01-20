import tests.CardTestDefault as CardTestDefault
from CardDaybreak import *
from CardBase import *
from tests.MockGame import MockGame

class VillageIdiotTests(CardTestDefault.CardTestDefault):
    def get_role(self):    
        return VillageIdiot

    def test_left_target(self):
        # Need a custom game to check the full rotation
        players = ['player1', 'player2', 'player3', 'self']
        roles = [Villager, Villager, Villager, self.get_role(), Villager, Villager, Villager]

        expected_order = ['player2', 'player3', 'player1', 'self', 'left', 'centre', 'right', 'wolf']

        self.original_order = players + ['left', 'centre', 'right', 'wolf']

        self.game = MockGame(players, roles)

        self.game.assign()

        card = self.game.original['self']

        card.do_action('left', None)

        self.assert_order(expected_order)


    def test_right_target(self):
        # Need a custom game to check the full rotation
        players = ['player1', 'player2', 'player3', 'self']
        roles = [Villager, Villager, Villager, self.get_role(), Villager, Villager, Villager]

        expected_order = ['player3', 'player1', 'player2', 'self', 'left', 'centre', 'right', 'wolf']

        self.original_order = players + ['left', 'centre', 'right', 'wolf']

        self.game = MockGame(players, roles)

        self.game.assign()

        card = self.game.original['self']

        card.do_action('right', None)

        self.assert_order(expected_order)





