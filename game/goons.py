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
    # goon info
    character_type = "Goon"

    # colors
    box_background_color = (255, 75, 75)
    button_color = (255, 150, 150)
    button_hover_color = (255, 200, 200)
    text_used_color = (255, 200, 200)

    # images
    idle_image = None
    hurt_image = None
    dead_image = None

    def __init__(self, x, y):
        super().__init__(x, y)

        # goon specific info
        self.quantumized = False
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
        if self.frozen_rounds == 0:
            char_y += self.float_offset

        # draw quantumized goon image
        if self.quantumized and self.visual_health > 0:

            # change goon color continuously
            current_image = current_image.copy()
            current_image.fill(self.quantum_color, special_flags=pygame.BLEND_RGB_MULT)

            # draw the goon in multiple parts
            if self.quantum_timer > 0:
                width, height = current_image.get_size()

                # draw the top part of the goon
                screen.blit(current_image,  (self.rect.x + self.shake_x, char_y),
                                            (0, 0, width, self.quantum_y))

                # draw the middle part of the goon
                screen.blit(current_image,  (self.rect.x + self.shake_x + self.quantum_offset, char_y + self.quantum_y),
                                            (0, self.quantum_y, width, self.quantum_height))

                # draw the bottom part of the goon
                screen.blit(current_image,  (self.rect.x + self.shake_x, char_y + self.quantum_y + self.quantum_height),
                                            (0, self.quantum_y + self.quantum_height, width, height - self.quantum_y - self.quantum_height))

            # draw goon in one part
            else:
                screen.blit(current_image, (self.rect.x + self.shake_x, char_y))

        # draw regular goon image
        else:
            screen.blit(current_image, (self.rect.x + self.shake_x, char_y))

        super().draw(screen, fonts, text_cache)

        # draw small circle next to name if inspecting goon
        if self == inspecting_character:
            pygame.draw.circle(screen, (255, 0, 0), (self.rect.x - 10, self.rect.y - 33), 5)
        
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

            # draw block barrier if having a barrier
            if self.block > 0:
                pygame.draw.rect(screen, (255, 100, 100), (self.rect.x -10, self.rect.y, 110, 110), 3)
                pygame.draw.rect(screen, (255, 100, 100), (self.rect.x, self.rect.y - 5, 105, 105), 3)
                pygame.draw.rect(screen, (255, 100, 100), (self.rect.x, self.rect.y, 120, 120), 3)

            # draw shield if having a shield
            if self.reduction_shield > 0:
                pygame.draw.circle(screen, (255, 0, 0), (self.rect.centerx, self.rect.centery), 55, 3)

        # draw highlight around goon
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos) and self.real_health > 0 and battle_state in ["Target Enemy", "Target Enemy or Self", "Target Any"]:
            pygame.draw.rect(screen, (255, 0, 0), self.rect, 3)

# ------------------------------
# ENDLESS GOON CLASSES
# ------------------------------

class EndlessGoon(Goon):
    def __init__(self, x, y, slot_id, quantumized):
        super().__init__(x, y)

        # endless goon specific info
        self.slot_id = slot_id
        self.quantumized = quantumized

        # quantumized animation
        self.quantum_hue = random.randint(0, 360)
        self.quantum_color = pygame.Color(0)
        self.quantum_timer = 0
        self.quantum_cooldown = 0
        self.quantum_y = 0
        self.quantum_height = 0
        self.quantum_offset = 0

    def update_idle_animation(self):
        super().update_idle_animation()

        # update quantumized animation
        if self.quantumized and self.visual_health > 0:

            # change goon color continuously
            self.quantum_hue = (self.quantum_hue + 2) % 360
            self.quantum_color.hsva = (self.quantum_hue, 75, 100, 100)

            # randomize the quantumized effect
            if self.quantum_cooldown <= 0:
                self.quantum_cooldown = random.randint(0, 120)
                self.quantum_timer = random.randint(0, 60)
                self.quantum_height = random.randint(10, 50)
                self.quantum_y = random.randint(1, 100 - self.quantum_height - 1)
                self.quantum_offset = random.randint(-40, 40)

            # decrease quantum timer and cooldown
            if self.quantum_timer > 0:
                self.quantum_timer -= 1
            else:
                self.quantum_cooldown -= 1

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add quantumized info to lore text
        if self.quantumized and self.name != "Spiteful Goon":
            lore.append((f"* This goon has been quantumized. When destroyed, it will perform its", "less"))
            lore.append((f"action on every {self.target}. The goon also drops double the gears. *", "normal"))

