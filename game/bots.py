# bots.py

import pygame
import random

# import game modules
from .characters import Character
from .helper import FloatingText, wrap_text
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
    def __init__(self, x, y):
        super().__init__(x, y)
        # bot specific info
        self.real_health = 10
        self.visual_health = 10
        self.acted = False
        self.current_frame = 0
        
        # images
        self.idle_images = []
        self.active_image = None
        self.hurt_image = None
        self.dead_image = None
    
    def load_images(self):
        # load all different bot images
        for path in self.idle_images_path:
            self.idle_images.append(pygame.image.load(path).convert_alpha())
        self.active_image = pygame.image.load(self.active_image_path).convert_alpha()
        for action in self.actions:
            action["image"] = pygame.image.load(action["image_path"]).convert_alpha()
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
        for action in self.actions:
            action["used"] = False

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)
        # add bot actions name and description to lore text
        for action in self.actions:
            lore.append((f"Action: {action['name']}", "normal"))
            # show different description for gun bot left gun if aiming is unlocked
            if action["name"] == "Left Gun" and action["aiming_unlocked"]:
                action_description_lines = wrap_text("Description: An attack that fires at an enemy. The damage is based on the timing of the attack. The marker will go up and down until you attack. The damage is based on where the marker is.", fonts, 560)
            else:
                action_description_lines = wrap_text(f"Description: {action['description']}", fonts, 560)
            for i, line in enumerate(action_description_lines):
                if i == len(action_description_lines) - 1:
                    lore.append((line, "normal"))
                else:
                    lore.append((line, "less"))
            self.lore_stats_text(lore, action)

