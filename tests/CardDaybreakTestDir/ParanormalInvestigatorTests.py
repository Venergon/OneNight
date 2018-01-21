import tests.CardTestDefault as CardTestDefault
from CardDaybreak import *
from CardBase import *
from Team import Team
from tests.MockGame import MockGame

class ParanormalInvestigatorTests(CardTestDefault.CardTestDefault):
    def get_role(self):    
        return ParanormalInvestigator

    def test_one_target(self):
        # Paranormal Investigator can look at just a single card
        # If it's just a villager then nothing bad happens

        
        flavour_text = self.card.do_action('player1', None)

        self.assert_order(self.original_order)

        self.assert_contains(flavour_text, "Villager", "Flavour text should contain the role of the card you're looking at")

        # The team should stay as villager
        self.assertEquals(self.card.win_team, Team.Villager)
        self.assertEquals(self.card.death_team, Team.Villager)

    def test_one_target_tanner(self):
        # If the paranormal investigator sees a tanner they should become a tanner
        flavour_text = self.card.do_action('player2', None)

        self.assert_order(self.original_order)

        self.assert_contains(flavour_text, "Tanner", "Flavour text should contain the role of the card you're looking at")

        self.assertEquals(self.card.win_team, Team.Tanner)
        self.assertEquals(self.card.death_team, Team.Tanner)

    def test_one_target_werewolf(self):
        # If the paranormal investigator sees a werewolf they should become a werewolf
        players = ['player1', 'self']
        roles = [Werewolf, self.get_role(), Villager, Villager, Villager]

        game = MockGame(players, roles)

        game.assign()

        card = self.game.original['self']

        flavour_text = card.do_action('player1', None)

        self.assert_contains(flavour_text, "Werewolf", "Flavour text should contain the role of the card you're looking at")

        self.assertEquals(self.card.win_team, Team.Werewolf)
        self.assertEquals(self.card.death_team, Team.Werewolf)

    def test_two_targets(self):
        # Investigator can look at two targets

        flavour_text = self.card.do_action('player1', 'player2')

        self.assert_order(self.original_order)

        self.assert_contains(flavour_text, "Villager", "Flavour text should contain the role of the card you're looking at")


        self.assert_contains(flavour_text, "Tanner", "Flavour text should contain the role of the card you're looking at")

        self.assertEquals(self.card.win_team, Team.Tanner)
        self.assertEquals(self.card.death_team, Team.Tanner)

    def test_two_targets_first_evil(self):
        # If the first target by the Investigator is evil, they don't look at the second one

        flavour_text = self.card.do_action('player2', 'player1')

        self.assert_order(self.original_order)




        self.assert_contains(flavour_text, "Tanner", "Flavour text should contain the role of the card you're looking at")


        self.assert_not_contains(flavour_text, "Villager", "Paranormal Investigator can't look at a second card if the first converted them")

        self.assertEquals(self.card.win_team, Team.Tanner)
        self.assertEquals(self.card.death_team, Team.Tanner)













