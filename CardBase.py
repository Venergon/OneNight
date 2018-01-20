from CardTemplate import *
from DotH import *
from Team import Team
import copy

centre_cards = ["left", "centre", "right", "wolf"]

# TODO: Doppelganger if I ever get around to doing it


# No special action, Townie
class Villager(Card):
    def __init__(self, game, player):
        super().__init__(game, player)
        self.win_team = Team.Villager
        self.death_team = Team.Villager

    def __str__(self):
        return "a lowly Villager"

    def actions_wanted(self):
        return [None]

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
        return "You are a Villager! You have no special abilities but must work with the other villagers " \
                "to find the werewolves."

    def do_action(self, person1=None, person2=None):
        if not self.is_legal_action(person1, person2):
            raise IsNotLegalError
        else:
            return "You had a nice day tending to your cattle and ensuring a good harvest, assuming you survive " \
                   "tomorrow."

    def any_changes(self):
        pass


# Can look at one other player's card or two of the centre cards, Townie
class Seer(Card):
    def __init__(self, game, player):
        super().__init__(game, player)
        self.win_team = Team.Villager
        self.death_team = Team.Villager
        self.order_num = 5

    def __str__(self):
        return "the mysterious Seer"

    def actions_wanted(self):
        return [("other", ), ("centre", "centre"), None]

    def is_legal_action(self, person1, person2):
        if person1 is None and person2 is None:
            return True
        elif person1 not in centre_cards and person1 in self.game.players and person2 is None:
            return True
        elif person1 in centre_cards and person2 is not None and person2 in centre_cards:
            return True
        else:
            return False

    def need_others(self):
        return None

    def add_others(self, others):
        raise NoKnowledgeError

    def init_text(self):
        return "You are the Seer! You may look at two centre cards or one card belonging to any other player."

    def do_action(self, person1=None, person2=None):
        if not self.is_legal_action(person1, person2):
            raise IsNotLegalError
        elif person1 is None:
            return "You decided that drawing attention to yourself through your magic might alert the werewolves and " \
                   "chose to lay low for a while."
        elif person2 is not None:
            return "You sensed that both {} ({} card) and {} ({} card) are not " \
                    "currently in town".format(str(self.game.peek(person1)), str(person1), str(self.game.peek(person2)), str(person2))
        else:
            return "You sensed that {} is in fact {}".format(str(person1), str(self.game.peek(person1)))

    def any_changes(self):
        pass


# Can swap two other players' cards, Townie
class Troublemaker(Card):
    def __init__(self, game, player):
        super().__init__(game, player)
        self.win_team = Team.Villager
        self.death_team = Team.Villager
        self.order_num = 7

    def __str__(self):
        return "the mischievous Troublemaker"

    def actions_wanted(self):
        return [("other", "other"), None]

    def is_legal_action(self, person1, person2):
        if person1 is None:
            return True
        elif person2 is None or person1 in centre_cards or person2 in centre_cards:
            return False
        elif person1 == self.original_player or person2 == self.original_player:
            return False
        elif person1 not in self.game.players or person2 not in self.game.players:
            return False
        else:
            return True

    def need_others(self):
        return None

    def add_others(self, others):
        raise NoKnowledgeError

    def init_text(self):
        return "You are the Troublemaker! You may swap two cards other than your own."

    def do_action(self, person1=None, person2=None):
        if not self.is_legal_action(person1, person2):
            raise IsNotLegalError
        elif person1 is None:
            return "You recognised that this situation is too serious for practical jokes and so acted like a " \
                   "model citizen. I knew you had it in you!"
        else:
            self.game.swap(person1, person2)
            return "Ah, the most fun of practical jokes, the forced body swap. {} and {} have now changed bodies " \
                   "and roles, although you didn't get a good enough look to see " \
                   "what either of them are".format(str(person1), str(person2))

    def any_changes(self):
        pass


