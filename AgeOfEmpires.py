# =========================
# Age of Empires 4 Simulation
# =========================

import json
import random
from datetime import datetime
from collections import defaultdict, Counter

from Utils import *
from Villager import Villager
from Building import TownCenter, House, MilitaryBuilding
from Unit import Unit
from Civilization import Civilization
from Civilization import CIVILIZATIONS, CIV_UNITS, AGES, AGE_BONUSES


MARKET_EXCHANGE_RATE = 0.7  # 1 birim almak için 1/0.7 = ~1.43 birim vermek gerekir

def market_exchange(player):
    print("\n--- Market ---")
    print("You can exchange your resources. Exchange rate: To get 1 unit, you must give {:.2f}.".format(1 / MARKET_EXCHANGE_RATE))
    print("Your current resources:")
    for r in RESOURCES:
        print(f"  {r}: {player.resources[r]}")
    print("Resource types: food, gold, wood, stone")
    from_res = input("Which resource do you want to sell? ").strip().lower()
    to_res = input("Which resource do you want to buy? ").strip().lower()
    if from_res not in RESOURCES or to_res not in RESOURCES or from_res == to_res:
        print("Invalid resource type.")
        return
    try:
        amount = int(input(f"How much {to_res} do you want to get? "))
        if amount <= 0:
            print("Amount must be positive.")
            return
    except Exception:
        print("Invalid amount.")
        return
    cost = int(amount / MARKET_EXCHANGE_RATE + 0.9999) 
    if player.resources[from_res] < cost:
        print(f"Not enough {from_res}! To get {amount} {to_res}, you need {cost} {from_res}.")
        return
    player.resources[from_res] -= cost
    player.resources[to_res] += amount
    print(f"You gave {cost} {from_res} and got {amount} {to_res}.")

def print_status(player, day, battle_interval, battle_done=False):
    print("\n" + "="*40)
    print(f"City: {player.name}")
    print(f"Age: {AGES[player.age]}")
    print(f"Day: {day} | Population: {player.population}/{player.max_population}")
    resource_str = " | ".join(f"{r.capitalize()}: {player.resources[r]}" for r in RESOURCES)
    print(f"Resources: {resource_str}")
    print(f"Villager count: {len(player.villagers)} (Per turn: {player.villagers_per_turn})")
    # Köylü atamaları gruplu göster
    if player.villager_assignments:
        va_counter = Counter(player.villager_assignments)
        print("Villager assignments: " + ", ".join(f"{count}x {res}" for res, count in va_counter.items()))
    # Birimleri gruplu göster
    print(f"Units: {len(player.units)}")
    if player.units:
        unit_counter = Counter(u.name for u in player.units)
        print("  " + ", ".join(f"{count}x {name}" for name, count in unit_counter.items()))
    # Binaları gruplu göster
    print(f"Buildings: {len(player.buildings)}")
    if player.buildings:
        b_counter = Counter(b.name for b in player.buildings)
        print("  " + ", ".join(f"{count}x {name}" for name, count in b_counter.items()))
        tc = next((b for b in player.buildings if b.type == "town_center"), None)
        if tc:
            bar_len = 20
            if player.name == "Chinese":
                max_hp = BASE_TC_HP["Chinese"][player.age]
            else:
                max_hp = BASE_TC_HP["default"][player.age]
            ratio = max(0, min(1, tc.hp / max_hp))
            filled = int(bar_len * ratio)
            print(f"Town Center HP: [{'#'*filled}{'-'*(bar_len-filled)}] {tc.hp}")
    # Askeri binaları gruplu göster
    print(f"Military Buildings: {len(player.military_buildings)}")
    if player.military_buildings:
        mb_counter = Counter(b.name for b in player.military_buildings)
        print("  " + ", ".join(f"{count}x {name}" for name, count in mb_counter.items()))
    print(f"Turn: {player.turn}")
    if day % battle_interval == 0 and not battle_done:
        print("!!! Battle day! You must enter 'battle' as a command. !!!")
    print("="*40)

