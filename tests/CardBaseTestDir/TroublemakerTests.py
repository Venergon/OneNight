import tests.CardTestDefault as CardTestDefault
from CardBase import *

class TroublemakerTests(CardTestDefault.CardTestDefault):
    def get_role(self):    
        return Troublemaker

    def test_two_targets(self):
        expected_order = ["player2", "player1", "self", "left", "centre", "right"]

        self.card.do_action("player1", "player2")

        self.assert_resulting_order(expected_order)