# ----- Unique Goons -----

class BasicGoon(EndlessGoon):
    # basic goon info
    name = "Basic Goon"
    description = "A basic enemy goon that deals damage to a bot."
    target = "Bot"
    projectile_offset = (-40, -40)

    # images
    idle_image_path = "assets/goons/basic_goon/basic_goon_idle.png"
    hurt_image_path = "assets/goons/basic_goon/basic_goon_hurt.png"
    dead_image_path = "assets/goons/basic_goon/basic_goon_dead.png"

    # sound effects
    attack_sound = pygame.mixer.Sound("assets/goons/basic_goon/basic_goon_sound.mp3")

    def __init__(self, x, y, slot_id, quantumized):
        super().__init__(x, y, slot_id, quantumized)

        # basic goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.gears_reward = random.randint(1, 5)
        self.damage = 1

    def perform_attack(self, active_effects, target):
        # perform action on target character
        damage, reduction = self.damage_calculations(target, self.damage)
        active_effects.append(LinearProjectile((255, 0, 0), self, target, self.projectile_offset, damage, reduction, "Damage"))
        self.attack_sound.play()

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add action stats to lore text
        lore.append((f"Damage: {self.damage}", "normal"))

class TankyGoon(EndlessGoon):
    # tanky goon info
    name = "Tanky Goon"
    description = "A tanky enemy goon that has more health than a basic goon."
    target = "Bot"
    projectile_offset = (-40, -40)

    # images
    idle_image_path = "assets/goons/tanky_goon/tanky_goon_idle.png"
    hurt_image_path = "assets/goons/tanky_goon/tanky_goon_hurt.png"
    dead_image_path = "assets/goons/tanky_goon/tanky_goon_dead.png"

    # sound effects
    attack_sound = pygame.mixer.Sound("assets/goons/tanky_goon/tanky_goon_sound.mp3")

    def __init__(self, x, y, slot_id, quantumized):
        super().__init__(x, y, slot_id, quantumized)

        # tanky goon specific info
        self.real_health = 10
        self.visual_health = 10
        self.gears_reward = random.randint(1, 10)
        self.damage = 1

    def perform_attack(self, active_effects, target):
        # perform action on target character
        damage, reduction = self.damage_calculations(target, self.damage)
        active_effects.append(LinearProjectile((255, 0, 0), self, target, self.projectile_offset, damage, reduction, "Damage"))
        self.attack_sound.play()

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add action stats to lore text
        lore.append((f"Damage: {self.damage}", "normal"))

class BounceGoon(EndlessGoon):
    # bounce goon info
    name = "Bounce Goon"
    description = "This goon shoots a ball that bounces between bots dealing damage."
    target = "Bot"
    projectile_offset = (-29, -33)

    # images
    idle_image_path = "assets/goons/bounce_goon/bounce_goon_idle.png"
    hurt_image_path = "assets/goons/bounce_goon/bounce_goon_hurt.png"
    dead_image_path = "assets/goons/bounce_goon/bounce_goon_dead.png"

    # sound effects
    attack_sound = pygame.mixer.Sound("assets/goons/bounce_goon/bounce_goon_sound.mp3")

    def __init__(self, x, y, slot_id, quantumized):
        super().__init__(x, y, slot_id, quantumized)

        # bounce goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.gears_reward = random.randint(1, 10)
        self.damage = 1
        self.bounce_amount = 2

    def perform_attack(self, active_effects, target):
        # perform action on target character
        damage, reduction = self.damage_calculations(target, self.damage)
        active_effects.append(BounceProjectile((255, 0, 0), self, target, self.projectile_offset, damage, "Goon", reduction, self.damage, self.bounce_amount-1, []))
        self.attack_sound.play()

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add action stats to lore text
        lore.append((f"Bounces: {self.bounce_amount}", "normal"))
        lore.append((f"Damage: {self.damage}", "normal"))