def group_units_for_battle(units):
    """Gruplar: (isim, tip, saldırı) -> {'count', 'hp', 'attack', 'unit'}"""
    grouped = {}
    for u in units:
        key = (u.name, u.type, u.attack)
        if key not in grouped:
            grouped[key] = {"count": 0, "hp": 0, "attack": u.attack, "unit": u}
        grouped[key]["count"] += 1
        grouped[key]["hp"] += u.hp
    return list(grouped.values())

def player_battle_turn_grouped(player, enemy):
    # Gruplı seçimli savaş
    if not player.units or not enemy.units:
        return
    print("\nSavaş turunuz!")
    # Grupları oluştur
    player_groups = group_units_for_battle(player.units)
    enemy_groups = group_units_for_battle(enemy.units)
    print("Sizin birlikleriniz:")
    for idx, g in enumerate(player_groups):
        print(f"{idx+1}. {g['count']} Adet {g['unit'].name} (HP:{g['hp']} ATK:{g['attack']})")
    print("Düşman birlikleri:")
    for idx, g in enumerate(enemy_groups):
        print(f"{idx+1}. {g['count']} Adet {g['unit'].name} (HP:{g['hp']} ATK:{g['attack']})")
    try:
        attacker_idx = int(input("Saldıracak birliğin numarası: ")) - 1
        defender_idx = int(input("Hedef düşman birliğinin numarası: ")) - 1
        attacker = player_groups[attacker_idx]
        defender = enemy_groups[defender_idx]
    except Exception:
        print("Geçersiz seçim, ilk birlikler savaşıyor.")
        attacker = player_groups[0]
        defender = enemy_groups[0]
    bonus = get_counter_bonus(attacker["unit"].type, defender["unit"].type)
    damage = int(attacker["attack"] * attacker["count"] * bonus)
    defender["hp"] -= damage
    print(f"Sizin {attacker['count']}x {attacker['unit'].name} birliğiniz, {enemy.name}'nin {defender['count']}x {defender['unit'].name} birliğine {damage} hasar verdi!")
    # Hasarı uygula, birimlerin hp'sini güncelle
    apply_group_damage(enemy.units, defender, damage)

def enemy_battle_turn_grouped(enemy, player):
    # AI gruplu saldırı: ilk gruplar birbirine saldırır
    if not enemy.units or not player.units:
        return
    enemy_groups = group_units_for_battle(enemy.units)
    player_groups = group_units_for_battle(player.units)
    attacker = enemy_groups[0]
    defender = player_groups[0]
    bonus = get_counter_bonus(attacker["unit"].type, defender["unit"].type)
    damage = int(attacker["attack"] * attacker["count"] * bonus)
    defender["hp"] -= damage
    print(f"{enemy.name}'nin {attacker['count']}x {attacker['unit'].name} birliği, sizin {defender['count']}x {defender['unit'].name} birliğinize {damage} hasar verdi!")
    apply_group_damage(player.units, defender, damage)

def apply_group_damage(units, group, damage):
    # group: {'count', 'hp', 'attack', 'unit'}
    # units: ilgili tarafın units listesi
    # Hasarı sırayla birimlere uygula, ölenleri units listesinden çıkar
    affected = [u for u in units if u.name == group["unit"].name and u.attack == group["attack"] and u.type == group["unit"].type]
    i = 0
    while damage > 0 and i < len(affected):
        u = affected[i]
        if damage >= u.hp:
            damage -= u.hp
            u.hp = 0
        else:
            u.hp -= damage
            damage = 0
        i += 1
    # Ölüleri units listesinden çıkar
    units[:] = [u for u in units if u.hp > 0]

def interactive_battle(player, enemy):
    print("\n--- Savaş Başladı ---")
    turn_player = True if random.choice([True, False]) else False
    print(f"{player.name if turn_player else enemy.name} ilk saldırıyor!")
    while player.units and enemy.units:
        if turn_player:
            player_battle_turn_grouped(player, enemy)
        else:
            enemy_battle_turn_grouped(enemy, player)
        turn_player = not turn_player
    winner = player if player.units else enemy
    print(f"{winner.name} wins the battle!")
    return winner

