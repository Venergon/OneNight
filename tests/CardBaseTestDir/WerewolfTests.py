import tests.CardTestDefault as CardTestDefault
from CardBase import *

class WerewolfTests(CardTestDefault.CardTestDefault):
    def get_role(self):    
        return Werewolf

    def test_one_centre(self):
        flavour_text = self.card.do_action("left", None)

        self.assert_contains(flavour_text, "Hunter")





