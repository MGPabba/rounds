import asyncio
import pygame
import math
import random

# initialize pygame and font module
pygame.init()
pygame.font.init()


# ------------------------------
# ANIMATIONS
# ------------------------------

class FloatingText:
    def __init__(self, color, x, y, text):
        # floating text info
        self.color = color
        self.x = x
        self.y = y
        self.text = text
        self.timer = 120
        self.active = True
    
    def update(self):
        # move text up and decrease timer, disappear when timer runs out
        self.y -= 1
        self.timer -= 1
        if self.timer <= 0:
            self.active = False

class Projectile:
    def __init__(self, color, source_char, target_char, projectile_offset, amount):
        # basic projectile info
        self.color = color
        self.source_char = source_char
        self.target_char = target_char
        self.projectile_offset = projectile_offset
        self.amount = amount
        self.active = True

        # calculate all of the projectile's movement info
        self.source_x = source_char.rect.centerx + projectile_offset[0]
        self.source_y = source_char.rect.centery + projectile_offset[1]
        self.target_x = target_char.rect.centerx
        self.target_y = target_char.rect.centery
        self.x = self.source_x
        self.y = self.source_y
        self.distance_x = self.target_x - self.source_x
        self.distance_y = self.target_y - self.source_y

class LinearProjectile(Projectile):
    def __init__(self, color, source_char, target_char, projectile_offset, amount, projectile_type):
        super().__init__(color, source_char, target_char, projectile_offset, amount)
        # linear projectile specific info
        self.projectile_type = projectile_type
        self.speed = 10
        self.distance = math.sqrt(self.distance_x ** 2 + self.distance_y ** 2)
        self.speed_x = self.distance_x / self.distance * self.speed
        self.speed_y = self.distance_y / self.distance * self.speed
    
    def update(self, active_effects):
        # move projectile towards target
        self.x += self.speed_x
        self.y += self.speed_y

        # damage or apply effect when projectile reaches
        if (self.speed_x > 0 and self.x >= self.target_x) or (self.speed_x < 0 and self.x <= self.target_x):
            self.active = False
            if self.projectile_type == "Damage":
                self.target_char.take_damage(active_effects, self.amount)
            elif self.projectile_type == "Fire":
                self.target_char.apply_fire(active_effects, self.amount)
            elif self.projectile_type == "Ice":
                self.target_char.apply_ice(active_effects, self.amount)
            elif self.projectile_type == "Mark":
                self.target_char.apply_mark(active_effects, self.amount)

class ChargeProjectile(LinearProjectile):
    def __init__(self, color, source_char, target_char, projectile_offset, amount, projectile_type, max_radius):
        super().__init__(color, source_char, target_char, projectile_offset, amount, projectile_type)
        # charge projectile specific info
        self.max_radius = max_radius
        self.current_radius = 0
        self.border = 1
        self.border_phase = "Grow"
    
    def update(self, active_effects):
        # projectile grows based on amount of charge
        if self.current_radius < self.max_radius:
            self.current_radius += 1
        else:
            super().update(active_effects)
            # border grows and shrinks as projectile moves towards target
            if self.border_phase == "Grow":
                self.border += 1
                if self.border >= self.max_radius:
                    self.border_phase = "Shrink"
            elif self.border_phase == "Shrink":
                self.border -= 1
                if self.border <= 0:
                    self.border_phase = "Grow"

class MarkProjectile(LinearProjectile):
    def __init__(self, color, source_char, target_char, projectile_offset, amount, projectile_type):
        super().__init__(color, source_char, target_char, projectile_offset, amount, projectile_type)
        # mark projectile specific info
        self.angle = 0
        self.rotation_speed = 0.5
    
    def update(self, active_effects):
        super().update(active_effects)
        # rotate projectile as it moves towards target
        self.angle -= self.rotation_speed

class PercentageProjectile(LinearProjectile):
    def __init__(self, color, source_char, target_char, projectile_offset, amount, projectile_type):
        super().__init__(color, source_char, target_char, projectile_offset, amount, projectile_type)
        # percentage projectile specific info
        self.line_one_angle = 0
        self.line_two_angle = 0
        self.rotation_speed = 0.2
    
    def update(self, active_effects):
        super().update(active_effects)

        # rotate one line clockwise as it moves towards target
        self.line_one_angle += self.rotation_speed
        self.line_one_x1 = self.x + math.cos(self.line_one_angle) * 10
        self.line_one_y1 = self.y + math.sin(self.line_one_angle) * 10
        self.line_one_x2 = self.x - math.cos(self.line_one_angle) * 5
        self.line_one_y2 = self.y - math.sin(self.line_one_angle) * 5

        # rotate the other line counterclockwise as it moves towards target
        self.line_two_angle -= self.rotation_speed
        self.line_two_x1 = self.x + math.cos(self.line_two_angle) * 10
        self.line_two_y1 = self.y + math.sin(self.line_two_angle) * 5
        self.line_two_x2 = self.x - math.cos(self.line_two_angle) * 10
        self.line_two_y2 = self.y - math.sin(self.line_two_angle) * 5

class ShieldProjectile(Projectile):
    def __init__(self, color, source_char, target_char, projectile_offset, amount):
        super().__init__(color, source_char, target_char, projectile_offset, amount)
        # shield projectile specific info
        self.progress = 0
        self.control_x = 800
        self.control_y1 = self.source_y + (self.target_y - self.source_y) * 0.1
        self.control_y2 = self.source_y + (self.target_y - self.source_y) * 0.9

    def update(self):
        # increase progress of projectile movement
        self.progress += 0.015

        # calculate projectile position using quadratic and cubic Bezier curve
        self.x = ((1 - self.progress) ** 2 * self.source_x
                  + 2 * (1 - self.progress) * self.progress * self.control_x
                  + self.progress ** 2 * self.target_x)
        self.y = ((1 - self.progress) ** 3 * self.source_y
                  + 3 * (1 - self.progress) ** 2 * self.progress * self.control_y1
                  + 3 * (1 - self.progress) * self.progress ** 2 * self.control_y2
                  + self.progress ** 3 * self.target_y)

        # apply shield when projectile reaches target
        if self.progress >= 1:
            self.active = False
            self.target_char.shield = self.amount

class ArcProjectile(Projectile):
    def __init__(self, color, source_char, target_char, projectile_offset, amount):
        super().__init__(color, source_char, target_char, projectile_offset, amount)
        # arc projectile specific info
        self.frames = 80
        self.current_frame = 0
        self.arc = 150
    
    def update(self):
        # move projectile in an arc towards target
        self.current_frame += 1
        self.progress = self.current_frame / self.frames
        self.base_x = self.source_x + self.distance_x * self.progress
        self.base_y = self.source_y + self.distance_y * self.progress
        self.curve_y = math.sin(self.progress * math.pi) * self.arc

class HealProjectile(ArcProjectile):
    def __init__(self, color, source_char, target_char, projectile_offset, amount):
        super().__init__(color, source_char, target_char, projectile_offset, amount)

    def update(self, active_effects):
        # move projectile in an arc towards target
        super().update()
        if self.target_char.name == "Rico Bot":
            max_x = math.sin(self.progress * math.pi) * (self.arc*0.5)
            curve_x = math.sin((self.progress**2) * math.pi) * (self.arc*0.5)
            self.x = self.base_x + (max_x + (max_x - curve_x))
            self.y = self.base_y - self.curve_y
        else:
            self.x = self.base_x + self.curve_y
            self.y = self.base_y - self.curve_y

        # heal when projectile reaches
        if self.current_frame >= self.frames:
            self.active = False
            self.target_char.take_heal(active_effects, self.amount)

class BounceProjectile(ArcProjectile):
    def __init__(self, color, source_char, target_char, projectile_offset, amount, bounce_amount, enemies_hit):
        super().__init__(color, source_char, target_char, projectile_offset, amount)
        # bounce projectile specific info
        self.bounce_amount = bounce_amount
        self.enemies_hit = enemies_hit
    
    def update(self, enemy_goons, active_effects):
        # move projectile in an arc towards target
        super().update()
        if len(self.enemies_hit) == 0:
            self.x = self.base_x + self.curve_y
            self.y = self.base_y - self.curve_y
        else:
            self.x = self.base_x - self.curve_y
            self.y = self.base_y - self.curve_y
        
        # damage when projectile reaches and bounce again if valid
        if self.current_frame >= self.frames:
            damage = self.target_char.damage_amount(self.amount)
            self.target_char.take_damage(active_effects, damage)
            self.active = False
            self.enemies_hit.append(self.target_char)
            if self.bounce_amount > 0:
                valid_targets = []
                for enemy in enemy_goons:
                    if enemy.real_health > 0 and enemy not in self.enemies_hit:
                        valid_targets.append(enemy)
                if valid_targets:
                    next_target = random.choice(valid_targets)
                    damage = next_target.damage_amount(self.amount)
                    next_target.real_health -= damage
                    active_effects.append(BounceProjectile(self.color, self.target_char, next_target, (0, 0), self.amount, self.bounce_amount - 1, self.enemies_hit))

