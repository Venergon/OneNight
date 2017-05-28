from CardBase import *

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

centre_cards = ["left", "centre", "right", "wolf"]

STAGE_BEFORE = 0
STAGE_NIGHT = 1
STAGE_DAY = 2
STAGE_DONE = 3



