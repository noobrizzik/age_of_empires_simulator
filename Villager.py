from Utils import VILLAGER_BASE_GATHER, CIV_BONUSES, AGE_BONUSES

class Villager:
    def __init__(self, civ):
        self.civ = civ

    def gather(self, resource, age):
        base = VILLAGER_BASE_GATHER
        bonus = CIV_BONUSES[self.civ][resource]
        age_bonus = AGE_BONUSES[age]
        return int(base * bonus * age_bonus)