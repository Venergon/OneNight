import tests.CardTestDefault as CardTestDefault
from CardBase import *

class SeerTests(CardTestDefault.CardTestDefault):
    def get_role(self):    
        return Seer

    def test_one_target(self):
        # Seer does not change anything but does look at a card
        
        flavour_text = self.card.do_action('player1', None)

        self.assert_resulting_order(self.original_order)

        self.assert_contains(flavour_text, "Villager", "Flavour text should contain the role of the card you're looking at")

        # Make sure it's actually the right card and not just Villager each time
        flavour_text = self.card.do_action('player2', None)

        self.assert_resulting_order(self.original_order)

        self.assert_contains(flavour_text, "Tanner", "Flavour text should contain the role of the card you're looking at")

    def test_two_centres(self):
        # Seer does not change anything but looks at two centre cards
        flavour_text = self.card.do_action('left', 'right')

        self.assert_resulting_order(self.original_order)
        self.assert_contains(flavour_text, "Hunter", "Flavour text should contain the role of the card you're looking at")

        self.assert_contains(flavour_text, "Seer", "Flavour text should contain the role of the card you're looking at")









