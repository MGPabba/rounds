import pygame
import random

# import game modules
from .helper import FloatingText, wrap_text
from .characters import Character, Enemy
from .projectiles import (
    LinearProjectile,
    ChargeProjectile,
    MarkProjectile,
    PercentageProjectile,
    ShieldProjectile,
    HealProjectile,
    BounceProjectile,
    GlitchyDamageProjectile,
    GlitchyHealProjectile,
    GlitchyBlockProjectile,
    LaserProjectile
)

# ------------------------------
# BOT CLASSES
# ------------------------------

class Bot(Character):
    def __init__(self, name, health, x, y, box_background_color, description, idle_images_path, active_image_path, hurt_image_path, dead_image_path, button_color, button_hover_color, text_used_color):
        super().__init__(name, health, x, y, box_background_color, description)
        # bot specific info
        self.acted = False
        self.current_frame = 0
        
        # images
        self.idle_images_path = idle_images_path
        self.active_image_path = active_image_path
        self.hurt_image_path = hurt_image_path
        self.dead_image_path = dead_image_path
        self.idle_images = []
        self.active_image = None
        self.hurt_image = None
        self.dead_image = None

        # colors
        self.button_color = button_color
        self.button_hover_color = button_hover_color
        self.text_used_color = text_used_color
    
    def load_images(self):
        # load all different bot images
        for path in self.idle_images_path:
            self.idle_images.append(pygame.image.load(path).convert_alpha())
        self.active_image = pygame.image.load(self.active_image_path).convert_alpha()
        self.actions[0]["image"] = pygame.image.load(self.actions[0]["image_path"]).convert_alpha()
        self.actions[1]["image"] = pygame.image.load(self.actions[1]["image_path"]).convert_alpha()
        self.hurt_image = pygame.image.load(self.hurt_image_path).convert_alpha()
        self.dead_image = pygame.image.load(self.dead_image_path).convert_alpha()

        # randomize starting idle frame and animation timer
        self.current_frame = random.randint(0, len(self.idle_images) - 1)
        self.animation_timer = random.randint(0, self.animation_speed)

    def update_idle_animation(self):
        # update idle animation when character is alive and doing nothing
        if self.visual_health > 0:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.idle_images)

    def check_actions(self):
        # check if both actions are used
        if self.actions[0]["used"] and self.actions[1]["used"]:
            self.acted = True
    
    def reset_actions(self):
        # reset actions for the next turn
        self.acted = False
        self.actions[0]["used"] = False
        self.actions[1]["used"] = False

    def lore_text(self, regular_font, lore):
        super().lore_text(regular_font, lore)
        # add bot actions name and description to lore text
        for action in self.actions:
            lore.append((f"Action: {action['name']}", "normal"))
            action_description_lines = wrap_text(f"Description: {action['description']}", regular_font, 560)
            for i, line in enumerate(action_description_lines):
                if i == len(action_description_lines) - 1:
                    lore.append((line, "normal"))
                else:
                    lore.append((line, "less"))
            self.lore_stats_text(lore, action)

class GunBot(Bot):
    def __init__(self, name, health, x, y, box_background_color, description, idle_images_path, active_image_path, hurt_image_path, dead_image_path, button_color, button_hover_color, text_used_color):
        super().__init__(name, health, x, y, box_background_color, description, idle_images_path, active_image_path, hurt_image_path, dead_image_path, button_color, button_hover_color, text_used_color)
        # action dictionary
        self.actions = [
            {
                "name": "Left Gun",
                "damage": 1,
                "used": False,
                "target_state": "Target Enemy",
                "image_path": "assets/bots/gun_bot/gun_bot_left_gun.png",
                "image": None,
                "description": "A basic attack that deals damage to a single enemy.",
                "scroll": 65,
                "projectile_offset": (-25, -49)
            },
            {
                "name": "Right Gun",
                "damage": 1,
                "used": False,
                "target_state": "Target Enemy",
                "image_path": "assets/bots/gun_bot/gun_bot_right_gun.png",
                "image": None,
                "description": "A basic attack that deals damage to a single enemy.",
                "scroll": 155,
                "projectile_offset": (32, -18)
            }
        ]
    
    def perform_action(self, active_effects, target_char, chosen_action):
        # perform action on target character based on which action is chosen
        if chosen_action == "Left Gun":
            damage = target_char.damage_amount(self.actions[0]["damage"])
            target_char.real_health -= damage
            active_effects.append(LinearProjectile((0, 0, 255), self, target_char, self.actions[0]["projectile_offset"], damage, "Damage"))
        elif chosen_action == "Right Gun":
            damage = target_char.damage_amount(self.actions[1]["damage"])
            target_char.real_health -= damage
            active_effects.append(LinearProjectile((0, 0, 255), self, target_char, self.actions[1]["projectile_offset"], damage, "Damage"))

    def lore_stats_text(self, lore, action):
        # add action stats to lore text
        if action["name"] == "Left Gun":
            lore.append((f"Damage: {action['damage']}", "normal"))
        elif action["name"] == "Right Gun":
            lore.append((f"Damage: {action['damage']}", "normal"))