class SpitefulGoon(EndlessGoon):
    # spiteful goon info
    name = "Spiteful Goon"
    description = "A spiteful goon this goon is. It will attack whoever attacked it last."
    target = "Bot"
    projectile_offset = (-33, -32)

    # images
    idle_image_path = "assets/goons/spiteful_goon/spiteful_goon_idle.png"
    hurt_image_path = "assets/goons/spiteful_goon/spiteful_goon_hurt.png"
    dead_image_path = "assets/goons/spiteful_goon/spiteful_goon_dead.png"

    # sound effects
    attack_sound = pygame.mixer.Sound("assets/goons/spiteful_goon/spiteful_goon_sound.mp3")

    def __init__(self, x, y, slot_id, quantumized):
        super().__init__(x, y, slot_id, quantumized)

        # spiteful goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.gears_reward = random.randint(1, 10)
        self.damage = 2
        self.last_attacker = None

    def perform_attack(self, active_effects, target):
        # perform action on target character
        if self.last_attacker and self.last_attacker.real_health > 0:
            target = self.last_attacker
        if self.quantumized and self.visual_health == 0:
            self.damage *= 2 
        damage, reduction = self.damage_calculations(target, self.damage)
        active_effects.append(LinearProjectile((255, 0, 0), self, target, self.projectile_offset, damage, reduction, "Spiteful Damage"))
        self.attack_sound.play()

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add alternate quantumized info to lore text
        if self.quantumized:
            lore.append((f"* This goon has been quantumized. When destroyed, it will perform its", "less"))
            lore.append((f"action on its last attacker with double damage. The goon also drops", "less"))
            lore.append((f"double the gears. *", "normal"))

        # add action stats to lore text
        lore.append((f"Damage: {self.damage}", "normal"))
        if self.last_attacker:
            lore.append((f"Last Attacker: {self.last_attacker.name}", "normal"))

# ----- Damage Goons -----

class PowerfulGoon(EndlessGoon):
    # powerful goon info
    name = "Powerful Goon"
    description = "A powerful enemy goon that attacks a bot while increasing its damage every round."
    target = "Bot"
    projectile_offset = (-40, -40)

    # images
    idle_image_path = "assets/goons/powerful_goon/powerful_goon_idle.png"
    hurt_image_path = "assets/goons/powerful_goon/powerful_goon_hurt.png"
    dead_image_path = "assets/goons/powerful_goon/powerful_goon_dead.png"

    # sound effects
    attack_sound = pygame.mixer.Sound("assets/goons/powerful_goon/powerful_goon_sound.mp3")

    def __init__(self, x, y, slot_id, quantumized):
        super().__init__(x, y, slot_id, quantumized)

        # powerful goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.gears_reward = random.randint(1, 10)
        self.damage = 1

    def perform_attack(self, active_effects, target):
        # perform action on target character
        damage, reduction = self.damage_calculations(target, self.damage)
        active_effects.append(LinearProjectile((255, 0, 0), self, target, self.projectile_offset, damage, reduction, "Damage"))
        self.attack_sound.play()

        # increase damage by 1 every round
        if self.visual_health > 0:
            self.damage += 1
            text = "+1 Damage"
            text_width = len(text) * 10
            text_x = random.randint(self.rect.left, self.rect.right - text_width)
            active_effects.append(FloatingText((255, 0, 0), text_x, self.rect.top + 10, text))

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add action stats to lore text
        lore.append((f"Damage: {self.damage}", "normal"))

