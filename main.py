import asyncio
import random
import pygame

# initialize pygame and font module
pygame.init()
pygame.font.init()


# ------------------------------
# TEXT ANIMATION
# ------------------------------

class FloatingText:
    def __init__(self, text, color, x, y):
        self.text = text
        self.color = color
        self.x = x
        self.y = y
        self.timer = 120

    def update(self):
        self.y -= 1
        self.timer -= 1

active_floating_texts = []


# ------------------------------
# CHARACTERS
# ------------------------------

class Character:
    def __init__(self, name, health, damage, x, y, w, h, image_path, dead_image_path):
        self.name = name
        self.health = health
        self.damage = damage
        self.rect = pygame.Rect(x, y, w, h)
        self.acted = False

        # images
        self.image_path = image_path
        self.dead_image_path = dead_image_path
        self.image = None
        self.dead_image = None

        # animation
        self.hurt_timer = 0
        self.shake_x = 0

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
        
        self.hurt_timer = 10

        # text animation
        text_x = random.randint(self.rect.x, self.rect.x + self.rect.width - 30)
        text_y = self.rect.y + 10
        active_floating_texts.append(FloatingText(f"-{amount}", (255, 0, 0), text_x, text_y))

    def take_heal(self, amount):
        self.health += amount

        # text animation
        text_x = random.randint(self.rect.x, self.rect.x + self.rect.width - 30)
        text_y = self.rect.y + 10
        active_floating_texts.append(FloatingText(f"+{amount}", (0, 255, 0), text_x, text_y))
    
    def hurt_animations(self):
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
            self.shake_x = random.randint(-5, 5)
        else:
            self.shake_x = 0

class GunBot(Character):
    def __init__(self, name, health, damage, x, y, w, h, image_path, dead_image_path):
        super().__init__(name, health, damage, x, y, w, h, image_path, dead_image_path)

        # actions
        self.left_gun_used = False
        self.right_gun_used = False
    
    def check_actions(self):
        if self.left_gun_used and self.right_gun_used:
            self.acted = True
    
    def reset_actions(self):
        self.acted = False
        self.left_gun_used = False
        self.right_gun_used = False

class HybridBot(Character):
    def __init__(self, name, health, damage, heal, x, y, w, h, image_path, dead_image_path):
        super().__init__(name, health, damage, x, y, w, h, image_path, dead_image_path)
        self.heal = heal

        # actions
        self.hybrid_gun_used = False
        self.heal_used = False
    
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
    "assets/gun_bot.png", # image_path
    "assets/gun_bot_dead.png", # dead_image_path
)

hybrid_bot = HybridBot(
    "Hybrid Bot", # name
    10, # health
    1, # damage
    2, # heal
    150, 300, # x, y
    100, 100, # w, h
    "assets/hybrid_bot.png", # image_path
    "assets/hybrid_bot_dead.png" # dead_image_path
)

player_bots = [gun_bot, hybrid_bot]

basic_goon_1 = Character(
    "Basic Goon", # name
    5, # health
    1, # damage
    950, 150, # x, y
    100, 100, # w, h
    "assets/basic_goon.png", # image_path
    "assets/basic_goon_dead.png" # dead_image_path
)

basic_goon_2 = Character(
    "Basic Goon", # name
    5, # health
    1, # damage
    950, 300, # x, y
    100, 100, # w, h
    "assets/basic_goon.png", # image_path
    "assets/basic_goon_dead.png" # dead_image_path
)

enemy_goons = [basic_goon_1, basic_goon_2]

def load_characters():
    for bot in player_bots:
        bot.image = pygame.image.load(bot.image_path).convert_alpha()
        bot.dead_image = pygame.image.load(bot.dead_image_path).convert_alpha()
    for enemy in enemy_goons:
        enemy.image = pygame.image.load(enemy.image_path).convert_alpha()
        enemy.dead_image = pygame.image.load(enemy.dead_image_path).convert_alpha() 


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