class RicoBot(Bot):
    def __init__(self, name, health, x, y, box_background_color, description, idle_images_path, active_image_path, hurt_image_path, dead_image_path, button_color, button_hover_color, text_used_color):
        super().__init__(name, health, x, y, box_background_color, description, idle_images_path, active_image_path, hurt_image_path, dead_image_path, button_color, button_hover_color, text_used_color)
        # action dictionary
        self.actions = [
            {
                "name": "Heal",
                "heal": 1,
                "used": False,
                "target_state": "Target Bot",
                "image_path": "assets/bots/rico_bot/rico_bot_heal.png",
                "image": None,
                "description": "Shoots a healing ball that heals a friendly bot.",
                "scroll": 65,
                "projectile_offset": (37, -21)
            },
            {
                "name": "Bounce",
                "damage": 1,
                "bounce_amount": 2,
                "used": False,
                "target_state": "Target Enemy",
                "image_path": "assets/bots/rico_bot/rico_bot_bounce.png",
                "image": None,
                "description": "Shoots a bouncy ball that bounces between enemies dealing damage.",
                "scroll": 155,
                "projectile_offset": (35, -20)
            }
        ]
    
    def perform_action(self, active_effects, target_char, chosen_action):
        # perform action on target character based on which action is chosen
        if chosen_action == "Heal":
            target_char.real_health += self.actions[0]["heal"]
            active_effects.append(HealProjectile((0, 255, 0), self, target_char, self.actions[0]["projectile_offset"], self.actions[0]["heal"]))
        elif chosen_action == "Bounce":
            damage = target_char.damage_amount(self.actions[1]["damage"])
            target_char.real_health -= damage
            active_effects.append(BounceProjectile((0, 255, 0), self, target_char, self.actions[1]["projectile_offset"], self.actions[1]["damage"], self.actions[1]["bounce_amount"] - 1, []))

    def lore_stats_text(self, lore, action):
        # add action stats to lore text
        if action["name"] == "Heal":
            lore.append((f"Heal: {action['heal']}", "normal"))
        elif action["name"] == "Bounce":
            lore.append((f"Bounces: {action['bounce_amount']}", "normal"))
            lore.append((f"Damage: {action['damage']}", "normal"))

