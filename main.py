import asyncio
import random
import pygame
import math

# initialize pygame and font module
pygame.init()
pygame.font.init()


# ------------------------------
# ANIMATIONS
# ------------------------------

class Animation:
    def __init__(self, color, x, y):
        # basic animation info
        self.color = color
        self.x = x
        self.y = y
        self.active = True

class FloatingText(Animation):
    def __init__(self, color, x, y, text):
        super().__init__(color, x, y)
        # floating text specific info
        self.text = text
        self.timer = 120
    
    def update(self):
        # move text up and decrease timer, disappear when timer runs out
        self.y -= 1
        self.timer -= 1
        if self.timer <= 0:
            self.active = False

class Projectile(Animation):
    def __init__(self, color, x, y, target_x, target_y, target_char):
        super().__init__(color, x, y)
        # projectile specific info
        self.target_x = target_x
        self.target_y = target_y
        self.target_char = target_char
        self.distance_x = target_x - x
        self.distance_y = target_y - y

class DamageProjectile(Projectile):
    def __init__(self, color, x, y, target_x, target_y, target_char, damage):
        super().__init__(color, x, y, target_x, target_y, target_char)
        # damage projectile specific info
        self.damage = damage
        self.frames = 100
        self.speed_x = self.distance_x / self.frames
        self.speed_y = self.distance_y / self.frames
    
    def update(self, active_effects):
        # move projectile towards target and damage when it reaches
        self.x += self.speed_x
        self.y += self.speed_y
        if (self.speed_x > 0 and self.x >= self.target_x) or (self.speed_x < 0 and self.x <= self.target_x):
            self.target_char.take_damage(active_effects, self.damage)
            self.active = False

class HealProjectile(Projectile):
    def __init__(self, color, x, y, target_x, target_y, target_char, heal):
        super().__init__(color, x, y, target_x, target_y, target_char)
        # heal projectile specific info
        self.heal = heal
        self.frames = 80
        self.current_frame = 0
        self.arc = 150
        self.start_x = x
        self.start_y = y
    
    def update(self, active_effects):
        # move projectile in an arc towards target and heal when it reaches
        self.current_frame += 1
        if self.current_frame >= self.frames:
            self.target_char.take_heal(active_effects, self.heal)
            self.active = False
        else:
            progress = self.current_frame / self.frames
            base_x = self.start_x + self.distance_x * progress
            base_y = self.start_y + self.distance_y * progress
            curve_y = math.sin(progress * math.pi) * self.arc
            if self.distance_x == 0 and self.distance_y == 0:
                max_x = math.sin(progress * math.pi) * (self.arc*0.5)
                curve_x = math.sin((progress**2) * math.pi) * (self.arc*0.5)
                self.x = base_x + (max_x + (max_x - curve_x))
                self.y = base_y - curve_y
            else:
                self.x = base_x + curve_y
                self.y = base_y - curve_y


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

        # animation
        self.animation_timer = 0
        self.animation_speed = 15
        self.hurt_timer = 0
        self.shake_x = 0  

    def take_damage(self, active_effects, amount):
        # reduce health and start hurt animation
        self.visual_health -= amount
        if self.visual_health < 0:
            self.visual_health = 0
        if self.real_health < 0:
            self.real_health = 0
        self.hurt_timer = 30

        # text animation
        text_x = random.randint(self.rect.left, self.rect.right - 30)
        text_y = self.rect.top + 10
        active_effects.append(FloatingText((255, 0, 0), text_x, text_y, f"-{amount}"))

    def take_heal(self, active_effects, amount):
        # increase health
        self.visual_health += amount

        # text animation
        text_x = random.randint(self.rect.left, self.rect.right - 30)
        text_y = self.rect.top + 10
        active_effects.append(FloatingText((0, 255, 0), text_x, text_y, f"+{amount}"))

    def hurt_animations(self):
        # shake character when hurt
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
            self.shake_x = random.randint(-5, 5)
        else:
            self.shake_x = 0

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