# Can steal someone else's card and then look at it, Townie
class Robber(Card):
    def __init__(self, game, player):
        super().__init__(game, player)
        self.win_team = Team.Villager
        self.death_team = Team.Villager
        self.order_num = 6

    def __str__(self):
        return "the dastardly Robber"

    def actions_wanted(self):
        return [("other",), None]

    def is_legal_action(self, person1, person2):
        if person1 is None:
            return True
        elif person2 is not None:
            return False
        elif person1 in centre_cards or person1 == self.original_player:
            return False
        elif person1 not in self.game.players:
            return False
        else:
            return True

    def need_others(self):
        return None

    def add_others(self, others):
        raise NoKnowledgeError

    def init_text(self):
        return "You are the Robber! You may steal someone else's card. You will then be told what it is"

    def do_action(self, person1=None, person2=None):
        if not self.is_legal_action(person1, person2):
            raise IsNotLegalError
        elif person1 is None:
            return "You have gone back on your old ways and chosen not to steal anything. Good on you!"
        else:
            original_player = self.original_player
            self.game.swap(person1, self.original_player)
            return "You have stolen {}'s card and are now {}!".format(str(person1), self.game.peek(original_player))

    def any_changes(self):
        pass


# Knows other Mason, Townie
class Mason(Card):
    def __init__(self, game, player):
        super().__init__(game, player)
        self.win_team = Team.Villager
        self.death_team = Team.Villager

    def __str__(self):
        return "an ominous Mason"

    def actions_wanted(self):
        return [None]

    def is_legal_action(self, person1, person2):
        if person1 is not None or person2 is not None:
            return False
        else:
            return True

    def need_others(self):
        return [Mason]

    def add_others(self, others):
        self.others = copy.deepcopy(others)
        if self.original_player not in centre_cards:
            self.others.remove(self.original_player)
        if not self.others:
            self.others = None

    def init_text(self):
        if self.others is None:
            return "You are a Mason! The other mason appears to have gone missing so you are on your own for now."
        else:
            return ("You are a Mason! You and {} have known each other for a long time and know that neither of you "
                    "could ever be werewolves").format(", ".join(map(lambda x: str(x), self.others)))

    def do_action(self, person1=None, person2=None):
        if not self.is_legal_action(person1, person2):
            raise IsNotLegalError
        else:
            return "You decided that this one town was not important enough to waste your night on and went back to" \
                   "planning eventual world control."

    def any_changes(self):
        pass


# Must swap their card with a centre card, Townie
class Drunk(Card):
    def __init__(self, game, player):
        super().__init__(game, player)
        self.win_team = Team.Villager
        self.death_team = Team.Villager

        self.order_num = 8

    def __str__(self):
        return "the helpless Drunk"

    def actions_wanted(self):
        return [("centre",)]

    def is_legal_action(self, person1, person2):
        if person1 is None or person2 is not None:
            return False
        elif person1 not in centre_cards:
            return False
        else:
            return True

    def need_others(self):
        return None

    def add_others(self, others):
        raise NoKnowledgeError

    def init_text(self):
        return "You are the Drunk! You cannot remember much about what happened last night or who you are. " \
               "You must choose"

    def do_action(self, person1=None, person2=None):
        if not self.is_legal_action(person1, person2):
            raise IsNotLegalError
        else:
            self.game.swap(person1, self.original_player)
            return "You stumble out of bed with a mind numbing hangover. You do not remember who or what you are " \
                   "but one thing is for sure - you are never going drinking again."

    def any_changes(self):
        pass


# If they are killed they kill who they vote for, Townie
class Hunter(Card):
    def __init__(self, game, player):
        super().__init__(game, player)
        self.win_team = Team.Villager
        self.death_team = Team.Hunter

    def __str__(self):
        return "the courageous Hunter"

    def actions_wanted(self):
        return [None]

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
        return "You are the Hunter! You do not have anything to do during the night but if you are killed you will " \
               "also kill whoever you are voting for"

    def do_action(self, person1=None, person2=None):
        if not self.is_legal_action(person1, person2):
            raise IsNotLegalError
        else:
            return "You looked around your house for your favourite silver bullets and polished up your gun, " \
                   "ensuring you are prepared for tomorrow."

    def any_changes(self):
        pass


# Sees their final role as the last thing in the night, Townie
class Insomniac(Card):
    def __init__(self, game, player):
        super().__init__(game, player)
        self.win_team = Team.Villager
        self.death_team = Team.Villager

        self.order_num = 9

    def __str__(self):
        return "the irritable Insomniac"

    def actions_wanted(self):
        return [None]

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
        return "You are the Insomniac! Due to your poor sleeping habits, you will be awake for any mysterious " \
               "happenings and will know if you have become something else."

    def do_action(self, person1=None, person2=None):
        if not self.is_legal_action(person1, person2):
            raise IsNotLegalError
        else:
            if self.original_player == self.player:
                return "You stayed up all night but the night has been surprisingly normal. Despite everything, it's " \
                       "still you."
            else:
                return "You stayed up all night alert for any changes. Suddenly a weird sensation comes over you. " \
                       "You feel a lot like {}!".format(str(self.game.peek(self.original_player)))

    def any_changes(self):
        pass