class ModBot(Bot):
    def __init__(self, name, health, x, y, box_background_color, description, idle_images_path, active_image_path, hurt_image_path, dead_image_path, button_color, button_hover_color, text_used_color):
        super().__init__(name, health, x, y, box_background_color, description, idle_images_path, active_image_path, hurt_image_path, dead_image_path, button_color, button_hover_color, text_used_color)
        # action dictionary
        self.actions = [
            {
                "name": "Percentage",
                "damage": 0.1,
                "used": False,
                "target_state": "Target Enemy",
                "image_path": "assets/bots/mod_bot/mod_bot_percentage.png",
                "image": None,
                "description": "Shoots a percentage projectile that damages an enemy. The amount of damage is based on the percentage of the enemy's current health. The amount of damage is rounded down with a minimum of 1 damage.",
                "scroll": 65,
                "projectile_offset": (-22, -26)
            },
            {
                "name": "Shield",
                "shield": 0.9,
                "used": False,
                "target_state": "Target Bot",
                "image_path": "assets/bots/mod_bot/mod_bot_shield.png",
                "image": None,
                "description": "Shoots a shield projectile that creates a shield around a friendly bot. The shield reduces enemy damage for one round. The damage taken is rounded up.",
                "scroll": 215,
                "projectile_offset": (21, 19)
            }
        ]

    def perform_action(self, active_effects, target_char, chosen_action):
        # perform action on target character based on which action is chosen
        if chosen_action == "Percentage":
            percentage_damage = max(1, int(target_char.real_health * self.actions[0]["damage"]))
            damage = target_char.damage_amount(percentage_damage)
            target_char.real_health -= damage
            active_effects.append(PercentageProjectile((200, 200, 200), self, target_char, self.actions[0]["projectile_offset"], damage, "Damage"))
        elif chosen_action == "Shield":
            active_effects.append(ShieldProjectile((200, 200, 200), self, target_char, self.actions[1]["projectile_offset"], self.actions[1]["shield"]))

    def lore_stats_text(self, lore, action):
        # add action stats to lore text
        if action["name"] == "Percentage":
            lore.append((f"Damage: {int(action['damage'] * 100)}%", "normal"))
        elif action["name"] == "Shield":
            lore.append((f"Damage Reduction: {round((1-action['shield']) * 100)}%", "normal"))

class ElementalBot(Bot):
    def __init__(self, name, health, x, y, box_background_color, description, idle_images_path, active_image_path, hurt_image_path, dead_image_path, button_color, button_hover_color, text_used_color):
        super().__init__(name, health, x, y, box_background_color, description, idle_images_path, active_image_path, hurt_image_path, dead_image_path, button_color, button_hover_color, text_used_color)
        # action dictionary
        self.actions = [
            {
                "name": "Fire",
                "damage": 1,
                "fire_rounds_amount": 2,
                "used": False,
                "target_state": "Target Enemy",
                "image_path": "assets/bots/elemental_bot/elemental_bot_fire.png",
                "image": None,
                "description": "Shoots a fire projectile at an enemy. Sets the enemy on fire, dealing damage over time. The fire does damage at the end of the round.",
                "scroll": 65,
                "projectile_offset": (-22, 11)
            },
            {
                "name": "Ice",
                "ice_hits_needed": 3,
                "used": False,
                "target_state": "Target Enemy",
                "image_path": "assets/bots/elemental_bot/elemental_bot_ice.png",
                "image": None,
                "description": "Shoots an ice projectile at an enemy. After the enemy has been hit multiple times, it will be frozen and cannot attack for a round.",
                "scroll": 220,
                "projectile_offset": (10, 13)
            }
        ]
    
    def perform_action(self, active_effects, target_char, chosen_action):
        # perform action on target character based on which action is chosen
        if chosen_action == "Fire":
            active_effects.append(LinearProjectile((255, 0, 0), self, target_char, self.actions[0]["projectile_offset"], self.actions[0]["fire_rounds_amount"], "Fire"))
        elif chosen_action == "Ice":
            active_effects.append(LinearProjectile((0, 255, 255), self, target_char, self.actions[1]["projectile_offset"], self.actions[1]["ice_hits_needed"], "Ice"))

    def lore_stats_text(self, lore, action):
        # add action stats to lore text
        if action["name"] == "Fire":
            lore.append((f"Fire Rounds: {action['fire_rounds_amount']}", "normal"))
            lore.append((f"Damage: {action['damage']}", "normal"))
        elif action["name"] == "Ice":
            lore.append((f"Ice Hits Needed: {action['ice_hits_needed']}", "normal"))