class GunBot(Bot):
    def __init__(self, x, y):
        super().__init__(x, y)
        # gun bot specific info
        self.name = "Gun Bot"
        self.description = "A bot with dual guns."

        # colors
        self.box_background_color = (50, 100, 255)
        self.button_color = (100, 150, 255)
        self.button_hover_color = (150, 200, 255)
        self.text_used_color = (150, 200, 255)

        # images
        self.idle_images_path = [
            "assets/bots/gun_bot/gun_bot_idle_1.png",
            "assets/bots/gun_bot/gun_bot_idle_2.png",
            "assets/bots/gun_bot/gun_bot_idle_3.png",
            "assets/bots/gun_bot/gun_bot_idle_4.png",
            "assets/bots/gun_bot/gun_bot_idle_5.png",
            "assets/bots/gun_bot/gun_bot_idle_4.png",
            "assets/bots/gun_bot/gun_bot_idle_3.png",
            "assets/bots/gun_bot/gun_bot_idle_2.png"
        ]
        self.active_image_path = "assets/bots/gun_bot/gun_bot_active.png"
        self.hurt_image_path = "assets/bots/gun_bot/gun_bot_hurt.png"
        self.dead_image_path = "assets/bots/gun_bot/gun_bot_dead.png"

        # action dictionary
        self.actions = [
            {
                "name": "Left Gun",
                "damage": 1,
                "aiming_unlocked": False,
                "marker_y": 40,
                "marker_y_direction": "Down",
                "marker_y_speed": 10,
                "zones": [],
                "used": False,
                "target_state": "Target Enemy",
                "image_path": "assets/bots/gun_bot/gun_bot_left_gun.png",
                "image": None,
                "description": "A basic attack that fires at an enemy.",
                "scroll": 65,
                "projectile_offset": (-20, -49)
            },
            {
                "name": "Right Gun",
                "damage": 1,
                "used": False,
                "target_state": "Target Enemy",
                "image_path": "assets/bots/gun_bot/gun_bot_right_gun.png",
                "image": None,
                "description": "A basic attack that fires at an enemy.",
                "scroll": 155,
                "projectile_offset": (35, -18)
            }
        ]
    
    def perform_action(self, active_effects, target_char, chosen_action):
        # perform action on target character based on which action is chosen
        if chosen_action == "Left Gun":
            # if aiming is unlocked, find the damage
            if self.actions[0]["aiming_unlocked"]:
                for zone in self.actions[0]["zones"]:
                    if zone["position"] <= self.actions[0]["marker_y"] < zone["position"] + zone["height"]:
                        self.actions[0]["damage"] = zone["damage"]
                        break
                active_effects.append(FloatingText((50, 100, 255), 50, self.actions[0]["marker_y"], f"{self.actions[0]['damage']}"))
            
            damage, reduction = target_char.damage_amount(self.actions[0]["damage"])
            target_char.real_health -= damage
            active_effects.append(LinearProjectile((0, 0, 255), self, target_char, self.actions[0]["projectile_offset"], damage, reduction, "Damage"))
        elif chosen_action == "Right Gun":
            damage, reduction = target_char.damage_amount(self.actions[1]["damage"])
            target_char.real_health -= damage
            active_effects.append(LinearProjectile((0, 0, 255), self, target_char, self.actions[1]["projectile_offset"], damage, reduction, "Damage"))

    def lore_stats_text(self, lore, action):
        # add action stats to lore text
        if action["name"] == "Left Gun":
            lore.append((f"Damage: {action['damage']}", "normal"))
        elif action["name"] == "Right Gun":
            lore.append((f"Damage: {action['damage']}", "normal"))

    def reset_gun_aiming(self):
        # reset damage
        self.actions[0]["damage"] = 1
        self.actions[0]["marker_y"] = 40
        self.actions[0]["marker_y_direction"] = "Down"
        self.actions[0]["zones"] = []

        # randomize the position and height of the 5 damage zone
        five_height = random.randint(10, 20)
        five_position = random.randint(60, 350)
        self.actions[0]["zones"] = [{
            "damage": 5,
            "position": five_position,
            "height": five_height
        }]

        # create a random damage sequence
        damage_sequence = []
        damage_sequence.append(random.randint(1, 4))
        damage_sequence.append(random.randint(3, 4))
        damage_sequence.append(random.randint(2, 4))
        damage_sequence.append(random.randint(1, 3))
        damage_sequence.append(random.randint(2, 3))
        damage_sequence.append(random.randint(1, 2))

        # create random heights for each damage zone
        zone_heights = []
        for _ in damage_sequence:
            height = random.randint(10, 50)
            zone_heights.append(height)

        # create the damage zones above the 5 damage zone
        above_zone_y = five_position
        for i, damage in enumerate(damage_sequence):
            zone_height = zone_heights[i]
            zone_position = max(40, above_zone_y - zone_height)
            actual_zone_height = above_zone_y - zone_position
            # if the current zone and previous zone have the same damage, merge them
            if i != 0 and damage_sequence[i-1] == damage:
                self.actions[0]["zones"][-1]["position"] = zone_position
                self.actions[0]["zones"][-1]["height"] += actual_zone_height
            # create a new zone
            else:
                self.actions[0]["zones"].append({
                    "damage": damage,
                    "position": zone_position,
                    "height": actual_zone_height
                })
            above_zone_y -= zone_height
            if above_zone_y <= 40:
                break

        # fill the remaining space at the top with a 1 damage zone
        if above_zone_y > 40:
            if damage_sequence[-1] == 1:
                self.actions[0]["zones"][-1]["position"] = 40
                self.actions[0]["zones"][-1]["height"] += above_zone_y - 40
            else:
                self.actions[0]["zones"].append({
                    "damage": 1,
                    "position": 40,
                    "height": above_zone_y - 40
                })

        # create the damage zones below the 5 damage zone
        below_zone_y = five_position + five_height
        for i, damage in enumerate(damage_sequence):
            zone_height = zone_heights[i]
            zone_position = below_zone_y
            actual_zone_height = min(zone_height, 413 - below_zone_y)
            # if the current zone and previous zone have the same damage, merge them
            if i != 0 and damage_sequence[i-1] == damage:
                self.actions[0]["zones"][-1]["height"] += actual_zone_height
            # create a new zone
            else:
                self.actions[0]["zones"].append({
                    "damage": damage,
                    "position": zone_position,
                    "height": actual_zone_height
                })
            below_zone_y += zone_height
            if below_zone_y >= 413:
                break

        # fill the remaining space at the bottom with a 1 damage zone
        if below_zone_y < 413:
            if damage_sequence[-1] == 1:
                self.actions[0]["zones"][-1]["height"] += 413 - below_zone_y
            else:
                self.actions[0]["zones"].append({
                    "damage": 1,
                    "position": below_zone_y,
                    "height": 413 - below_zone_y
                })

    def update_gun_aiming(self):
        # move the marker down
        if self.actions[0]["marker_y_direction"] == "Down":
            self.actions[0]["marker_y"] += self.actions[0]["marker_y_speed"]
            # change marker direction when it reaches the bottom
            if self.actions[0]["marker_y"] > 413:
                self.actions[0]["marker_y"] = 413
                self.actions[0]["marker_y_direction"] = "Up"

        # move the marker up
        elif self.actions[0]["marker_y_direction"] == "Up":
            self.actions[0]["marker_y"] -= self.actions[0]["marker_y_speed"]
            # change marker direction when it reaches the top
            if self.actions[0]["marker_y"] < 40:
                self.actions[0]["marker_y"] = 40
                self.actions[0]["marker_y_direction"] = "Down"

