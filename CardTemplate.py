class Card(object):
    def __init__(self, game, player):
        self.game = game
        self.original_player = player
        self.player = player
        self.win_team = None
        self.death_team = None
        self.others = None

    def __str__(self):
        return "a generic character"

    def actions_wanted(self):
        raise NotImplementedError

    @staticmethod
    def __repr__():
        return self.__name__

    def __repr__(self):
        return "{}(!currentgame!, {}, {})".format(type(self).__name__, repr(self.player), repr(self.original_player))

    def is_legal_action(self, person1, person2):
        raise NotImplementedError

    def need_others(self):
        raise NotImplementedError

    def add_others(self, others):
        self.others = others

    def init_text(self):
        raise NotImplementedError

    def do_action(self, person1=None, person2=None):
        raise NotImplementedError

    def any_changes(self):
        raise NotImplementedError

    def die(self):
        return self.death_team

    def win(self, winners):
        if self.win_team in winners:
            return True
        else:
            return False

    def change_player(self, player):
        self.player = player
