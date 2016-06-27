from enum import Enum


class IsNotLegalError(TypeError):
    pass


class NoKnowledgeError(Exception):
    pass


class InvalidVoteError(ValueError):
    pass


class SelfVoteError(InvalidVoteError):
    pass


class InvalidPlayerVoteError(InvalidVoteError):
    pass

centre_cards = ["left", "centre", "right"]


class Team(Enum):
    Villager = "Villagers"
    Werewolf = "Werewolves"
    Tanner = "Tanner"
    Hunter = "Hunter"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

