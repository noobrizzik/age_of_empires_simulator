# Constants
AGES = ["Dark Age", "Feudal Age", "Castle Age", "Imperial Age"]
MAX_POPULATION = 200
CIVILIZATIONS = [
    "English", "French", "Mongol", "Ottoman", "Chinese", "Abbasid"
]

# --- Hata Yönetimi ---
class SimulationError(Exception):
    pass

# --- Medeniyet Bonusları ve Oyun Verileri ---
CIV_BONUSES = {
    "English": {"food": 1.2, "gold": 1.0, "wood": 1.0, "stone": 1.0},
    "French": {"food": 1.0, "gold": 1.2, "wood": 1.0, "stone": 1.0},
    "Mongol": {"food": 1.0, "gold": 1.1, "wood": 1.1, "stone": 1.0},
    "Ottoman": {"food": 1.1, "gold": 1.0, "wood": 1.0, "stone": 1.1},
    "Chinese": {"food": 1.0, "gold": 1.0, "wood": 1.0, "stone": 1.2},
    "Abbasid": {"food": 1.0, "gold": 1.0, "wood": 1.2, "stone": 1.0},
}
AGE_BONUSES = [1.0, 1.15, 1.3, 1.5]
RESOURCES = ["food", "gold", "wood", "stone"]
BASE_TC_HP = {
    "default": [2000, 2500, 3500, 5000],
    "Chinese": [2500, 3000, 4000, 6000]
}
MILITARY_BUILDINGS = {
    "barracks": {"age": 0, "name": "Barracks"},
    "archery": {"age": 1, "name": "Archery Range"},
    "stable": {"age": 1, "name": "Stable"},
    "siege": {"age": 2, "name": "Siege Workshop"}
}
CIV_BUILDING_EXCEPTIONS = {
    "English": {"archery": 0},
    "Mongol": {"stable": 0},
    "Chinese": {"siege": 0}
}
CIV_UNITS = {
    "English": {
        "barracks": [
            {"name": "Spearman", "age": 0, "hp": 100, "atk": 20, "type": "spear", "cost": {"food": 50, "gold": 20}},
            {"name": "English Man-at-Arms", "age": 1, "hp": 140, "atk": 35, "type": "maa", "cost": {"food": 100, "gold": 40}}
        ],
        "archery": [
            {"name": "Longbowman", "age": 0, "hp": 80, "atk": 30, "type": "longbow", "cost": {"food": 40, "wood": 50}},
            {"name": "Crossbowman", "age": 1, "hp": 90, "atk": 35, "type": "crossbow", "cost": {"food": 60, "wood": 60}},
            {"name": "Handcannoneer", "age": 2, "hp": 80, "atk": 50, "type": "gunner", "cost": {"food": 80, "gold": 100}}
        ],
        "stable": [
            {"name": "Light Cavalry", "age": 1, "hp": 110, "atk": 30, "type": "light_cav", "cost": {"food": 80, "gold": 30}},
            {"name": "Heavy Knight", "age": 2, "hp": 160, "atk": 55, "type": "heavy_cav", "cost": {"food": 120, "gold": 120}}
        ],
        "siege": [
            {"name": "Battering Ram", "age": 2, "hp": 200, "atk": 80, "type": "ram", "cost": {"wood": 200}},
            {"name": "Mangonel", "age": 2, "hp": 120, "atk": 70, "type": "mangonel", "cost": {"wood": 160, "gold": 100}},
            {"name": "Bombard", "age": 3, "hp": 150, "atk": 120, "type": "bombard", "cost": {"gold": 300, "wood": 200}}
        ]
    },
    "French": {
        "barracks": [
            {"name": "Spearman", "age": 0, "hp": 100, "atk": 20, "type": "spear", "cost": {"food": 50, "gold": 20}},
            {"name": "Man-at-Arms", "age": 1, "hp": 135, "atk": 33, "type": "maa", "cost": {"food": 100, "gold": 40}}
        ],
        "archery": [
            {"name": "Archer", "age": 1, "hp": 80, "atk": 28, "type": "archer", "cost": {"food": 40, "wood": 50}},
            {"name": "French Crossbowman", "age": 1, "hp": 90, "atk": 36, "type": "crossbow", "cost": {"food": 60, "wood": 60}},
            {"name": "Handcannoneer", "age": 2, "hp": 80, "atk": 50, "type": "gunner", "cost": {"food": 80, "gold": 100}}
        ],
        "stable": [
            {"name": "Light Cavalry", "age": 1, "hp": 110, "atk": 30, "type": "light_cav", "cost": {"food": 80, "gold": 30}},
            {"name": "French Royal Knight", "age": 2, "hp": 170, "atk": 60, "type": "heavy_cav", "cost": {"food": 130, "gold": 130}}
        ],
        "siege": [
            {"name": "Battering Ram", "age": 2, "hp": 200, "atk": 80, "type": "ram", "cost": {"wood": 200}},
            {"name": "Mangonel", "age": 2, "hp": 120, "atk": 70, "type": "mangonel", "cost": {"wood": 160, "gold": 100}},
            {"name": "Culverin", "age": 3, "hp": 150, "atk": 125, "type": "culverin", "cost": {"gold": 320, "wood": 200}}
        ]
    },
    "Mongol": {
        "barracks": [
            {"name": "Spearman", "age": 0, "hp": 100, "atk": 20, "type": "spear", "cost": {"food": 50, "gold": 20}},
            {"name": "Man-at-Arms", "age": 1, "hp": 135, "atk": 33, "type": "maa", "cost": {"food": 100, "gold": 40}}
        ],
        "archery": [
            {"name": "Archer", "age": 1, "hp": 80, "atk": 28, "type": "archer", "cost": {"food": 40, "wood": 50}},
            {"name": "Mangudai", "age": 1, "hp": 70, "atk": 40, "type": "mangudai", "cost": {"food": 60, "gold": 60}},
            {"name": "Handcannoneer", "age": 2, "hp": 80, "atk": 50, "type": "gunner", "cost": {"food": 80, "gold": 100}}
        ],
        "stable": [
            {"name": "Light Cavalry", "age": 0, "hp": 110, "atk": 30, "type": "light_cav", "cost": {"food": 80, "gold": 30}},
            {"name": "Keshik", "age": 2, "hp": 150, "atk": 58, "type": "heavy_cav", "cost": {"food": 120, "gold": 110}}
        ],
        "siege": [
            {"name": "Battering Ram", "age": 2, "hp": 200, "atk": 80, "type": "ram", "cost": {"wood": 200}},
            {"name": "Mangonel", "age": 2, "hp": 120, "atk": 70, "type": "mangonel", "cost": {"wood": 160, "gold": 100}},
            {"name": "Hui-Hui Pao", "age": 3, "hp": 150, "atk": 130, "type": "huihui", "cost": {"gold": 340, "wood": 200}}
        ]
    },
    "Ottoman": {
        "barracks": [
            {"name": "Spearman", "age": 0, "hp": 100, "atk": 20, "type": "spear", "cost": {"food": 50, "gold": 20}},
            {"name": "Ottoman Armored", "age": 1, "hp": 145, "atk": 36, "type": "maa", "cost": {"food": 110, "gold": 45}}
        ],
        "archery": [
            {"name": "Archer", "age": 1, "hp": 80, "atk": 28, "type": "archer", "cost": {"food": 40, "wood": 50}},
            {"name": "Crossbowman", "age": 1, "hp": 90, "atk": 35, "type": "crossbow", "cost": {"food": 60, "wood": 60}},
            {"name": "Janissary", "age": 2, "hp": 85, "atk": 55, "type": "gunner", "cost": {"food": 90, "gold": 110}}
        ],
        "stable": [
            {"name": "Light Cavalry", "age": 1, "hp": 110, "atk": 30, "type": "light_cav", "cost": {"food": 80, "gold": 30}},
            {"name": "Heavy Akıncı", "age": 2, "hp": 155, "atk": 57, "type": "heavy_cav", "cost": {"food": 120, "gold": 120}}
        ],
        "siege": [
            {"name": "Battering Ram", "age": 2, "hp": 200, "atk": 80, "type": "ram", "cost": {"wood": 200}},
            {"name": "Mangonel", "age": 2, "hp": 120, "atk": 70, "type": "mangonel", "cost": {"wood": 160, "gold": 100}},
            {"name": "Great Bombard", "age": 3, "hp": 160, "atk": 140, "type": "bombard", "cost": {"gold": 350, "wood": 220}}
        ]
    },
    "Chinese": {
        "barracks": [
            {"name": "Spearman", "age": 0, "hp": 100, "atk": 20, "type": "spear", "cost": {"food": 50, "gold": 20}},
            {"name": "Imperial Guard", "age": 1, "hp": 150, "atk": 38, "type": "maa", "cost": {"food": 110, "gold": 45}}
        ],
        "archery": [
            {"name": "Archer", "age": 1, "hp": 80, "atk": 28, "type": "archer", "cost": {"food": 40, "wood": 50}},
            {"name": "Zhuge Nu", "age": 1, "hp": 85, "atk": 42, "type": "zhuge", "cost": {"food": 70, "wood": 70}},
            {"name": "Grenadier", "age": 2, "hp": 90, "atk": 60, "type": "gunner", "cost": {"food": 100, "gold": 120}}
        ],
        "stable": [
            {"name": "Light Cavalry", "age": 1, "hp": 110, "atk": 30, "type": "light_cav", "cost": {"food": 80, "gold": 30}},
            {"name": "Heavy Knight", "age": 2, "hp": 160, "atk": 55, "type": "heavy_cav", "cost": {"food": 120, "gold": 120}}
        ],
        "siege": [
            {"name": "Battering Ram", "age": 2, "hp": 200, "atk": 80, "type": "ram", "cost": {"wood": 200}},
            {"name": "Bee Thrower", "age": 2, "hp": 120, "atk": 75, "type": "bee", "cost": {"wood": 180, "gold": 120}},
            {"name": "Bombard", "age": 3, "hp": 150, "atk": 120, "type": "bombard", "cost": {"gold": 300, "wood": 200}}
        ]
    },
    "Abbasid": {
        "barracks": [
            {"name": "Spearman", "age": 0, "hp": 100, "atk": 20, "type": "spear", "cost": {"food": 50, "gold": 20}},
            {"name": "Ghulam", "age": 1, "hp": 140, "atk": 36, "type": "maa", "cost": {"food": 105, "gold": 42}}
        ],
        "archery": [
            {"name": "Archer", "age": 1, "hp": 80, "atk": 28, "type": "archer", "cost": {"food": 40, "wood": 50}},
            {"name": "Crossbowman", "age": 1, "hp": 90, "atk": 35, "type": "crossbow", "cost": {"food": 60, "wood": 60}},
            {"name": "Handcannoneer", "age": 2, "hp": 80, "atk": 50, "type": "gunner", "cost": {"food": 80, "gold": 100}}
        ],
        "stable": [
            {"name": "Camel Rider", "age": 1, "hp": 120, "atk": 35, "type": "camel", "cost": {"food": 90, "gold": 40}},
            {"name": "Heavy Camel Rider", "age": 2, "hp": 170, "atk": 60, "type": "heavy_camel", "cost": {"food": 130, "gold": 130}}
        ],
        "siege": [
            {"name": "Battering Ram", "age": 2, "hp": 200, "atk": 80, "type": "ram", "cost": {"wood": 200}},
            {"name": "Fire Mangonel", "age": 2, "hp": 120, "atk": 80, "type": "fire_mangonel", "cost": {"wood": 180, "gold": 120}},
            {"name": "Shah Tower", "age": 3, "hp": 180, "atk": 100, "type": "shah_tower", "cost": {"gold": 350, "wood": 250}}
        ]
    }
}
COUNTERS = {
    "spear": ["light_cav", "heavy_cav", "camel"],
    "maa": ["archer", "spear"],
    "longbow": ["maa", "spear"],
    "archer": ["maa", "spear"],
    "crossbow": ["maa", "heavy_cav", "camel", "heavy_camel"],
    "gunner": ["maa", "heavy_cav", "camel", "heavy_camel", "ram", "bombard", "culverin", "huihui", "shah_tower"],
    "mangudai": ["archer", "longbow", "maa"],
    "zhuge": ["maa", "heavy_cav"],
    "camel": ["light_cav", "heavy_cav"],
    "heavy_camel": ["heavy_cav", "maa"],
    "light_cav": ["archer", "longbow", "crossbow", "gunner"],
    "heavy_cav": ["archer", "longbow", "crossbow", "gunner", "ram", "mangonel", "bee", "fire_mangonel"],
    "ram": ["town_center", "building"],
    "mangonel": ["maa", "archer", "longbow", "crossbow"],
    "bee": ["maa", "archer", "longbow", "crossbow"],
    "fire_mangonel": ["maa", "archer", "longbow", "crossbow"],
    "bombard": ["town_center", "building", "ram", "mangonel", "bee", "fire_mangonel"],
    "culverin": ["bombard", "ram", "mangonel", "bee", "fire_mangonel"],
    "huihui": ["bombard", "ram", "mangonel", "bee", "fire_mangonel"],
    "shah_tower": ["town_center"]
}
def get_counter_bonus(attacker_type, defender_type):
    if defender_type in COUNTERS.get(attacker_type, []):
        return 1.5
    return 1.0

