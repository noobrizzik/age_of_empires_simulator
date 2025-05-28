from Utils import BASE_TC_HP

class Building:
    def __init__(self, name, hp, building_type):
        self.name = name
        self.hp = hp
        self.type = building_type

    def is_destroyed(self):
        return self.hp <= 0

# Şehir Merkezi
class TownCenter(Building):
    def __init__(self, civ, age):
        hp = BASE_TC_HP["Chinese"][age] if civ == "Chinese" else BASE_TC_HP["default"][age]
        super().__init__("Town Center", hp, "town_center")

# Nüfus Binası
class House(Building):
    def __init__(self, civ):
        if civ == "Chinese":
            name = "Village"
            hp = 300
            pop = 20
        else:
            name = "House"
            hp = 150
            pop = 10
        super().__init__(name, hp, "population")
        self.pop = pop

# Askeri Bina
class MilitaryBuilding(Building):
    def __init__(self, name, hp, building_type):
        super().__init__(name, hp, building_type)
