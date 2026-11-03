# goons.py

# import libraries
import pygame
import random

# import game modules
from .characters import Character
from .effects import (
    FloatingText,
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
    PatrolProjectile
)

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

    def draw(self, screen, fonts, text_cache, battle_state, inspecting_character, elemental_bot):
        # dead image
        if self.visual_health <= 0:
            current_image = self.dead_image

        # hurt image
        elif self.hurt_timer > 0:
            current_image = self.hurt_image

        # idle image        
        else:
            current_image = self.idle_image

        # move up and down
        char_y = self.rect.y
        if not self.frozen:
            char_y += self.float_offset

        # draw goon image
        screen.blit(current_image, (self.rect.x + self.shake_x, char_y))

        super().draw(screen, fonts, text_cache)

        # draw small circle next to name if inspecting goon
        if self == inspecting_character:
            pygame.draw.circle(screen, (255, 0, 0), (self.rect.x - 10, self.rect.y - 33), 5)

        # draw highlight around goon
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos) and self.real_health > 0 and battle_state in ["Target Enemy", "Target Enemy or Self", "Target Any"]:
            pygame.draw.rect(screen, (255, 0, 0), self.rect, 3)
        
        # draw character status effects
        if self.visual_health > 0:

            # draw boxes for number of ice hits and how many needed
            if self.ice_hits > 0:
                for i in range(elemental_bot.actions[1]["ice_hits_needed"]):
                    if elemental_bot.actions[1]["ice_hits_needed"] == 3:
                        box_x_offset = 28
                    elif elemental_bot.actions[1]["ice_hits_needed"] == 2:
                        box_x_offset = 19
                    box_rect = pygame.Rect(self.rect.right - box_x_offset + (i * 9), self.rect.y - 11, 10, 10)
                    if i < self.ice_hits:
                        pygame.draw.rect(screen, (0, 255, 255), box_rect)
                    else:
                        pygame.draw.rect(screen, (0, 255, 255), box_rect, 1)
            
            # draw boxes for number of mark hits and how many needed
            if self.mark_hits > 0:
                for i in range(2):
                    box_rect = pygame.Rect(self.rect.right - 19 + (i * 9), self.rect.y - 21, 10, 10)
                    if i < self.mark_hits:
                        pygame.draw.rect(screen, (255, 255, 0), box_rect)
                    else:
                        pygame.draw.rect(screen, (255, 255, 0), box_rect, 1)

# ------------------------------
# ENDLESS GOON CLASSES
# ------------------------------

class BasicGoon(Goon):
    # basic goon info
    name = "Basic Goon"
    description = "A basic enemy goon that deals damage to a bot."
    target = "Bot"
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
    description = "A tanky enemy goon that has more health than a basic goon."
    target = "Bot"
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

        # tanky goon specific info
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
    target = "Bot"
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

        # powerful goon specific info
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

class HealingGoon(Goon):
    # healing goon info
    name = "Healing Goon"
    description = "A healing goon that heals a fellow goon."
    target = "Goon"
    projectile_offset = (0, 0)
    min_gears = 1
    max_gears = 10

    # images
    idle_image_path = "assets/goons/healing_goon/healing_goon_idle.png"
    hurt_image_path = "assets/goons/healing_goon/healing_goon_hurt.png"
    dead_image_path = "assets/goons/healing_goon/healing_goon_dead.png"
    idle_image = None
    hurt_image = None
    dead_image = None

    def __init__(self, x, y, slot_id):
        super().__init__(x, y, slot_id)

        # healing goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.heal = 1

    def perform_attack(self, active_effects, target):
        # perform action on target character
        target.real_health += self.heal
        active_effects.append(HealProjectile((255, 0, 0), self, target, self.projectile_offset, self.heal, "Goon"))

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add action stats to lore text
        lore.append((f"Heal: {self.heal}", "normal"))

class BounceGoon(Goon):
    # bounce goon info
    name = "Bounce Goon"
    description = "This goon shoots a ball that bounces between bots dealing damage."
    target = "Bot"
    projectile_offset = (-29, -33)
    min_gears = 1
    max_gears = 10

    # images
    idle_image_path = "assets/goons/bounce_goon/bounce_goon_idle.png"
    hurt_image_path = "assets/goons/bounce_goon/bounce_goon_hurt.png"
    dead_image_path = "assets/goons/bounce_goon/bounce_goon_dead.png"
    idle_image = None
    hurt_image = None
    dead_image = None

    def __init__(self, x, y, slot_id):
        super().__init__(x, y, slot_id)

        # bounce goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.damage = 1
        self.bounce_amount = 2

    def perform_attack(self, active_effects, target):
        # perform action on target character
        damage, reduction = target.damage_amount(self.damage)
        target.real_health -= damage
        active_effects.append(BounceProjectile((255, 0, 0), self, target, self.projectile_offset, damage, "Goon", reduction, self.damage, self.bounce_amount-1, []))

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add action stats to lore text
        lore.append((f"Bounces: {self.bounce_amount}", "normal"))
        lore.append((f"Damage: {self.damage}", "normal"))

class FireGoon(Goon):
    # fire goon info
    name = "Fire Goon"
    description = "This goon sets a bot on fire."
    target = "Bot"
    projectile_offset = (-5, -30)
    min_gears = 1
    max_gears = 10

    # images
    idle_image_path = "assets/goons/fire_goon/fire_goon_idle.png"
    hurt_image_path = "assets/goons/fire_goon/fire_goon_hurt.png"
    dead_image_path = "assets/goons/fire_goon/fire_goon_dead.png"
    idle_image = None
    hurt_image = None
    dead_image = None

    def __init__(self, x, y, slot_id):
        super().__init__(x, y, slot_id)

        # fire goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.fire_rounds_amount = 3

    def perform_attack(self, active_effects, target):
        # perform action on target character
        active_effects.append(LinearProjectile((255, 0, 0), self, target, self.projectile_offset, self.fire_rounds_amount, 0, "Fire"))

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add action stats to lore text
        lore.append((f"Fire Rounds: {self.fire_rounds_amount}", "normal"))