VILLAGER_BASE_GATHER = 15
AGE_UP_COSTS = [
    {"food": 400, "gold": 200},   # Feudal Age
    {"food": 1200, "gold": 600, "wood": 300},  # Castle Age
    {"food": 2400, "gold": 1200, "wood": 600, "stone": 400}  # Imperial Age
]
VILLAGER_BUY_COST = {"food": 50}
CIV_AI_STYLES = {
    "English": {
        "focus": "archery",
        "aggression": 0.5,
        "eco": 0.5,
        "siege": 0.3,
        "unit_pref": ["archery", "barracks"],
        "house_priority": 0.5
    },
    "French": {
        "focus": "stable",
        "aggression": 0.7,
        "eco": 0.4,
        "siege": 0.4,
        "unit_pref": ["stable", "barracks"],
        "house_priority": 0.4
    },
    "Mongol": {
        "focus": "raiding",
        "aggression": 0.8,
        "eco": 0.3,
        "siege": 0.6,
        "unit_pref": ["stable", "archery"],
        "house_priority": 0.0  # Mongol ev yapmaz
    },
    "Ottoman": {
        "focus": "balanced",
        "aggression": 0.6,
        "eco": 0.6,
        "siege": 0.5,
        "unit_pref": ["barracks", "archery", "siege"],
        "house_priority": 0.5
    },
    "Chinese": {
        "focus": "eco",
        "aggression": 0.4,
        "eco": 0.8,
        "siege": 0.6,
        "unit_pref": ["archery", "siege"],
        "house_priority": 0.7
    },
    "Abbasid": {
        "focus": "counter",
        "aggression": 0.5,
        "eco": 0.7,
        "siege": 0.4,
        "unit_pref": ["barracks", "stable"],
        "house_priority": 0.6
    }
}