class LazerBot(Bot):
    def __init__(self, name, health, x, y, box_background_color, description, idle_images_path, active_image_path, hurt_image_path, dead_image_path, button_color, button_hover_color, text_used_color):
        super().__init__(name, health, x, y, box_background_color, description, idle_images_path, active_image_path, hurt_image_path, dead_image_path, button_color, button_hover_color, text_used_color)
        # action dictionary
        self.actions = [
            {
                "name": "Pierce",
                "damage": 1,
                "movement_mode": False,
                "used": False,
                "target_state": "Target Line",
                "image_path": "assets/bots/lazer_bot/lazer_bot_pierce.png",
                "image": None,
                "description": "Fires a laser beam that can pierce through multiple enemies in a straight line. The laser beam can be aimed with the mouse position. Click to fire the laser beam and all enemies in the line will take damage. Click on lazer bot to enter into movement mode. While in movement mode, you can move lazer bot up and down with the mouse position. Click on lazer bot again to exit movement mode. You can use movement mode to have better aim with the laser beam.",
                "scroll": 65,
                "projectile_offset": (11, -1)
            },
            {
                "name": "Barrage",
                "damage": 1,
                "barrage_charge": 0,
                "barrage_charge_needed": 20,
                "used": True,
                "target_state": "Target Enemy",
                "image_path": "assets/bots/lazer_bot/lazer_bot_barrage.png",
                "image": None,
                "description": "Fires a laser beam at every enemy in the battle. This action can only be used after charging up the barrage. Each enemy hit with the Pierce action will charge up the barrage.",
                "scroll": 275,
                "projectile_offset": (-12, -8)
            }
        ]

    def reset_actions(self):
        # reset actions for the next turn
        self.acted = False
        self.actions[0]["used"] = False

    def perform_action(self, active_effects, target_list, chosen_action, laser_end):
        # perform action on target characters based on which action is chosen
        if chosen_action == "Pierce":
            # create laser projectile and damage all enemies hit by the laser
            active_effects.append(LaserProjectile((self.rect.centerx + self.actions[0]["projectile_offset"][0], self.rect.centery + self.actions[0]["projectile_offset"][1]), laser_end))
            for enemy in target_list:
                damage = enemy.damage_amount(self.actions[0]["damage"])
                enemy.real_health -= damage
                enemy.take_damage(active_effects, damage)
                self.actions[1]["barrage_charge"] += 1
            # check if barrage is charged and reset used status if it is
            if self.actions[1]["barrage_charge"] >= self.actions[1]["barrage_charge_needed"] and self.actions[1]["used"]:
                self.actions[1]["used"] = False
                active_effects.append(FloatingText((255, 50, 255), self.rect.x, self.rect.top - 20, "Barrage Ready!"))
        
        elif chosen_action == "Barrage":
            # damage all enemies on the field and reset barrage charge
            self.actions[1]["barrage_charge"] -= self.actions[1]["barrage_charge_needed"]
            for enemy in target_list:
                if enemy.real_health > 0:
                    damage = enemy.damage_amount(self.actions[1]["damage"])
                    enemy.real_health -= damage
                    active_effects.append(LaserProjectile((self.rect.centerx + self.actions[1]["projectile_offset"][0], self.rect.centery + self.actions[1]["projectile_offset"][1]), (enemy.rect.centerx, enemy.rect.centery)))
                    enemy.take_damage(active_effects, damage)

    def lore_stats_text(self, lore, action):
        # add action stats to lore text
        if action["name"] == "Pierce":
            lore.append((f"Damage: {action['damage']}", "normal"))
        elif action["name"] == "Barrage":
            lore.append((f"Damage: {action['damage']}", "normal"))
            lore.append((f"Current Charge: {action['barrage_charge']}", "normal"))
            lore.append((f"Charge Needed: {action['barrage_charge_needed']}", "normal"))

