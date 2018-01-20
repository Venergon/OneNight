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
        self.original_order = ["player1", "player2", "self", "left", "centre", "right", "wolf"]

    def get_card_order(self):
        return [
                self.get_player_for_card(original_owner)
                for original_owner in self.original_order
                ]
        

    # Works out which player owns a card, based on its original owner
    def get_player_for_card(self, original_owner):
        card = self.game.original[original_owner]
        return card.player

    # Asserts that the new order of cards is the same as the order that we expect
    def assert_order(self, expected, actual = None):
        # If actual is None then we assume it's using the main game
        if actual is None:
            actual = self.get_card_order()

        self.assertEqual(actual, expected)

    # Checks that one piece of text contains an expected substring, ignoring case
    def assert_contains(self, text, expected, msg=None):
        text = text.lower()
        expected = expected.lower()

        self.assertIn(expected, text, msg)

    # No targets is generally assumed to be fine and not do anything, subclasses will need to override if doing nothing is illegal
    def test_no_targets(self):
        self.card.do_action(None, None)

        self.assert_order(self.original_order)

    # All other actions are assumed to be illegal, any subclasses should override any legal actions
    def test_one_target(self):
        with self.assertRaises(IsNotLegalError):
            self.card.do_action("player1", None)


    def test_two_targets(self):
        with self.assertRaises(IsNotLegalError):
            self.card.do_action("player1", "player2")

    def test_one_centre(self):
        with self.assertRaises(IsNotLegalError):
            self.card.do_action("centre", None)

    def test_two_centres(self):
        with self.assertRaises(IsNotLegalError):
            self.card.do_action("left", "right")

    # Test all of the functions, make sure none of them give an error and that they return the right type of object (no testing of the logic yet)
    def test_str(self):
        self.assertIsInstance(str(self.card), str)

    def test_actions_wanted(self):
        self.assertIsInstance(self.card.actions_wanted(), list)

    def test_is_legal_action(self):
        # Regardless of which options are used it should still return either True or False
        possible_options = [None, 'player1', 'player2', 'self', 'left', 'centre', 'right']

        for option1 in possible_options:
            for option2 in possible_options:
                self.assertIsInstance(self.card.is_legal_action(option1, option2), bool)

    def test_need_others(self):
        # Either the card does need others 
        # in which case the return value should be a list, 
        # or it doesn't in which case the return value should be None
        self.assertIsInstance(self.card.need_others(), (type(None), list))

    def test_add_others(self):
        # if need_others returns None 
        # then add_others should be an exception, 
        # otherwise add_others should work fine
        if self.card.need_others():
            self.card.add_others(['player1', 'self'])
        else:
            with self.assertRaises(NoKnowledgeError):
                self.card.add_others(['player1', 'self'])

    def test_init_text(self):
        self.assertIsInstance(self.card.init_text(), str)

    def test_any_changes(self):
        # The card can do anything it wants here except throw an exception
        self.card.any_changes()





