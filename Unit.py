class Unit:
    def __init__(self, name, hp, attack, unit_type, cost, special=None):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.type = unit_type
        self.cost = cost
        self.special = special or {}

    def is_alive(self):
        return self.hp > 0