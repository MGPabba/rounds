# goons.py

import random
import pygame

# import game modules
from .characters import Character
from .projectiles import LinearProjectile

# ------------------------------
# GOON CLASSES
# ------------------------------

class Goon(Character):
    def __init__(self, x, y, slot_id):
        super().__init__(x, y)
        # goon specific info
        self.slot_id = slot_id
        self.box_background_color = (255, 75, 75)

        # animation
        self.float_direction = 2
        self.float_offset = random.choice([-4, -2, 0, 2, 4])

    @classmethod
    def load_images(cls):
        # load images for the goon
        cls.idle_image = pygame.image.load(cls.idle_image_path).convert_alpha()
        cls.hurt_image = pygame.image.load(cls.hurt_image_path).convert_alpha()
        cls.dead_image = pygame.image.load(cls.dead_image_path).convert_alpha()

    def update_idle_animation(self):
        # move goon up and down when alive and not hurt
        if self.visual_health > 0 and self.hurt_timer == 0:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.float_offset += self.float_direction
                if self.float_offset >= 4:
                    self.float_direction = -2
                elif self.float_offset <= -4:
                    self.float_direction = 2

class BasicGoon(Goon):
    # basic goon info
    name = "Basic Goon"
    description = "A basic enemy goon that deals damage to a bot."
    projectile_offset = (-40, -40)
    min_gears = 1
    max_gears = 5

    # images
    idle_image_path = "assets/goons/basic_goon/basic_goon_idle.png"
    hurt_image_path = "assets/goons/basic_goon/basic_goon_hurt.png"
    dead_image_path = "assets/goons/basic_goon/basic_goon_dead.png"
    idle_image = None
    hurt_image = None
    dead_image = None

    def __init__(self, x, y, slot_id):
        super().__init__(x, y, slot_id)
        # basic goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.damage = 1

    def perform_attack(self, active_effects, target):
        # perform action on target character
        damage, reduction = target.damage_amount(self.damage)
        target.real_health -= damage
        active_effects.append(LinearProjectile((255, 0, 0), self, target, self.projectile_offset, damage, reduction, "Damage"))

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)
        # add action stats to lore text
        lore.append((f"Damage: {self.damage}", "normal"))

class TankyGoon(Goon):
    # tanky goon info
    name = "Tanky Goon"
    description = "A tanky enemy goon that deals damage to a bot and has more health than a basic goon."
    projectile_offset = (-40, -40)
    min_gears = 1
    max_gears = 10

    # images
    idle_image_path = "assets/goons/tanky_goon/tanky_goon_idle.png"
    hurt_image_path = "assets/goons/tanky_goon/tanky_goon_hurt.png"
    dead_image_path = "assets/goons/tanky_goon/tanky_goon_dead.png"
    idle_image = None
    hurt_image = None
    dead_image = None

    def __init__(self, x, y, slot_id):
        super().__init__(x, y, slot_id)
        # basic goon specific info
        self.real_health = 10
        self.visual_health = 10
        self.damage = 1

    def perform_attack(self, active_effects, target):
        # perform action on target character
        damage, reduction = target.damage_amount(self.damage)
        target.real_health -= damage
        active_effects.append(LinearProjectile((255, 0, 0), self, target, self.projectile_offset, damage, reduction, "Damage"))

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)
        # add action stats to lore text
        lore.append((f"Damage: {self.damage}", "normal"))

class PowerfulGoon(Goon):
    # powerful goon info
    name = "Powerful Goon"
    description = "A powerful enemy goon that deals more damage to a bot than a basic goon."
    projectile_offset = (-40, -40)
    min_gears = 1
    max_gears = 10

    # images
    idle_image_path = "assets/goons/powerful_goon/powerful_goon_idle.png"
    hurt_image_path = "assets/goons/powerful_goon/powerful_goon_hurt.png"
    dead_image_path = "assets/goons/powerful_goon/powerful_goon_dead.png"
    idle_image = None
    hurt_image = None
    dead_image = None

    def __init__(self, x, y, slot_id):
        super().__init__(x, y, slot_id)
        # basic goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.damage = 2

    def perform_attack(self, active_effects, target):
        # perform action on target character
        damage, reduction = target.damage_amount(self.damage)
        target.real_health -= damage
        active_effects.append(LinearProjectile((255, 0, 0), self, target, self.projectile_offset, damage, reduction, "Damage"))

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)
        # add action stats to lore text
        lore.append((f"Damage: {self.damage}", "normal"))