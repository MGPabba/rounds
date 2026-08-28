# import game modules
from game.bots import gun_bot, rico_bot, mod_bot, elemental_bot, lazer_bot, chaos_bot, duplo_bot

# all bots and their unlock conditions
all_bots = [
    {"bot": gun_bot,        "cost": 0,  "round": 1, "unlocked": True},
    {"bot": rico_bot,       "cost": 5,  "round": 2, "unlocked": False},
    {"bot": mod_bot,        "cost": 10, "round": 3, "unlocked": False},
    {"bot": elemental_bot,  "cost": 20, "round": 4, "unlocked": False},
    {"bot": lazer_bot,      "cost": 30, "round": 5, "unlocked": False},
    {"bot": chaos_bot,      "cost": 40, "round": 6, "unlocked": False},
    {"bot": duplo_bot,      "cost": 50, "round": 7, "unlocked": False}
]

# all bot upgrades and their costs
bot_upgrades = {
    "Gun Bot": [
        {
            "action": "Left Gun",
            "level": 0,
            "buff_desc_1": "+1 damage",
            "buff_desc_2": ["Damage: 1 -> 2", "Damage: 2 -> 3", "Damage: 3 -> 4"],
            "cost": [5, 10, 15]
        },
        {
            "action": "Right Gun",
            "level": 0,
            "buff_desc_1": "+1 damage",
            "buff_desc_2": ["Damage: 1 -> 2", "Damage: 2 -> 3", "Damage: 3 -> 4"],
            "cost": [5, 10, 15]
        }
    ],
    "Rico Bot": [
        {
            "action": "Heal",
            "level": 0,
            "buff_desc_1": "+1 heal",
            "buff_desc_2": ["Heal: 1 -> 2", "Heal: 2 -> 3", "Heal: 3 -> 4"],
            "cost": [5, 10, 15]
        },
        {
            "action": "Bounce",
            "level": 0,
            "buff_desc_1": "+1 damage",
            "buff_desc_2": ["Damage: 1 -> 2", "Damage: 2 -> 3", "Damage: 3 -> 4"],
            "cost": [5, 10, 15]
        },
        {
            "action": "Bounce",
            "level": 0,
            "buff_desc_1": "+1 bounce",
            "buff_desc_2": ["Bounces: 2 -> 3", "Bounces: 3 -> 4", "Bounces: 4 -> 5"],
            "cost": [5, 10, 15]
        }
    ],
    "Mod Bot": [
        {
            "action": "Percentage",
            "level": 0,
            "buff_desc_1": "+10% damage",
            "buff_desc_2": ["Damage: 10% -> 20%", "Damage: 20% -> 30%", "Damage: 30% -> 40%"],
            "cost": [5, 10, 15]
        },
        {
            "action": "Shield",
            "level": 0,
            "buff_desc_1": "+10% reduction",
            "buff_desc_2": ["Reduction: 10% -> 20%", "Reduction: 20% -> 30%", "Reduction: 30% -> 40%"],
            "cost": [5, 10, 15]
        }
    ],
    "Elemental Bot": [
        {
            "action": "Fire",
            "level": 0,
            "buff_desc_1": "+1 damage",
            "buff_desc_2": ["Damage: 1 -> 2", "Damage: 2 -> 3", "Damage: 3 -> 4"],
            "cost": [5, 10, 15]
        },
        {
            "action": "Fire",
            "level": 0,
            "buff_desc_1": "+1 round",
            "buff_desc_2": ["Round: 1 -> 2", "Round: 2 -> 3", "Round: 3 -> 4"],
            "cost": [5, 10, 15]
        },
        {
            "action": "Ice",
            "level": 0,
            "buff_desc_1": "-1 freeze hit needed",
            "buff_desc_2": ["Hits Needed: 3 -> 2", "Hits Needed: 2 -> 1"],
            "cost": [10, 20]
        }
    ],
    "Lazer Bot": [
        {
            "action": "Pierce",
            "level": 0,
            "buff_desc_1": "+1 damage",
            "buff_desc_2": ["Damage: 1 -> 2", "Damage: 2 -> 3", "Damage: 3 -> 4"],
            "cost": [5, 10, 15]
        },
        {
            "action": "Barrage",
            "level": 0,
            "buff_desc_1": "+1 damage",
            "buff_desc_2": ["Damage: 1 -> 2", "Damage: 2 -> 3", "Damage: 3 -> 4"],
            "cost": [5, 10, 15]
        },
        {
            "action": "Barrage",
            "level": 0,
            "buff_desc_1": "-2 barrage charge",
            "buff_desc_2": ["Charge Needed: 10 -> 8", "Charge Needed: 8 -> 6", "Charge Needed: 6 -> 4"],
            "cost": [5, 10, 15]
        }
    ],
    "Chaos Bot": [
        {
            "action": "Random",
            "level": 0,
            "buff_desc_1": "+1 min power",
            "buff_desc_2": ["Min Power: 1 -> 2", "Min Power: 2 -> 3", "Min Power: 3 -> 4"],
            "cost": [5, 10, 15]
        },
        {
            "action": "Random",
            "level": 0,
            "buff_desc_1": "+1 max power",
            "buff_desc_2": ["Max Power: 5 -> 6", "Max Power: 6 -> 7", "Max Power: 7 -> 8"],
            "cost": [5, 10, 15]
        },
        {
            "action": "Barrier",
            "level": 0,
            "buff_desc_1": "+10% block",
            "buff_desc_2": ["Block: 10% -> 20%", "Block: 20% -> 30%", "Block: 30% -> 40%"],
            "cost": [5, 10, 20]
        }
    ],
    "Duplo Bot": [
        {
            "action": "Mark",
            "level": 0,
            "buff_desc_1": "-1 mark hit needed",
            "buff_desc_2": ["Hits Needed: 2 -> 1"],
            "cost": [20]
        }
    ]
}