class PercentageGoon(EndlessGoon):
    # percentage goon info
    name = "Percentage Goon"
    description = "A goon that deals damage to a bot based on its current health. The amount of damage is rounded down with a minimum of 1 damage."
    target = "Bot"
    projectile_offset = (-24, -36)

    # images
    idle_image_path = "assets/goons/percentage_goon/percentage_goon_idle.png"
    hurt_image_path = "assets/goons/percentage_goon/percentage_goon_hurt.png"
    dead_image_path = "assets/goons/percentage_goon/percentage_goon_dead.png"

    # sound effects
    attack_sound = pygame.mixer.Sound("assets/goons/percentage_goon/percentage_goon_sound.mp3")

    def __init__(self, x, y, slot_id, quantumized):
        super().__init__(x, y, slot_id, quantumized)

        # percentage goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.gears_reward = random.randint(1, 10)
        self.damage = 25

    def perform_attack(self, active_effects, target):
        # perform action on target character
        damage, reduction = self.damage_calculations(target, max(1, int(target.real_health * (self.damage / 100))))
        active_effects.append(PercentageProjectile((255, 0, 0), self, target, self.projectile_offset, damage, reduction, "Damage"))
        self.attack_sound.play()

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add action stats to lore text
        lore.append((f"Damage: {self.damage}%", "normal"))

class RandomGoon(EndlessGoon):
    # random goon info
    name = "Random Goon"
    description = "A goon that deals random amounts of damage to a bot."
    target = "Bot"
    projectile_offset = (-40, -45)

    # images
    idle_image_path = "assets/goons/random_goon/random_goon_idle.png"
    hurt_image_path = "assets/goons/random_goon/random_goon_hurt.png"
    dead_image_path = "assets/goons/random_goon/random_goon_dead.png"

    # sound effects
    attack_sound = pygame.mixer.Sound("assets/goons/random_goon/random_goon_sound.mp3")

    def __init__(self, x, y, slot_id, quantumized):
        super().__init__(x, y, slot_id, quantumized)

        # random goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.gears_reward = random.randint(1, 10)
        self.damage = 3

    def perform_attack(self, active_effects, target):
        # perform action on target character
        chosen_damage = random.randint(self.damage - 2, self.damage + 2)
        damage, reduction = self.damage_calculations(target, chosen_damage)
        active_effects.append(GlitchyDamageProjectile((255, 0, 0), self, target, self.projectile_offset, damage, reduction))
        self.attack_sound.play()

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add action stats to lore text
        lore.append((f"Min Damage: {self.damage - 2}", "normal"))
        lore.append((f"Max Damage: {self.damage + 2}", "normal"))

class ChargeGoon(EndlessGoon):
    # charge goon info
    name = "Charge Goon"
    description = "A goon that either charges, which doubles its damage, or attacks, which damages a bot."
    target = "Bot"
    projectile_offset = (3, 10)

    # images
    idle_image_path = "assets/goons/charge_goon/charge_goon_idle.png"
    hurt_image_path = "assets/goons/charge_goon/charge_goon_hurt.png"
    dead_image_path = "assets/goons/charge_goon/charge_goon_dead.png"

    # sound effects
    attack_sound = pygame.mixer.Sound("assets/goons/charge_goon/charge_goon_attack_sound.mp3")
    charge_sound = pygame.mixer.Sound("assets/goons/charge_goon/charge_goon_charge_sound.mp3")

    def __init__(self, x, y, slot_id, quantumized):
        super().__init__(x, y, slot_id, quantumized)

        # charge goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.gears_reward = random.randint(1, 10)
        self.damage = 1
        self.projectile_radius = 2

    def perform_attack(self, active_effects, target):
        # perform action on target character
        choice = random.choices(["charge", "attack"], weights=[60, 40])[0]

        # if goon chooses to charge, double its damage
        if choice == "charge" and self.visual_health > 0:
            self.damage *= 2
            self.projectile_radius += 2
            text = "Charged!"
            text_width = len(text) * 10
            text_x = random.randint(self.rect.left, self.rect.right - text_width)
            active_effects.append(FloatingText((255, 0, 0), text_x, self.rect.top + 10, text))
            self.charge_sound.play()

        # if goon chooses to attack, damage a bot
        else:
            damage, reduction = self.damage_calculations(target, self.damage)
            active_effects.append(ChargeProjectile((255, 0, 0), self, target, self.projectile_offset, damage, reduction, "Damage", self.projectile_radius))
            self.attack_sound.play()
            if self.visual_health > 0:
                self.damage = 1
                self.projectile_radius = 2

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add action stats to lore text
        lore.append((f"Damage: {self.damage}", "normal"))