class LaserProjectile():
    def __init__(self, start_pos, end_pos):
        # basic laser projectile info
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.timer = 40
        self.alpha = 255
        self.active = True

    def update(self):
        # decrease timer and alpha, disappear when timer runs out
        self.timer -= 1
        if self.timer < 20:
            self.alpha = int((self.timer / 20) * 255)
        if self.timer <= 0:
            self.active = False

class GlitchyProjectile(Projectile):
    def __init__(self, color, source_char, target_char, projectile_offset, amount):
        super().__init__(color, source_char, target_char, projectile_offset, amount)
        # glitchy projectile specific info
        self.shake_x = 0
        self.shake_y = 0

    def update(self):
        # randomly shake projectile
        shake_roll = random.randint(1, 100)
        if shake_roll <= 20:
            self.shake_x = random.randint(-10, 10)
            self.shake_y = random.randint(-10, 10)

class GlitchyDamageProjectile(GlitchyProjectile):
    def __init__(self, color, source_char, target_char, projectile_offset, amount):
        super().__init__(color, source_char, target_char, projectile_offset, amount)
        # glitchy damage projectile specific info
        self.speed = 10
        self.distance = math.sqrt(self.distance_x ** 2 + self.distance_y ** 2)
        self.speed_x = self.distance_x / self.distance * self.speed
        self.speed_y = self.distance_y / self.distance * self.speed

    def update(self, active_effects):
        super().update()
        
        # move projectile towards target
        self.x += self.speed_x
        self.y += self.speed_y

        # damage when projectile reaches
        if (self.speed_x > 0 and self.x >= self.target_x) or (self.speed_x < 0 and self.x <= self.target_x):
            self.active = False
            self.target_char.take_damage(active_effects, self.amount)

class GlitchyHealProjectile(GlitchyProjectile):
    def __init__(self, color, source_char, target_char, projectile_offset, amount):
        super().__init__(color, source_char, target_char, projectile_offset, amount)
        # glitchy heal projectile specific info
        self.movement = "Forward"
        self.speed = 7

    def update(self, active_effects):
        super().update()

        # move projectile forward
        if self.movement == "Forward":
            self.x += self.speed
            if self.x >= 600:
                if self.target_y < self.y:
                    self.movement = "Upward"
                else:
                    self.movement = "Downward"

        # move projectile upward or downward towards target
        elif self.movement == "Upward":
            self.y -= self.speed
            if self.y <= self.target_y:
                self.movement = "Backward"
        elif self.movement == "Downward":
            self.y += self.speed
            if self.y >= self.target_y:
                self.movement = "Backward"

        # move projectile backward towards target
        elif self.movement == "Backward":
            self.x -= self.speed

            # heal when projectile reaches target
            if self.x <= self.target_x:
                self.active = False
                self.target_char.take_heal(active_effects, self.amount)

class GlitchyBlockProjectile(GlitchyProjectile):
    def __init__(self, color, source_char, target_char, projectile_offset, amount):
        super().__init__(color, source_char, target_char, projectile_offset, amount)
        # glitchy block projectile specific info
        self.movement = "Forward"
        self.speed = 20

    def update(self):
        super().update()

        # move projectile forward
        if self.movement == "Forward":
            self.x += 5
            if self.x >= 600:
                self.movement = "Backward"
                self.distance_x = self.target_x - self.x
                self.distance_y = self.target_y - self.y
                self.distance = math.sqrt(self.distance_x ** 2 + self.distance_y ** 2)
                self.speed_x = self.distance_x / self.distance * self.speed
                self.speed_y = self.distance_y / self.distance * self.speed

        # move projectile towards target
        elif self.movement == "Backward":
            self.x += self.speed_x
            self.y += self.speed_y

            # apply block when projectile reaches target
            if (self.speed_x > 0 and self.x >= self.target_x) or (self.speed_x < 0 and self.x <= self.target_x):
                self.active = False
                self.target_char.block = self.amount


# ------------------------------
# CHARACTERS
# ------------------------------

class Character:
    def __init__(self, name, health, x, y, box_background_color, description):
        # basic character info
        self.name = name
        self.real_health = health
        self.visual_health = health
        self.rect = pygame.Rect(x, y, 100, 100)
        self.box_background_color = box_background_color
        self.description = description

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
                return 0

        # double damage if marked
        if self.marked:
            damage *= 2
        
        # reduce damage if shield is active
        if self.shield > 0:
            damage = math.ceil(damage * self.shield)
        
        return damage

    def take_damage(self, active_effects, damage):
        # reduce health
        self.visual_health -= damage
        if self.visual_health < 0:
            self.visual_health = 0
        if self.real_health < 0:
            self.real_health = 0

        # text animation
        if damage == 0:
            text = "Blocked!"
            color = (255, 255, 0)
        else:
            self.hurt_timer = 30
            text = f"-{damage}"
            color = (255, 0, 0)
        text_width = len(text) * 10
        text_x = random.randint(self.rect.left, self.rect.right - text_width)
        active_effects.append(FloatingText(color, text_x, self.rect.top + 10, text))

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
        if self.ice_hits == ice_hits_needed:
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
        if self.mark_hits == mark_hits_needed:
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

    def lore_text(self, regular_font, lore):
        # add character name and description to lore text
        lore.append((f"Name: {self.name}", "normal"))
        description_lines = wrap_text(f"Description: {self.description}", regular_font, 560)
        for i, line in enumerate(description_lines):
            if i == len(description_lines) - 1:
                lore.append((line, "normal"))
            else:
                lore.append((line, "less"))

class Enemy(Character):
    def __init__(self, name, health, damage, min_gears, max_gears, slot_id, x, y, box_background_color, description, idle_image, hurt_image, dead_image):
        super().__init__(name, health, x, y, box_background_color, description)
        # enemy specific info
        self.damage = damage
        self.min_gears = min_gears
        self.max_gears = max_gears
        self.slot_id = slot_id

        # images
        self.idle_image = idle_image
        self.hurt_image = hurt_image
        self.dead_image = dead_image

        # animation
        self.float_direction = 2
        self.float_offset = random.choice([-4, -2, 0, 2, 4])

    def update_idle_animation(self):
        # move enemy up and down when alive and not hurt
        if self.visual_health > 0 and self.hurt_timer == 0:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.float_offset += self.float_direction
                if self.float_offset >= 4:
                    self.float_direction = -2
                elif self.float_offset <= -4:
                    self.float_direction = 2

    def lore_text(self, regular_font, lore):
        super().lore_text(regular_font, lore)
        # add enemy damage to lore text
        lore.append((f"Damage: {self.damage}", "normal"))

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

