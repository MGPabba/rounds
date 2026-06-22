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
        self.color = color
        self.x = x
        self.y = y
        self.active = True

class FloatingText(Animation):
    def __init__(self, color, x, y, text):
        super().__init__(color, x, y)
        self.text = text
        self.timer = 120
    
    def update(self):
        self.y -= 1
        self.timer -= 1
        if self.timer <= 0:
            self.active = False

class Projectile(Animation):
    def __init__(self, color, x, y, target_x, target_y, target_char):
        super().__init__(color, x, y)
        self.target_x = target_x
        self.target_y = target_y
        self.target_char = target_char
        self.distance_x = target_x - x
        self.distance_y = target_y - y

class DamageProjectile(Projectile):
    def __init__(self, color, x, y, target_x, target_y, target_char, damage):
        super().__init__(color, x, y, target_x, target_y, target_char)
        self.damage = damage
        self.frames = 100
        self.speed_x = self.distance_x / self.frames
        self.speed_y = self.distance_y / self.frames
    
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if (self.speed_x > 0 and self.x >= self.target_x) or (self.speed_x < 0 and self.x <= self.target_x):
            self.target_char.take_damage(self.damage)
            self.active = False

class HealProjectile(Projectile):
    def __init__(self, color, x, y, target_x, target_y, target_char, heal):
        super().__init__(color, x, y, target_x, target_y, target_char)
        self.heal = heal
        self.frames = 80
        self.current_frame = 0
        self.arc = 150
        self.start_x = x
        self.start_y = y
    
    def update(self):
        self.current_frame += 1
        if self.current_frame >= self.frames:
            self.target_char.take_heal(self.heal)
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

active_effects = []


# ------------------------------
# CHARACTERS
# ------------------------------

class Character:
    def __init__(self, name, health, damage, x, y, w, h, idle_images_path, hurt_image_path, dead_image_path):
        self.name = name
        self.health = health
        self.ghost_health = health
        self.damage = damage
        self.rect = pygame.Rect(x, y, w, h)
        self.acted = False

        # images
        self.idle_images_path = idle_images_path
        self.hurt_image_path = hurt_image_path
        self.dead_image_path = dead_image_path
        self.idle_images = []
        self.hurt_image = None
        self.dead_image = None

        # animation
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 15
        self.hurt_timer = 0
        self.shake_x = 0

    def load_images(self):
        for path in self.idle_images_path:
            self.idle_images.append(pygame.image.load(path).convert_alpha())
        self.hurt_image = pygame.image.load(self.hurt_image_path).convert_alpha()
        self.dead_image = pygame.image.load(self.dead_image_path).convert_alpha()

        # randomize starting idle frame and animation timer
        self.current_frame = random.randint(0, len(self.idle_images) - 1)
        self.animation_timer = random.randint(0, self.animation_speed)

    def update_idle_animation(self):
        if self.health > 0:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.idle_images)

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
        
        self.hurt_timer = 30

        # text animation
        text_x = random.randint(self.rect.left, self.rect.right - 30)
        text_y = self.rect.top + 10
        active_effects.append(FloatingText((255, 0, 0), text_x, text_y, f"-{amount}"))

    def take_heal(self, amount):
        self.health += amount

        # text animation
        text_x = random.randint(self.rect.left, self.rect.right - 30)
        text_y = self.rect.top + 10
        active_effects.append(FloatingText((0, 255, 0), text_x, text_y, f"+{amount}"))

    def hurt_animations(self):
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
            self.shake_x = random.randint(-5, 5)
        else:
            self.shake_x = 0

class GunBot(Character):
    def __init__(self, name, health, damage, x, y, w, h, idle_images_path, hurt_image_path, dead_image_path, active_image_path, left_gun_chosen_image_path, right_gun_chosen_image_path):
        super().__init__(name, health, damage, x, y, w, h, idle_images_path, hurt_image_path, dead_image_path)

        # colors
        self.action_background_color = (50, 100, 255)
        self.button_color = (100, 150, 255)
        self.used_text_color = (150, 200, 255)

        #images
        self.active_image_path = active_image_path
        self.left_gun_chosen_image_path = left_gun_chosen_image_path
        self.right_gun_chosen_image_path = right_gun_chosen_image_path
        self.active_image = None
        self.left_gun_chosen_image = None
        self.right_gun_chosen_image = None

        # actions
        self.left_gun_used = False
        self.right_gun_used = False
    
    def load_images(self):
        super().load_images()
        self.active_image = pygame.image.load(self.active_image_path).convert_alpha()
        self.left_gun_chosen_image = pygame.image.load(self.left_gun_chosen_image_path).convert_alpha()
        self.right_gun_chosen_image = pygame.image.load(self.right_gun_chosen_image_path).convert_alpha()

    def check_actions(self):
        if self.left_gun_used and self.right_gun_used:
            self.acted = True
    
    def reset_actions(self):
        self.acted = False
        self.left_gun_used = False
        self.right_gun_used = False