# ----- Effect Goons -----

class FireGoon(EndlessGoon):
    # fire goon info
    name = "Fire Goon"
    description = "This goon sets a bot on fire. Fire damage ignores effects."
    target = "Bot"
    projectile_offset = (-5, -30)

    # images
    idle_image_path = "assets/goons/fire_goon/fire_goon_idle.png"
    hurt_image_path = "assets/goons/fire_goon/fire_goon_hurt.png"
    dead_image_path = "assets/goons/fire_goon/fire_goon_dead.png"

    # sound effects
    attack_sound = pygame.mixer.Sound("assets/goons/fire_goon/fire_goon_sound.mp3")

    def __init__(self, x, y, slot_id, quantumized):
        super().__init__(x, y, slot_id, quantumized)

        # fire goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.gears_reward = random.randint(1, 10)
        self.fire_rounds_amount = 3

    def perform_attack(self, active_effects, target):
        # perform action on target character
        active_effects.append(LinearProjectile((255, 0, 0), self, target, self.projectile_offset, self.fire_rounds_amount, 0, "Fire"))
        self.attack_sound.play()

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add action stats to lore text
        lore.append((f"Fire Rounds: {self.fire_rounds_amount}", "normal"))

class IceGoon(EndlessGoon):
    # ice goon info
    name = "Ice Goon"
    description = "A goon that fires an ice projectile at a bot. After the bot has been hit multiple times, it will be frozen and cannot attack for a round."
    target = "Bot"
    projectile_offset = (-3, -33)

    # images
    idle_image_path = "assets/goons/ice_goon/ice_goon_idle.png"
    hurt_image_path = "assets/goons/ice_goon/ice_goon_hurt.png"
    dead_image_path = "assets/goons/ice_goon/ice_goon_dead.png"

    # sound effects
    attack_sound = pygame.mixer.Sound("assets/goons/ice_goon/ice_goon_sound.mp3")

    def __init__(self, x, y, slot_id, quantumized):
        super().__init__(x, y, slot_id, quantumized)

        # ice goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.gears_reward = random.randint(1, 10)

    def perform_attack(self, active_effects, target):
        # perform action on target character
        active_effects.append(LinearProjectile((255, 0, 0), self, target, self.projectile_offset, 2, 0, "Ice"))
        self.attack_sound.play()

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add action stats to lore text
        lore.append(("Ice Hits Needed: 2", "normal"))

class MarkGoon(EndlessGoon):
    # mark goon info
    name = "Mark Goon"
    description = "This goon marks a bot. A marked bot takes double damage from all sources for a round."
    target = "Bot"
    projectile_offset = (-25, -24)

    # images
    idle_image_path = "assets/goons/mark_goon/mark_goon_idle.png"
    hurt_image_path = "assets/goons/mark_goon/mark_goon_hurt.png"
    dead_image_path = "assets/goons/mark_goon/mark_goon_dead.png"

    # sound effects
    attack_sound = pygame.mixer.Sound("assets/goons/mark_goon/mark_goon_sound.mp3")

    def __init__(self, x, y, slot_id, quantumized):
        super().__init__(x, y, slot_id, quantumized)

        # mark goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.gears_reward = random.randint(1, 10)

    def perform_attack(self, active_effects, target):
        # perform action on target character
        active_effects.append(MarkProjectile((255, 0, 0), self, target, self.projectile_offset, 1, 0, "Mark"))
        self.attack_sound.play()

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add action stats to lore text
        lore.append(("Mark Hits Needed: 1", "normal"))