# Can see other werewolves, if there is only one werewolf they can look at a centre card, Werewolf
class Werewolf(Wolf):
    def __init__(self, game, player):
        super().__init__(game, player)
        self.win_team = Team.Werewolf
        self.death_team = Team.Werewolf
        self.order_num = 2

    def __str__(self):
        return "A BLOODY WEREWOLF"

    def actions_wanted(self):
        if self.others is not None:
            return [None]
        else:
            return [("centre",), None]

    def is_legal_action(self, person1, person2):
        if self.others is not None:
            if person1 is not None:
                return False
            else:
                return True
        elif person2 is not None:
            return False
        elif person1 is None:
            return True
        elif person1 not in centre_cards:
            return False
        else:
            return True

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
            return "You are a Werewolf! Unfortunately there are no other werewolves however that means you may " \
                   "choose a card from the centre to look at. You win with the werewolves so make sure you do not die."
        else:
            return ("You are a Werewolf! You and the other werewolves ({}) must work to make sure none of you "
                    "are killed.").format(", ".join(map(lambda x: str(x), self.others)))

    def do_action(self, person1=None, person2=None):
        if not self.is_legal_action(person1, person2):
            raise IsNotLegalError
        elif person1 is None:
            return "You get a good night's sleep in preparation for tomorrow. Just one more day and this town is " \
                   "yours; don't blow it!"
        elif isinstance(self.game.peek(person1), Wolf):
            return ("As you are preparing for tomorrow night, you see another {}, deserting the mission. "
                    "You realise your mission is going to be a lot tougher...").format(str(self.game.peek(person1)))
        else:
            return ("You scan the area, ready to pounce on any unsuspecting villagers. Luckily for you, {} chose "
                    "tonight of all nights to sneak out to their lover. You pounce and slowly rip them apart limb by "
                    "limb. Perfect, you now have a full stomach and a flawless "
                    "disguise...").format(str(self.game.peek(person1)))

    def any_changes(self):
        pass


# Sees the werewolves, dying does not cause a werewolf loss, Werewolf
class Minion(Card):
    def __init__(self, game, player):
        super().__init__(game, player)
        self.win_team = Team.Werewolf
        self.death_team = Team.Villager

    def __str__(self):
        return "THE TRAITOROUS MINION"

    def actions_wanted(self):
        return [None]

    def is_legal_action(self, person1, person2):
        if person1 is not None or person2 is not None:
            return False
        else:
            return True

    def need_others(self):
        return [Wolf]

    def add_others(self, others):
        self.others = copy.deepcopy(others)

    def init_text(self):
        if self.others is None:
            return "You are the Minion! Due to the lack of werewolves, you have decided to experiment with alchemy " \
                   "and have turned yourself into a werewolf."
        else:
            return ("You are the Minion! You are working secretly to help the werewolves ({}) and don't care if you "
                    "yourself die. The werewolves do not know who you are.").format(", ".join(map(lambda x: str(x), self.others)))

    def do_action(self, person1=None, person2=None):
        if not self.is_legal_action(person1, person2):
            raise IsNotLegalError
        else:
            return 'You spent the night scheming and thinking up the ways you will trick the foolish villagers. This ' \
                   'will be fun...'

    def any_changes(self):
        if not self.game.card_in_play(Wolf):
            self.death_team = Team.Werewolf


# Wants to die, Independent
class Tanner(Card):
    def __init__(self, game, player):
        super().__init__(game, player)
        self.win_team = Team.Tanner
        self.death_team = Team.Tanner

    def __str__(self):
        return "the pitiful Tanner"

    def actions_wanted(self):
        return [None]

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
        return "You are the Tanner! You have never liked your job and see this whole werewolf commotion as a chance " \
               "to get yourself killed."

    def do_action(self, person1=None, person2=None):
        if not self.is_legal_action(person1, person2):
            raise IsNotLegalError
        else:
            return "You toil away in the late hours of the night, finally happy that this night could be your last."

    def any_changes(self):
        pass
