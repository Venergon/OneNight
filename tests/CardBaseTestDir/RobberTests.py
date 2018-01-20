import tests.CardTestDefault as CardTestDefault
from CardBase import *

class RobberTests(CardTestDefault.CardTestDefault):
    def get_role(self):    
        return Robber

    def test_one_target(self):
        expected_order = ['self', 'player2', 'player1', 'left', 'centre', 'right', 'wolf']

        flavour_text = self.card.do_action('player1', None)

        self.assert_order(expected_order)

        self.assert_contains(flavour_text, "Villager")