class RicoBot(Bot):
    def __init__(self, x, y):
        super().__init__(x, y)
        # rico bot specific info
        self.name = "Rico Bot"
        self.description = "A bot that just loves balls."

        # colors
        self.box_background_color = (50, 200, 50)
        self.button_color = (100, 230, 100)
        self.button_hover_color = (150, 250, 150)
        self.text_used_color = (150, 250, 150)

        # images
        self.idle_images_path = [
            "assets/bots/rico_bot/rico_bot_idle_1.png",
            "assets/bots/rico_bot/rico_bot_idle_2.png",
            "assets/bots/rico_bot/rico_bot_idle_3.png",
            "assets/bots/rico_bot/rico_bot_idle_4.png",
            "assets/bots/rico_bot/rico_bot_idle_5.png",
            "assets/bots/rico_bot/rico_bot_idle_4.png",
            "assets/bots/rico_bot/rico_bot_idle_3.png",
            "assets/bots/rico_bot/rico_bot_idle_2.png"
        ]
        self.active_image_path = "assets/bots/rico_bot/rico_bot_active.png"
        self.hurt_image_path = "assets/bots/rico_bot/rico_bot_hurt.png"
        self.dead_image_path = "assets/bots/rico_bot/rico_bot_dead.png"

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
            damage, reduction = target_char.damage_amount(self.actions[1]["damage"])
            target_char.real_health -= damage
            active_effects.append(BounceProjectile((0, 255, 0), self, target_char, self.actions[1]["projectile_offset"], damage, reduction, self.actions[1]["damage"], self.actions[1]["bounce_amount"] - 1, []))

    def lore_stats_text(self, lore, action):
        # add action stats to lore text
        if action["name"] == "Heal":
            lore.append((f"Heal: {action['heal']}", "normal"))
        elif action["name"] == "Bounce":
            lore.append((f"Bounces: {action['bounce_amount']}", "normal"))
            lore.append((f"Damage: {action['damage']}", "normal"))