class HybridBot(Character):
    def __init__(self, name, health, damage, heal, x, y, w, h, idle_images_path, hurt_image_path, dead_image_path, active_image_path, hybrid_gun_chosen_image_path, heal_chosen_image_path):
        super().__init__(name, health, damage, x, y, w, h, idle_images_path, hurt_image_path, dead_image_path)
        self.heal = heal

        # colors
        self.action_background_color = (50, 200, 50)
        self.button_color = (100, 230, 100)
        self.used_text_color = (150, 250, 150)

        # images
        self.active_image_path = active_image_path
        self.hybrid_gun_chosen_image_path = hybrid_gun_chosen_image_path
        self.heal_chosen_image_path = heal_chosen_image_path
        self.active_image = None
        self.hybrid_gun_chosen_image = None
        self.heal_chosen_image = None

        # actions
        self.hybrid_gun_used = False
        self.heal_used = False
    
    def load_images(self):
        super().load_images()
        self.active_image = pygame.image.load(self.active_image_path).convert_alpha()
        self.hybrid_gun_chosen_image = pygame.image.load(self.hybrid_gun_chosen_image_path).convert_alpha()
        self.heal_chosen_image = pygame.image.load(self.heal_chosen_image_path).convert_alpha()

    def check_actions(self):
        if self.hybrid_gun_used and self.heal_used:
            self.acted = True
    
    def reset_actions(self):
        self.acted = False
        self.hybrid_gun_used = False
        self.heal_used = False

gun_bot = GunBot(
    "Gun Bot", # name
    10, # health
    1, # damage
    150, 150, # x, y
    100, 100, # w, h
    [
        "assets/gun_bot/gun_bot_idle_1.png",
        "assets/gun_bot/gun_bot_idle_2.png",
        "assets/gun_bot/gun_bot_idle_3.png",
        "assets/gun_bot/gun_bot_idle_4.png",
        "assets/gun_bot/gun_bot_idle_3.png",
        "assets/gun_bot/gun_bot_idle_2.png"
    ], # idle_images_path
    "assets/gun_bot/gun_bot_hurt.png", # hurt_image_path
    "assets/gun_bot/gun_bot_dead.png", # dead_image_path
    "assets/gun_bot/gun_bot_active.png", # active_image_path
    "assets/gun_bot/gun_bot_left_gun.png", # left_gun_chosen_image_path
    "assets/gun_bot/gun_bot_right_gun.png" # right_gun_chosen_image_path
)

hybrid_bot = HybridBot(
    "Hybrid Bot", # name
    10, # health
    1, # damage
    2, # heal
    150, 300, # x, y
    100, 100, # w, h
    [
        "assets/hybrid_bot/hybrid_bot_idle_1.png",
        "assets/hybrid_bot/hybrid_bot_idle_2.png",
        "assets/hybrid_bot/hybrid_bot_idle_3.png",
        "assets/hybrid_bot/hybrid_bot_idle_4.png",
        "assets/hybrid_bot/hybrid_bot_idle_3.png",
        "assets/hybrid_bot/hybrid_bot_idle_2.png"
    ], # idle_images_path
    "assets/hybrid_bot/hybrid_bot_hurt.png", # hurt_image_path
    "assets/hybrid_bot/hybrid_bot_dead.png", # dead_image_path
    "assets/hybrid_bot/hybrid_bot_active.png", # active_image_path
    "assets/hybrid_bot/hybrid_bot_hybrid_gun.png", # hybrid_gun_chosen_image_path
    "assets/hybrid_bot/hybrid_bot_heal.png" # heal_chosen_image_path
)

player_bots = [gun_bot, hybrid_bot]