class NerfGoon(EndlessGoon):
    # nerf goon info
    name = "Nerf Goon"
    description = "A goon like this nerfs a bot's damage for a round. The damage nerf can't nerf the damage below 1."
    target = "Bot"
    projectile_offset = (-30, -15)

    # images
    idle_image_path = "assets/goons/nerf_goon/nerf_goon_idle.png"
    hurt_image_path = "assets/goons/nerf_goon/nerf_goon_hurt.png"
    dead_image_path = "assets/goons/nerf_goon/nerf_goon_dead.png"

    # sound effects
    attack_sound = pygame.mixer.Sound("assets/goons/nerf_goon/nerf_goon_sound.mp3")

    def __init__(self, x, y, slot_id, quantumized):
        super().__init__(x, y, slot_id, quantumized)

        # nerf goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.gears_reward = random.randint(1, 10)
        self.nerf_amount = 1

    def perform_attack(self, active_effects, target):
        # perform action on target character
        active_effects.append(LinearProjectile((255, 0, 0), self, target, self.projectile_offset, self.nerf_amount, 0, "Nerf"))
        self.attack_sound.play()

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add action stats to lore text
        lore.append((f"Nerf: -{self.nerf_amount} Damage", "normal"))

# ----- Support Goons -----

class ReductionGoon(EndlessGoon):
    # reduction goon info
    name = "Reduction Goon"
    description = "This goon gives a fellow goon a damage reduction shield."
    target = "Goon"
    projectile_offset = (-34, 0)

    # images
    idle_image_path = "assets/goons/reduction_goon/reduction_goon_idle.png"
    hurt_image_path = "assets/goons/reduction_goon/reduction_goon_hurt.png"
    dead_image_path = "assets/goons/reduction_goon/reduction_goon_dead.png"

    # sound effects
    attack_sound = pygame.mixer.Sound("assets/goons/reduction_goon/reduction_goon_sound.mp3")

    def __init__(self, x, y, slot_id, quantumized):
        super().__init__(x, y, slot_id, quantumized)

        # reduction goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.gears_reward = random.randint(1, 10)
        self.reduction_shield_amount = 0.5

    def perform_attack(self, active_effects, target):
        # perform action on target character
        active_effects.append(ShieldProjectile((255, 0, 0), self, target, self.projectile_offset, self.reduction_shield_amount))
        self.attack_sound.play()

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add action stats to lore text
        lore.append((f"Damage Reduction: {round((1-self.reduction_shield_amount) * 100)}%", "normal"))

class BlockGoon(EndlessGoon):
    # block goon info
    name = "Block Goon"
    description = "This goon gives a fellow goon a block barrier."
    target = "Goon"
    projectile_offset = (-36, -16)

    # images
    idle_image_path = "assets/goons/block_goon/block_goon_idle.png"
    hurt_image_path = "assets/goons/block_goon/block_goon_hurt.png"
    dead_image_path = "assets/goons/block_goon/block_goon_dead.png"

    # sound effects
    attack_sound = pygame.mixer.Sound("assets/goons/block_goon/block_goon_sound.mp3")

    def __init__(self, x, y, slot_id, quantumized):
        super().__init__(x, y, slot_id, quantumized)

        # block goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.gears_reward = random.randint(1, 10)
        self.block_amount = 50

    def perform_attack(self, active_effects, target):
        # perform action on target character
        active_effects.append(GlitchyBlockProjectile((255, 0, 0), self, target, self.projectile_offset, self.block_amount))
        self.attack_sound.play()

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add action stats to lore text
        lore.append((f"Block Chance: {self.block_amount}%", "normal"))

class HealingGoon(EndlessGoon):
    # healing goon info
    name = "Healing Goon"
    description = "A healing goon that heals a fellow goon."
    target = "Goon"
    projectile_offset = (0, 0)

    # images
    idle_image_path = "assets/goons/healing_goon/healing_goon_idle.png"
    hurt_image_path = "assets/goons/healing_goon/healing_goon_hurt.png"
    dead_image_path = "assets/goons/healing_goon/healing_goon_dead.png"

    # sound effects
    attack_sound = pygame.mixer.Sound("assets/goons/healing_goon/healing_goon_sound.mp3")

    def __init__(self, x, y, slot_id, quantumized):
        super().__init__(x, y, slot_id, quantumized)

        # healing goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.gears_reward = random.randint(1, 10)
        self.heal = 1

    def perform_attack(self, active_effects, target):
        # perform action on target character
        target.real_health += self.heal
        active_effects.append(HealProjectile((255, 0, 0), self, target, self.projectile_offset, self.heal, "Goon"))
        self.attack_sound.play()

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add action stats to lore text
        lore.append((f"Heal: {self.heal}", "normal"))