class ModBot(Bot):
    def __init__(self, x, y):
        super().__init__(x, y)
        # mod bot specific info
        self.name = "Mod Bot"
        self.description = "A bot full of mod power."

        # colors
        self.box_background_color = (100, 100, 100)
        self.button_color = (150, 150, 150)
        self.button_hover_color = (200, 200, 200)
        self.text_used_color = (190, 190, 190)

        # images
        self.idle_images_path = [
            "assets/bots/mod_bot/mod_bot_idle_1.png",
            "assets/bots/mod_bot/mod_bot_idle_2.png",
            "assets/bots/mod_bot/mod_bot_idle_3.png",
            "assets/bots/mod_bot/mod_bot_idle_4.png",
            "assets/bots/mod_bot/mod_bot_idle_5.png",
            "assets/bots/mod_bot/mod_bot_idle_4.png",
            "assets/bots/mod_bot/mod_bot_idle_3.png",
            "assets/bots/mod_bot/mod_bot_idle_2.png"
        ]
        self.active_image_path = "assets/bots/mod_bot/mod_bot_active.png"
        self.hurt_image_path = "assets/bots/mod_bot/mod_bot_hurt.png"
        self.dead_image_path = "assets/bots/mod_bot/mod_bot_dead.png"
        
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
            damage, reduction = target_char.damage_amount(percentage_damage)
            target_char.real_health -= damage
            active_effects.append(PercentageProjectile((200, 200, 200), self, target_char, self.actions[0]["projectile_offset"], damage, reduction, "Damage"))
        elif chosen_action == "Shield":
            active_effects.append(ShieldProjectile((200, 200, 200), self, target_char, self.actions[1]["projectile_offset"], self.actions[1]["shield"]))

    def lore_stats_text(self, lore, action):
        # add action stats to lore text
        if action["name"] == "Percentage":
            lore.append((f"Damage: {int(action['damage'] * 100)}%", "normal"))
        elif action["name"] == "Shield":
            lore.append((f"Damage Reduction: {round((1-action['shield']) * 100)}%", "normal"))

class ElementalBot(Bot):
    def __init__(self, x, y):
        super().__init__(x, y)
        # elemental bot specific info
        self.name = "Elemental Bot"
        self.description = "A bot that can manipulate the elements."

        # colors
        self.box_background_color = (150, 0, 150)
        self.button_color = (200, 50, 200)
        self.button_hover_color = (250, 100, 250)
        self.text_used_color = (225, 100, 225)

        # images
        self.idle_images_path = [
            "assets/bots/elemental_bot/elemental_bot_idle_1.png",
            "assets/bots/elemental_bot/elemental_bot_idle_2.png",
            "assets/bots/elemental_bot/elemental_bot_idle_3.png",
            "assets/bots/elemental_bot/elemental_bot_idle_4.png",
            "assets/bots/elemental_bot/elemental_bot_idle_5.png",
            "assets/bots/elemental_bot/elemental_bot_idle_4.png",
            "assets/bots/elemental_bot/elemental_bot_idle_3.png",
            "assets/bots/elemental_bot/elemental_bot_idle_2.png"
        ]
        self.active_image_path = "assets/bots/elemental_bot/elemental_bot_active.png"
        self.hurt_image_path = "assets/bots/elemental_bot/elemental_bot_hurt.png"
        self.dead_image_path = "assets/bots/elemental_bot/elemental_bot_dead.png"

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
            active_effects.append(LinearProjectile((255, 0, 0), self, target_char, self.actions[0]["projectile_offset"], self.actions[0]["fire_rounds_amount"], 0, "Fire"))
        elif chosen_action == "Ice":
            active_effects.append(LinearProjectile((0, 255, 255), self, target_char, self.actions[1]["projectile_offset"], self.actions[1]["ice_hits_needed"], 0, "Ice"))

    def lore_stats_text(self, lore, action):
        # add action stats to lore text
        if action["name"] == "Fire":
            lore.append((f"Fire Rounds: {action['fire_rounds_amount']}", "normal"))
            lore.append((f"Damage: {action['damage']}", "normal"))
        elif action["name"] == "Ice":
            lore.append((f"Ice Hits Needed: {action['ice_hits_needed']}", "normal"))

