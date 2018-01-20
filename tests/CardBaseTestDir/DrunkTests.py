import tests.CardTestDefault as CardTestDefault
from CardBase import *

class DrunkTests(CardTestDefault.CardTestDefault):
    def get_role(self):    
        return Drunk

    def test_no_targets(self):
        # The drunk can't choose to not do anything
        with self.assertRaises(IsNotLegalError):
            self.card.do_action(None, None)





