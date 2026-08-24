import pygame

# import game modules
from .helper import FloatingText, dynamic_text
from .bots import gun_bot, rico_bot, elemental_bot, lazer_bot
from .projectiles import (
    LinearProjectile,
    ChargeProjectile,
    MarkProjectile,
    PercentageProjectile,
    ShieldProjectile,
    BounceProjectile,
    GlitchyDamageProjectile,
    GlitchyHealProjectile,
    GlitchyBlockProjectile,
    LaserProjectile
)

# ------------------------------
# UPDATE ANIMATIONS
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

# ------------------------------
# DRAWING CHARACTERS AND STATUS EFFECTS
# ------------------------------

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

# ------------------------------
# DRAWING SHOP BOX AND MENU
# ------------------------------

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

# ------------------------------
# DRAWING ACTION BOX AND BUTTONS
# ------------------------------

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

# ------------------------------
# DRAWING LORE BOX AND TEXT
# ------------------------------

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

# ------------------------------
# DRAWING PROJECTILE EFFECTS
# ------------------------------

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

# ------------------------------
# DRAWING SCREEN AND MAIN MENU
# ------------------------------

def draw_screen(screen, regular_font, floating_font, font_cache, player_bots, enemy_goons, active_effects, battle_state, active_bot, chosen_action, inspecting_character, scroll_y, gears, rounds):
    # background color
    screen.fill((0, 0, 0))

    # draw bots and goons with animations based on their states and actions
    draw_characters(screen, regular_font, player_bots, enemy_goons, active_bot, chosen_action, inspecting_character)

    # draw bots and goons status effects
    draw_character_status_effects(screen, regular_font, player_bots, enemy_goons, battle_state)

    # draw shop box above action box
    draw_shop_box(screen, regular_font, font_cache, battle_state, active_bot, gears, rounds)

    # draw shop menu if opened
    draw_shop_menu(screen, font_cache, battle_state, gears)

    # draw action options based on active bot and chosen action
    draw_action_box(screen, font_cache, battle_state, active_bot, chosen_action)

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