class LazerBot(Bot):
    def __init__(self, x, y):
        super().__init__(x, y)
        # lazer bot specific info
        self.name = "Lazer Bot"
        self.description = "A bot with the coolest laser powers."

        # colors
        self.box_background_color = (255, 50, 200)
        self.button_color = (255, 125, 225)
        self.button_hover_color = (255, 175, 245)
        self.text_used_color = (255, 175, 225)

        # images
        self.idle_images_path = [
            "assets/bots/lazer_bot/lazer_bot_idle_1.png",
            "assets/bots/lazer_bot/lazer_bot_idle_2.png",
            "assets/bots/lazer_bot/lazer_bot_idle_3.png",
            "assets/bots/lazer_bot/lazer_bot_idle_4.png",
            "assets/bots/lazer_bot/lazer_bot_idle_5.png",
            "assets/bots/lazer_bot/lazer_bot_idle_4.png",
            "assets/bots/lazer_bot/lazer_bot_idle_3.png",
            "assets/bots/lazer_bot/lazer_bot_idle_2.png"
        ]
        self.active_image_path = "assets/bots/lazer_bot/lazer_bot_active.png"
        self.hurt_image_path = "assets/bots/lazer_bot/lazer_bot_hurt.png"
        self.dead_image_path = "assets/bots/lazer_bot/lazer_bot_dead.png"

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
                damage, reduction = enemy.damage_amount(self.actions[0]["damage"])
                enemy.real_health -= damage
                enemy.take_damage(active_effects, damage, reduction)
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
                    damage, reduction = enemy.damage_amount(self.actions[1]["damage"])
                    enemy.real_health -= damage
                    active_effects.append(LaserProjectile((self.rect.centerx + self.actions[1]["projectile_offset"][0], self.rect.centery + self.actions[1]["projectile_offset"][1]), (enemy.rect.centerx, enemy.rect.centery)))
                    enemy.take_damage(active_effects, damage, reduction)

    def lore_stats_text(self, lore, action):
        # add action stats to lore text
        if action["name"] == "Pierce":
            lore.append((f"Damage: {action['damage']}", "normal"))
        elif action["name"] == "Barrage":
            lore.append((f"Damage: {action['damage']}", "normal"))
            lore.append((f"Current Charge: {action['barrage_charge']}", "normal"))
            lore.append((f"Charge Needed: {action['barrage_charge_needed']}", "normal"))

class ChaosBot(Bot):
    def __init__(self, x, y):
        super().__init__(x, y)
        # chaos bot specific info
        self.name = "Chaos Bot"
        self.description = "A bot full of powerful chaos, use carefully."

        # colors
        self.box_background_color = (255, 155, 0)
        self.button_color = (255, 205, 100)
        self.button_hover_color = (255, 230, 175)
        self.text_used_color = (255, 230, 175)

        # images
        self.idle_images_path = [
            "assets/bots/chaos_bot/chaos_bot_idle_1.png",
            "assets/bots/chaos_bot/chaos_bot_idle_2.png",
            "assets/bots/chaos_bot/chaos_bot_idle_3.png",
            "assets/bots/chaos_bot/chaos_bot_idle_4.png",
            "assets/bots/chaos_bot/chaos_bot_idle_5.png"
        ]
        self.active_image_path = "assets/bots/chaos_bot/chaos_bot_active.png"
        self.hurt_image_path = "assets/bots/chaos_bot/chaos_bot_hurt.png"
        self.dead_image_path = "assets/bots/chaos_bot/chaos_bot_dead.png"

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
            # damage enemy or heal bot
            random_amount = random.randint(self.actions[0]["min_power"], self.actions[0]["max_power"])
            if isinstance(target_char, Bot):
                target_char.real_health += random_amount
                active_effects.append(GlitchyHealProjectile((255, 155, 0), self, target_char, self.actions[0]["projectile_offset"], random_amount))
            else:
                damage, reduction = target_char.damage_amount(random_amount)
                target_char.real_health -= damage
                active_effects.append(GlitchyDamageProjectile((255, 155, 0), self, target_char, self.actions[0]["projectile_offset"], damage, reduction))
                
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
    def __init__(self, x, y):
        super().__init__(x, y)
        # duplo bot specific info
        self.name = "Duplo Bot"
        self.description = "A bot made of doubling power."

        # colors
        self.box_background_color = (200, 200, 0)
        self.button_color = (220, 220, 50)
        self.button_hover_color = (240, 240, 100)
        self.text_used_color = (255, 240, 100)

        # images
        self.idle_images_path = [
            "assets/bots/duplo_bot/duplo_bot_idle_1.png",
            "assets/bots/duplo_bot/duplo_bot_idle_2.png",
            "assets/bots/duplo_bot/duplo_bot_idle_3.png",
            "assets/bots/duplo_bot/duplo_bot_idle_4.png",
            "assets/bots/duplo_bot/duplo_bot_idle_5.png"
        ]
        self.active_image_path = "assets/bots/duplo_bot/duplo_bot_active.png"
        self.hurt_image_path = "assets/bots/duplo_bot/duplo_bot_hurt.png"
        self.dead_image_path = "assets/bots/duplo_bot/duplo_bot_dead.png"

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
                damage, reduction = target_char.damage_amount(self.actions[0]["damage"])
                target_char.real_health -= damage
                active_effects.append(ChargeProjectile((255, 255, 0), self, target_char, self.actions[0]["projectile_offset"], damage, reduction, "Damage", self.actions[0]["projectile_radius"]))
                self.actions[0]["damage"] = 1
                self.actions[0]["projectile_radius"] = 2
        elif chosen_action == "Mark":
            active_effects.append(MarkProjectile((255, 255, 0), self, target_char, self.actions[1]["projectile_offset"], self.actions[1]["mark_hits_needed"], 0, "Mark"))

    def lore_stats_text(self, lore, action):
        # add action stats to lore text
        if action["name"] == "Charge":
            lore.append((f"Damage: {action['damage']}", "normal"))
        elif action["name"] == "Mark":
            lore.append((f"Mark Hits Needed: {action['mark_hits_needed']}", "normal"))