def select_bot(mouse_pos, active_bot, battle_state):
    for bot in player_bots:
        # bot is selected if it's clicked, alive, and hasn't acted yet
        if bot.rect.collidepoint(mouse_pos) and bot.health > 0 and not bot.acted:
            active_bot = bot
            battle_state = "Select Action"
            return battle_state, active_bot
    
    return battle_state, active_bot

def select_action(mouse_pos, active_bot, battle_state, chosen_action):
    # action button rectangles
    left_button_rect = pygame.Rect(70, 635, 100, 45)
    right_button_rect = pygame.Rect(190, 635, 100, 45)

    # action is chosen based on which button is clicked
    if active_bot == gun_bot:
        if left_button_rect.collidepoint(mouse_pos) and not active_bot.left_gun_used:
            chosen_action = "Left Gun"
            battle_state = "Damage Enemy"
        elif right_button_rect.collidepoint(mouse_pos) and not active_bot.right_gun_used:
            chosen_action = "Right Gun"
            battle_state = "Damage Enemy"
    
    elif active_bot == hybrid_bot:
        if left_button_rect.collidepoint(mouse_pos) and not active_bot.hybrid_gun_used:
            chosen_action = "Hybrid Gun"
            battle_state = "Damage Enemy"
        elif right_button_rect.collidepoint(mouse_pos) and not active_bot.heal_used:
            chosen_action = "Heal"
            battle_state = "Heal Friendly"
    
    return battle_state, chosen_action

def check_bot_turn(player_bots):
    for bot in player_bots:
        if bot.health > 0 and not bot.acted:
            return "Select Bot"
    return "Enemy Turn"

def damage_enemy(mouse_pos, active_bot, chosen_action, battle_log, scroll_index):
    for enemy in enemy_goons:
        if enemy.rect.collidepoint(mouse_pos) and enemy.health > 0:
            # damage the target enemy
            enemy.take_damage(active_bot.damage)
            
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
    return "Damage Enemy", active_bot, chosen_action, scroll_index

def heal_friendly(mouse_pos, active_bot, chosen_action, battle_log, scroll_index):
    for bot in player_bots:
        if bot.rect.collidepoint(mouse_pos) and bot.health > 0:
            # heal the target bot
            bot.take_heal(active_bot.heal)
            # mark the action as used for the active bot
            active_bot.heal_used = True
            active_bot.check_actions()

            # add to battle log and reset active bot and chosen action
            battle_log.append(f"{active_bot.name} heals {bot.name} for {active_bot.heal} HP!")
            scroll_index = 0
            active_bot = None
            chosen_action = None

            return check_bot_turn(player_bots), active_bot, chosen_action, scroll_index
    return "Heal Friendly", active_bot, chosen_action, scroll_index

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
                if battle_state == "Select Bot":
                    battle_state, active_bot = select_bot(mouse_pos, active_bot, battle_state)

                elif battle_state == "Select Action":
                    battle_state, chosen_action = select_action(mouse_pos, active_bot, battle_state, chosen_action)
                
                elif battle_state == "Damage Enemy":
                    battle_state, active_bot, chosen_action, scroll_index = damage_enemy(mouse_pos, active_bot, chosen_action, battle_log, scroll_index)
                
                elif battle_state == "Heal Friendly":
                    battle_state, active_bot, chosen_action, scroll_index = heal_friendly(mouse_pos, active_bot, chosen_action, battle_log, scroll_index)
    
    return running, battle_state, active_bot, chosen_action, battle_log, scroll_index


# ------------------------------
# ENEMY TURN
# ------------------------------

def enemy_attacks(battle_log):
    # each alive enemy attacks a random alive bot
    for enemy in enemy_goons:
        if enemy.health > 0:
            bots_alive = []
            for bot in player_bots:
                if bot.health > 0:
                    bots_alive.append(bot)
            
            if bots_alive:
                target = random.choice(bots_alive)
                target.take_damage(enemy.damage)
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
        if enemy.health > 0:
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
        if bot.health > 0:
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

