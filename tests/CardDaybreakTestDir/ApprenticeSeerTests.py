import tests.CardTestDefault as CardTestDefault
from CardDaybreak import *

class ApprenticeSeerTests(CardTestDefault.CardTestDefault):
    def get_role(self):    
        return ApprenticeSeer

    def test_one_centre(self):
        # Apprentice seer does not change anything 
        # but does look at a centre card


        flavour_text = self.card.do_action('left', None)

        self.assert_order(self.original_order)
        self.assert_contains(flavour_text, "Hunter", "Flavour text should contain the role of the card you're looking at")
