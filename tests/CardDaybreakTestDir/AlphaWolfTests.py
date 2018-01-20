import tests.CardTestDefault as CardTestDefault
from CardDaybreak import *
from CardBase import *
from tests.MockGame import MockGame

class AlphaWolfTests(CardTestDefault.CardTestDefault):
    def get_role(self):    
        return AlphaWolf

    def test_no_targets(self):
        with self.assertRaises(IsNotLegalError):
            self.card.do_action(None, None)

    def test_one_target(self):
        # Alpha wolf swaps someone with the wolf card
        expected_order = ['wolf', 'player2', 'self', 'left', 'centre', 'right', 'player1']

        self.card.do_action('player1', None)

        self.assert_order(expected_order)

    def test_one_target_and_one_centre_no_wolves(self):
        # Alpha wolf swaps someone with the wolf card 
        # and can look at a centre if there are no other wolves
        expected_order = ['wolf', 'player2', 'self', 'left', 'centre', 'right', 'player1']

        flavour_text = self.card.do_action('player1', 'left')

        self.assert_order(expected_order)

        self.assert_contains(flavour_text, "Hunter")

    def test_one_target_and_one_centre_too_many_wolves(self):
        # If there are multiple wolves then the alpha wolf
        # can't look at a centre card

        # Need a custom game in which there are multiple werewolves
        players = ['player1', 'player2', 'self']
        roles = [Werewolf, Villager, self.get_role(), Villager, Villager, Villager]

        game = MockGame(players, roles)

        game.assign()

        card = game.original['self']

        with self.assertRaises(IsNotLegalError):
            card.do_action('player1', 'left')





