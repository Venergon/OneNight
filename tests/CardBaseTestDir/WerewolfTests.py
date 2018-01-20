import tests.CardTestDefault as CardTestDefault
from CardBase import *
from tests.MockGame import MockGame

class WerewolfTests(CardTestDefault.CardTestDefault):
    def get_role(self):    
        return Werewolf

    def test_one_centre(self):
        flavour_text = self.card.do_action("left", None)

        self.assert_contains(flavour_text, "Hunter")

    def test_one_centre_too_many_wolves(self):
        # Need a custom game in which there are multiple werewolves
        players = ['player1', 'player2', 'self']
        roles = [Werewolf, Villager, self.get_role(), Villager, Villager, Villager]

        game = MockGame(players, roles)

        game.assign()

        card = game.original['self']

        with self.assertRaises(IsNotLegalError):
            card.do_action('left', None)