class RandomGoon(Goon):
    # random goon info
    name = "Random Goon"
    description = "A goon that deals random amounts of damage to a bot."
    target = "Bot"
    projectile_offset = (-40, -45)
    min_gears = 1
    max_gears = 10

    # images
    idle_image_path = "assets/goons/random_goon/random_goon_idle.png"
    hurt_image_path = "assets/goons/random_goon/random_goon_hurt.png"
    dead_image_path = "assets/goons/random_goon/random_goon_dead.png"
    idle_image = None
    hurt_image = None
    dead_image = None

    def __init__(self, x, y, slot_id):
        super().__init__(x, y, slot_id)

        # random goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.damage = 3

    def perform_attack(self, active_effects, target):
        # perform action on target character
        chosen_damage = random.randint(self.damage - 2, self.damage + 2)
        damage, reduction = target.damage_amount(chosen_damage)
        target.real_health -= damage
        active_effects.append(GlitchyDamageProjectile((255, 0, 0), self, target, self.projectile_offset, damage, reduction))

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add action stats to lore text
        lore.append((f"Min Damage: {self.damage - 2}", "normal"))
        lore.append((f"Max Damage: {self.damage + 2}", "normal"))

class ChargeGoon(Goon):
    # charge goon info
    name = "Charge Goon"
    description = "A goon that either charges, which doubles its damage, or attacks, which damages a bot."
    target = "Bot"
    projectile_offset = (3, 10)
    min_gears = 1
    max_gears = 10

    # images
    idle_image_path = "assets/goons/charge_goon/charge_goon_idle.png"
    hurt_image_path = "assets/goons/charge_goon/charge_goon_hurt.png"
    dead_image_path = "assets/goons/charge_goon/charge_goon_dead.png"
    idle_image = None
    hurt_image = None
    dead_image = None

    def __init__(self, x, y, slot_id):
        super().__init__(x, y, slot_id)

        # charge goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.damage = 1
        self.projectile_radius = 2

    def perform_attack(self, active_effects, target):
        # perform action on target character
        choice = random.choices(["charge", "attack"], weights=[60, 40])[0]

        # if goon chooses to charge, double its damage
        if choice == "charge":
            self.damage *= 2
            self.projectile_radius += 2
            text = "Charged!"
            text_width = len(text) * 10
            text_x = random.randint(self.rect.left, self.rect.right - text_width)
            active_effects.append(FloatingText((255, 0, 0), text_x, self.rect.top + 10, text))

        # if goon chooses to attack, damage a bot
        else:
            damage, reduction = target.damage_amount(self.damage)
            target.real_health -= damage
            active_effects.append(ChargeProjectile((255, 0, 0), self, target, self.projectile_offset, damage, reduction, "Damage", self.projectile_radius))
            self.damage = 1
            self.projectile_radius = 2

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add action stats to lore text
        lore.append((f"Damage: {self.damage}", "normal"))

# ------------------------------
# STORY GOON CLASSES
# ------------------------------

class DummyGoon(Goon):
    # dummy goon info
    name = "Dummy Goon"
    description = "A dummy robot that is used for testing purposes."
    target = "Bot"
    projectile_offset = (-40, -40)
    min_gears = 5
    max_gears = 5

    # images
    idle_image_path = "assets/goons/dummy_goon/dummy_goon_idle.png"
    hurt_image_path = "assets/goons/dummy_goon/dummy_goon_hurt.png"
    dead_image_path = "assets/goons/dummy_goon/dummy_goon_dead.png"
    idle_image = None
    hurt_image = None
    dead_image = None

    def __init__(self, x, y, slot_id):
        super().__init__(x, y, slot_id)

        # dummy goon specific info
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

class PatrollingGoon(Goon):
    # patrolling goon info
    name = "Patrolling Goon"
    description = "A patrolling robot that patrols the streets. It deals damage to a bot it finds."
    target = "Bot"
    projectile_offset = (-16, -25)
    min_gears = 1
    max_gears = 5

    # images
    idle_image_path = "assets/goons/patrolling_goon/patrolling_goon_idle.png"
    hurt_image_path = "assets/goons/patrolling_goon/patrolling_goon_hurt.png"
    dead_image_path = "assets/goons/patrolling_goon/patrolling_goon_dead.png"
    mini_image_path = "assets/goons/patrolling_goon/patrolling_goon_idle.png"
    idle_image = None
    hurt_image = None
    dead_image = None
    mini_image = None

    def __init__(self, x, y, slot_id):
        super().__init__(x, y, slot_id)

        # patrolling goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.damage = 1

    @classmethod
    def load_images(cls):
        super().load_images()

        # load goon mini image
        cls.mini_image = pygame.image.load(cls.mini_image_path).convert_alpha()
        cls.mini_image = pygame.transform.scale_by(cls.mini_image, 0.5)

    def perform_attack(self, active_effects, target):
        # perform action on target character
        damage, reduction = target.damage_amount(self.damage)
        target.real_health -= damage
        active_effects.append(PatrolProjectile((255, 0, 0), self, target, self.projectile_offset, damage, reduction, "Damage"))

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add action stats to lore text
        lore.append((f"Damage: {self.damage}", "normal"))