class ChaosBot(Bot):
    def __init__(self, name, health, x, y, box_background_color, description, idle_images_path, active_image_path, hurt_image_path, dead_image_path, button_color, button_hover_color, text_used_color):
        super().__init__(name, health, x, y, box_background_color, description, idle_images_path, active_image_path, hurt_image_path, dead_image_path, button_color, button_hover_color, text_used_color)
        # action dictionary
        self.actions = [
            {
                "name": "Random",
                "min_power": 1,
                "max_power": 5,
                "used": False,
                "target_state": "Target Any",
                "image_path": "assets/bots/chaos_bot/chaos_bot_random.png",
                "image": None,
                "description": "Shoots a glitchy projectile that can heal a friendly bot or damage an enemy. The amount of healing or damage is random.",
                "scroll": 65,
                "projectile_offset": (-6, 6)
            },
            {
                "name": "Barrier",
                "block": 10,
                "used": False,
                "target_state": "Target Bot",
                "image_path": "assets/bots/chaos_bot/chaos_bot_barrier.png",
                "image": None,
                "description": "Shoots a glitchy projectile that creates a barrier around a friendly bot. The barrier has a chance to block enemy damage for one round.",
                "scroll": 200,
                "projectile_offset": (-5, 6)
            }
        ]

    def update_idle_animation(self):
        # update idle animation to be random when character is alive and doing nothing
        if self.visual_health > 0:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = random.randint(0, len(self.idle_images) - 1)

    def perform_action(self, active_effects, target_char, chosen_action):
        # perform action on target character based on which action is chosen
        if chosen_action == "Random":
            random_amount = random.randint(self.actions[0]["min_power"], self.actions[0]["max_power"])
            if isinstance(target_char, Enemy):
                damage = target_char.damage_amount(random_amount)
                target_char.real_health -= damage
                active_effects.append(GlitchyDamageProjectile((255, 155, 0), self, target_char, self.actions[0]["projectile_offset"], damage))
            else:
                target_char.real_health += random_amount
                active_effects.append(GlitchyHealProjectile((255, 155, 0), self, target_char, self.actions[0]["projectile_offset"], random_amount))
        elif chosen_action == "Barrier":
            active_effects.append(GlitchyBlockProjectile((255, 155, 0), self, target_char, self.actions[1]["projectile_offset"], self.actions[1]["block"]))

    def lore_stats_text(self, lore, action):
        # add action stats to lore text
        if action["name"] == "Random":
            lore.append((f"Min Power: {action['min_power']}", "normal"))
            lore.append((f"Max Power: {action['max_power']}", "normal"))
        elif action["name"] == "Barrier":
            lore.append((f"Block Chance: {action['block']}%", "normal"))

class DuploBot(Bot):
    def __init__(self, name, health, x, y, box_background_color, description, idle_images_path, active_image_path, hurt_image_path, dead_image_path, button_color, button_hover_color, text_used_color):
        super().__init__(name, health, x, y, box_background_color, description, idle_images_path, active_image_path, hurt_image_path, dead_image_path, button_color, button_hover_color, text_used_color)
        # action dictionary
        self.actions = [
            {
                "name": "Charge",
                "damage": 1,
                "projectile_radius": 2,
                "used": False,
                "target_state": "Target Enemy or Self",
                "image_path": "assets/bots/duplo_bot/duplo_bot_charge.png",
                "image": None,
                "description": "Charge or attack. Click on Duplo Bot to charge. Charging doubles the damage. Click on an enemy to attack. The damage will reset to 1 after attacking.",
                "scroll": 65,
                "projectile_offset": (26, -28)
            },
            {
                "name": "Mark",
                "mark_hits_needed": 2,
                "used": False,
                "target_state": "Target Enemy",
                "image_path": "assets/bots/duplo_bot/duplo_bot_mark.png",
                "image": None,
                "description": "Shoots a marker at an enemy. After the enemy has been hit multiple times, it will be marked and take double damage from all sources for a round.",
                "scroll": 195,
                "projectile_offset": (26, -28)
            }
        ]

    def perform_action(self, active_effects, target_char, chosen_action):
        # perform action on target character based on which action is chosen
        if chosen_action == "Charge":
            # if target character is self, increase damage
            if target_char == self:
                self.actions[0]["damage"] *= 2
                self.actions[0]["projectile_radius"] += 2
                text = "Charged!"
                text_width = len(text) * 10
                text_x = random.randint(self.rect.left, self.rect.right - text_width)
                active_effects.append(FloatingText((255, 255, 0), text_x, self.rect.top + 10, text))
            # if target character is an enemy, deal damage and reset damage
            else:
                damage = target_char.damage_amount(self.actions[0]["damage"])
                target_char.real_health -= damage
                active_effects.append(ChargeProjectile((255, 255, 0), self, target_char, self.actions[0]["projectile_offset"], damage, "Damage", self.actions[0]["projectile_radius"]))
                self.actions[0]["damage"] = 1
                self.actions[0]["projectile_radius"] = 2
        elif chosen_action == "Mark":
            active_effects.append(MarkProjectile((255, 255, 0), self, target_char, self.actions[1]["projectile_offset"], self.actions[1]["mark_hits_needed"], "Mark"))

    def lore_stats_text(self, lore, action):
        # add action stats to lore text
        if action["name"] == "Charge":
            lore.append((f"Damage: {action['damage']}", "normal"))
        elif action["name"] == "Mark":
            lore.append((f"Mark Hits Needed: {action['mark_hits_needed']}", "normal"))

