# import game modules
from game.bots import gun_bot, rico_bot, mod_bot, elemental_bot, lazer_bot, chaos_bot, duplo_bot

# all bots and their unlock conditions
all_bots = [
    {"bot": gun_bot,        "cost": 0,  "round": 1, "confirm": False, "unlocked": True},
    {"bot": rico_bot,       "cost": 0,  "round": 1, "confirm": False, "unlocked": True},
    {"bot": mod_bot,        "cost": 10, "round": 3, "confirm": False, "unlocked": False},
    {"bot": elemental_bot,  "cost": 20, "round": 4, "confirm": False, "unlocked": False},
    {"bot": lazer_bot,      "cost": 30, "round": 5, "confirm": False, "unlocked": False},
    {"bot": chaos_bot,      "cost": 40, "round": 6, "confirm": False, "unlocked": False},
    {"bot": duplo_bot,      "cost": 50, "round": 7, "confirm": False, "unlocked": False}
]

# all bot upgrades and their costs
bot_upgrades = {
    "Gun Bot": [
        {
            "action": "Left Gun",
            "action_number": 0,
            "stat": "aiming_unlocked",
            "level": 0,
            "buff_desc_1": "Unlock Aiming",
            "buff_desc_2": ["Locked -> Unlocked"],
            "amount": [True],
            "cost": [100],
            "confirm": False
        },
        {
            "action": "Right Gun",
            "action_number": 1,
            "stat": "damage",
            "level": 0,
            "buff_desc_1": "+1 damage",
            "buff_desc_2": ["Damage: 1 -> 2", "Damage: 2 -> 3", "Damage: 3 -> 4", "Damage: 4 -> 5"],
            "amount": [2, 3, 4, 5],
            "cost": [5, 10, 15, 20],
            "confirm": False
        }
    ],
    "Rico Bot": [
        {
            "action": "Heal",
            "action_number": 0,
            "stat": "heal",
            "level": 0,
            "buff_desc_1": "+1 heal",
            "buff_desc_2": ["Heal: 1 -> 2", "Heal: 2 -> 3", "Heal: 3 -> 4", "Heal: 4 -> 5"],
            "amount": [2, 3, 4, 5],
            "cost": [5, 10, 15, 20],
            "confirm": False
        },
        {
            "action": "Bounce",
            "action_number": 1,
            "stat": "damage",
            "level": 0,
            "buff_desc_1": "+1 damage",
            "buff_desc_2": ["Damage: 1 -> 2", "Damage: 2 -> 3", "Damage: 3 -> 4", "Damage: 4 -> 5"],
            "amount": [2, 3, 4, 5],
            "cost": [5, 10, 15, 20],
            "confirm": False
        },
        {
            "action": "Bounce",
            "action_number": 1,
            "stat": "bounce_amount",
            "level": 0,
            "buff_desc_1": "+1 bounce",
            "buff_desc_2": ["Bounces: 2 -> 3", "Bounces: 3 -> 4", "Bounces: 4 -> 5", "Bounces: 5 -> 6"],
            "amount": [3, 4, 5, 6],
            "cost": [10, 25, 40, 55],
            "confirm": False
        }
    ],
    "Mod Bot": [
        {
            "action": "Percentage",
            "action_number": 0,
            "stat": "damage",
            "level": 0,
            "buff_desc_1": "+10% damage",
            "buff_desc_2": ["Damage: 10% -> 20%", "Damage: 20% -> 30%", "Damage: 30% -> 40%", "Damage: 40% -> 50%"],
            "amount": [0.2, 0.3, 0.4, 0.5],
            "cost": [20, 30, 40, 50],
            "confirm": False
        },
        {
            "action": "Shield",
            "action_number": 1,
            "stat": "shield",
            "level": 0,
            "buff_desc_1": "+10% reduction",
            "buff_desc_2": ["Reduction: 10% -> 20%", "Reduction: 20% -> 30%", "Reduction: 30% -> 40%", "Reduction: 40% -> 50%"],
            "amount": [0.8, 0.7, 0.6, 0.5],
            "cost": [20, 30, 40, 50],
            "confirm": False
        }
    ],
    "Elemental Bot": [
        {
            "action": "Fire",
            "action_number": 0,
            "stat": "damage",
            "level": 0,
            "buff_desc_1": "+1 damage",
            "buff_desc_2": ["Damage: 1 -> 2", "Damage: 2 -> 3", "Damage: 3 -> 4", "Damage: 4 -> 5"],
            "amount": [2, 3, 4, 5],
            "cost": [10, 20, 30, 40],
            "confirm": False
        },
        {
            "action": "Fire",
            "action_number": 0,
            "stat": "fire_rounds_amount",
            "level": 0,
            "buff_desc_1": "+1 round",
            "buff_desc_2": ["Round: 2 -> 3", "Round: 3 -> 4", "Round: 4 -> 5"],
            "amount": [3, 4, 5],
            "cost": [10, 20, 30],
            "confirm": False
        },
        {
            "action": "Ice",
            "action_number": 1,
            "stat": "ice_hits_needed",
            "level": 0,
            "buff_desc_1": "-1 freeze hit needed",
            "buff_desc_2": ["Hits Needed: 3 -> 2", "Hits Needed: 2 -> 1"],
            "amount": [2, 1],
            "cost": [25, 50],
            "confirm": False
        }
    ],
    "Lazer Bot": [
        {
            "action": "Pierce",
            "action_number": 0,
            "stat": "damage",
            "level": 0,
            "buff_desc_1": "+1 damage",
            "buff_desc_2": ["Damage: 1 -> 2", "Damage: 2 -> 3", "Damage: 3 -> 4", "Damage: 4 -> 5"],
            "amount": [2, 3, 4, 5],
            "cost": [10, 20, 30, 40],
            "confirm": False
        },
        {
            "action": "Barrage",
            "action_number": 1,
            "stat": "damage",
            "level": 0,
            "buff_desc_1": "+1 damage",
            "buff_desc_2": ["Damage: 1 -> 2", "Damage: 2 -> 3", "Damage: 3 -> 4", "Damage: 4 -> 5"],
            "amount": [2, 3, 4, 5],
            "cost": [10, 20, 30, 40],
            "confirm": False
        },
        {
            "action": "Barrage",
            "action_number": 1,
            "stat": "barrage_charge_needed",
            "level": 0,
            "buff_desc_1": "-5 barrage charge",
            "buff_desc_2": ["Charge Needed: 20 -> 15", "Charge Needed: 15 -> 10", "Charge Needed: 10 -> 5"],
            "amount": [15, 10, 5],
            "cost": [10, 30, 50],
            "confirm": False
        }
    ],
    "Chaos Bot": [
        {
            "action": "Random",
            "action_number": 0,
            "stat": "min_power",
            "level": 0,
            "buff_desc_1": "+1 min power",
            "buff_desc_2": ["Min Power: 1 -> 2", "Min Power: 2 -> 3", "Min Power: 3 -> 4", "Min Power: 4 -> 5"],
            "amount": [2, 3, 4, 5],
            "cost": [10, 20, 30, 40],
            "confirm": False
        },
        {
            "action": "Random",
            "action_number": 0,
            "stat": "max_power",
            "level": 0,
            "buff_desc_1": "+1 max power",
            "buff_desc_2": ["Max Power: 5 -> 6", "Max Power: 6 -> 7", "Max Power: 7 -> 8", "Max Power: 8 -> 9", "Max Power: 9 -> 10"],
            "amount": [6, 7, 8, 9, 10],
            "cost": [10, 20, 30, 40, 50],
            "confirm": False
        },
        {
            "action": "Barrier",
            "action_number": 1,
            "stat": "block",
            "level": 0,
            "buff_desc_1": "+10% block",
            "buff_desc_2": ["Block: 10% -> 20%", "Block: 20% -> 30%", "Block: 30% -> 40%", "Block: 40% -> 50%"],
            "amount": [20, 30, 40, 50],
            "cost": [20, 30, 40, 50],
            "confirm": False
        }
    ],
    "Duplo Bot": [
        {
            "action": "Mark",
            "action_number": 1,
            "stat": "mark_hits_needed",
            "level": 0,
            "buff_desc_1": "-1 mark hit needed",
            "buff_desc_2": ["Hits Needed: 2 -> 1"],
            "amount": [1],
            "cost": [50],
            "confirm": False
        }
    ]
}
