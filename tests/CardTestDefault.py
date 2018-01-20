# CardTestDefault.py
# A subclass of unittest.TestCase containing the setup that is common to all of the cards
# Each card test will subclass this
# By Alex Rowell (Venergon)

import unittest
from DotH import *
from cardMapping import *
from tests.MockGame import MockGame

# player1 is a Villager, player2 is a Tanner, left is a Hunter, centre is a Werewolf, right is a Seer

class CardTestDefault(unittest.TestCase):
    def setUp(self):
        # We only need 2 other players plus the centre cards to test the currently implemented classes
        names = ["player1", "player2", "self"]
        roles = [Villager, Tanner, self.get_role()]

        self.game = MockGame(names, roles)

        self.game.assign()

        self.card = self.game.matchup["self"]

        # The original order that the cards were dealt out with, to compare with the new order after a change
        self.original_order = ["player1", "player2", "self", "left", "centre", "right"]

    def get_card_order(self):
        return [
                self.get_player_for_card(original_owner)
                for original_owner in self.original_order
                ]
        

    # Works out which player owns a card, based on its original owner
    def get_player_for_card(self, original_owner):
        card = self.game.matchup[original_owner]
        return card.player

    # Asserts that the new order of cards is the same as the order that we expect
    def assert_resulting_order(self, expected):
        self.assertEqual(self.get_card_order(), expected)

    # Checks that one piece of text contains an expected substring, ignoring case
    def assert_contains(self, text, expected, msg=None):
        text = text.lower()
        expected = expected.lower()

        self.assertTrue(expected in text, msg)

    # No targets is generally assumed to be fine and not do anything, subclasses will need to override if doing nothing is illegal
    def test_no_targets(self):
        self.card.do_action(None, None)

        self.assert_resulting_order(self.original_order)

    # All other actions are assumed to be illegal, any subclasses should override any legal actions
    def test_one_target(self):
        with self.assertRaises(IsNotLegalError):
            self.card.do_action("player1", None)


    def test_two_targets(self):
        with self.assertRaises(IsNotLegalError):
            self.card.do_action("player1", "player2")

    def test_one_centre(self):
        with self.assertRaises(IsNotLegalError):
            self.card.do_action("left", None)

    def test_two_centres(self):
        with self.assertRaises(IsNotLegalError):
            self.card.do_action("left", "right")




