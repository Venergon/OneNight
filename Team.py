from enum import Enum

class Team(Enum):
    Villager = "Villagers"
    Werewolf = "Werewolves"
    Tanner = "Tanner"
    Hunter = "Hunter"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