# ------------------------------
# BOT INSTANCES
# ------------------------------

gun_bot = GunBot(
    "Gun Bot", # name
    10, # health
    200, 100, # x, y
    (50, 100, 255), # box_background_color
    "A bot equipped with dual guns.", # description
    [
        "assets/bots/gun_bot/gun_bot_idle_1.png",
        "assets/bots/gun_bot/gun_bot_idle_2.png",
        "assets/bots/gun_bot/gun_bot_idle_3.png",
        "assets/bots/gun_bot/gun_bot_idle_4.png",
        "assets/bots/gun_bot/gun_bot_idle_3.png",
        "assets/bots/gun_bot/gun_bot_idle_2.png"
    ], # idle_images_path
    "assets/bots/gun_bot/gun_bot_active.png", # active_image_path
    "assets/bots/gun_bot/gun_bot_hurt.png", # hurt_image_path
    "assets/bots/gun_bot/gun_bot_dead.png", # dead_image_path
    (100, 150, 255), # button_color
    (150, 200, 255), # button_hover_color
    (150, 200, 255) # text_used_color
)

rico_bot = RicoBot(
    "Rico Bot", # name
    10, # health
    200, 275, # x, y
    (50, 200, 50), # box_background_color
    "A bot that just loves balls.", # description
    [
        "assets/bots/rico_bot/rico_bot_idle_1.png",
        "assets/bots/rico_bot/rico_bot_idle_2.png",
        "assets/bots/rico_bot/rico_bot_idle_3.png",
        "assets/bots/rico_bot/rico_bot_idle_4.png",
        "assets/bots/rico_bot/rico_bot_idle_5.png",
        "assets/bots/rico_bot/rico_bot_idle_4.png",
        "assets/bots/rico_bot/rico_bot_idle_3.png",
        "assets/bots/rico_bot/rico_bot_idle_2.png"
    ], # idle_images_path
    "assets/bots/rico_bot/rico_bot_active.png", # active_image_path
    "assets/bots/rico_bot/rico_bot_hurt.png", # hurt_image_path
    "assets/bots/rico_bot/rico_bot_dead.png", # dead_image_path
    (100, 230, 100), # button_color
    (150, 250, 150), # button_hover_color
    (150, 250, 150) # text_used_color
)

elemental_bot = ElementalBot(
    "Elemental Bot", # name
    10, # health
    200, 450, # x, y
    (150, 0, 150), # box_background_color
    "A bot that can manipulate the elements.", # description
    [
        "assets/bots/elemental_bot/elemental_bot_idle_1.png",
        "assets/bots/elemental_bot/elemental_bot_idle_2.png",
        "assets/bots/elemental_bot/elemental_bot_idle_3.png",
        "assets/bots/elemental_bot/elemental_bot_idle_4.png",
        "assets/bots/elemental_bot/elemental_bot_idle_5.png",
        "assets/bots/elemental_bot/elemental_bot_idle_4.png",
        "assets/bots/elemental_bot/elemental_bot_idle_3.png",
        "assets/bots/elemental_bot/elemental_bot_idle_2.png"
    ], # idle_images_path
    "assets/bots/elemental_bot/elemental_bot_active.png", # active_image_path
    "assets/bots/elemental_bot/elemental_bot_hurt.png", # hurt_image_path
    "assets/bots/elemental_bot/elemental_bot_dead.png", # dead_image_path
    (200, 50, 200), # button_color
    (250, 100, 250), # button_hover_color
    (225, 100, 225) # text_used_color
)