class GunBot(Bot):
    def __init__(self, name, health, x, y, box_background_color, description, idle_images_path, active_image_path, hurt_image_path, dead_image_path, button_color, button_hover_color, text_used_color):
        super().__init__(name, health, x, y, box_background_color, description, idle_images_path, active_image_path, hurt_image_path, dead_image_path, button_color, button_hover_color, text_used_color)

        self.actions = [
            {
                "name": "Left Gun",
                "type": "Damage",
                "power": 1,
                "used": False,
                "target_state": "Damage Enemy",
                "image_path": "assets/bots/gun_bot/gun_bot_left_gun.png",
                "image": None,
                "description": "A basic attack that deals damage to a single enemy.",
                "scroll": 65
            },
            {
                "name": "Right Gun",
                "type": "Damage",
                "power": 1,
                "used": False,
                "target_state": "Damage Enemy",
                "image_path": "assets/bots/gun_bot/gun_bot_right_gun.png",
                "image": None,
                "description": "A basic attack that deals damage to a single enemy.",
                "scroll": 155
            }
        ]

class HybridBot(Bot):
    def __init__(self, name, health, x, y, box_background_color, description, idle_images_path, active_image_path, hurt_image_path, dead_image_path, button_color, button_hover_color, text_used_color):
        super().__init__(name, health, x, y, box_background_color, description, idle_images_path, active_image_path, hurt_image_path, dead_image_path, button_color, button_hover_color, text_used_color)

        self.actions = [
            {
                "name": "Attack",
                "type": "Damage",
                "power": 1,
                "used": False,
                "target_state": "Damage Enemy",
                "image_path": "assets/bots/hybrid_bot/hybrid_bot_hybrid_gun.png",
                "image": None,
                "description": "A basic attack that deals damage to a single enemy.",
                "scroll": 65
            },
            {
                "name": "Heal",
                "type": "Heal",
                "power": 2,
                "used": False,
                "target_state": "Heal Friendly",
                "image_path": "assets/bots/hybrid_bot/hybrid_bot_heal.png",
                "image": None,
                "description": "A basic healing ability that heals to a friendly bot.",
                "scroll": 155
            }
        ]