def siege(winner, loser):
    print("Siege phase begins!")
    tc = next((b for b in loser.buildings if b.type == "town_center"), None)
    if not tc:
        print("No Town Center found!")
        return
    siege_units = [u for u in winner.units if u.type in ["ram", "bombard", "culverin", "huihui", "shah_tower"]]
    siege_damage = sum(u.attack for u in siege_units)
    if siege_damage == 0:
        print("No siege units to damage the Town Center!")
        return False
    tc.hp -= siege_damage
    print(f"{winner.name} deals {siege_damage} siege damage to {loser.name}'s Town Center!")
    if tc.hp <= 0:
        print(f"{loser.name}'s Town Center is destroyed! {winner.name} wins the game!")
        return True
    else:
        print(f"{loser.name}'s Town Center HP: {tc.hp}")
        return False

def print_unit_options(civ, building_type, age):
    # Aynı isimli birimleri sadece bir kez göster
    units_raw = [u for u in CIV_UNITS[civ][building_type] if u["age"] <= age]
    seen_names = set()
    units = []
    for u in units_raw:
        if u["name"] not in seen_names:
            units.append(u)
            seen_names.add(u["name"])
    print(f"\n{MILITARY_BUILDINGS[building_type]['name']} için mevcut birimler:")
    for idx, u in enumerate(units):
        print(f"  {idx+1}. {u['name']} (HP:{u['hp']} ATK:{u['atk']} COST:{u['cost']})")

def add_new_villager(civ):
    pass

def apply_age_bonuses(civ):
    for u in civ.units:
        u.attack = int(u.attack * AGE_BONUSES[civ.age])
        u.hp = int(u.hp * AGE_BONUSES[civ.age])

def update_after_battle(civ):
    civ.units = [u for u in civ.units if u.is_alive()]

def update_after_siege(civ):
    civ.buildings = [b for b in civ.buildings if not b.is_destroyed()]
    civ.military_buildings = [b for b in civ.military_buildings if not b.is_destroyed()]

def save_with_timestamp(civ):
    filename = input("Kaydetmek için dosya adı girin (uzantı gerekmez): ").strip()
    if not filename.endswith(".json"):
        filename += ".json"
    civ.save(filename)
    print(f"Game saved as {filename}")


def give_ai_starting_units(enemy):
    # Find first available military building for this civ
    civ_units = CIV_UNITS[enemy.name]
    for btype in ["barracks", "archery", "stable", "siege"]:
        if btype in civ_units:
            # Find first unit available at age 0
            for idx, unit in enumerate(civ_units[btype]):
                if unit["age"] == 0:
                    # Build the building if not present
                    if not any(b.type == btype for b in enemy.military_buildings):
                        enemy.build_military(btype, silent=True)
                    # Add 5 units of this type
                    for _ in range(5):
                        enemy.train_unit(btype, idx, silent=True)
                    return
    # If no age 0 unit, fallback: do nothing

def get_military_building_discount(player, btype):
    """
    Her askeri bina türü için, sahip olunan bina sayısına göre indirim oranı döndürür.
    1 bina: %0, 2: %10, 3: %20, ..., 6+: %50 (maksimum)
    """
    count = sum(1 for b in player.military_buildings if b.type == btype)
    if count <= 1:
        return 0.0
    elif count >= 6:
        return 0.5
    else:
        return 0.1 * (count - 1)

def apply_discount_to_cost(cost, discount):
    """Verilen maliyete indirim uygular ve yeni maliyeti döndürür."""
    if not cost:
        return cost
    return {r: int(c * (1 - discount) + 0.9999) for r, c in cost.items()}