basic_goon_1 = Character(
    "Basic Goon", # name
    5, # health
    1, # damage
    950, 150, # x, y
    100, 100, # w, h
    [
        "assets/basic_goon/basic_goon_idle_1.png",
        "assets/basic_goon/basic_goon_idle_2.png",
        "assets/basic_goon/basic_goon_idle_3.png",
        "assets/basic_goon/basic_goon_idle_4.png",
        "assets/basic_goon/basic_goon_idle_3.png",
        "assets/basic_goon/basic_goon_idle_2.png"
    ], # idle_images_path
    "assets/basic_goon/basic_goon_hurt.png", # hurt_image_path
    "assets/basic_goon/basic_goon_dead.png" # dead_image_path
)

basic_goon_2 = Character(
    "Basic Goon", # name
    5, # health
    1, # damage
    950, 300, # x, y
    100, 100, # w, h
    [
        "assets/basic_goon/basic_goon_idle_1.png",
        "assets/basic_goon/basic_goon_idle_2.png",
        "assets/basic_goon/basic_goon_idle_3.png",
        "assets/basic_goon/basic_goon_idle_4.png",
        "assets/basic_goon/basic_goon_idle_3.png",
        "assets/basic_goon/basic_goon_idle_2.png"
    ], # idle_images_path
    "assets/basic_goon/basic_goon_hurt.png", # hurt_image_path
    "assets/basic_goon/basic_goon_dead.png" # dead_image_path
)

enemy_goons = [basic_goon_1, basic_goon_2]


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

def scroll_math(mouse_pos, event, battle_log, scroll_index):
    # battle log rectangle
    battle_log_rect = pygame.Rect(360, 615, 790, 85)

    # scroll through the battle log if mouse is scrolled over it
    if battle_log_rect.collidepoint(mouse_pos):
        # scroll up
        if event.button == 4:
            if scroll_index < len(battle_log) - 3:
                scroll_index += 1
        # scroll down
        elif event.button == 5:
            if scroll_index > 0:
                scroll_index -= 1
    
    return scroll_index

def select_bot(mouse_pos, active_bot, battle_state, chosen_action):
    for bot in player_bots:
        # bot is selected if it's clicked, alive, and hasn't acted yet
        if bot.rect.collidepoint(mouse_pos) and bot.ghost_health > 0 and not bot.acted:
            # bot is deselected if clicked again
            if active_bot == bot:
                active_bot = None
            else:
                active_bot = bot
            chosen_action = None
            battle_state = "Select Action"
            return battle_state, active_bot, chosen_action
    
    return battle_state, active_bot, chosen_action

def select_action(mouse_pos, active_bot, battle_state, chosen_action):
    # action button rectangles
    left_button_rect = pygame.Rect(70, 630, 150, 50)
    right_button_rect = pygame.Rect(240, 630, 150, 50)

    # gun bot action is chosen based on which button is clicked and action is deselected if clicked again
    if active_bot == gun_bot:
        if left_button_rect.collidepoint(mouse_pos) and not active_bot.left_gun_used:
            if chosen_action == "Left Gun":
                chosen_action = None
                battle_state = "Select Action"
            else:
                chosen_action = "Left Gun"
                battle_state = "Damage Enemy"
        elif right_button_rect.collidepoint(mouse_pos) and not active_bot.right_gun_used:
            if chosen_action == "Right Gun":
                chosen_action = None
                battle_state = "Select Action"
            else:
                chosen_action = "Right Gun"
                battle_state = "Damage Enemy"
    
    # hybrid bot action is chosen based on which button is clicked and action is deselected if clicked again
    elif active_bot == hybrid_bot:
        if left_button_rect.collidepoint(mouse_pos) and not active_bot.hybrid_gun_used:
            if chosen_action == "Hybrid Gun":
                chosen_action = None
                battle_state = "Select Action"
            else:
                chosen_action = "Hybrid Gun"
                battle_state = "Damage Enemy"
        elif right_button_rect.collidepoint(mouse_pos) and not active_bot.heal_used:
            if chosen_action == "Heal":
                chosen_action = None
                battle_state = "Select Action"
            else:
                chosen_action = "Heal"
                battle_state = "Heal Friendly"
    
    return battle_state, chosen_action

def check_bot_turn(player_bots):
    for bot in player_bots:
        if bot.ghost_health > 0 and not bot.acted:
            return "Select Bot"
    return "Enemy Turn"