class HealerBot(Bot):
    def __init__(self, x, y):
        super().__init__(x, y)
        # healer bot specific info
        self.name = "Healer Bot"
        self.description = "A bot thats been infused with healing magic."

        # colors
        self.box_background_color = (50, 200, 50)
        self.button_color = (100, 230, 100)
        self.button_hover_color = (150, 250, 150)
        self.text_used_color = (150, 250, 150)

        # images
        self.idle_images_path = [
            "assets/bots/healer_bot/healer_bot_idle_1.png",
            "assets/bots/healer_bot/healer_bot_idle_3.png",
            "assets/bots/healer_bot/healer_bot_idle_2.png",
            "assets/bots/healer_bot/healer_bot_idle_3.png",
            "assets/bots/healer_bot/healer_bot_idle_4.png",
            "assets/bots/healer_bot/healer_bot_idle_3.png",
            "assets/bots/healer_bot/healer_bot_idle_5.png",
            "assets/bots/healer_bot/healer_bot_idle_3.png"
        ]
        self.active_image_path = "assets/bots/healer_bot/healer_bot_active.png"
        self.hurt_image_path = "assets/bots/healer_bot/healer_bot_hurt.png"
        self.dead_image_path = "assets/bots/healer_bot/healer_bot_dead.png"

        # action dictionary
        self.actions = [
            {
                "name": "Heal",
                "heal": 1,
                "used": False,
                "target_state": "Target Bot",
                "image_path": "assets/bots/healer_bot/healer_bot_heal.png",
                "image": None,
                "description": "Heals a friendly bot.",
                "scroll": 65,
                "projectile_offset": (0, 0)
            }
        ]

    def check_actions(self):
        # check if action is used
        if self.actions[0]["used"]:
            self.acted = True
    
    def perform_action(self, active_effects, target_char, chosen_action):
        # perform action on target character based on which action is chosen
        if chosen_action == "Heal":
            target_char.real_health += self.actions[0]["heal"]
            active_effects.append(HealProjectile((0, 255, 0), self, target_char, self.actions[0]["projectile_offset"], self.actions[0]["heal"]))

    def lore_stats_text(self, lore, action):
        # add action stats to lore text
        if action["name"] == "Heal":
            lore.append((f"Heal: {action['heal']}", "normal"))
