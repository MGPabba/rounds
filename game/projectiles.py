import math
import random

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

# ------------------------------
# PROJECTILE CLASSES FOR GUN BOT AND ELEMENTAL BOT
# ------------------------------

class LinearProjectile(Projectile):
    def __init__(self, color, source_char, target_char, projectile_offset, amount, reduction, projectile_type):
        super().__init__(color, source_char, target_char, projectile_offset, amount)
        # linear projectile specific info
        self.reduction = reduction
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
                self.target_char.take_damage(active_effects, self.amount, self.reduction)
            elif self.projectile_type == "Fire":
                self.target_char.apply_fire(active_effects, self.amount)
            elif self.projectile_type == "Ice":
                self.target_char.apply_ice(active_effects, self.amount)
            elif self.projectile_type == "Mark":
                self.target_char.apply_mark(active_effects, self.amount)

# ------------------------------
# PROJECTILE CLASSES FOR DUPLO BOT
# ------------------------------

class ChargeProjectile(LinearProjectile):
    def __init__(self, color, source_char, target_char, projectile_offset, amount, reduction, projectile_type, max_radius):
        super().__init__(color, source_char, target_char, projectile_offset, amount, reduction, projectile_type)
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
    def __init__(self, color, source_char, target_char, projectile_offset, amount, reduction, projectile_type):
        super().__init__(color, source_char, target_char, projectile_offset, amount, reduction, projectile_type)
        # mark projectile specific info
        self.angle = 0
        self.rotation_speed = 0.5
    
    def update(self, active_effects):
        super().update(active_effects)
        # rotate projectile as it moves towards target
        self.angle -= self.rotation_speed

# ------------------------------
# PROJECTILE CLASSES FOR MOD BOT
# ------------------------------

class PercentageProjectile(LinearProjectile):
    def __init__(self, color, source_char, target_char, projectile_offset, amount, reduction, projectile_type):
        super().__init__(color, source_char, target_char, projectile_offset, amount, reduction, projectile_type)
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

# ------------------------------
# PROJECTILE CLASSES FOR RICO BOT
# ------------------------------

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
            damage, reduction = self.target_char.damage_amount(self.amount)
            self.target_char.take_damage(active_effects, damage, reduction)
            self.active = False
            self.enemies_hit.append(self.target_char)
            if self.bounce_amount > 0:
                valid_targets = []
                for enemy in enemy_goons:
                    if enemy.real_health > 0 and enemy not in self.enemies_hit:
                        valid_targets.append(enemy)
                if valid_targets:
                    next_target = random.choice(valid_targets)
                    damage, reduction = next_target.damage_amount(self.amount)
                    next_target.real_health -= damage
                    active_effects.append(BounceProjectile(self.color, self.target_char, next_target, (0, 0), self.amount, self.bounce_amount - 1, self.enemies_hit))

# ------------------------------
# PROJECTILE CLASSES FOR CHAOS BOT
# ------------------------------

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
    def __init__(self, color, source_char, target_char, projectile_offset, amount, reduction):
        super().__init__(color, source_char, target_char, projectile_offset, amount)
        # glitchy damage projectile specific info
        self.reduction = reduction
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
            self.target_char.take_damage(active_effects, self.amount, self.reduction)

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
# PROJECTILE CLASSES FOR LAZER BOT
# ------------------------------

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
