import tests.CardTestDefault as CardTestDefault
from CardDaybreak import *
from CardBase import *
from tests.MockGame import MockGame

class MysticWolfTests(CardTestDefault.CardTestDefault):
    def get_role(self):    
        return MysticWolf

    def test_one_target(self):
        # Mystic Wolf does not change anything but does look at a card
        
        flavour_text = self.card.do_action('player1', None)

        self.assert_order(self.original_order)

        self.assert_contains(flavour_text, "Villager", "Flavour text should contain the role of the card you're looking at")

        # Make sure it's actually the right card and not just Villager each time
        flavour_text = self.card.do_action('player2', None)

        self.assert_order(self.original_order)

        self.assert_contains(flavour_text, "Tanner", "Flavour text should contain the role of the card you're looking at")



    def test_one_target_and_one_centre_no_wolves(self):
        # Mystic Wolf looks at a card 
        # and can look at a centre if there are no other wolves
        flavour_text = self.card.do_action('player1', 'left')

        self.assert_contains(flavour_text, "Villager")
        self.assert_contains(flavour_text, "Hunter")

    def test_one_target_and_one_centre_too_many_wolves(self):
        # If there are multiple wolves then the mystic wolf
        # can't look at a centre card

        # Need a custom game in which there are multiple werewolves
        players = ['player1', 'player2', 'self']
        roles = [Werewolf, Villager, self.get_role(), Villager, Villager, Villager]

        game = MockGame(players, roles)

        game.assign()

        card = game.original['self']

        with self.assertRaises(IsNotLegalError):
            card.do_action('player1', 'left')
