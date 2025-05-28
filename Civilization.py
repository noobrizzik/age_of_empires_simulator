from Villager import Villager
import random
from Unit import Unit
import json
from Building import House, TownCenter, MilitaryBuilding

from Utils import *

class Civilization:
    def __init__(self, name):
        self.name = name
        self.age = 0
        self.villagers = [Villager(name) for _ in range(6)]
        self.villager_assignments = []  # No assignments at start
        self.villagers_per_turn = 1  # Will increase with each age
        self.units = []
        self.buildings = [TownCenter(name, 0)]
        self.houses = []
        self.military_buildings = []
        self.resources = {r: 250 for r in RESOURCES}
        self.population = len(self.villagers)
        self.max_population = 10 if name != "Mongol" else MAX_POPULATION
        self.turn = 1
        if name == "Mongol":
            self.max_population = MAX_POPULATION

    def can_pay(self, cost):
        return all(self.resources.get(r, 0) >= v for r, v in cost.items())

    def pay(self, cost):
        for r, v in cost.items():
            self.resources[r] -= v

    def next_age(self, silent=False):
        if self.age < 3:
            cost = AGE_UP_COSTS[self.age]
            if not self.can_pay(cost):
                if not silent:
                    print(f"Not enough resources to advance age! Required: {cost}")
                return
            self.pay(cost)
            self.age += 1
            self.buildings = [TownCenter(self.name, self.age) if b.type == "town_center" else b for b in self.buildings]
            self.villagers_per_turn += 1
            if not silent:
                print(f"{self.name} advanced to {AGES[self.age]}! Now you get {self.villagers_per_turn} villagers per turn.")
            new_villagers = []
            new_assignments = []
            for _ in range(self.villagers_per_turn):
                if self.population < self.max_population:
                    new_villagers.append(Villager(self.name))
            if new_villagers and not silent:
                new_assignments = self.assign_new_villagers(len(new_villagers))
            elif new_villagers:
                # AI veya sessiz modda otomatik dağıt
                per_res = len(new_villagers) // len(RESOURCES)
                extra = len(new_villagers) % len(RESOURCES)
                res_list = []
                for r in RESOURCES:
                    res_list += [r] * per_res
                res_list += random.choices(RESOURCES, k=extra)
                random.shuffle(res_list)
                new_assignments = res_list
            for v, a in zip(new_villagers, new_assignments):
                self.villagers.append(v)
                self.villager_assignments.append(a)
                self.population += 1
            if not silent:
                print(f"You advanced an age, {len(new_villagers)} new villagers added! Total villagers: {len(self.villagers)}")
        else:
            if not silent:
                print("Already at max age.")

    def add_house(self, silent=False, count=1):
        if self.name == "Mongol":
            if not silent:
                print("Mongols do not need houses!")
            return
        house_cost = {"wood": 50, "stone": 25}
        max_possible = min(
            self.resources["wood"] // house_cost["wood"],
            self.resources["stone"] // house_cost["stone"]
        )
        count = min(count, max_possible)
        if count <= 0:
            if not silent:
                print("Not enough resources! (Required: 50 wood, 25 stone)")
            return
        for r in RESOURCES:
            self.resources[r] -= house_cost.get(r, 0) * count
        for _ in range(count):
            house = House(self.name)
            self.houses.append(house)
            self.max_population += house.pop
            self.buildings.append(house)
        if not silent:
            print(f"{count} {house.name} built! Max population: {self.max_population}")

    def build_military(self, building_type, silent=False, count=1):
        min_age = MILITARY_BUILDINGS[building_type]["age"]
        if building_type in CIV_BUILDING_EXCEPTIONS.get(self.name, {}):
            min_age = CIV_BUILDING_EXCEPTIONS[self.name][building_type]
        if self.age < min_age:
            if not silent:
                print(f"{MILITARY_BUILDINGS[building_type]['name']} requires age {min_age+1}.")
            return
        cost = {"wood": 150}
        max_possible = self.resources["wood"] // cost["wood"]
        count = min(count, max_possible)
        if count <= 0:
            if not silent:
                print("Not enough resources to build military building!")
            return
        for r in RESOURCES:
            self.resources[r] -= cost.get(r, 0) * count
        for _ in range(count):
            b = MilitaryBuilding(MILITARY_BUILDINGS[building_type]["name"], 500, building_type)
            self.military_buildings.append(b)
            self.buildings.append(b)
        if not silent:
            print(f"{count} {MILITARY_BUILDINGS[building_type]['name']} built!")

    def daily_villager_growth(self):
        new_villagers = []
        for _ in range(self.villagers_per_turn):
            if self.population < self.max_population:
                new_villagers.append(Villager(self.name))
        if new_villagers:
            assignments = self.assign_new_villagers(len(new_villagers))
            for v, a in zip(new_villagers, assignments):
                self.villagers.append(v)
                self.villager_assignments.append(a)
                self.population += 1
                print(f"New villager added! Total villagers: {len(self.villagers)}")

    def buy_villager(self, count=1):
        max_possible = self.resources["food"] // VILLAGER_BUY_COST["food"]
        count = min(count, max_possible, self.max_population - self.population)
        if count <= 0:
            if self.population >= self.max_population:
                print("Population limit reached!")
            else:
                print(f"Not enough food! (Required: {VILLAGER_BUY_COST['food']})")
            return
        self.resources["food"] -= VILLAGER_BUY_COST["food"] * count
        if count > 0:
            assignments = self.assign_new_villagers(count)
            for i in range(count):
                self.villagers.append(Villager(self.name))
                self.villager_assignments.append(assignments[i])
                self.population += 1
            print(f"{count} new villager(s) bought with food!")

    def gather_resources(self, show_new_assign=True):
        # Sadece atanmamış köylüler için kaynak sor
        if show_new_assign:
            for i, assignment in enumerate(self.villager_assignments):
                if assignment is None:
                    while True:
                        res = input(f"Select resource for new villager {i+1} (food/gold/wood/stone): ").strip().lower()
                        if res in RESOURCES:
                            self.villager_assignments[i] = res
                            break
                        else:
                            print("Invalid resource, please enter again.")
        total = {r: 0 for r in RESOURCES}
        for v, res in zip(self.villagers, self.villager_assignments):
            if res is not None:
                amount = v.gather(res, self.age)
                self.resources[res] += amount
                total[res] += amount
        print(f"Resources gathered: {total}")

    def assign_villagers(self):
        print("\nTo assign villagers to resources:")
        print("1. Auto distribute (evenly)")
        print("2. Manual assignment (ask for each villager)")
        print("3. Bulk assignment (assign a number of villagers to each resource)")
        choice = input("Your choice (1/2/3): ").strip()
        assignments = []
        n = len(self.villagers)
        if choice == "1":
            per_res = n // len(RESOURCES)
            extra = n % len(RESOURCES)
            res_list = []
            for r in RESOURCES:
                res_list += [r] * per_res
            res_list += random.choices(RESOURCES, k=extra)
            random.shuffle(res_list)
            assignments = res_list
            print(f"Auto assignment: {dict((r, assignments.count(r)) for r in RESOURCES)}")
        elif choice == "3":
            remaining = n
            assignments = [None] * n
            print("Resources: " + ", ".join(RESOURCES))
            idx = 0
            for r in RESOURCES:
                if remaining == 0:
                    break
                while True:
                    try:
                        cnt = int(input(f"How many villagers to assign to '{r}'? (Remaining: {remaining}): "))
                        if 0 <= cnt <= remaining:
                            break
                    except:
                        pass
                    print("Invalid number.")
                for _ in range(cnt):
                    assignments[idx] = r
                    idx += 1
                remaining -= cnt
            # Kalan köylüler varsa ilk kaynağa ata
            for i in range(n):
                if assignments[i] is None:
                    assignments[i] = RESOURCES[0]
            print(f"Bulk assignment: {dict((r, assignments.count(r)) for r in RESOURCES)}")
        else:
            res_options = {str(i+1): r for i, r in enumerate(RESOURCES)}
            print("Resources:")
            for i, r in enumerate(RESOURCES, 1):
                print(f"{i}. {r}")
            for i in range(n):
                while True:
                    res_in = input(f"Resource for villager {i+1} (number or name): ").strip().lower()
                    if res_in in res_options:
                        res = res_options[res_in]
                        break
                    elif res_in in RESOURCES:
                        res = res_in
                        break
                    else:
                        print("Invalid resource, please enter again.")
                assignments.append(res)
        self.villager_assignments = assignments

    def assign_new_villagers(self, new_count):
        print(f"\nYou must assign resources for {new_count} new villager(s).")
        print("1. Auto distribute (evenly)")
        print("2. Manual assignment (ask for each villager)")
        print("3. Bulk assignment (assign a number of villagers to each resource)")
        choice = input("Your choice (1/2/3): ").strip()
        assignments = []
        n = new_count
        if choice == "1":
            per_res = n // len(RESOURCES)
            extra = n % len(RESOURCES)
            res_list = []
            for r in RESOURCES:
                res_list += [r] * per_res
            res_list += random.choices(RESOURCES, k=extra)
            random.shuffle(res_list)
            assignments = res_list
            print(f"Auto assignment: {dict((r, assignments.count(r)) for r in RESOURCES)}")
        elif choice == "3":
            remaining = n
            assignments = [None] * n
            print("Resources: " + ", ".join(RESOURCES))
            idx = 0
            for r in RESOURCES:
                if remaining == 0:
                    break
                while True:
                    try:
                        cnt = int(input(f"How many villagers to assign to '{r}'? (Remaining: {remaining}): "))
                        if 0 <= cnt <= remaining:
                            break
                    except:
                        pass
                    print("Invalid number.")
                for _ in range(cnt):
                    assignments[idx] = r
                    idx += 1
                remaining -= cnt
            # Kalan köylüler varsa ilk kaynağa ata
            for i in range(n):
                if assignments[i] is None:
                    assignments[i] = RESOURCES[0]
            print(f"Bulk assignment: {dict((r, assignments.count(r)) for r in RESOURCES)}")
        else:
            res_options = {str(i+1): r for i, r in enumerate(RESOURCES)}
            print("Resources:")
            for i, r in enumerate(RESOURCES, 1):
                print(f"{i}. {r}")
            for i in range(n):
                while True:
                    res_in = input(f"Resource for new villager {i+1} (number or name): ").strip().lower()
                    if res_in in res_options:
                        res = res_options[res_in]
                        break
                    elif res_in in RESOURCES:
                        res = res_in
                        break
                    else:
                        print("Invalid resource, please enter again.")
                assignments.append(res)
        return assignments

    def can_train_unit(self, unit_cost):
        return all(self.resources[r] >= unit_cost.get(r, 0) for r in RESOURCES)

    def train_unit(self, building_type, unit_idx, silent=False, count=1, discount=0.0):
        if not any(b.type == building_type for b in self.military_buildings):
            if not silent:
                print(f"You need a {MILITARY_BUILDINGS[building_type]['name']} to train this unit!")
            return False
        available_units = [u for u in CIV_UNITS[self.name][building_type] if u["age"] <= self.age]
        if unit_idx < 0 or unit_idx >= len(available_units):
            if not silent:
                print("Invalid unit selection.")
            return False
        unit_data = available_units[unit_idx]
        # İndirimli maliyet uygula
        cost = unit_data["cost"]
        if discount > 0 and cost:
            cost = {r: int(cost[r] * (1 - discount) + 0.9999) for r in cost}
        max_possible = min(
            self.max_population - self.population,
            min(self.resources.get(r, 0) // cost.get(r, 0) if cost.get(r, 0) > 0 else float('inf') for r in cost)
        )
        count = min(count, max_possible)
        if count <= 0:
            if not silent:
                print("Not enough resources or population limit reached!")
            return False
        for r in RESOURCES:
            self.resources[r] -= cost.get(r, 0) * count
        for _ in range(count):
            unit = Unit(unit_data["name"], unit_data["hp"], unit_data["atk"], unit_data["type"], unit_data["cost"])
            self.units.append(unit)
            self.population += 1
        if not silent:
            print(f"{count} {unit_data['name']} trained!")
        return True

    def status(self):
        return {
            "civilization": self.name,
            "age": AGES[self.age],
            "resources": self.resources,
            "population": self.population,
            "max_population": self.max_population,
            "villagers": len(self.villagers),
            "villager_assignments": self.villager_assignments,
            "units": [u.name for u in self.units],
            "buildings": [b.name for b in self.buildings],
            "military_buildings": [b.name for b in self.military_buildings],
            "turn": self.turn
        }

    def save(self, filename):
        try:
            with open(filename, "w") as f:
                json.dump(self.status(), f, indent=2)
        except Exception as e:
            raise SimulationError(f"Save failed: {e}")

    def ai_turn(self):
        style = CIV_AI_STYLES[self.name]
        # Askeri bina kurma (öncelikli binalar)
        for btype in style["unit_pref"]:
            if not any(b.type == btype for b in self.military_buildings):
                self.build_military(btype, silent=True)
        # Diğer askeri binalar (daha düşük ihtimalle)
        for btype in MILITARY_BUILDINGS:
            if btype not in style["unit_pref"]:
                if not any(b.type == btype for b in self.military_buildings):
                    if random.random() < 0.3:
                        self.build_military(btype, silent=True)
        # Çağ atlama (ekonomik odaklılar daha erken atlar)
        if self.age < 3 and random.random() < (0.25 + style["eco"] * 0.25):
            self.next_age(silent=True)
            apply_age_bonuses(self)
        # Ev yapımı (ekonomik ve pop odaklılar daha çok yapar)
        if self.name != "Mongol" and random.random() < (style["house_priority"] + 0.2):
            self.add_house(silent=True)
        # Asker üretimi (odak birimlere öncelik, daha yüksek olasılık)
        for btype in style["unit_pref"]:
            if btype in CIV_UNITS[self.name]:
                available_units = [u for u in CIV_UNITS[self.name][btype] if u["age"] <= self.age]
                if available_units and any(b.type == btype for b in self.military_buildings):
                    # Saldırganlık arttıkça daha çok asker üretir
                    for _ in range(random.randint(1, 3)):  # AI bir turda birden fazla asker üretebilir
                        if random.random() < (0.7 + style["aggression"] * 0.3):
                            idx = random.randint(0, len(available_units)-1)
                            self.train_unit(btype, idx, silent=True)
        # Diğer birimler (daha düşük ihtimalle, ama yine de üret)
        for btype in MILITARY_BUILDINGS:
            if btype not in style["unit_pref"] and btype in CIV_UNITS[self.name]:
                available_units = [u for u in CIV_UNITS[self.name][btype] if u["age"] <= self.age]
                if available_units and any(b.type == btype for b in self.military_buildings):
                    for _ in range(random.randint(1, 2)):
                        if random.random() < 0.3:
                            idx = random.randint(0, len(available_units)-1)
                            self.train_unit(btype, idx, silent=True)
        # Kuşatma odaklılar daha çok siege birimi üretir
        if "siege" in style["unit_pref"]:
            btype = "siege"
            if btype in CIV_UNITS[self.name]:
                available_units = [u for u in CIV_UNITS[self.name][btype] if u["age"] <= self.age]
                if available_units and any(b.type == btype for b in self.military_buildings):
                    for _ in range(random.randint(1, 2)):
                        if random.random() < (style["siege"] + 0.3):
                            idx = random.randint(0, len(available_units)-1)
                            self.train_unit(btype, idx, silent=True)


def apply_age_bonuses(civ):
    # Çağ bonusu: mevcut ve yeni askerlerin gücü artar
    for u in civ.units:
        u.attack = int(u.attack * AGE_BONUSES[civ.age])
        u.hp = int(u.hp * AGE_BONUSES[civ.age])