def damage_enemy(mouse_pos, battle_state, active_bot, chosen_action, battle_log, scroll_index):
    for enemy in enemy_goons:
        if enemy.rect.collidepoint(mouse_pos) and enemy.ghost_health > 0:
            # damage the target enemy
            enemy.ghost_health -= active_bot.damage
            active_effects.append(DamageProjectile((0, 0, 255), active_bot.rect.centerx, active_bot.rect.centery, enemy.rect.centerx, enemy.rect.centery, enemy, active_bot.damage))
            
            # mark the action as used for the active bot
            if active_bot == gun_bot:
                if chosen_action == "Left Gun":
                    active_bot.left_gun_used = True
                elif chosen_action == "Right Gun":
                    active_bot.right_gun_used = True
            elif active_bot == hybrid_bot:
                active_bot.hybrid_gun_used = True
            active_bot.check_actions()
            
            # add to battle log and reset active bot and chosen action
            battle_log.append(f"{active_bot.name} attacks {enemy.name} for {active_bot.damage} damage!")
            scroll_index = 0
            active_bot = None
            chosen_action = None

            return check_bot_turn(player_bots), active_bot, chosen_action, scroll_index
    return battle_state, active_bot, chosen_action, scroll_index

def heal_friendly(mouse_pos, battle_state, active_bot, chosen_action, battle_log, scroll_index):
    for bot in player_bots:
        if bot.rect.collidepoint(mouse_pos) and bot.ghost_health > 0:
            # heal the target bot
            bot.ghost_health += active_bot.heal
            active_effects.append(HealProjectile((0, 255, 0), active_bot.rect.centerx, active_bot.rect.centery, bot.rect.centerx, bot.rect.centery, bot, active_bot.heal))
            
            # mark the action as used for the active bot
            active_bot.heal_used = True
            active_bot.check_actions()

            # add to battle log and reset active bot and chosen action
            battle_log.append(f"{active_bot.name} heals {bot.name} for {active_bot.heal} HP!")
            scroll_index = 0
            active_bot = None
            chosen_action = None

            return check_bot_turn(player_bots), active_bot, chosen_action, scroll_index
    return battle_state, active_bot, chosen_action, scroll_index

def player_turn(running, battle_state, active_bot, chosen_action, battle_log, scroll_index):
    for event in pygame.event.get():
        # check for quit events
        running = game_quit(event)
        if not running:
            break
        
        # do things based on the mouse
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # update scroll index based on mouse scroll
            if event.button in [4, 5]:
                scroll_index = scroll_math(mouse_pos, event, battle_log, scroll_index)
            
            # handle player actions based on battle state and mouse clicks
            elif event.button == 1:

                # if battle is over, dont allow any more actions
                if battle_state in ["Victory!", "Defeat!"]:
                    continue

                # select bot
                bot_selected = False
                if battle_state != "Heal Friendly":
                    old_battle_state = battle_state
                    battle_state, active_bot, chosen_action = select_bot(mouse_pos, active_bot, battle_state, chosen_action)
                    if battle_state != old_battle_state:
                        bot_selected = True
                
                # if not changing bot, then other actions can be done
                if not bot_selected:
                    # select action
                    action_selected = False
                    old_chosen_action = chosen_action
                    battle_state, chosen_action = select_action(mouse_pos, active_bot, battle_state, chosen_action)
                    if chosen_action != old_chosen_action:
                        action_selected = True
                    
                    # if not changing action, then carry out the chosen action
                    if not action_selected:
                        if battle_state == "Damage Enemy":
                            battle_state, active_bot, chosen_action, scroll_index = damage_enemy(mouse_pos, battle_state, active_bot, chosen_action, battle_log, scroll_index)
                        
                        elif battle_state == "Heal Friendly":
                            battle_state, active_bot, chosen_action, scroll_index = heal_friendly(mouse_pos, battle_state, active_bot, chosen_action, battle_log, scroll_index)
            
            # right click to cancel action or bot
            elif event.button == 3:
                if battle_state in ["Damage Enemy", "Heal Friendly"]:
                    chosen_action = None
                    battle_state = "Select Action"
                elif battle_state == "Select Action":
                    active_bot = None
                    battle_state = "Select Bot"
    
    return running, battle_state, active_bot, chosen_action, battle_log, scroll_index


# ------------------------------
# ENEMY TURN
# ------------------------------

def enemy_attacks(battle_log):
    # each alive enemy attacks a random alive bot
    for enemy in enemy_goons:
        if enemy.ghost_health > 0:
            bots_alive = []
            for bot in player_bots:
                if bot.ghost_health > 0:
                    bots_alive.append(bot)
            
            if bots_alive:
                target = random.choice(bots_alive)
                target.ghost_health -= enemy.damage
                active_effects.append(DamageProjectile((255, 0, 0), enemy.rect.x, enemy.rect.y, target.rect.centerx, target.rect.centery, target, enemy.damage))
                battle_log.append(f"{enemy.name} attacks {target.name} for {enemy.damage} damage!")