class ElementalBot(Bot):
    def __init__(self, name, health, x, y, box_background_color, description, idle_images_path, active_image_path, hurt_image_path, dead_image_path, button_color, button_hover_color, text_used_color):
        super().__init__(name, health, x, y, box_background_color, description, idle_images_path, active_image_path, hurt_image_path, dead_image_path, button_color, button_hover_color, text_used_color)
        # action dictionary
        self.actions = [
            {
                "name": "Fire",
                "damage": 1,
                "fire_rounds_amount": 3,
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
                "barrage_charge_needed": 10,
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
            if self.actions[1]["barrage_charge"] >= self.actions[1]["barrage_charge_needed"]:
                self.actions[1]["used"] = False
        
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
                "block": 50,
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
            lore.append((f"Min Damage: {action['min_power']}", "normal"))
            lore.append((f"Max Damage: {action['max_power']}", "normal"))
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
                "shield": 0.5,
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
            lore.append((f"Damage Reduction: {int(action['shield'] * 100)}%", "normal"))

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

chaos_bot = ChaosBot(
    "Chaos Bot", # name
    10, # health
    350, 250, # x, y
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
    350, 400, # x, y
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

# catalog of different enemy types
enemy_catalog = {
    "basic_goon": {
        "name": "Basic Goon",
        "health": 5,
        "damage": 1,
        "min_gears": 1,
        "max_gears": 5,
        "box_background_color": (255, 75, 75),
        "description": "A simple enemy goon that deals damage to a single target.",
        "idle_image_path": "assets/enemies/basic_goon/basic_goon_idle.png",
        "hurt_image_path": "assets/enemies/basic_goon/basic_goon_hurt.png",
        "dead_image_path": "assets/enemies/basic_goon/basic_goon_dead.png"
    }
}


# ------------------------------
# PLAYER TURN
# ------------------------------

def game_quit(event):
    # quit game if window is closed or escape key is pressed
    if event.type == pygame.QUIT:
        return False
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        return False
    return True

def scroll_math(mouse_pos, event, lore_height, target_scroll_y):
    # lore rectangle
    lore_rect = pygame.Rect(600, 620, 580, 90)

    # scroll through the lore box if mouse is scrolled over it
    if lore_rect.collidepoint(mouse_pos):
        max_scroll_index = max(0, lore_height - 80)
        # scroll up (text moves down)
        if event.button == 4:
            target_scroll_y = max(0, target_scroll_y - 30)
        # scroll down (text moves up)
        elif event.button == 5:
            target_scroll_y = min(max_scroll_index, target_scroll_y + 30)
    
    return target_scroll_y

def open_shop(mouse_pos, battle_state, previous_battle_state):
    # shop button rectangle
    shop_button_rect = pygame.Rect(40, 530, 100, 50)
    # open shop if button is clicked and close shop if button is clicked again
    if shop_button_rect.collidepoint(mouse_pos) and not lazer_bot.actions[0]["movement_mode"]:
        if battle_state == "Shop":
            battle_state = previous_battle_state
        else:
            previous_battle_state = battle_state
            battle_state = "Shop"
    return battle_state, previous_battle_state

def shop_upgrade(mouse_pos, gears):
    # upgrade button rectangles
    left_gun_upgrade_rect = pygame.Rect(670, 150, 150, 50)
    right_gun_upgrade_rect = pygame.Rect(670, 240, 150, 50)
    heal_upgrade_rect = pygame.Rect(670, 380, 150, 50)
    attack_upgrade_rect = pygame.Rect(670, 470, 150, 50)

    # upgrade bot action if upgrade button is clicked and player has enough gears
    if left_gun_upgrade_rect.collidepoint(mouse_pos) and gears >= 5:
        gun_bot.actions[0]["damage"] += 1
        gears -= 5
    elif right_gun_upgrade_rect.collidepoint(mouse_pos) and gears >= 5:
        gun_bot.actions[1]["damage"] += 1
        gears -= 5
    elif heal_upgrade_rect.collidepoint(mouse_pos) and gears >= 5:
        rico_bot.actions[0]["heal"] += 1
        gears -= 5
    elif attack_upgrade_rect.collidepoint(mouse_pos) and gears >= 5:
        rico_bot.actions[1]["damage"] += 1
        gears -= 5
    
    return gears

def harvest_gears(mouse_pos, enemy_goons, active_effects, gears, enemy_slots):
    for i in range(len(enemy_goons) - 1, -1, -1):
        # harvest gears from dead enemies if clicked and remove them from the game
        enemy = enemy_goons[i]
        if enemy.rect.collidepoint(mouse_pos) and enemy.visual_health == 0:
            enemy_gears = random.randint(enemy.min_gears, enemy.max_gears)
            gears += enemy_gears
            active_effects.append(FloatingText((100, 100, 100), enemy.rect.left, enemy.rect.centery, f"+{enemy_gears} gears"))
            enemy_slots[enemy.slot_id]["occupied"] = False
            enemy_goons.pop(i)
            break
    return gears

def inspect_enemy(mouse_pos, enemy_goons, inspecting_character, scroll_y, target_scroll_y):
    for enemy in enemy_goons:
        # inspect enemy if it's clicked and alive when its not time to target enemy
        if enemy.rect.collidepoint(mouse_pos) and enemy.real_health > 0:
            # enemy inspection is deselected if clicked again
            if inspecting_character == enemy:
                inspecting_character = None
            else:
                inspecting_character = enemy
                target_scroll_y = 0
                scroll_y = 0
            break
    return inspecting_character, scroll_y, target_scroll_y

def select_bot(mouse_pos, player_bots, battle_state, active_bot, chosen_action, inspecting_character, scroll_y, target_scroll_y):
    for bot in player_bots:
        # bot is selected if it's clicked, alive, and hasn't acted yet
        if bot.rect.collidepoint(mouse_pos) and bot.real_health > 0 and not bot.acted:
            # if lazer bot is active and pierce is chosen, lazer bot can't be deselected by clicking on it again
            if active_bot == bot and active_bot.name == "Lazer Bot" and chosen_action == "Pierce":
                break
            # if duplo bot is active and charge is chosen, duplo bot can't be deselected by clicking on it again
            elif active_bot == bot and active_bot.name == "Duplo Bot" and chosen_action == "Charge":
                break
            # bot is deselected if clicked again
            elif active_bot == bot:
                inspecting_character = None
                active_bot = None
            else:
                inspecting_character = bot
                active_bot = bot
                target_scroll_y = 0
                scroll_y = 0
            battle_state = "Player Turn"
            chosen_action = None
            break
    return battle_state, active_bot, chosen_action, inspecting_character, scroll_y, target_scroll_y

def select_action(mouse_pos, event, battle_state, active_bot, chosen_action, inspecting_character, scroll_y, target_scroll_y):
    # action button rectangles
    left_button_rect = pygame.Rect(120, 640, 150, 50)
    right_button_rect = pygame.Rect(290, 640, 150, 50)

    # bot action is chosen based on which button is clicked or pressed and action is deselected if clicked or pressed again
    if active_bot:
        if (mouse_pos and (left_button_rect.collidepoint(mouse_pos)) or (event and event.key == pygame.K_1)) and not active_bot.actions[0]["used"]:
            if chosen_action == active_bot.actions[0]["name"]:
                chosen_action = None
                battle_state = "Player Turn"
            else:
                chosen_action = active_bot.actions[0]["name"]
                battle_state = active_bot.actions[0]["target_state"]
                target_scroll_y = active_bot.actions[0]["scroll"]
            
            # if enemy is being inspected, switch inspecting to active bot when action is chosen
            if inspecting_character != active_bot:
                target_scroll_y = active_bot.actions[0]["scroll"]
                scroll_y = active_bot.actions[0]["scroll"]
                inspecting_character = active_bot

        elif (mouse_pos and (right_button_rect.collidepoint(mouse_pos)) or (event and event.key == pygame.K_2)) and not active_bot.actions[1]["used"]:
            if chosen_action == active_bot.actions[1]["name"]:
                chosen_action = None
                battle_state = "Player Turn"
            else:
                chosen_action = active_bot.actions[1]["name"]
                battle_state = active_bot.actions[1]["target_state"]
                target_scroll_y = active_bot.actions[1]["scroll"]
            
            # if enemy is being inspected, switch inspecting to active bot when action is chosen
            if inspecting_character != active_bot:
                target_scroll_y = active_bot.actions[1]["scroll"]
                scroll_y = active_bot.actions[1]["scroll"]
                inspecting_character = active_bot
    
    return battle_state, chosen_action, inspecting_character, scroll_y, target_scroll_y

def check_bot_turn(player_bots, enemy_goons):
    # check if all enemies are dead
    no_enemies_alive = True
    for enemy in enemy_goons:
        if enemy.real_health > 0:
            no_enemies_alive = False
            break
    if no_enemies_alive:
        return "Player Turn Over"

    # check if all bots finished their actions
    for bot in player_bots:
        if bot.real_health > 0 and not bot.acted:
            return "Player Turn"
    return "Player Turn Over"

def execute_laser_action(mouse_pos, player_bots, enemy_goons, active_effects, battle_state, active_bot, chosen_action, inspecting_character):
    # bot enters and exits movement mode when clicked on
    if active_bot.rect.collidepoint(mouse_pos) and not active_bot.actions[0]["movement_mode"]:
        active_bot.actions[0]["movement_mode"] = True
    elif active_bot.rect.collidepoint(mouse_pos) and active_bot.actions[0]["movement_mode"]:
        active_bot.actions[0]["movement_mode"] = False
    
    # perform pierce action if lazer bot is not in movement mode and mouse is clicked to the right of lazer bot
    elif active_bot.actions[0]["movement_mode"] == False and mouse_pos[0] > active_bot.rect.centerx + active_bot.actions[0]["projectile_offset"][0]:
        # calculate the start position, end position, and direction of the laser beam based on the mouse position and lazer bot's position
        start_x = active_bot.rect.centerx + active_bot.actions[0]["projectile_offset"][0]
        start_y = active_bot.rect.centery + active_bot.actions[0]["projectile_offset"][1]
        direction_x = mouse_pos[0] - start_x
        direction_y = mouse_pos[1] - start_y
        length = (direction_x ** 2 + direction_y ** 2) ** 0.5
        end_x = start_x + direction_x / length * 1000
        end_y = start_y + direction_y / length * 1000

        # find all enemies hit by the laser beam
        enemies_hit = []
        for enemy in enemy_goons:
            if enemy.real_health > 0 and enemy.rect.clipline(start_x, start_y, end_x, end_y):
                enemies_hit.append(enemy)
        active_bot.perform_action(active_effects, enemies_hit, chosen_action, (end_x, end_y))
        active_bot.actions[0]["used"] = True

        # check if active bot used both actions and reset for next action
        active_bot.check_actions()
        active_bot = None
        chosen_action = None
        inspecting_character = None

        return check_bot_turn(player_bots, enemy_goons), active_bot, chosen_action, inspecting_character
    return battle_state, active_bot, chosen_action, inspecting_character

def execute_action(mouse_pos, player_bots, enemy_goons, characters, active_effects, battle_state, active_bot, chosen_action, inspecting_character,):
    for char in characters:
        if char.rect.collidepoint(mouse_pos) and char.real_health > 0:
            # mark chosen action as used
            for action in active_bot.actions:
                if action["name"] == chosen_action:
                    action["used"] = True
                    break
            
            # perform the action chosen on the target character
            if chosen_action == "Barrage":
                active_bot.perform_action(active_effects, enemy_goons, chosen_action, None)
            else:
                active_bot.perform_action(active_effects, char, chosen_action)
            
            # check if active bot used both actions and reset for next action
            active_bot.check_actions()
            active_bot = None
            chosen_action = None
            inspecting_character = None

            return check_bot_turn(player_bots, enemy_goons), active_bot, chosen_action, inspecting_character
    return battle_state, active_bot, chosen_action, inspecting_character

def player_turn(event, mouse_pos, player_bots, enemy_goons, active_effects, battle_state, previous_battle_state, active_bot, chosen_action, inspecting_character, lore_height, scroll_y, target_scroll_y, gears, enemy_slots):
    # if game is over, dont allow any more actions
    if battle_state == "Game Over":
        return battle_state, previous_battle_state, active_bot, chosen_action, inspecting_character, scroll_y, target_scroll_y, gears
 
    # update target scroll based on mouse scroll
    if event.button in [4, 5]:
        target_scroll_y = scroll_math(mouse_pos, event, lore_height, target_scroll_y)
    
    # handle player actions based on battle state and mouse clicks
    elif event.button == 1:
        # open or close shop
        battle_state, previous_battle_state = open_shop(mouse_pos, battle_state, previous_battle_state)

        # upgrade bot actions if shop is open
        if battle_state == "Shop":
            gears = shop_upgrade(mouse_pos, gears)

        else:
            # if lazer bot is in movement mode, other actions are disabled
            if not lazer_bot.actions[0]["movement_mode"]:
                # harvest gears
                gears = harvest_gears(mouse_pos, enemy_goons, active_effects, gears, enemy_slots)

                # inspect enemy if not targeting enemy
                if battle_state not in ["Target Enemy", "Target Enemy or Self", "Target Any"]:
                    inspecting_character, scroll_y, target_scroll_y = inspect_enemy(mouse_pos, enemy_goons, inspecting_character, scroll_y, target_scroll_y)

                # select bot if not targeting bot
                if battle_state not in ["Target Bot", "Target Any"]:
                    battle_state, active_bot, chosen_action, inspecting_character, scroll_y, target_scroll_y = select_bot(mouse_pos, player_bots, battle_state, active_bot, chosen_action, inspecting_character, scroll_y, target_scroll_y)
                
                # select action if bot is selected
                battle_state, chosen_action, inspecting_character, scroll_y, target_scroll_y = select_action(mouse_pos, None, battle_state, active_bot, chosen_action, inspecting_character, scroll_y, target_scroll_y)
                
            # carry out the chosen action
            if battle_state == "Target Line":
                battle_state, active_bot, chosen_action, inspecting_character = execute_laser_action(mouse_pos, player_bots, enemy_goons, active_effects, battle_state, active_bot, chosen_action, inspecting_character)
            elif battle_state == "Target Enemy":
                battle_state, active_bot, chosen_action, inspecting_character = execute_action(mouse_pos, player_bots, enemy_goons, enemy_goons, active_effects, battle_state, active_bot, chosen_action, inspecting_character)
            elif battle_state == "Target Bot":
                battle_state, active_bot, chosen_action, inspecting_character = execute_action(mouse_pos, player_bots, enemy_goons, player_bots, active_effects, battle_state, active_bot, chosen_action, inspecting_character)
            elif battle_state in ["Target Enemy or Self", "Target Any"]:
                battle_state, active_bot, chosen_action, inspecting_character = execute_action(mouse_pos, player_bots, enemy_goons, player_bots + enemy_goons, active_effects, battle_state, active_bot, chosen_action, inspecting_character)

    # right click to close shop or cancel action or bot
    elif event.button == 3:
        if battle_state == "Shop":
            battle_state = previous_battle_state
        elif not lazer_bot.actions[0]["movement_mode"]:
            if chosen_action:
                chosen_action = None
                battle_state = "Player Turn"
            elif active_bot:
                inspecting_character = None
                active_bot = None
            elif inspecting_character:
                inspecting_character = None

    return battle_state, previous_battle_state, active_bot, chosen_action, inspecting_character, scroll_y, target_scroll_y, gears

def handle_input(running, player_bots, enemy_goons, active_effects, game_state, battle_state, previous_battle_state, active_bot, chosen_action, inspecting_character, lore_height, scroll_y, target_scroll_y, gears, enemy_slots):
    for event in pygame.event.get():
        # check for quit events
        running = game_quit(event)
        if not running:
            break
        
        # do things based on the mouse
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # handle main menu input
            if game_state == "Main Menu":
                if event.button == 1:
                    # check if endless mode button is clicked
                    endless_button_rect = pygame.Rect(500, 500, 200, 80)
                    if endless_button_rect.collidepoint(mouse_pos):
                        game_state = "Endless Mode"
            
            # handle battle input
            elif game_state == "Endless Mode":
                battle_state, previous_battle_state, active_bot, chosen_action, inspecting_character, scroll_y, target_scroll_y, gears = player_turn(
                    event, mouse_pos, player_bots, enemy_goons, active_effects, battle_state, previous_battle_state, active_bot, chosen_action, inspecting_character, lore_height, scroll_y, target_scroll_y, gears, enemy_slots)
        
        elif event.type == pygame.KEYDOWN:
            if not lazer_bot.actions[0]["movement_mode"]:
                # select action if bot is selected based on key press
                battle_state, chosen_action, inspecting_character, scroll_y, target_scroll_y = select_action(None, event, battle_state, active_bot, chosen_action, inspecting_character, scroll_y, target_scroll_y)

    return running, game_state, battle_state, previous_battle_state, active_bot, chosen_action, inspecting_character, scroll_y, target_scroll_y, gears


# ------------------------------
# ENEMY TURN
# ------------------------------

def enemy_attacks(player_bots, enemy_goons, active_effects, battle_state):
    if battle_state == "Enemy Turn":
        for enemy in enemy_goons:
            if enemy.real_health > 0:
                # skip the enemy turn if frozen
                if enemy.frozen:
                    continue
                
                # attack a random alive bot
                bots_alive = []
                for bot in player_bots:
                    if bot.real_health > 0:
                        bots_alive.append(bot)
                if bots_alive:
                    target = random.choice(bots_alive)
                    damage = target.damage_amount(enemy.damage)
                    target.real_health -= damage
                    active_effects.append(LinearProjectile((255, 0, 0), enemy, target, (-50, -50), damage, "Damage"))
        battle_state = "Enemy Turn Over"
    return battle_state

def round_end(player_bots, enemy_goons, active_effects, battle_state, rounds):
    # does fire damage to characters on fire
    for char in player_bots + enemy_goons:
        if char.real_health > 0 and char.fire_rounds > 0:
            char.fire_rounds -= 1
            if char in player_bots:
                damage = char.damage_amount(1)
                char.real_health -= damage
                char.take_damage(active_effects, damage)
            elif char in enemy_goons:
                damage = char.damage_amount(elemental_bot.actions[0]["damage"])
                char.real_health -= damage
                char.take_damage(active_effects, damage)
    
    # resets for next turn
    for bot in player_bots:
        bot.reset_actions()
    for char in player_bots + enemy_goons:
        char.frozen = False
        char.marked = False
        char.block = 0
        char.shield = 0
    battle_state = "Player Turn"
    rounds += 1
    return battle_state, rounds

def spawn_enemy(x, y, slot_id):
    # randomize the enemy spawn position within a range
    x_offset = random.randint(0, 100)
    y_offset = random.randint(40, 100)

    # create a new enemy
    stats = enemy_catalog["basic_goon"]
    new_enemy = Enemy(
        stats["name"],
        stats["health"],
        stats["damage"],
        stats["min_gears"],
        stats["max_gears"],
        slot_id,
        x + x_offset,
        y + y_offset,
        stats["box_background_color"],
        stats["description"],
        stats["idle_image"],
        stats["hurt_image"],
        stats["dead_image"],
    )
    return new_enemy

def spawn_state(enemy_goons, active_effects, gears, rounds, max_enemies, enemy_slots):
    # determine how many enemies to spawn based on the round
    spawns = 0
    if rounds <= 10:
        spawns = 1
    else:
        spawns = 2
    
    # increase the max number of enemies every 5 rounds, up to a maximum of 9
    if max_enemies <= 9 and rounds % 5 == 0:
        max_enemies += 1
    
    for _ in range(spawns):
        # remove dead enemies and harvest gears if there are max number of enemies on the field
        if len(enemy_goons) == max_enemies:
            for i in range(len(enemy_goons) - 1, -1, -1):
                enemy = enemy_goons[i]
                if enemy.visual_health == 0:
                    enemy_gears = random.randint(enemy.min_gears, enemy.max_gears)
                    gears += enemy_gears
                    active_effects.append(FloatingText((100, 100, 100), enemy.rect.left, enemy.rect.centery, f"+{enemy_gears} gears"))
                    enemy_slots[enemy.slot_id]["occupied"] = False
                    enemy_goons.pop(i)
                    break
        
        # spawn new enemies if there are empty slots
        if len(enemy_goons) < max_enemies:
            empty_slots = []
            for i, slot in enumerate(enemy_slots):
                if not slot["occupied"]:
                    empty_slots.append(i)
            if empty_slots:
                slot_id = random.choice(empty_slots)
                slot = enemy_slots[slot_id]
                new_enemy = spawn_enemy(slot["x"], slot["y"], slot_id)
                enemy_goons.append(new_enemy)
                slot["occupied"] = True
    
    return gears, max_enemies

def enemy_turn(player_bots, enemy_goons, active_effects, battle_state, gears, rounds, max_enemies, enemy_slots):
    # change to enemy turn if player turn is over and all projectiles have reached their target
    if battle_state == "Player Turn Over":
        projectiles_effects_active = False
        for effect in active_effects:
            if not isinstance(effect, FloatingText):
                projectiles_effects_active = True
                break
        if not projectiles_effects_active:
            battle_state = "Enemy Turn"

    # enemy attack logic
    battle_state = enemy_attacks(player_bots, enemy_goons, active_effects, battle_state)

    # change to round end if enemy turn is over and all projectiles have reached their target
    if battle_state == "Enemy Turn Over":
        projectiles_effects_active = False
        for effect in active_effects:
            if not isinstance(effect, FloatingText):
                projectiles_effects_active = True
                break
        if not projectiles_effects_active:
            battle_state = "Round End"

    if battle_state == "Round End":
        # end of round logic
        battle_state, rounds = round_end(player_bots, enemy_goons, active_effects, battle_state, rounds)

        # spawn new enemies based on the round and max enemies
        gears, max_enemies = spawn_state(enemy_goons, active_effects, gears, rounds, max_enemies, enemy_slots)
    
    return battle_state, gears, rounds, max_enemies


# ------------------------------
# GAME BEGINNING AND ENDING
# ------------------------------

def spawn_inital_enemies(enemy_goons, enemy_slots):
    # spawn two basic goons at the start of the game in random empty slots
    for _ in range(2):
        empty_slots = []
        for i, slot in enumerate(enemy_slots):
            if not slot["occupied"]:
                empty_slots.append(i)
        slot_id = random.choice(empty_slots)
        slot = enemy_slots[slot_id]
        new_enemy = spawn_enemy(slot["x"], slot["y"], slot_id)
        enemy_goons.append(new_enemy)
        slot["occupied"] = True

def check_game_over(player_bots, battle_state, scroll_y, target_scroll_y):
    # check if battle state is already game over
    if battle_state == "Game Over":
        return battle_state, scroll_y, target_scroll_y
    
    # game ends when all bots are dead
    game_end = True
    for bot in player_bots:
        if bot.real_health > 0:
            game_end = False
            break
    if game_end:
        target_scroll_y = 0
        scroll_y = 0
        battle_state = "Game Over"
    
    return battle_state, scroll_y, target_scroll_y


# ------------------------------
# DRAWING, ANIMATION, AND RENDERING
# ------------------------------

def update_animations(player_bots, enemy_goons, active_effects, battle_state, active_bot, scroll_y, target_scroll_y):
    # update characters shake when they are hurt
    for char in player_bots + enemy_goons:
        char.hurt_animations()

    # update idle animation frames
    for char in player_bots + enemy_goons:
        char.update_idle_animation()

    # update lazer bot position if in movement mode
    if battle_state == "Target Line" and active_bot.actions[0]["movement_mode"]:
        mouse_pos_y = pygame.mouse.get_pos()[1]
        active_bot.rect.centery = max(1, min(730, mouse_pos_y))

    # update and remove effects
    for effect in active_effects[:]:
        if isinstance(effect, FloatingText) or isinstance(effect, LaserProjectile) or isinstance(effect, GlitchyBlockProjectile) or isinstance(effect, ShieldProjectile):
            effect.update()
        elif isinstance(effect, BounceProjectile):
            effect.update(enemy_goons, active_effects)
        else:
            effect.update(active_effects)
        if not effect.active:
            active_effects.remove(effect)
    
    # update scrolling position for lore box
    scroll_y += (target_scroll_y - scroll_y) * 0.2
    if abs(target_scroll_y - scroll_y) < 0.1:
        scroll_y = target_scroll_y
    return scroll_y

def draw_characters(screen, regular_font, player_bots, enemy_goons, active_bot, chosen_action, inspecting_character):
    for char in player_bots + enemy_goons:
        # dead state
        if char.visual_health <= 0:
            current_image = char.dead_image
            current_image.set_alpha(50)

        # hurt state
        elif char.hurt_timer > 0:
            current_image = char.hurt_image
            current_image.set_alpha(255)

        # action chosen state
        elif char == active_bot and chosen_action:
            for action in active_bot.actions:
                if chosen_action == action["name"]:
                    current_image = action["image"]

        # active state
        elif char == active_bot:
            current_image = char.active_image

        # idle state        
        else:
            if char in player_bots:
                current_image = char.idle_images[char.current_frame]
                if char.acted:
                    current_image.set_alpha(150)
                else:
                    current_image.set_alpha(255)
            elif char in enemy_goons:
                current_image = char.idle_image
                current_image.set_alpha(255)

        # move enemies up and down
        char_y = char.rect.y
        if char in enemy_goons and not char.frozen:
            char_y += char.float_offset

        # draw character image
        screen.blit(current_image, (char.rect.x + char.shake_x, char_y))

        # draw name and health
        name_text = regular_font.render(char.name, True, (255, 255, 255))
        health_text = regular_font.render(f"HP: {char.visual_health}", True, (255, 255, 255))
        screen.blit(name_text, (char.rect.x, char.rect.y - 40))
        screen.blit(health_text, (char.rect.x, char.rect.y - 20))

        # draw small circle next to name if inspecting character
        if char == inspecting_character:
            if char in player_bots:
                color = (0, 0, 255)
                dot_offset = 1
            elif char in enemy_goons:
                color = (255, 0, 0)
                dot_offset = 0
            pygame.draw.circle(screen, color, (char.rect.x - 10, char.rect.y - 33 - dot_offset), 5)

def draw_character_status_effects(screen, regular_font, player_bots, enemy_goons, battle_state):
    for char in player_bots + enemy_goons:
        if char.visual_health > 0:
            # draw overlay on character if frozen or on fire
            if char.frozen:
                overlay = pygame.Surface((100, 100), pygame.SRCALPHA)
                overlay.fill((0, 255, 255, 100))
                screen.blit(overlay, char.rect)
            elif char.fire_rounds > 0:
                overlay = pygame.Surface((100, 100), pygame.SRCALPHA)
                overlay.fill((255, 0, 0, 100))
                screen.blit(overlay, char.rect)

            # draw number of fire rounds at bottom left of character
            if char.fire_rounds > 0:
                fire_text = regular_font.render(f"{char.fire_rounds}", True, (255, 0, 0))
                screen.blit(fire_text, (char.rect.x + 2, char.rect.bottom - 16))
            
            # draw boxes for number of ice hits and how many needed
            if char.ice_hits > 0:
                for i in range(elemental_bot.actions[1]["ice_hits_needed"]):
                    if elemental_bot.actions[1]["ice_hits_needed"] == 3:
                        box_x_offset = 28
                    elif elemental_bot.actions[1]["ice_hits_needed"] == 2:
                        box_x_offset = 19
                    box_rect = pygame.Rect(char.rect.right - box_x_offset + (i * 9), char.rect.y - 11, 10, 10)
                    if i < char.ice_hits:
                        pygame.draw.rect(screen, (0, 255, 255), box_rect)
                    else:
                        pygame.draw.rect(screen, (0, 255, 255), box_rect, 1)
            
            # draw boxes for number of mark hits and how many needed
            if char.mark_hits > 0:
                for i in range(2):
                    box_rect = pygame.Rect(char.rect.right - 19 + (i * 9), char.rect.y - 21, 10, 10)
                    if i < char.mark_hits:
                        pygame.draw.rect(screen, (255, 255, 0), box_rect)
                    else:
                        pygame.draw.rect(screen, (255, 255, 0), box_rect, 1)

            # draw "M" if marked
            if char.marked:
                mark_text = regular_font.render("M", True, (255, 255, 0))
                screen.blit(mark_text, (char.rect.x - 16, char.rect.y - 20))

            # draw block barrier
            if char.block > 0:
                pygame.draw.rect(screen, (255, 200, 0), (char.rect.x -10, char.rect.y, 110, 110), 3)
                pygame.draw.rect(screen, (255, 200, 0), (char.rect.x, char.rect.y - 5, 105, 105), 3)
                pygame.draw.rect(screen, (255, 200, 0), (char.rect.x, char.rect.y, 120, 120), 3)

            # draw shield
            if char.shield > 0:
                pygame.draw.circle(screen, (200, 200, 200), (char.rect.centerx, char.rect.centery), 55, 3)

            # highlight character if hovering and valid target
            mouse_pos = pygame.mouse.get_pos()
            if char.rect.collidepoint(mouse_pos) and char.real_health > 0:
                if char in enemy_goons and battle_state in ["Target Enemy", "Target Enemy or Self", "Target Any"]:
                    pygame.draw.rect(screen, (255, 0, 0), char.rect, 3)
                elif (char in player_bots and battle_state in ["Target Bot", "Target Any"]) or (char.name == "Lazer Bot" and battle_state == "Target Line") or (char.name == "Duplo Bot" and battle_state == "Target Enemy or Self"):
                    pygame.draw.rect(screen, (0, 255, 0), char.rect, 3)
                elif char in player_bots and battle_state not in ["Game Over", "Shop"] and not char.acted and not lazer_bot.actions[0]["movement_mode"]:
                    pygame.draw.rect(screen, (0, 0, 255), char.rect, 3)

def dynamic_text(font_cache, text, max_width, max_height, color):
    # default font size
    font_size = 30

    # decrease font size until it fits within the max width and height
    while font_size > 10:
        temp_font = font_cache[font_size]
        text_width, text_height = temp_font.size(text)
        if text_width <= max_width and text_height <= max_height:
            return temp_font.render(text, True, color)
        font_size -= 1

    # use the smallest font if text is too long
    smallest_font = font_cache[10]
    return smallest_font.render(text, True, color)

def draw_action_button(screen, font_cache, battle_state, active_bot, x, y, text, used, chosen):
    # button rectangle
    button_rect = pygame.Rect(x, y, 150, 50)
    
    # change button color based on hover and chosen state
    mouse_pos = pygame.mouse.get_pos()
    if battle_state != "Shop" and not lazer_bot.actions[0]["movement_mode"]:
        if chosen and button_rect.collidepoint(mouse_pos):
            button_color = (255, 125, 125)
        elif not used and button_rect.collidepoint(mouse_pos):
            button_color = active_bot.button_hover_color
        else:
            button_color = active_bot.button_color
    else:
        button_color = active_bot.button_color

    # draw button rectangle
    pygame.draw.rect(screen, button_color, button_rect)

    # if it's the chosen action, highlight and change text
    if chosen:
        text = f"Cancel {text}"
        pygame.draw.rect(screen, (0, 255, 0), button_rect, 4)

    # gray out if it's already used
    if not used:
        text_color = (255, 255, 255)
    else:
        text_color = active_bot.text_used_color
    
    # dynamically adjust font size to fit the button
    button_text = dynamic_text(font_cache, text, 140, 40, text_color)

    # center the text on the button
    button_text_rect = button_text.get_rect(center=button_rect.center)
    button_text_rect.y += 1

    # draw button text
    screen.blit(button_text, button_text_rect)

def draw_action_box(screen, font_cache, battle_state, active_bot, chosen_action):
    # draw action box background
    if active_bot:
        color = active_bot.box_background_color
    else:
        color = (50, 50, 50)
    pygame.draw.rect(screen, color, (100, 620, 360, 90))
    pygame.draw.rect(screen, (255, 255, 255), (100, 620, 360, 90), 3)

    # draw action buttons based on active bot
    if active_bot:
        for index, action in enumerate(active_bot.actions):
            if index == 0:
                x = 120
            else:
                x = 290
            draw_action_button(screen, font_cache, battle_state, active_bot, x, 640, action["name"], action["used"], chosen_action == action["name"])

def draw_shop_box(screen, regular_font, font_cache, battle_state, active_bot, gears, rounds):
    # draw shop box background
    if active_bot:
        box_color = active_bot.box_background_color
    else:
        box_color = (50, 50, 50)
    pygame.draw.rect(screen, box_color, (20, 510, 140, 90))
    pygame.draw.rect(screen, (255, 255, 255), (20, 510, 140, 90), 3)

    # draw shop button with hover effect
    button_rect = pygame.Rect(40, 530, 100, 50)
    mouse_pos = pygame.mouse.get_pos()
    if button_rect.collidepoint(mouse_pos) and battle_state == "Shop":
        button_color = (255, 125, 125)
    elif active_bot:
        if button_rect.collidepoint(mouse_pos) and not lazer_bot.actions[0]["movement_mode"]:
            button_color = active_bot.button_hover_color
        else:
            button_color = active_bot.button_color
    else:
        if button_rect.collidepoint(mouse_pos) and battle_state != "Game Over" and not lazer_bot.actions[0]["movement_mode"]:
            button_color = (200, 200, 200)
        else:
            button_color = (150, 150, 150)
    pygame.draw.rect(screen, button_color, button_rect)

    # draw shop text
    if battle_state == "Shop":
        text = "Close Shop"
    else:
        text = "Shop"
    shop_text = dynamic_text(font_cache, text, 90, 40, (255, 255, 255))
    shop_text_rect = shop_text.get_rect(center=(90, 555))
    screen.blit(shop_text, shop_text_rect)

    # draw info box background
    pygame.draw.rect(screen, box_color, (20, 453, 140, 60))
    pygame.draw.rect(screen, (255, 255, 255), (20, 453, 140, 60), 3)

    # draw round and gears text
    round_text = regular_font.render(f"Round: {rounds}", True, (255, 255, 255))
    gears_text = regular_font.render(f"Gears: {gears}", True, (255, 255, 255))
    round_text_rect = round_text.get_rect(center=(90, 473))
    gears_text_rect = gears_text.get_rect(center=(90, 493))
    screen.blit(round_text, round_text_rect)
    screen.blit(gears_text, gears_text_rect)

def draw_shop_menu(screen, font_cache, battle_state, gears):
    if battle_state == "Shop":
        mouse_pos = pygame.mouse.get_pos()
        
        # dictionary of shop upgrades for each bot
        shop_items = [
            {
                "bot": gun_bot,
                "name": "Gun Bot",
                "upgrades": [
                    {"action": "Left Gun", "buff": "+1 damage", "cost": "5 gears"},
                    {"action": "Right Gun", "buff": "+1 damage", "cost": "5 gears"}
                ]
            },
            {
                "bot": rico_bot,
                "name": "Rico Bot",
                "upgrades": [
                    {"action": "Heal", "buff": "+1 heal", "cost": "5 gears"},
                    {"action": "Attack", "buff": "+1 damage", "cost": "5 gears"}
                ]
            }
        ]

        # the center x-coordinate for each column
        col_x_center_1 = 175
        col_x_center_2 = 365
        col_x_center_3 = 555
        col_x_center_4 = 745

        # draw each shop row and column with the bots upgrades
        for i, item in enumerate(shop_items):
            # draw the background box for the bots upgrades
            box_y = 80 + (i * 230)
            pygame.draw.rect(screen, item["bot"].box_background_color, (80, box_y, 760, 230))

            # draw the header for each column
            header_y = box_y + 27
            heading_name = dynamic_text(font_cache, item["name"], 180, 40, (255, 255, 255))
            screen.blit(heading_name, heading_name.get_rect(center=(col_x_center_1, header_y)))
            heading_buff = dynamic_text(font_cache, "Buff", 180, 40, (255, 255, 255))
            screen.blit(heading_buff, heading_buff.get_rect(center=(col_x_center_2, header_y)))
            heading_cost = dynamic_text(font_cache, "Cost", 180, 40, (255, 255, 255))
            screen.blit(heading_cost, heading_cost.get_rect(center=(col_x_center_3, header_y)))
            heading_upgrade = dynamic_text(font_cache, "Upgrade", 180, 40, (255, 255, 255))
            screen.blit(heading_upgrade, heading_upgrade.get_rect(center=(col_x_center_4, header_y)))

            # draw each upgrade row for the bot
            for j, upgrade in enumerate(item["upgrades"]):
                # calculate the y-coordinate center for each row and button
                row_y = box_y + 95 + (j * 90)
                button_y = box_y + 70 + (j * 90)

                # draw the action, buff, and cost text for each upgrade
                action = dynamic_text(font_cache, upgrade["action"], 180, 40, (255, 255, 255))
                screen.blit(action, action.get_rect(center=(col_x_center_1, row_y)))
                buff = dynamic_text(font_cache, upgrade["buff"], 180, 40, (255, 255, 255))
                screen.blit(buff, buff.get_rect(center=(col_x_center_2, row_y)))
                cost = dynamic_text(font_cache, upgrade["cost"], 180, 40, (255, 255, 255))
                screen.blit(cost, cost.get_rect(center=(col_x_center_3, row_y)))

                # draw the upgrade button with color change based on hover and if enough gears
                button_rect = pygame.Rect(670, button_y, 150, 50)
                if button_rect.collidepoint(mouse_pos) and gears >= int(upgrade["cost"].split()[0]):
                    button_color = item["bot"].button_hover_color
                else:
                    button_color = item["bot"].button_color
                pygame.draw.rect(screen, button_color, button_rect)

                # draw the upgrade button text with color change based on if enough gears
                if gears >= int(upgrade["cost"].split()[0]):
                    text_color = (255, 255, 255)
                else:
                    text_color = item["bot"].text_used_color
                button_text = dynamic_text(font_cache, "Upgrade", 140, 40, text_color)
                screen.blit(button_text, button_text.get_rect(center=(col_x_center_4, row_y)))

        # shop menu outline
        pygame.draw.rect(screen, (255, 255, 255), (80, 80, 760, 460), 3)

        # gun bot row lines
        pygame.draw.line(screen, (255, 255, 255), (80, 130), (839, 130), 2)
        pygame.draw.line(screen, (255, 255, 255), (80, 220), (839, 220), 2)
        pygame.draw.line(screen, (255, 255, 255), (80, 310), (839, 310), 3)

        # rico bot row lines
        pygame.draw.line(screen, (255, 255, 255), (80, 360), (839, 360), 2)
        pygame.draw.line(screen, (255, 255, 255), (80, 450), (839, 450), 2)

        # columns lines
        pygame.draw.line(screen, (255, 255, 255), (270, 80), (270, 539), 3)
        pygame.draw.line(screen, (255, 255, 255), (460, 80), (460, 539), 3)
        pygame.draw.line(screen, (255, 255, 255), (650, 80), (650, 539), 3)

def wrap_text(text, regular_font, max_width):
    # split the text into a list of words
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        # check if adding the next word to the current line exceeds the max width
        test_line = f"{current_line} {word}".strip()
        if regular_font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            # add the current line to list of lines if its over the max width
            lines.append(current_line.strip())
            current_line = word

    # add the last line
    if current_line:
        lines.append(current_line.strip())

    return lines

def draw_lore_box(screen, regular_font, battle_state, inspecting_character, scroll_y, rounds):
    # draw lore box background
    if inspecting_character:
        color = inspecting_character.box_background_color
    else:
        color = (50, 50, 50)
    pygame.draw.rect(screen, color, (600, 620, 580, 90))
    pygame.draw.rect(screen, (255, 255, 255), (600, 620, 580, 90), 3)

    lore = []
    # lore text based on battle state or inspecting character
    if battle_state == "Game Over":
        lore.append(("The enemies have defeated all your bots!", "normal"))
        lore.append((f"You have survived for a total of {rounds} rounds.", "normal"))
        lore.append(("Game Over!", "normal"))
    elif inspecting_character:
        inspecting_character.lore_text(regular_font, lore)

    # calculate lore height
    lore_height = 0
    for line, type in lore:
        if line.startswith("Action:"):
            lore_height += 15
        if type == "normal":
            lore_height += 25
        elif type == "less":
            lore_height += 20

    # create a surface for the lore text with see through background
    lore_canvas = pygame.Surface((580, max(1, lore_height)), pygame.SRCALPHA)

    # draw lore text into the lore canvas
    y_offset = 5
    for line, type in lore:
        if line.startswith("Action:"):
            y_offset += 15
        lore_text = regular_font.render(line, True, (255, 255, 255))
        lore_canvas.blit(lore_text, (0, y_offset))
        if type == "normal":
            y_offset += 25
        elif type == "less":
            y_offset += 20

    # draw the visible part of lore canvas onto the screen based on scroll position
    visible_rect = pygame.Rect(0, int(scroll_y), 580, 80)
    screen.blit(lore_canvas, (610, 625), visible_rect)
    
    # update lore height for scrolling calculations
    lore_height = max(0, y_offset - 5)

    return lore_height

def draw_laser(screen, enemy_goons, battle_state, active_bot):
    if battle_state == "Target Line" and not active_bot.actions[0]["movement_mode"]:
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[0] > active_bot.rect.centerx + active_bot.actions[0]["projectile_offset"][0]:
            # calculate the start position, end position, and direction of the laser beam based on the mouse position and lazer bot's position
            start_x = active_bot.rect.centerx + active_bot.actions[0]["projectile_offset"][0]
            start_y = active_bot.rect.centery + active_bot.actions[0]["projectile_offset"][1]
            direction_x = mouse_pos[0] - start_x
            direction_y = mouse_pos[1] - start_y
            length = (direction_x ** 2 + direction_y ** 2) ** 0.5
            end_x = start_x + direction_x / length * 1000
            end_y = start_y + direction_y / length * 1000

            # highlight all enemies being hit by the laser
            for enemy in enemy_goons:
                if enemy.real_health > 0 and enemy.rect.clipline(start_x, start_y, end_x, end_y):
                    pygame.draw.rect(screen, (255, 0, 0), enemy.rect, 3)

            # draw the laser beam
            pygame.draw.line(screen, (255, 50, 255), (start_x, start_y), (end_x, end_y), 3)

def draw_effects(screen, floating_font, active_effects):
    # draw animation based on its type
    for effect in active_effects:
        # draw floating text
        if isinstance(effect, FloatingText):
            text = floating_font.render(effect.text, True, effect.color)
            screen.blit(text, (effect.x, effect.y))

        # draw laser projectile
        elif isinstance(effect, LaserProjectile):
            laser_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            if effect.timer > 20:
                pygame.draw.line(laser_surface, (255, 50, 255, 255), effect.start_pos, effect.end_pos, 7)
            else:
                pygame.draw.line(laser_surface, (255, 50, 255, effect.alpha), effect.start_pos, effect.end_pos, 3)
            screen.blit(laser_surface, (0, 0))

        # draw charge projectiles
        elif isinstance(effect, ChargeProjectile):
            pygame.draw.circle(screen, effect.color, (int(effect.x), int(effect.y)), effect.current_radius)
            pygame.draw.circle(screen, (150, 150, 0), (int(effect.x), int(effect.y)), effect.current_radius, effect.border)

        # draw mark projectiles
        elif isinstance(effect, MarkProjectile):
            pygame.draw.arc(screen, effect.color, (effect.x-5, effect.y-5, 10, 10), effect.angle, effect.angle + 3.14, 2)

        # draw percentage projectiles
        elif isinstance(effect, PercentageProjectile):
            pygame.draw.line(screen, effect.color, (effect.line_one_x1, effect.line_one_y1), (effect.line_one_x2, effect.line_one_y2), 2)
            pygame.draw.line(screen, effect.color, (effect.line_two_x1, effect.line_two_y1), (effect.line_two_x2, effect.line_two_y2), 2)

        # draw shield projectiles
        elif isinstance(effect, ShieldProjectile):
            pygame.draw.circle(screen, effect.color, (int(effect.x), int(effect.y)), 5, 2)

        # draw linear projectiles
        elif isinstance(effect, LinearProjectile):
            if effect.projectile_type == "Damage":
                pygame.draw.rect(screen, effect.color, (effect.x, effect.y, 10, 5))
            else:
                pygame.draw.ellipse(screen, effect.color, (int(effect.x), int(effect.y), 10, 5))

        # draw glitchy projectiles
        elif isinstance(effect, GlitchyDamageProjectile) or isinstance(effect, GlitchyHealProjectile):
            pygame.draw.rect(screen, effect.color, (effect.x + effect.shake_x, effect.y + effect.shake_y, 10, 10))
        elif isinstance(effect, GlitchyBlockProjectile):
            pygame.draw.rect(screen, effect.color, (effect.x + effect.shake_x, effect.y + effect.shake_y, 10, 10), 2)
        
        # draw arc projectiles
        else:
            pygame.draw.circle(screen, effect.color, (int(effect.x), int(effect.y)), 5)

def draw_screen(screen, regular_font, floating_font, font_cache, player_bots, enemy_goons, active_effects, battle_state, active_bot, chosen_action, inspecting_character, scroll_y, gears, rounds):
    # background color
    screen.fill((0, 0, 0))

    # draw bots and goons with animations based on their states and actions
    draw_characters(screen, regular_font, player_bots, enemy_goons, active_bot, chosen_action, inspecting_character)

    # draw bots and goons status effects
    draw_character_status_effects(screen, regular_font, player_bots, enemy_goons, battle_state)

    # draw action options based on active bot and chosen action
    draw_action_box(screen, font_cache, battle_state, active_bot, chosen_action)

    # draw shop box in the middle
    draw_shop_box(screen, regular_font, font_cache, battle_state, active_bot, gears, rounds)

    # draw shop menu if opened
    draw_shop_menu(screen, font_cache, battle_state, gears)

    # draw lore box with scrolling
    lore_height = draw_lore_box(screen, regular_font, battle_state, inspecting_character, scroll_y, rounds)

    # draw laser beam if lazer bot is using its pierce
    draw_laser(screen, enemy_goons, battle_state, active_bot)
    
    # draw effects damage or heal numbers or projectiles
    draw_effects(screen, floating_font, active_effects)

    # temp box
    if active_bot:
        temp_box_color = active_bot.box_background_color
    else:
        temp_box_color = (50, 50, 50)
    pygame.draw.rect(screen, temp_box_color, (20, 620, 60, 90))
    pygame.draw.rect(screen, (255, 255, 255), (20, 620, 60, 90), 3)

    return lore_height

def draw_main_menu(screen, title_font, regular_font, font_cache):
    # draw main menu background
    screen.fill((10, 10, 25))

    # draw title text
    welcome_text = regular_font.render("Welcome to", True, (255, 255, 255))
    welcome_text_rect = welcome_text.get_rect(center=(600, 160))
    screen.blit(welcome_text, welcome_text_rect)
    title_text = title_font.render("Rounds", True, (255, 255, 255))
    title_text_rect = title_text.get_rect(center=(600, 200))
    screen.blit(title_text, title_text_rect)

    # button rectangles
    story_button_rect = pygame.Rect(500, 335, 200, 80)
    endless_button_rect = pygame.Rect(500, 500, 200, 80)

    # change button color based on hover
    mouse_pos = pygame.mouse.get_pos()
    if endless_button_rect.collidepoint(mouse_pos):
        button_color = (150, 150, 255)
    else:
        button_color = (100, 100, 255)

    # draw story mode button
    pygame.draw.rect(screen, (100, 100, 100), story_button_rect)
    story_text_1 = dynamic_text(font_cache, "Story Mode", 180, 30, (255, 255, 255))
    story_text_2 = dynamic_text(font_cache, "(Coming Soon!)", 180, 30, (255, 255, 255))
    story_text_rect_1 = story_text_1.get_rect(center=(600, 360))
    story_text_rect_2 = story_text_2.get_rect(center=(600, 390))
    screen.blit(story_text_1, story_text_rect_1)
    screen.blit(story_text_2, story_text_rect_2)

    # draw endless mode button
    pygame.draw.rect(screen, button_color, endless_button_rect)
    endless_text = dynamic_text(font_cache, "Endless Mode", 180, 80, (255, 255, 255))
    endless_text_rect = endless_text.get_rect(center=(600, 540))
    screen.blit(endless_text, endless_text_rect)


# ------------------------------
# MAIN
# ------------------------------

async def main():
    # screen settings
    screen = pygame.display.set_mode((1200, 730))
    # title
    pygame.display.set_caption("Rounds")
    # setup timer to control game speed
    clock = pygame.time.Clock()

    # setup fonts
    title_font = pygame.font.SysFont(None, 120)
    regular_font = pygame.font.SysFont(None, 24)
    floating_font = pygame.font.SysFont(None, 30)
    font_cache = {}
    for size in range(10, 31):
        font_cache[size] = pygame.font.SysFont(None, size)

    # slots for enemies to spawn in
    enemy_slots = [
        {"x": 600, "y": 0, "occupied": False}, # front, top
        {"x": 600, "y": 200, "occupied": False}, # front, middle
        {"x": 600, "y": 400, "occupied": False}, # front, bottom
        {"x": 800, "y": 0, "occupied": False}, # middle, top
        {"x": 800, "y": 200, "occupied": False}, # middle, middle
        {"x": 800, "y": 400, "occupied": False}, # middle, bottom
        {"x": 1000, "y": 0, "occupied": False}, # back, top
        {"x": 1000, "y": 200, "occupied": False}, # back, middle
        {"x": 1000, "y": 400, "occupied": False} # back, bottom
    ]

    # inital list of characters and effects
    # gun_bot, rico_bot, elemental_bot, lazer_bot, chaos_bot, duplo_bot, mod_bot
    player_bots = [gun_bot, rico_bot, elemental_bot, lazer_bot, chaos_bot, duplo_bot, mod_bot]
    enemy_goons = []
    active_effects = []

    # inital game state variables
    game_state = "Main Menu"
    previous_game_state = "Main Menu"
    battle_state = "Player Turn"
    previous_battle_state = "Player Turn"

    # inital variables for player turn
    active_bot = None
    chosen_action = None

    # inital variables related to lore box
    inspecting_character = None
    lore_height = 0
    scroll_y = 0.0
    target_scroll_y = 0.0

    # inital variables for game progression
    gears = 0
    rounds = 1
    max_enemies = 3
    running = True

    # load initial character images
    for char in player_bots:
        char.load_images()
    for enemy, stats in enemy_catalog.items():
        stats["idle_image"] = pygame.image.load(stats["idle_image_path"]).convert_alpha()
        stats["hurt_image"] = pygame.image.load(stats["hurt_image_path"]).convert_alpha()
        stats["dead_image"] = pygame.image.load(stats["dead_image_path"]).convert_alpha()

    while running:

        # handle input events based on game state and battle state
        running, game_state, battle_state, previous_battle_state, active_bot, chosen_action, inspecting_character, scroll_y, target_scroll_y, gears = handle_input(
            running, player_bots, enemy_goons, active_effects, game_state, battle_state, previous_battle_state, active_bot, chosen_action, inspecting_character, lore_height, scroll_y, target_scroll_y, gears, enemy_slots)

        if game_state == "Endless Mode" and previous_game_state != "Endless Mode":
            # setup for the first round of endless mode
            spawn_inital_enemies(enemy_goons, enemy_slots)
            previous_game_state = "Endless Mode"

        if game_state == "Main Menu":
            # screen for main menu
            draw_main_menu(screen, title_font, regular_font, font_cache)

        elif game_state == "Endless Mode":
            # enemy turn logic
            battle_state, gears, rounds, max_enemies = enemy_turn(player_bots, enemy_goons, active_effects, battle_state, gears, rounds, max_enemies, enemy_slots)

            # check if game is over
            battle_state, scroll_y, target_scroll_y = check_game_over(player_bots, battle_state, scroll_y, target_scroll_y)

            # update animations
            scroll_y = update_animations(player_bots, enemy_goons, active_effects, battle_state, active_bot, scroll_y, target_scroll_y)

            # drawing, animation, and rendering
            lore_height = draw_screen(
                screen, regular_font, floating_font, font_cache, player_bots, enemy_goons, active_effects, battle_state, active_bot, chosen_action, inspecting_character, scroll_y, gears, rounds)

        # keeps the game from flickering
        pygame.display.flip()
        # makes the game run at 60 frames per second
        clock.tick(60)
        # prevents freezing in the web
        await asyncio.sleep(0)
    
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())