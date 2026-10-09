# characters.py

import pygame
import math
import random

# import game modules
from .helper import FloatingText, wrap_text

# ------------------------------
# CHARACTER CLASS
# ------------------------------

class Character:
    def __init__(self, x, y):
        # basic character info
        self.rect = pygame.Rect(x, y, 100, 100)

        # status effects
        self.fire_rounds = 0
        self.ice_hits = 0
        self.frozen = False
        self.mark_hits = 0
        self.marked = False
        self.block = 0
        self.shield = 0

        # animation
        self.animation_timer = 0
        self.animation_speed = 15
        self.hurt_timer = 0
        self.shake_x = 0  

    def damage_amount(self, damage):
        # calculate damage amount based on block chance
        if self.block > 0:
            block_roll = random.randint(1, 100)
            if block_roll <= self.block:
                return 0, 0

        # double damage if marked
        if self.marked:
            damage *= 2
        
        # reduce damage if shield is active
        if self.shield > 0:
            og_damage = damage
            damage = math.ceil(damage * self.shield)
            reduction = og_damage - damage
        else:
            reduction = 0
        
        return damage, reduction

    def take_damage(self, active_effects, damage, reduction):
        # reduce health
        self.visual_health -= damage
        if self.visual_health < 0:
            self.visual_health = 0
        if self.real_health < 0:
            self.real_health = 0

        # text animation
        if damage == 0:
            text = "Blocked!"
            color = (255, 155, 0)
        else:
            self.hurt_timer = 30
            text = f"-{damage}"
            color = (255, 0, 0)
        text_width = len(text) * 10
        text_x = random.randint(self.rect.left, self.rect.right - text_width)
        active_effects.append(FloatingText(color, text_x, self.rect.top + 10, text))

        # reduction text animation
        if reduction > 0:
            reduction_text = f"{reduction} reduced"
            reduction_text_width = len(reduction_text) * 10
            reduction_text_x = random.randint(self.rect.left, self.rect.right - reduction_text_width)
            active_effects.append(FloatingText((200, 200, 200), reduction_text_x, self.rect.top + 30, reduction_text))

    def take_heal(self, active_effects, amount):
        # increase health
        self.visual_health += amount

        # text animation
        text_x = random.randint(self.rect.left, self.rect.right - 30)
        active_effects.append(FloatingText((0, 255, 0), text_x, self.rect.top + 10, f"+{amount}"))

    def apply_fire(self, active_effects, fire_rounds_amount):
        # add fire rounds
        self.fire_rounds += fire_rounds_amount

        # text animation
        text = f"+{fire_rounds_amount} fire"
        text_width = len(text) * 10
        text_x = random.randint(self.rect.left, self.rect.right - text_width)
        active_effects.append(FloatingText((255, 100, 0), text_x, self.rect.top + 10, text))

    def apply_ice(self, active_effects, ice_hits_needed):
        # add ice hits, freeze if enough hits, and display text animation
        self.ice_hits += 1
        if self.ice_hits >= ice_hits_needed:
            self.frozen = True
            self.ice_hits = 0
            text = "Frozen!"
        else:
            text = "+1 ice"
        text_width = len(text) * 10
        text_x = random.randint(self.rect.left, self.rect.right - text_width)
        active_effects.append(FloatingText((0, 255, 255), text_x, self.rect.top + 10, text))

    def apply_mark(self, active_effects, mark_hits_needed):
        # add mark hits, mark if enough hits, and display text animation
        self.mark_hits += 1
        if self.mark_hits >= mark_hits_needed:
            self.marked = True
            self.mark_hits = 0
            text = "Marked!"
        else:
            text = "+1 mark"
        text_width = len(text) * 10
        text_x = random.randint(self.rect.left, self.rect.right - text_width)
        active_effects.append(FloatingText((255, 255, 0), text_x, self.rect.top + 10, text))

    def hurt_animations(self):
        # shake character when hurt
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
            self.shake_x = random.randint(-5, 5)
        else:
            self.shake_x = 0

    def lore_text(self, fonts, lore):
        # add character name and description to lore text
        lore.append((f"Name: {self.name}", "normal"))
        description_lines = wrap_text(f"Description: {self.description}", fonts, 560)
        for i, line in enumerate(description_lines):
            if i == len(description_lines) - 1:
                lore.append((line, "normal"))
            else:
                lore.append((line, "less"))