def enemy_turn(battle_state, battle_log):
    if battle_state == "Enemy Turn":
        # enemy attack logic
        enemy_attacks(battle_log)
        
        # resets for next turn
        for bot in player_bots:
            bot.reset_actions()
        battle_state = "Select Bot"
    
    return battle_state


# ------------------------------
# GAME ENDING
# ------------------------------

def check_game_over(battle_state, battle_log):
    # chceck if battle state is already victory or defeat
    if battle_state == "Victory!" or battle_state == "Defeat!":
        return battle_state

    # player wins if all enemies are dead
    winning = True
    for enemy in enemy_goons:
        if enemy.ghost_health > 0:
            winning = False
            break
    if winning:
        battle_log.append("------------------------------")
        battle_log.append("All of the enemies are defeated! You win!")
        battle_log.append("------------------------------")
        return "Victory!"
    
    # player loses if all bots are dead
    losing = True
    for bot in player_bots:
        if bot.ghost_health > 0:
            losing = False
            break
    if losing:
        battle_log.append("------------------------------")
        battle_log.append("All of your bots are defeated! You lose!")
        battle_log.append("------------------------------")
        return "Defeat!"
    
    return battle_state


# ------------------------------
# DRAWING, ANIMATION, AND RENDERING
# ------------------------------

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

def draw_characters(screen, font, characters, active_bot, chosen_action):
    for char in characters:
        # dead state
        if char.health <= 0:
            current_image = char.dead_image
            current_image.set_alpha(100)

        # hurt state
        elif char.hurt_timer > 0:
            current_image = char.hurt_image

        # action chosen state
        elif char == active_bot and chosen_action:
            if isinstance(char, GunBot):
                if chosen_action == "Left Gun":
                    current_image = char.left_gun_chosen_image
                elif chosen_action == "Right Gun":
                    current_image = char.right_gun_chosen_image
            elif isinstance(char, HybridBot):
                if chosen_action == "Hybrid Gun":
                    current_image = char.hybrid_gun_chosen_image
                elif chosen_action == "Heal":
                    current_image = char.heal_chosen_image

        # active state
        elif char == active_bot:
            current_image = char.active_image

        # idle state
        else:
            current_image = char.idle_images[char.current_frame]
            if char.acted:
                current_image.set_alpha(150)
            else:
                current_image.set_alpha(255)
        
        # draw character image
        screen.blit(current_image, (char.rect.x + char.shake_x, char.rect.y))

        # draw name and health
        name_text = font.render(char.name, True, (255, 255, 255))
        health_text = font.render(f"HP: {char.health}", True, (255, 255, 255))
        screen.blit(name_text, (char.rect.x, char.rect.y - 40))
        screen.blit(health_text, (char.rect.x, char.rect.y - 20))

def draw_action_button(screen, font_cache, active_bot, x, y, text, used, chosen):
    # draw button background
    pygame.draw.rect(screen, active_bot.button_color, (x, y, 150, 50))

    # if it's the chosen action, highlight and change text
    if chosen:
        text = f"Cancel {text}"
        pygame.draw.rect(screen, (0, 255, 0), (x, y, 150, 50), 4)

    # gray out if it's already used
    if not used:
        text_color = (255, 255, 255)
    else:
        text_color = active_bot.used_text_color
    
    # dynamically adjust font size to fit the button
    button_text = dynamic_text(font_cache, text, 140, 40, text_color)

    # center the text on the button
    text_width, text_height = button_text.get_size()
    text_x = x + (150 - text_width) // 2
    text_y = y + (50 - text_height) // 2

    # draw button text
    screen.blit(button_text, (text_x, text_y))

def draw_action_options(screen, font_cache, active_bot, chosen_action):
    # draw action background
    if active_bot:
        color = active_bot.action_background_color
    else:
        color = (50, 50, 50)
    pygame.draw.rect(screen, color, (50, 610, 360, 90))
    pygame.draw.rect(screen, (255, 255, 255), (50, 610, 360, 90), 3)

    # draw action buttons based on active bot
    if active_bot == gun_bot:
        draw_action_button(screen, font_cache, active_bot, 70, 630, "Left Gun", active_bot.left_gun_used, chosen_action == "Left Gun")
        draw_action_button(screen, font_cache, active_bot, 240, 630, "Right Gun", active_bot.right_gun_used, chosen_action == "Right Gun")
    elif active_bot == hybrid_bot:
        draw_action_button(screen, font_cache, active_bot, 70, 630, "Attack", active_bot.hybrid_gun_used, chosen_action == "Hybrid Gun")
        draw_action_button(screen, font_cache, active_bot, 240, 630, "Heal", active_bot.heal_used, chosen_action == "Heal")