mod_bot = ModBot(
    "Mod Bot", # name
    10, # health
    350, 100, # x, y
    (100, 100, 100), # box_background_color
    "A bot full of mod power.", # description
    [
        "assets/bots/mod_bot/mod_bot_idle_1.png",
        "assets/bots/mod_bot/mod_bot_idle_2.png",
        "assets/bots/mod_bot/mod_bot_idle_3.png",
        "assets/bots/mod_bot/mod_bot_idle_4.png",
        "assets/bots/mod_bot/mod_bot_idle_5.png",
        "assets/bots/mod_bot/mod_bot_idle_4.png",
        "assets/bots/mod_bot/mod_bot_idle_3.png",
        "assets/bots/mod_bot/mod_bot_idle_2.png"
    ], # idle_images_path
    "assets/bots/mod_bot/mod_bot_active.png", # active_image_path
    "assets/bots/mod_bot/mod_bot_hurt.png", # hurt_image_path
    "assets/bots/mod_bot/mod_bot_dead.png", # dead_image_path
    (150, 150, 150), # button_color
    (200, 200, 200), # button_hover_color
    (190, 190, 190) # text_used_color
)

chaos_bot = ChaosBot(
    "Chaos Bot", # name
    10, # health
    350, 275, # x, y
    (255, 155, 0), # box_background_color
    "A bot full of powerful chaos, use carefully.", # description
    [
        "assets/bots/chaos_bot/chaos_bot_idle_1.png",
        "assets/bots/chaos_bot/chaos_bot_idle_2.png",
        "assets/bots/chaos_bot/chaos_bot_idle_3.png",
        "assets/bots/chaos_bot/chaos_bot_idle_4.png",
        "assets/bots/chaos_bot/chaos_bot_idle_5.png"
    ], # idle_images_path
    "assets/bots/chaos_bot/chaos_bot_active.png", # active_image_path
    "assets/bots/chaos_bot/chaos_bot_hurt.png", # hurt_image_path
    "assets/bots/chaos_bot/chaos_bot_dead.png", # dead_image_path
    (255, 205, 100), # button_color
    (255, 230, 175), # button_hover_color
    (255, 230, 175) # text_used_color
)

duplo_bot = DuploBot(
    "Duplo Bot", # name
    10, # health
    350, 450, # x, y
    (200, 200, 0), # box_background_color
    "A bot made of doubling power.", # description
    [
        "assets/bots/duplo_bot/duplo_bot_idle_1.png",
        "assets/bots/duplo_bot/duplo_bot_idle_2.png",
        "assets/bots/duplo_bot/duplo_bot_idle_3.png",
        "assets/bots/duplo_bot/duplo_bot_idle_4.png",
        "assets/bots/duplo_bot/duplo_bot_idle_5.png"
    ], # idle_images_path
    "assets/bots/duplo_bot/duplo_bot_active.png", # active_image_path
    "assets/bots/duplo_bot/duplo_bot_hurt.png", # hurt_image_path
    "assets/bots/duplo_bot/duplo_bot_dead.png", # dead_image_path
    (220, 220, 50), # button_color
    (240, 240, 100), # button_hover_color
    (255, 240, 100) # text_used_color
)

lazer_bot = LazerBot(
    "Lazer Bot", # name
    10, # health
    480, 300, # x, y
    (255, 50, 200), # box_background_color
    "A bot with the coolest laser powers.", # description
    [
        "assets/bots/lazer_bot/lazer_bot_idle_1.png",
        "assets/bots/lazer_bot/lazer_bot_idle_2.png",
        "assets/bots/lazer_bot/lazer_bot_idle_3.png",
        "assets/bots/lazer_bot/lazer_bot_idle_4.png",
        "assets/bots/lazer_bot/lazer_bot_idle_5.png",
        "assets/bots/lazer_bot/lazer_bot_idle_4.png",
        "assets/bots/lazer_bot/lazer_bot_idle_3.png",
        "assets/bots/lazer_bot/lazer_bot_idle_2.png"
    ], # idle_images_path
    "assets/bots/lazer_bot/lazer_bot_active.png", # active_image_path
    "assets/bots/lazer_bot/lazer_bot_hurt.png", # hurt_image_path
    "assets/bots/lazer_bot/lazer_bot_dead.png", # dead_image_path
    (255, 125, 225), # button_color
    (255, 175, 245), # button_hover_color
    (255, 175, 225) # text_used_color
)
