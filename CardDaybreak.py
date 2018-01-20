from CardTemplate import *
from DotH import *
from Team import Team
import copy

# TODO: Curator, Revealer, Bodyguard, Witch, Sentinel, Paranomal Investigator


# Can move everyone's card either one to the left or one to the right, Townie
class VillageIdiot(Card):
    def actions_wanted(self):
        return [("direction",), None]

    def __init__(self, game, player):
        super().__init__(game, player)
        self.win_team = Team.Villager
        self.death_team = Team.Villager

        self.order_num = 7.2

    def __str__(self):
        return "The chaotic village idiot"

    def is_legal_action(self, person1, person2):
        if person2 is not None:
            return False
        if person1 is None or person1 == "left" or person1 == "right":
            return True
        else:
            return False

    def need_others(self):
        return None

    def add_others(self, others):
        raise NoKnowledgeError

    def init_text(self):
        return "You are the Village Idiot! Always the klutz, you once tripped on your own foot and broke the body " \
               "swap device you were given as a birthday present. Now it is unstable and if activated will move " \
               "the consciousness of everyone but you one body in a direction. You can choose to activate it and " \
               "move everyone left, move everyone right or not activate it at all (in which case you choose no target)."

    def do_action(self, person1=None, person2=None):
        if not self.is_legal_action(person1, person2):
            raise IsNotLegalError
        elif person1 is None:
            return "You decide not to activate the device, there's gonna be enough chaos tonight."
        else:
            # Find all of the players so we know which things to swap
            other_players = []

            for player in self.game.arranged_players:
                # This set of conditions is to make sure not to swap yourself and to wrap around
                if player == self.original_player:
                    continue
                else:
                    other_players.append(player)

            if person1 == 'left':
                # Swap from the left to the right, this will cause everyone to move to the left
                # Ignore swapping the last player with the first as that will actually put the second player last
                previous_player = None
                for player in reversed(other_players):
                    if previous_player is not None:
                        self.game.swap(previous_player, player)

                    previous_player = player

                return "You activate the device and swap everyone's roles one to the left. You however feel like you " \
                       "haven't been swapped... at least not by your device..."

            elif person1 == 'right':
                # Do the same as for moving to the left, but instead start from the right and move left
                previous_player = None
                for player in other_players:
                    if previous_player is not None:
                        self.game.swap(previous_player, player)

                    previous_player = player


                return "You activate the device and swap everyone's roles one to the right. You however feel like you " \
                       "haven't been swapped... at least not by your device..."

    def any_changes(self):
        pass

# Like the seer but can only see a centre card
class ApprenticeSeer(Card):
    def __init__(self, game, player):
        super().__init__(game, player)
        self.win_team = Team.Villager
        self.death_team = Team.Villager

        self.order_num = 5.2

    def __str__(self):
        return "the curious Apprentice Seer"

    def actions_wanted(self):
        return [("centre",), None]

    def is_legal_action(self, person1, person2):
        if person2 is not None:
            return False
        if person1 is None or person1 in centre_cards:
            return True
        return False

    def need_others(self):
        return None

    def add_others(self, others):
        raise NoKnowledgeError

    def init_text(self):
        return "You are the Apprentice Seer! Since you are still learning, " \
               "you only have the power to look at one centre card."

    def do_action(self, person1=None, person2=None):
        if not self.is_legal_action(person1, person2):
            raise IsNotLegalError
        elif person1 is None:
            return "Still not confident in your abilities, you decide to stay safe for tonight."
        else:
            return "You sense that {} is not currently with us".format(self.game.peek(person1))

    def any_changes(self):
        pass

# Does not wake up with the other werewolves, werewolf
class DreamWolf(Wolf):
    def actions_wanted(self):
        return [None]

    def __init__(self, game, player):
        super().__init__(game, player)
        self.win_team = Team.Werewolf
        self.death_team = Team.Werewolf

    def __str__(self):
        return "THE LAZY DREAM WOLF"

    def is_legal_action(self, person1, person2):
        if person1 is not None or person2 is not None:
            return False
        else:
            return True

    def need_others(self):
        return None

    def add_others(self, others):
        raise NoKnowledgeError

    def init_text(self):
        return "You are the Dream Wolf! Your strict sleep pattern means that you could not get up during the " \
                "night and so do not know who the other werewolves are. They however do know who you are."

    def do_action(self, person1=None, person2=None):
        if not self.is_legal_action(person1, person2):
            raise IsNotLegalError
        else:
            return "After a pleasant sleep, you wake up energised and ready to slay some villagers."

    def any_changes(self):
        pass