def main():
    print("="*50)
    print("Welcome to Age of Empires 4 Simulation!")
    print("""
How to Play:

Goal: Develop your civilization, gather resources, build structures and train units to defeat your opponent and destroy their Town Center.

Game Flow:
- Each turn, your villagers gather resources. Resources: food, gold, wood, stone.
- Use resources to produce new villagers, buildings, and units.
- Build houses/villages to increase your population cap.
- Advancing ages (ageup) unlocks stronger units and buildings, and grants new villagers each age.
- Every 3 turns, a battle occurs. Your units fight the opponent's units.
- After battle, the winner can deal siege damage to the loser's Town Center.
- The side whose Town Center is destroyed loses the game.

Commands:
1. assign      : Assign villagers to resources. You can use 3 different models (auto, manual, bulk).
2. gather      : Gather resources. For unassigned villagers, you will be prompted to assign a resource.
3. house       : Build a population building (House/Village) to increase your max population.
4. ageup       : Advance to the next age. Costs resources, grants age bonuses and new villagers.
5. build       : Build a military building (Barracks, Archery Range, Stable, Siege Workshop).
6. train       : Train military units. Requires the relevant military building and resources.
7. buyvillager : Buy additional villagers using food.
8. market      : Exchange resources.
9. save        : Save the game.
10. next       : Proceed to the next turn. (AI also acts, villagers gather resources.)
11. exit       : Exit the game.

Additional Info:
- Each villager is assigned to a resource and gathers from it each turn.
- You can reassign villagers at any time (assign command).
- To train units, you must first build the relevant military building.
- Battles start automatically, but you can choose which of your groups attacks which enemy group.
- Your resources and population are limited, so act strategically!
- You can save the game with 'save' and continue later with 'load' at the start.

Good luck!
    """)
    print("="*50)
    print("Choose your civilization or load a game:")
    for i, civ in enumerate(CIVILIZATIONS):
        print(f"  {i+1}. {civ}")
    print(f"  {len(CIVILIZATIONS)+1}. Load from file")
    
    while True:
        idx = input("Enter number: ").strip()
        if idx == str(len(CIVILIZATIONS)+1):
            fname = input("Enter filename to load: ").strip()
            try:
                player = load_game(fname)
                print(f"Loaded game for {player.name}.")
                break
            except Exception as e:
                print(f"Error loading game: {e}")
        else:
            try:
                idx = int(idx) - 1
                if 0 <= idx < len(CIVILIZATIONS):
                    player = Civilization(CIVILIZATIONS[idx])
                    print("\nYou must assign your initial villagers.")
                    player.assign_villagers()
                    break
                else:
                    print("Invalid number. Please choose a valid option.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    enemy = Civilization(random.choice([c for c in CIVILIZATIONS if c != player.name]))

    give_ai_starting_units(enemy)

    day = 1
    battle_interval = 3  # Every 3 turns, a battle occurs

    # Eğer yüklenen oyunda villager_assignments yoksa ilk atama iste
    if not hasattr(player, "villager_assignments") or not player.villager_assignments or any(a is None for a in player.villager_assignments):
        print("\nYou must assign your initial villagers.")
        player.assign_villagers()

    command_list = [
        "assign", "gather", "house", "ageup", "build", "train",
        "buyvillager", "market", "save", "load", "next", "exit"
    ]

    battle_done = False
    while True:
        print_status(player, day, battle_interval, battle_done)
        print("Commands:")
        ncol = 3
        nrow = (len(command_list) + ncol - 1) // ncol
        for row in range(nrow):
            line = ""
            for col in range(ncol):
                idx = row + col * nrow
                if idx < len(command_list):
                    line += f"{idx+1}. {command_list[idx]}".ljust(15)
            print(line)
        cmd_input = input("Command (name or number): ").strip().lower()
        if cmd_input.isdigit():
            cmd_idx = int(cmd_input) - 1
            if 0 <= cmd_idx < len(command_list):
                cmd = command_list[cmd_idx]
            else:
                print("Invalid command number.")
                continue
        else:
            cmd = cmd_input

        try:
            if cmd == "assign":
                player.assign_villagers()
            elif cmd == "gather":
                player.gather_resources()
            elif cmd == "house":
                house_cost = {"wood": 50, "stone": 25}
                max_possible = min(
                    player.resources["wood"] // house_cost["wood"],
                    player.resources["stone"] // house_cost["stone"]
                )
                print(f"You can build up to {max_possible} houses with your current resources.")
                try:
                    count = int(input("How many houses do you want to build? (Default 1): ") or "1")
                except Exception:
                    count = 1
                player.add_house(count=count)
            elif cmd == "ageup":
                player.next_age()
                apply_age_bonuses(player)
            elif cmd == "build":
                print("Military buildings:")
                btype_keys = list(MILITARY_BUILDINGS.keys())
                for i, btype in enumerate(btype_keys, 1):
                    print(f"  {i}. {btype} - {MILITARY_BUILDINGS[btype]['name']}")
                btype_input = input("Building type (name or number): ").strip().lower()
                if btype_input.isdigit():
                    idx = int(btype_input) - 1
                    if 0 <= idx < len(btype_keys):
                        btype = btype_keys[idx]
                    else:
                        print("Invalid building number.")
                        continue
                else:
                    btype = btype_input
                if btype in MILITARY_BUILDINGS:
                    cost = {"wood": 150}
                    max_possible = player.resources["wood"] // cost["wood"]
                    print(f"You can build up to {max_possible} military buildings with your current resources.")
                    try:
                        count = int(input("How many military buildings do you want to build? (Default 1): ") or "1")
                    except Exception:
                        count = 1
                    player.build_military(btype, count=count)
                else:
                    print("Invalid building type.")
            elif cmd == "train":
                print("Military buildings:")
                btype_keys = list(CIV_UNITS[player.name].keys())
                for i, btype in enumerate(btype_keys, 1):
                    print(f"  {i}. {btype}")
                btype_input = input("Building type (name or number): ").strip().lower()
                if btype_input.isdigit():
                    idx = int(btype_input) - 1
                    if 0 <= idx < len(btype_keys):
                        btype = btype_keys[idx]
                    else:
                        print("Invalid building number.")
                        continue
                else:
                    btype = btype_input
                if btype in CIV_UNITS[player.name]:
                    unit_list_raw = [u for u in CIV_UNITS[player.name][btype] if u["age"] <= player.age]
                    seen_names = set()
                    unit_list = []
                    for u in unit_list_raw:
                        if u["name"] not in seen_names:
                            unit_list.append(u)
                            seen_names.add(u["name"])
                    # İndirim oranını hesapla
                    discount = get_military_building_discount(player, btype)
                    print(f"\nAvailable units for {MILITARY_BUILDINGS[btype]['name']} (Discount: %{int(discount*100)}):")
                    for i, u in enumerate(unit_list, 1):
                        discounted_cost = apply_discount_to_cost(u['cost'], discount)
                        cost_str = ", ".join(f"{r}:{discounted_cost[r]}" for r in discounted_cost) if discounted_cost else "-"
                        print(f"  {i}. {u['name']} (HP:{u['hp']} ATK:{u['atk']} COST:{cost_str})")
                    unit_input = input("Unit number: ").strip()
                    if unit_input.isdigit():
                        idx = int(unit_input) - 1
                        if 0 <= idx < len(unit_list):
                            orig_idx = unit_list_raw.index(unit_list[idx])
                            unit_data = unit_list[idx]
                            # Max hesapla
                            max_pop = player.max_population - player.population
                            discounted_cost = apply_discount_to_cost(unit_data["cost"], discount)
                            if discounted_cost:
                                max_res = float('inf')
                                for r in discounted_cost:
                                    c = discounted_cost[r]
                                    if c > 0:
                                        max_res = min(max_res, player.resources.get(r, 0) // c)
                                max_possible = min(max_pop, int(max_res))
                            else:
                                max_possible = max_pop
                            print(f"You can train up to {max_possible} {unit_data['name']} with your current resources and population.")
                            try:
                                count = int(input("How many of this unit do you want to train? (Default 1): ") or "1")
                            except Exception:
                                count = 1
                            # Kaynakları indirimli olarak kontrol et ve düş
                            if count > 0 and max_possible > 0:
                                total_cost = {r: discounted_cost[r] * count for r in discounted_cost}
                                if all(player.resources.get(r, 0) >= total_cost[r] for r in total_cost):
                                    for r in total_cost:
                                        player.resources[r] -= total_cost[r]
                                    for _ in range(count):
                                        player.train_unit(btype, orig_idx, count=1)
                                        # Son eklenen birimlere çağ bonusu uygula
                                        for u in player.units[-1:]:
                                            u.attack = int(u.attack * AGE_BONUSES[player.age])
                                            u.hp = int(u.hp * AGE_BONUSES[player.age])
                                else:
                                    print("Not enough resources.")
                            else:
                                print("Invalid amount.")
                        else:
                            print("Invalid unit number.")
                    else:
                        print("Invalid unit number.")
                else:
                    print("This building is not available for your civilization.")
            elif cmd == "buyvillager":
                max_possible = min(
                    player.resources["food"] // VILLAGER_BUY_COST["food"],
                    player.max_population - player.population
                )
                print(f"You can buy up to {max_possible} villagers with your current resources and population.")
                try:
                    count = int(input("How many villagers do you want to buy? (Default 1): ") or "1")
                except Exception:
                    count = 1
                player.buy_villager(count=count)
            elif cmd == "market":
                market_exchange(player)
            elif cmd == "save":
                save_with_timestamp(player)
            elif cmd == "load":
                fname = input("Enter filename to load: ").strip()
                player = load_game(fname)
                print(f"Loaded game for {player.name}.")
            elif cmd == "next":
                day += 1
                player.turn += 1
                player.daily_villager_growth()
                player.gather_resources(show_new_assign=False)
                enemy.daily_villager_growth()
                enemy.gather_resources(show_new_assign=False)
                enemy.ai_turn()
                enemy.ai_turn()
                # Savaş günü ise otomatik olarak interaktif savaş başlat
                if day % battle_interval == 0:
                    print("\n!!! Battle day! Battle begins... !!!")
                    winner = interactive_battle(player, enemy)
                    update_after_battle(player)
                    update_after_battle(enemy)
                    battle_done = True
                    # Savaş sonrası kazananın askerleri varsa kuşatma uygula
                    if winner == player and player.units:
                        if siege(player, enemy):
                            update_after_siege(enemy)
                            print("You won the game!")
                            break
                    elif winner == enemy and enemy.units:
                        if siege(enemy, player):
                            update_after_siege(player)
                            print("AI won the game!")
                            break
                else:
                    battle_done = False
            elif cmd == "exit":
                print("Exiting. Good game!")
                break
            else:
                print("Unknown command.")
        except SimulationError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

def load_game(filename):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        civ = Civilization(data["civilization"])
        civ.age = AGES.index(data["age"])
        civ.resources = data["resources"]
        civ.population = data["population"]
        civ.max_population = data["max_population"]
        civ.turn = data.get("turn", 1)
        # Villager ve atamalar
        civ.villagers = [Villager(civ.name) for _ in range(data.get("villagers", 6))]
        civ.villager_assignments = data.get("villager_assignments", [None] * len(civ.villagers))  # Atamalar yükleniyor
        # Binalar
        civ.buildings = []
        for bname in data.get("buildings", []):
            if bname == "Town Center":
                civ.buildings.append(TownCenter(civ.name, civ.age))
            elif bname in ["House", "Village"]:
                civ.buildings.append(House(civ.name))
            else:
                # Askeri bina mı?
                for k, v in MILITARY_BUILDINGS.items():
                    if v["name"] == bname:
                        civ.buildings.append(MilitaryBuilding(bname, 500, k))
        # Askeri binalar
        civ.military_buildings = []
        for bname in data.get("military_buildings", []):
            for k, v in MILITARY_BUILDINGS.items():
                if v["name"] == bname:
                    civ.military_buildings.append(MilitaryBuilding(bname, 500, k))
        # Birimler
        civ.units = []
        for uname in data.get("units", []):
            # Tüm birimlerden isme göre bul
            found = False
            for btype in CIV_UNITS[civ.name]:
                for u in CIV_UNITS[civ.name][btype]:
                    if u["name"] == uname:
                        civ.units.append(Unit(u["name"], u["hp"], u["atk"], u["type"], u["cost"]))
                        found = True
                        break
                if found:
                    break
        return civ
    except Exception as e:
        raise SimulationError(f"Load failed: {e}")

if __name__ == "__main__":
    main()