gun_bot = GunBot(
    "Gun Bot", # name
    10, # health
    150, 150, # x, y
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

hybrid_bot = HybridBot(
    "Hybrid Bot", # name
    10, # health
    150, 300, # x, y
    (50, 200, 50), # box_background_color
    "A versatile bot that can attack and heal.", # description
    [
        "assets/bots/hybrid_bot/hybrid_bot_idle_1.png",
        "assets/bots/hybrid_bot/hybrid_bot_idle_2.png",
        "assets/bots/hybrid_bot/hybrid_bot_idle_3.png",
        "assets/bots/hybrid_bot/hybrid_bot_idle_4.png",
        "assets/bots/hybrid_bot/hybrid_bot_idle_3.png",
        "assets/bots/hybrid_bot/hybrid_bot_idle_2.png"
    ], # idle_images_path
    "assets/bots/hybrid_bot/hybrid_bot_active.png", # active_image_path
    "assets/bots/hybrid_bot/hybrid_bot_hurt.png", # hurt_image_path
    "assets/bots/hybrid_bot/hybrid_bot_dead.png", # dead_image_path
    (100, 230, 100), # button_color
    (150, 250, 150), # button_hover_color
    (150, 250, 150) # text_used_color
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
    lore_rect = pygame.Rect(600, 620, 560, 90)

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
    shop_button_rect = pygame.Rect(450, 640, 100, 50)

    # open shop if button is clicked and close shop if button is clicked again
    if shop_button_rect.collidepoint(mouse_pos):
        if battle_state == "Shop":
            battle_state = previous_battle_state
        else:
            previous_battle_state = battle_state
            battle_state = "Shop"
    return battle_state, previous_battle_state

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
            return gears
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
            return inspecting_character, scroll_y, target_scroll_y
    return inspecting_character, scroll_y, target_scroll_y

def select_bot(mouse_pos, player_bots, battle_state, active_bot, chosen_action, inspecting_character, scroll_y, target_scroll_y):
    for bot in player_bots:
        # bot is selected if it's clicked, alive, and hasn't acted yet
        if bot.rect.collidepoint(mouse_pos) and bot.real_health > 0 and not bot.acted:
            # bot is deselected if clicked again
            if active_bot == bot:
                inspecting_character = None
                active_bot = None
            else:
                inspecting_character = bot
                active_bot = bot
                target_scroll_y = 0
                scroll_y = 0
            chosen_action = None
            battle_state = "Select Action"
            return battle_state,  active_bot, chosen_action, inspecting_character, scroll_y, target_scroll_y
    return battle_state, active_bot, chosen_action, inspecting_character, scroll_y, target_scroll_y

def select_action(mouse_pos, battle_state, active_bot, chosen_action, inspecting_character, scroll_y, target_scroll_y):
    # action button rectangles
    left_button_rect = pygame.Rect(60, 640, 150, 50)
    right_button_rect = pygame.Rect(230, 640, 150, 50)

    # bot action is chosen based on which button is clicked and action is deselected if clicked again
    if active_bot:
        if left_button_rect.collidepoint(mouse_pos) and not active_bot.actions[0]["used"]:
            if chosen_action == active_bot.actions[0]["name"]:
                chosen_action = None
                battle_state = "Select Action"
            else:
                chosen_action = active_bot.actions[0]["name"]
                battle_state = active_bot.actions[0]["target_state"]
                target_scroll_y = active_bot.actions[0]["scroll"]
            
            # if enemy is being inspected, switch inspecting to active bot when action is chosen
            if inspecting_character != active_bot:
                target_scroll_y = active_bot.actions[0]["scroll"]
                scroll_y = active_bot.actions[0]["scroll"]
                inspecting_character = active_bot

        elif right_button_rect.collidepoint(mouse_pos) and not active_bot.actions[1]["used"]:
            if chosen_action == active_bot.actions[1]["name"]:
                chosen_action = None
                battle_state = "Select Action"
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

def check_bot_turn(player_bots):
    for bot in player_bots:
        if bot.real_health > 0 and not bot.acted:
            return "Select Bot"
    return "Enemy Turn"

def execute_action(mouse_pos, player_bots, characters, active_effects, battle_state, active_bot, chosen_action, inspecting_character,):
    for char in characters:
        if char.rect.collidepoint(mouse_pos) and char.real_health > 0:
            # determine the power of the chosen action and mark it as used
            power = 0
            for action in active_bot.actions:
                if action["name"] == chosen_action:
                    power = action["power"]
                    action["used"] = True
                    break
            
            # damage or heal the target character
            if battle_state == "Damage Enemy":
                char.real_health -= power
                active_effects.append(DamageProjectile((0, 0, 255), active_bot.rect.centerx, active_bot.rect.centery, char.rect.centerx, char.rect.centery, char, power))
            elif battle_state == "Heal Friendly":
                char.real_health += power
                active_effects.append(HealProjectile((0, 255, 0), active_bot.rect.centerx, active_bot.rect.centery, char.rect.centerx, char.rect.centery, char, power))
            
            # check if active bot used both actions and reset for next action
            active_bot.check_actions()
            inspecting_character = None
            active_bot = None
            chosen_action = None

            return check_bot_turn(player_bots), active_bot, chosen_action, inspecting_character
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

        if battle_state != "Shop":
            # harvest gears
            gears = harvest_gears(mouse_pos, enemy_goons, active_effects, gears, enemy_slots)

            # inspect enemy if not targeting enemy
            if battle_state != "Damage Enemy":
                inspecting_character, scroll_y, target_scroll_y = inspect_enemy(mouse_pos, enemy_goons, inspecting_character, scroll_y, target_scroll_y)

            # select bot if not healing friendly
            if battle_state != "Heal Friendly":
                battle_state, active_bot, chosen_action, inspecting_character, scroll_y, target_scroll_y = select_bot(mouse_pos, player_bots, battle_state, active_bot, chosen_action, inspecting_character, scroll_y, target_scroll_y)
            
            # select actions if bot is selected
            battle_state, chosen_action, inspecting_character, scroll_y, target_scroll_y = select_action(mouse_pos, battle_state, active_bot, chosen_action, inspecting_character, scroll_y, target_scroll_y)
                
            # carry out the chosen action
            if battle_state == "Damage Enemy":
                battle_state, active_bot, chosen_action, inspecting_character = execute_action(mouse_pos, player_bots, enemy_goons, active_effects, battle_state, active_bot, chosen_action, inspecting_character)
            elif battle_state == "Heal Friendly":
                battle_state, active_bot, chosen_action, inspecting_character = execute_action(mouse_pos, player_bots, player_bots, active_effects, battle_state, active_bot, chosen_action, inspecting_character)

    # right click to close shop or cancel action or bot
    elif event.button == 3:
        if battle_state == "Shop":
            battle_state = previous_battle_state
        elif battle_state in ["Damage Enemy", "Heal Friendly"]:
            chosen_action = None
            battle_state = "Select Action"
        elif battle_state == "Select Action":
            inspecting_character = None
            active_bot = None
            battle_state = "Select Bot"
        elif battle_state == "Select Bot":
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

    return running, game_state, battle_state, previous_battle_state, active_bot, chosen_action, inspecting_character, scroll_y, target_scroll_y, gears


# ------------------------------
# ENEMY TURN
# ------------------------------

def enemy_attacks(enemy_goons, player_bots, active_effects):
    # each alive enemy attacks a random alive bot
    for enemy in enemy_goons:
        if enemy.real_health > 0:
            bots_alive = []
            for bot in player_bots:
                if bot.real_health > 0:
                    bots_alive.append(bot)
            
            if bots_alive:
                target = random.choice(bots_alive)
                target.real_health -= enemy.damage
                active_effects.append(DamageProjectile((255, 0, 0), enemy.rect.x, enemy.rect.y, target.rect.centerx, target.rect.centery, target, enemy.damage))

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

def spawn_state(enemy_goons, active_effects, gears, round, max_enemies, enemy_slots):
    # determine how many enemies to spawn based on the round
    spawns = 0
    if round == 3:
        spawns = 1
    elif round >= 5 and round <= 10:
        spawns = 1
    elif round > 10:
        spawns = 2
    
    # increase the max number of enemies every 5 rounds, up to a maximum of 9
    if max_enemies <= 9 and round % 5 == 0:
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

def enemy_turn(player_bots, enemy_goons, active_effects, battle_state, gears, round, max_enemies, enemy_slots):
    if battle_state == "Enemy Turn":
        # enemy attack logic
        enemy_attacks(enemy_goons, player_bots, active_effects)
        
        # resets for next turn
        for bot in player_bots:
            bot.reset_actions()
        battle_state = "Select Bot"
        round += 1

        # spawn new enemies based on the round and max enemies
        gears, max_enemies = spawn_state(enemy_goons, active_effects, gears, round, max_enemies, enemy_slots)
    
    return battle_state, gears, round, max_enemies


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
        return "Game Over", scroll_y, target_scroll_y
    
    return battle_state, scroll_y, target_scroll_y


# ------------------------------
# DRAWING, ANIMATION, AND RENDERING
# ------------------------------

def update_animations(player_bots, enemy_goons, active_effects, scroll_y, target_scroll_y):
    # update characters shake when they are hurt
    for char in player_bots + enemy_goons:
        char.hurt_animations()

    # update idle animation frames
    for char in player_bots + enemy_goons:
        char.update_idle_animation()

    # update and remove effects
    for effect in active_effects[:]:
        if isinstance(effect, DamageProjectile) or isinstance(effect, HealProjectile):
            effect.update(active_effects)
        elif isinstance(effect, FloatingText):
            effect.update()
        if not effect.active:
            active_effects.remove(effect)
    
    # update scrolling position for lore box
    scroll_y += (target_scroll_y - scroll_y) * 0.2
    if abs(target_scroll_y - scroll_y) < 0.1:
        scroll_y = target_scroll_y
    return scroll_y

def draw_characters(screen, regular_font, player_bots, enemy_goons, battle_state, active_bot, chosen_action, inspecting_character):
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
        if char in enemy_goons:
            char_y += char.float_offset

        # draw character image
        screen.blit(current_image, (char.rect.x + char.shake_x, char_y))

        # highlight character if hovering and valid target
        mouse_pos = pygame.mouse.get_pos()
        if char.rect.collidepoint(mouse_pos) and char.real_health > 0:
            if char in enemy_goons and battle_state == "Damage Enemy":
                pygame.draw.rect(screen, (255, 0, 0), char.rect, 3)
            elif char in player_bots and battle_state == "Heal Friendly":
                pygame.draw.rect(screen, (0, 255, 0), char.rect, 3)
            elif char in player_bots and battle_state not in ["Game Over", "Shop"] and not char.acted:
                pygame.draw.rect(screen, (0, 0, 255), char.rect, 3)

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
    if battle_state != "Shop":
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

def draw_action_options(screen, font_cache, battle_state, active_bot, chosen_action):
    # draw action box background
    if active_bot:
        color = active_bot.box_background_color
    else:
        color = (50, 50, 50)
    pygame.draw.rect(screen, color, (40, 620, 360, 90))
    pygame.draw.rect(screen, (255, 255, 255), (40, 620, 360, 90), 3)

    # draw action buttons based on active bot
    if active_bot:
        for index, action in enumerate(active_bot.actions):
            if index == 0:
                x = 60
            else:
                x = 230
            draw_action_button(screen, font_cache, battle_state, active_bot, x, 640, action["name"], action["used"], chosen_action == action["name"])

def draw_shop_box(screen, regular_font, font_cache, battle_state, active_bot, gears, round):
    # draw shop box background
    if active_bot:
        box_color = active_bot.box_background_color
    else:
        box_color = (50, 50, 50)
    pygame.draw.rect(screen, box_color, (430, 620, 140, 90))
    pygame.draw.rect(screen, (255, 255, 255), (430, 620, 140, 90), 3)

    # draw shop button with hover effect
    button_rect = pygame.Rect(450, 640, 100, 50)
    mouse_pos = pygame.mouse.get_pos()
    if button_rect.collidepoint(mouse_pos) and battle_state == "Shop":
        button_color = (255, 125, 125)
    elif active_bot:
        if button_rect.collidepoint(mouse_pos):
            button_color = active_bot.button_hover_color
        else:
            button_color = active_bot.button_color
    else:
        if button_rect.collidepoint(mouse_pos) and battle_state != "Game Over":
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
    shop_text_rect = shop_text.get_rect(center=(500, 665))
    screen.blit(shop_text, shop_text_rect)

    # draw info box background
    pygame.draw.rect(screen, box_color, (430, 563, 140, 60))
    pygame.draw.rect(screen, (255, 255, 255), (430, 563, 140, 60), 3)

    # draw round and gears text
    round_text = regular_font.render(f"Round: {round}", True, (255, 255, 255))
    gears_text = regular_font.render(f"Gears: {gears}", True, (255, 255, 255))
    round_text_rect = round_text.get_rect(center=(500, 583))
    gears_text_rect = gears_text.get_rect(center=(500, 603))
    screen.blit(round_text, round_text_rect)
    screen.blit(gears_text, gears_text_rect)

def draw_shop_menu(screen, battle_state, active_bot):
    if battle_state == "Shop":
        # draw shop menu background
        if active_bot:
            box_color = active_bot.box_background_color
        else:
            box_color = (50, 50, 50)
        pygame.draw.rect(screen, box_color, (80, 80, 1040, 486))
        pygame.draw.rect(screen, (255, 255, 255), (80, 80, 1040, 486), 3)

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

def draw_lore_box(screen, regular_font, player_bots, enemy_goons, battle_state, inspecting_character, scroll_y, round):
    # draw lore box background
    if inspecting_character:
        color = inspecting_character.box_background_color
    else:
        color = (50, 50, 50)
    pygame.draw.rect(screen, color, (600, 620, 560, 90))
    pygame.draw.rect(screen, (255, 255, 255), (600, 620, 560, 90), 3)

    lore = []
    # lore text based on battle state
    if battle_state == "Game Over":
        lore.append(("The enemies have defeated all your bots!", "header"))
        lore.append((f"You have survived for a total of {round} rounds.", "header"))
        lore.append(("Game Over!", "header"))

    # lore text based on inspecting character
    elif inspecting_character:
        lore.append((f"Name: {inspecting_character.name}", "header"))
        description_lines = wrap_text(f"Description: {inspecting_character.description}", regular_font, 540)
        for i, line in enumerate(description_lines):
            if i == len(description_lines) - 1:
                lore.append((line, "header"))
            else:
                lore.append((line, "body"))
        if inspecting_character in player_bots:
            for action in inspecting_character.actions:
                lore.append((f"Action: {action['name']}", "header"))
                action_description_lines = wrap_text(f"Description: {action['description']}", regular_font, 540)
                for i, line in enumerate(action_description_lines):
                    if i == len(action_description_lines) - 1:
                        lore.append((line, "header"))
                    else:
                        lore.append((line, "body"))
                lore.append((f"{action['type']}: {action['power']}", "header"))
        elif inspecting_character in enemy_goons:
            lore.append((f"Damage: {inspecting_character.damage}", "header"))

    # calculate lore height
    lore_height = 0
    for line, type in lore:
        if line.startswith("Action:"):
            lore_height += 15
        if type == "header":
            lore_height += 25
        elif type == "body":
            lore_height += 20

    # create a surface for the lore text with see through background
    lore_canvas = pygame.Surface((560, max(1, lore_height)), pygame.SRCALPHA)

    # draw lore text into the lore canvas
    y_offset = 5
    for line, type in lore:
        if line.startswith("Action:"):
            y_offset += 15
        lore_text = regular_font.render(line, True, (255, 255, 255))
        lore_canvas.blit(lore_text, (0, y_offset))
        if type == "header":
            y_offset += 25
        elif type == "body":
            y_offset += 20

    # draw the visible part of lore canvas onto the screen based on scroll position
    visible_rect = pygame.Rect(0, int(scroll_y), 540, 80)
    screen.blit(lore_canvas, (610, 625), visible_rect)
    
    # update lore height for scrolling calculations
    lore_height = y_offset

    return lore_height

def draw_effects(screen, floating_font, active_effects):
    # draw animation based on its type
    for effect in active_effects:
        # draw floating text
        if isinstance(effect, FloatingText):
            text = floating_font.render(effect.text, True, effect.color)
            screen.blit(text, (effect.x, effect.y))
        # draw damage projectile
        elif isinstance(effect, DamageProjectile):
            pygame.draw.rect(screen, effect.color, (effect.x, effect.y, 10, 5))
        # draw heal projectile
        elif isinstance(effect, HealProjectile):
            pygame.draw.circle(screen, effect.color, (int(effect.x), int(effect.y)), 5)

def draw_screen(screen, regular_font, floating_font, font_cache, player_bots, enemy_goons, active_effects, battle_state, active_bot, chosen_action, inspecting_character, scroll_y, gears, round):
    # background color
    screen.fill((0, 0, 0))

    # draw bots and goons with animations based on their states and actions
    draw_characters(screen, regular_font, player_bots, enemy_goons, battle_state, active_bot, chosen_action, inspecting_character)

    # draw action options based on active bot and chosen action
    draw_action_options(screen, font_cache, battle_state, active_bot, chosen_action)

    # draw shop box in the middle
    draw_shop_box(screen, regular_font, font_cache, battle_state, active_bot, gears, round)

    # draw shop meny if opened
    draw_shop_menu(screen, battle_state, active_bot)

    # draw lore box with scrolling
    lore_height = draw_lore_box(screen, regular_font, player_bots, enemy_goons, battle_state, inspecting_character, scroll_y, round)
    
    # draw effects damage or heal numbers or projectiles
    draw_effects(screen, floating_font, active_effects)

    return lore_height


# ------------------------------
# MAIN MENU
# ------------------------------

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
    screen = pygame.display.set_mode((1200, 750))
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
    player_bots = [gun_bot, hybrid_bot]
    enemy_goons = []
    active_effects = []

    # inital game state variables
    game_state = "Main Menu"
    previous_game_state = "Main Menu"
    battle_state = "Select Bot"
    previous_battle_state = "Select Bot"

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
    round = 1
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
            battle_state, gears, round, max_enemies = enemy_turn(player_bots, enemy_goons, active_effects, battle_state, gears, round, max_enemies, enemy_slots)

            # check if game is over
            battle_state, scroll_y, target_scroll_y = check_game_over(player_bots, battle_state, scroll_y, target_scroll_y)

            # update animations
            scroll_y = update_animations(player_bots, enemy_goons, active_effects, scroll_y, target_scroll_y)

            # drawing, animation, and rendering
            lore_height = draw_screen(
                screen, regular_font, floating_font, font_cache, player_bots, enemy_goons, active_effects, battle_state, active_bot, chosen_action, inspecting_character, scroll_y, gears, round)

        # keeps the game from flickering
        pygame.display.flip()
        # makes the game run at 60 frames per second
        clock.tick(60)
        # prevents freezing in the web
        await asyncio.sleep(0)
    
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())