# Can view another player's card, Werewolf
class MysticWolf(Wolf):
    def actions_wanted(self):
        if self.others is None:
            return [('other', 'centre'), ('other',), (None,'centre'), None]
        else:
            return [('other',), None]

    def __init__(self, game, player):
        super().__init__(game, player)
        self.win_team = Team.Werewolf
        self.death_team = Team.Werewolf

        self.order_num = 2.3

    def __str__(self):
        return "THE MYSTERIOUS MYSTIC WOLF"

    def is_legal_action(self, person1, person2):
        person1_valid = (person1 is None or (person1 not in centre_cards and person1 != self.original_player))
        person2_valid = (person2 is None or (self.others is None and person2 in centre_cards))

        return person1_valid and person2_valid

    def need_others(self):
        return [Wolf]

    def add_others(self, others):
        self.others = copy.deepcopy(others)
        if self.original_player in self.others:
            self.others.remove(self.original_player)
        if not self.others:
            self.others = None

    def init_text(self):
        if self.others is None:
            return "You are the Mystic Wolf! Although you do not have any allies, you may view one other player's " \
                   "card. You may also view one of the centre cards (the other player is the first target, the " \
                   "centre card is the second)."
        else:
            return ("You are the Mystic Wolf! In addition to working together with the other werewolves ({}), you "
                    "may pick one other player to view their card.").format(", ".join(self.others))

    def do_action(self, person1=None, person2=None):
        if not self.is_legal_action(person1, person2):
            raise IsNotLegalError
        else:
            text_to_return = []
            if person1:
                text_to_return.append(("Using ancient magic lost to all but a few, you see that {} is actually {}."
                                       ).format(person1, self.game.peek(person1)))
            if person2:
                text_to_return.append("As you wait for sunrise, you see {} running out of the village."
                                      .format(self.game.peek(person2)))

            return " ".join(text_to_return)

    def any_changes(self):
        pass


# Must convert one other player into a werewolf, Werewolf
class AlphaWolf(Wolf):
    def __init__(self, game, player):
        super().__init__(game, player)
        self.win_team = Team.Werewolf
        self.death_team = Team.Werewolf

        self.order_num = 2.2

    def __str__(self):
        return "THE WILY ALPHA WOLF"

    def actions_wanted(self):
        if self.others is None:
            return [('non_wolf', 'centre'), ('non_wolf',)]
        else:
            return [('non_wolf',)]

    def is_legal_action(self, person1, person2):
        person1_valid = (person1 is not None and person1 not in centre_cards and not isinstance(self.game.original[person1], Wolf))
        person2_valid = (person2 is None or (self.others is None and person2 in centre_cards))
        return (person1_valid and person2_valid)

    def need_others(self):
        return [Wolf]

    def add_others(self, others):
        self.others = copy.deepcopy(others)
        if self.original_player in self.others:
            self.others.remove(self.original_player)
        if not self.others:
            self.others = None

    def init_text(self):
        if self.others is None:
            return "You are the Alpha Wolf! You do not currently have any allies however you must pick one villager " \
                   "to convert into a wolfling (they will have no knowledge of being converted). As well, " \
                   "you may pick one of the centre cards to look at (the conversion is your first target, " \
                   "viewing is your second)."
        else:
            return ("You are the Alpha Wolf! In addition to working together with the other werewolves ({}), you "
                    "must also pick one villager to convert into a werewolf (they will have no knowledge of being "
                    "converted, you cannot pick another werewolf).").format(", ".join(self.others))

    def do_action(self, person1=None, person2=None):
        if not self.is_legal_action(person1, person2):
            raise IsNotLegalError
        else:
            self.game.swap(person1, 'wolf')

            if person2:
                return ("Along with converting {} into a werewolf, you saw that {} was {}."
                    ).format(person1, person2, self.game.peek(person2))
            else:
                return ("Excellent, your new apprentice {} is well on their way to becoming a full grown werewolf. " \
                       "Today will be fun...").format(person1)

    def any_changes(self):
        pass

# Special role to be used ONLY as the centre wolf card, other than that is effectively a normal werewolf
class Wolfling(Wolf):
    def __init__(self, game, player):
        super().__init__(game, player)
        self.win_team = Team.Werewolf
        self.death_team = Team.Werewolf

    def __str__(self):
        return "THE CUTE AND CUDDLY WOLFLING"

    def actions_wanted(self):
        raise ValueError("The Wolfling should never have actions_wanted called on it")

    def need_others(self):
        raise ValueError("The Wolfling should never have need_others called on it")

    def add_others(self, others):
        raise ValueError("The Wolfling should never have add_others called on it")

    def init_text(self):
        raise ValueError("The Wolfling should never have init_text called on it")

    def is_legal_action(self, person1, person2):
        raise ValueError("The Wolfling should never have is_legal_action called on it")

    def do_action(self, person1=None, person2=None):
        raise ValueError("The Wolfling should never have do_action called on it")

    def any_changes(self):
        pass
