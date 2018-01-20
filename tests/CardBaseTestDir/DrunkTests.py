import tests.CardTestDefault as CardTestDefault
from CardBase import *

class DrunkTests(CardTestDefault.CardTestDefault):
    def get_role(self):    
        return Drunk

    def test_no_targets(self):
        # The drunk can't choose to not do anything
        with self.assertRaises(IsNotLegalError):
            self.card.do_action(None, None)

    def test_one_centre(self):
        # The drunk swaps out their card with a centre one
        expected_order = ["player1", "player2", "left", "self", "centre", "right", "wolf"]

        self.card.do_action("left", None)

        self.assert_order(expected_order)