def draw_battle_log(screen, font, battle_log, scroll_index):
    # draw battle log background
    pygame.draw.rect(screen, (40, 40, 40), (460, 615, 690, 85))
    pygame.draw.rect(screen, (200, 200, 200), (460, 615, 690, 85), 2)

    # determine start and end lines based on scrolling
    if len(battle_log) <= 3:
        lines_to_show = battle_log
    else:
        start_line = len(battle_log) - 3 - scroll_index
        end_line = len(battle_log) - scroll_index
        lines_to_show = battle_log[start_line:end_line]

    # draw log text
    for i, line in enumerate(lines_to_show):
        log_text = font.render(line, True, (255, 255, 255))
        screen.blit(log_text, (470, 625 + i * 25))

def draw_effects(screen, combat_font):
    # draw animation based on its type
    for effect in active_effects:
        # draw floating text
        if isinstance(effect, FloatingText):
            text = combat_font.render(effect.text, True, effect.color)
            screen.blit(text, (effect.x, effect.y))
        # draw damage projectile
        elif isinstance(effect, DamageProjectile):
            pygame.draw.rect(screen, effect.color, (effect.x, effect.y, 10, 5))
        # draw heal projectile
        elif isinstance(effect, HealProjectile):
            pygame.draw.circle(screen, effect.color, (int(effect.x), int(effect.y)), 5)

def draw_screen(screen, font, combat_font, font_cache, active_bot, chosen_action, battle_log, scroll_index):
    # background color
    screen.fill((0, 0, 0))

    # draw bots and goons with animations based on their states and actions
    draw_characters(screen, font, player_bots, active_bot, chosen_action)
    draw_characters(screen, font, enemy_goons, active_bot, chosen_action)
    
    draw_action_options(screen, font_cache, active_bot, chosen_action)

    draw_battle_log(screen, font, battle_log, scroll_index)
    
    draw_effects(screen, combat_font)


# ------------------------------
# ANIMATION UPDATES
# ------------------------------

def update_effects():
    # update and remove effects
    for effect in active_effects[:]:
        effect.update()
        if not effect.active:
            active_effects.remove(effect)

def update_animations():
    # update characters position when they are hurt
    for bot in player_bots:
        bot.hurt_animations()
    for enemy in enemy_goons:
        enemy.hurt_animations()

    # update idle animation frames
    for bot in player_bots:
        bot.update_idle_animation()
    for enemy in enemy_goons:
        enemy.update_idle_animation()

    # update effects
    update_effects()


async def main():
    # screen settings
    screen = pygame.display.set_mode((1200, 750))
    # title
    pygame.display.set_caption("Rounds")
    # setup timer to control game speed
    clock = pygame.time.Clock()

    # setup fonts
    font = pygame.font.SysFont(None, 24)
    combat_font = pygame.font.SysFont(None, 30)
    font_cache = {}
    for size in range(10, 31):
        font_cache[size] = pygame.font.SysFont(None, size)

    # load character images
    for bot in player_bots:
        bot.load_images()
    for enemy in enemy_goons:
        enemy.load_images()

    # initial game state
    battle_state = "Select Bot"
    active_bot = None
    chosen_action = None
    battle_log = []
    scroll_index = 0
    running = True
    battle_log.append("Welcome to Rounds! Select a bot to start your turn.")

    while running:

        # update animations
        update_animations()

        # player turn logic
        running, battle_state, active_bot, chosen_action, battle_log, scroll_index = player_turn(running, battle_state, active_bot, chosen_action, battle_log, scroll_index)

        # enemy turn logic
        battle_state = enemy_turn(battle_state, battle_log)

        # check if game is over
        battle_state = check_game_over(battle_state, battle_log)

        # drawing, animation, and rendering
        draw_screen(screen, font, combat_font, font_cache, active_bot, chosen_action, battle_log, scroll_index)

        # keeps the game from flickering
        pygame.display.flip()
        # makes the game run at 60 frames per second
        clock.tick(60)
        # prevents freezing in the web
        await asyncio.sleep(0)
    
    pygame.quit()
    # comment for testing purposes

if __name__ == "__main__":
    asyncio.run(main())