def draw_characters(screen, font, characters):
    # draw characters
    for char in characters:
        if char.health > 0:
            if char.acted:
                char.image.set_alpha(150)
            else:
                char.image.set_alpha(255)
            screen.blit(char.image, (char.rect.x + char.shake_x, char.rect.y))
        else:
            char.dead_image.set_alpha(100)
            screen.blit(char.dead_image, (char.rect.x + char.shake_x, char.rect.y))

        # draw name and health
        name_text = font.render(char.name, True, (255, 255, 255))
        health_text = font.render(f"HP: {char.health}", True, (255, 255, 255))
        screen.blit(name_text, (char.rect.x, char.rect.y - 40))
        screen.blit(health_text, (char.rect.x, char.rect.y - 20))

def draw_action_button(screen, font, x, text, used, chosen):
    # draw button background
    pygame.draw.rect(screen, (60, 60, 60), (x, 635, 100, 45))

    # highlight if it's the chosen action
    if chosen:
        pygame.draw.rect(screen, (0, 255, 0), (x, 635, 100, 45), 3)

    # draw button text
    if not used:
        color = (255, 255, 255)
    else:
        color = (100, 100, 100)
    button_text = font.render(text, True, color)
    screen.blit(button_text, (x + 10, 650))

def draw_action_options(screen, font, active_bot, chosen_action):
    # draw action background
    pygame.draw.rect(screen, (40, 40, 40), (50, 615, 260, 85))
    pygame.draw.rect(screen, (200, 200, 200), (50, 615, 260, 85), 2)

    # draw action buttons based on active bot
    if active_bot == gun_bot:
        draw_action_button(screen, font, 70, "Attack", active_bot.left_gun_used, chosen_action == "Left Gun")
        draw_action_button(screen, font, 190, "Attack", active_bot.right_gun_used, chosen_action == "Right Gun")
    elif active_bot == hybrid_bot:
        draw_action_button(screen, font, 70, "Attack", active_bot.hybrid_gun_used, chosen_action == "Hybrid Gun")
        draw_action_button(screen, font, 190, "Heal", active_bot.heal_used, chosen_action == "Heal")

def draw_battle_log(screen, font, battle_log, scroll_index):
    # draw battle log background
    pygame.draw.rect(screen, (40, 40, 40), (360, 615, 790, 85))
    pygame.draw.rect(screen, (200, 200, 200), (360, 615, 790, 85), 2)

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
        screen.blit(log_text, (370, 625 + i * 25))

def draw_floating_text(screen, combat_font):
    # draw floating text
    for text in active_floating_texts:
        text_surface = combat_font.render(text.text, True, text.color)
        screen.blit(text_surface, (text.x, text.y))

def draw_screen(screen, font, combat_font, active_bot, chosen_action, battle_log, scroll_index):
    # background color
    screen.fill((0, 0, 0))

    # draw bots and goons
    draw_characters(screen, font, player_bots)
    draw_characters(screen, font, enemy_goons)
    
    # highlight active bot
    if active_bot:
        pygame.draw.rect(screen, (0, 255, 0), active_bot.rect, 5)
    
    # draw action options
    draw_action_options(screen, font, active_bot, chosen_action)

    # draw battle log
    draw_battle_log(screen, font, battle_log, scroll_index)
    
    # draw floating text
    draw_floating_text(screen, combat_font)


# ------------------------------
# ANIMATION UPDATES
# ------------------------------

def update_character_hurt_position(characters):
    for char in characters:
        char.hurt_animations()

def update_floating_texts():
    # updates and removes floating text
    for text in active_floating_texts[:]:
        text.update()
        if text.timer <= 0:
            active_floating_texts.remove(text)

def update_animations():
    # update characters  position when they are hurt
    update_character_hurt_position(player_bots)
    update_character_hurt_position(enemy_goons)

    # update floating text
    update_floating_texts()


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

    load_characters()

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
        draw_screen(screen, font, combat_font, active_bot, chosen_action, battle_log, scroll_index)

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