class HealtonGoon(EndlessGoon):
    # healton goon info
    name = "Healton Goon"
    description = "A goon that heals random amounts to a fellow goon."
    target = "Goon"
    projectile_offset = (-5, -40)

    # images
    idle_image_path = "assets/goons/healton_goon/healton_goon_idle.png"
    hurt_image_path = "assets/goons/healton_goon/healton_goon_hurt.png"
    dead_image_path = "assets/goons/healton_goon/healton_goon_dead.png"

    # sound effects
    attack_sound = pygame.mixer.Sound("assets/goons/healton_goon/healton_goon_sound.mp3")

    def __init__(self, x, y, slot_id, quantumized):
        super().__init__(x, y, slot_id, quantumized)

        # healton goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.gears_reward = random.randint(1, 10)
        self.heal_amount = 3

    def perform_attack(self, active_effects, target):
        # perform action on target character
        chosen_heal = random.randint(self.heal_amount - 2, self.heal_amount + 2)
        target.real_health += chosen_heal
        active_effects.append(GlitchyHealProjectile((255, 0, 0), self, target, self.projectile_offset, chosen_heal))
        self.attack_sound.play()

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add action stats to lore text
        lore.append((f"Min Heal: {self.heal_amount - 2}", "normal"))
        lore.append((f"Max Heal: {self.heal_amount + 2}", "normal"))

# ------------------------------
# STORY GOON CLASSES
# ------------------------------

class DummyGoon(Goon):
    # dummy goon info
    name = "Dummy Goon"
    description = "A dummy robot that is used for testing purposes."
    target = "Bot"
    projectile_offset = (-40, -40)

    # images
    idle_image_path = "assets/goons/dummy_goon/dummy_goon_idle.png"
    hurt_image_path = "assets/goons/dummy_goon/dummy_goon_hurt.png"
    dead_image_path = "assets/goons/dummy_goon/dummy_goon_dead.png"

    # sound effects
    attack_sound = pygame.mixer.Sound("assets/goons/dummy_goon/dummy_goon_sound.mp3")

    def __init__(self, x, y):
        super().__init__(x, y)

        # dummy goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.gears_reward = 5
        self.damage = 1

    def perform_attack(self, active_effects, target):
        # perform action on target character
        damage, reduction = self.damage_calculations(target, self.damage)
        active_effects.append(LinearProjectile((255, 0, 0), self, target, self.projectile_offset, damage, reduction, "Damage"))
        self.attack_sound.play()

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

    # images
    idle_image_path = "assets/goons/patrolling_goon/patrolling_goon_idle.png"
    hurt_image_path = "assets/goons/patrolling_goon/patrolling_goon_hurt.png"
    dead_image_path = "assets/goons/patrolling_goon/patrolling_goon_dead.png"
    mini_image_path = "assets/goons/patrolling_goon/patrolling_goon_idle.png"
    mini_image = None

    # sound effects
    attack_sound = pygame.mixer.Sound("assets/goons/patrolling_goon/patrolling_goon_sound.mp3")

    def __init__(self, x, y):
        super().__init__(x, y)

        # patrolling goon specific info
        self.real_health = 5
        self.visual_health = 5
        self.gears_reward = random.randint(1, 5)
        self.damage = 1

    @classmethod
    def load_images(cls):
        super().load_images()

        # load goon mini image
        cls.mini_image = pygame.image.load(cls.mini_image_path).convert_alpha()
        cls.mini_image = pygame.transform.scale_by(cls.mini_image, 0.5)

    def perform_attack(self, active_effects, target):
        # perform action on target character
        damage, reduction = self.damage_calculations(target, self.damage)
        active_effects.append(PatrolProjectile((255, 0, 0), self, target, self.projectile_offset, damage, reduction, "Damage"))
        self.attack_sound.play()

    def lore_text(self, fonts, lore):
        super().lore_text(fonts, lore)

        # add action stats to lore text
        lore.append((f"Damage: {self.damage}", "normal"))
