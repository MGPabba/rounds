import pygame

# import game modules
from .helper import FloatingText, dynamic_text
from .bots import elemental_bot, lazer_bot
from .shop import all_bots, bot_upgrades
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

def update_animations(player_bots, enemy_goons, active_effects, battle_state, active_bot, lore_scroll_y, lore_target_scroll_y, menu_scroll_y, menu_target_scroll_y):
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
    lore_scroll_y += (lore_target_scroll_y - lore_scroll_y) * 0.2
    if abs(lore_target_scroll_y - lore_scroll_y) < 0.1:
        lore_scroll_y = lore_target_scroll_y

    # update scrolling position for menu
    menu_scroll_y += (menu_target_scroll_y - menu_scroll_y) * 0.2
    if abs(menu_target_scroll_y - menu_scroll_y) < 0.1:
        menu_scroll_y = menu_target_scroll_y

    return lore_scroll_y, menu_scroll_y

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

def draw_shop_bar(screen, shop_title_font, battle_state):
    if battle_state == "Shop":
        for i in range(len(all_bots)):
            mouse_pos = pygame.mouse.get_pos()

            # draw bot button if unlocked
            if all_bots[i]["unlocked"]:

                # navigation button
                button_rect = pygame.Rect(180, 40 + i * 80, 80, 80)
                if button_rect.collidepoint(mouse_pos):
                    button_color = all_bots[i]["bot"].button_color
                else:
                    button_color = all_bots[i]["bot"].box_background_color
                pygame.draw.rect(screen, button_color, button_rect)

                # bot first letter of name
                bot_letter_text = shop_title_font.render(all_bots[i]["bot"].name[0], True, (255, 255, 255))
                bot_letter_rect = bot_letter_text.get_rect(center=(220, 80 + i * 80))
                screen.blit(bot_letter_text, bot_letter_rect)

            # draw ? if not unlocked
            else:
                pygame.draw.rect(screen, all_bots[i]["bot"].box_background_color, (180, 40 + i * 80, 80, 80))
                question_mark_text = shop_title_font.render("?", True, (255, 255, 255))
                question_mark_rect = question_mark_text.get_rect(center=(220, 80 + i * 80))
                screen.blit(question_mark_text, question_mark_rect)

            # line between buttons
            if i != 0:
                pygame.draw.line(screen, (255, 255, 255), (180, 40 + i * 80), (260, 40 + i * 80), 3)

        # shop nav bar outline
        pygame.draw.rect(screen, (255, 255, 255), (180, 40, 80, 560), 3)

def draw_shop_text(menu_canvas, font_cache, text, color, center_x, center_y):
    # draw text on the shop menu
    text_label = dynamic_text(font_cache, text, 180, 40, color)
    text_rect = text_label.get_rect(center=(center_x, center_y))
    menu_canvas.blit(text_label, text_rect)

def draw_shop_menu(screen, shop_title_font, font_cache, battle_state, menu_height, menu_scroll_y, gears, rounds):
    if battle_state == "Shop":
        # get mouse position relative to shop menu
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = (mouse_pos[0] - 257, mouse_pos[1] - 40 + menu_scroll_y)

        # calculate the shop menu height
        menu_height = 0
        for i in range(len(bot_upgrades)):
            if all_bots[i]["unlocked"]:
                menu_height += len(bot_upgrades[all_bots[i]["bot"].name]) * 90 + 100
            else:
                menu_height += 90

        # create a surface for the shop menu
        menu_canvas = pygame.Surface((760, menu_height))

        menu_y = 0
        for i in range(len(bot_upgrades)):
            # draw bot and its upgrades if unlocked
            if all_bots[i]["unlocked"]:

                # background box for each bot and its upgrades
                pygame.draw.rect(menu_canvas, all_bots[i]["bot"].box_background_color, (0, menu_y, 760, len(bot_upgrades[all_bots[i]["bot"].name]) * 90 + 100))

                # bot name title
                bot_name_text = shop_title_font.render(all_bots[i]["bot"].name, True, (255, 255, 255))
                bot_name_rect = bot_name_text.get_rect(center=(380, menu_y + 26))
                menu_canvas.blit(bot_name_text, bot_name_rect)

                # line under bot name row
                menu_y += 50
                pygame.draw.line(menu_canvas, (255, 255, 255), (0, menu_y), (760, menu_y), 3)
                column_top_y = menu_y

                # heading row
                draw_shop_text(menu_canvas, font_cache, "Action", (255, 255, 255), 95, menu_y + 26)
                draw_shop_text(menu_canvas, font_cache, "Buff", (255, 255, 255), 285, menu_y + 26)
                draw_shop_text(menu_canvas, font_cache, "Cost", (255, 255, 255), 475, menu_y + 26)
                draw_shop_text(menu_canvas, font_cache, "Upgrade", (255, 255, 255), 665, menu_y + 26)

                # line under heading row
                menu_y += 50
                pygame.draw.line(menu_canvas, (255, 255, 255), (0, menu_y), (760, menu_y), 3)

                for j in range(len(bot_upgrades[all_bots[i]["bot"].name])):
                    # upgrade information
                    upgrade = bot_upgrades[all_bots[i]["bot"].name][j]

                    # upgrade action
                    draw_shop_text(menu_canvas, font_cache, upgrade["action"], (255, 255, 255), 95, menu_y + 46)

                    # upgrade row if not max level
                    if upgrade["level"] < len(upgrade["cost"]):
                        cost_number = upgrade["cost"][upgrade["level"]]

                        # upgrade buff and cost
                        draw_shop_text(menu_canvas, font_cache, upgrade["buff_desc_1"], (255, 255, 255), 285, menu_y + 31)
                        draw_shop_text(menu_canvas, font_cache, upgrade["buff_desc_2"][upgrade["level"]], (255, 255, 255), 285, menu_y + 61)
                        draw_shop_text(menu_canvas, font_cache, f"{cost_number} Gears", (255, 255, 255), 475, menu_y + 46)

                        # upgrade button
                        button_rect = pygame.Rect(590, menu_y + 20, 150, 50)
                        if gears >= cost_number and button_rect.collidepoint(mouse_pos):
                            button_color = all_bots[i]["bot"].button_hover_color
                        else:
                            button_color = all_bots[i]["bot"].button_color
                        pygame.draw.rect(menu_canvas, button_color, button_rect)

                        # upgrade text
                        if gears >= cost_number:
                            button_text_color = (255, 255, 255)
                        else:
                            button_text_color = all_bots[i]["bot"].text_used_color
                        draw_shop_text(menu_canvas, font_cache, "Upgrade", button_text_color, 665, menu_y + 46)

                    # upgrade row if max level
                    else:
                        draw_shop_text(menu_canvas, font_cache, "Max Level", (255, 255, 255), 285, menu_y + 46)
                        draw_shop_text(menu_canvas, font_cache, "Max Level", (255, 255, 255), 475, menu_y + 46)
                        draw_shop_text(menu_canvas, font_cache, "Max Level", (255, 255, 255), 665, menu_y + 46)

                    # line under upgrade row
                    menu_y += 90
                    pygame.draw.line(menu_canvas, (255, 255, 255), (0, menu_y), (760, menu_y), 3)

                # column lines
                pygame.draw.line(menu_canvas, (255, 255, 255), (190, column_top_y), (190, menu_y), 3)
                pygame.draw.line(menu_canvas, (255, 255, 255), (380, column_top_y), (380, menu_y), 3)
                pygame.draw.line(menu_canvas, (255, 255, 255), (570, column_top_y), (570, menu_y), 3)

                # line before bot name row
                if i != 0:
                    pygame.draw.line(menu_canvas, (255, 255, 255), (0, column_top_y - 50), (760, column_top_y - 50), 3)

            # draw locked bot not yet available
            elif all_bots[i]["round"] > rounds:

                # background box for locked bot
                pygame.draw.rect(menu_canvas, all_bots[i]["bot"].box_background_color, (0, menu_y, 760, 90))

                # bot name title
                bot_name_text = shop_title_font.render(all_bots[i]["bot"].name, True, (255, 255, 255))
                bot_name_rect = bot_name_text.get_rect(center=(190, menu_y + 46))
                menu_canvas.blit(bot_name_text, bot_name_rect)

                # bot unlock round
                unlock_text = dynamic_text(font_cache, f"Available after round {all_bots[i]["round"] - 1}", 380, 40, (255, 255, 255))
                unlock_rect = unlock_text.get_rect(center=(475, menu_y + 46))
                menu_canvas.blit(unlock_text, unlock_rect)

                # line before unlock row
                menu_y += 90
                pygame.draw.line(menu_canvas, (255, 255, 255), (0, menu_y - 90), (760, menu_y - 90), 3)

            # draw locked bot if not unlocked
            else:

                # background box for locked bot
                pygame.draw.rect(menu_canvas, all_bots[i]["bot"].box_background_color, (0, menu_y, 760, 90))

                # bot name title
                bot_name_text = shop_title_font.render(all_bots[i]["bot"].name, True, (255, 255, 255))
                bot_name_rect = bot_name_text.get_rect(center=(190, menu_y + 46))
                menu_canvas.blit(bot_name_text, bot_name_rect)

                # bot unlock cost
                draw_shop_text(menu_canvas, font_cache, f"Unlock Cost:", (255, 255, 255), 475, menu_y + 31)
                draw_shop_text(menu_canvas, font_cache, f"{all_bots[i]["cost"]} Gears", (255, 255, 255), 475, menu_y + 61)

                # unlock button
                button_rect = pygame.Rect(590, menu_y + 20, 150, 50)
                if gears >= all_bots[i]["cost"] and button_rect.collidepoint(mouse_pos):
                    button_color = all_bots[i]["bot"].button_hover_color
                else:
                    button_color = all_bots[i]["bot"].button_color
                pygame.draw.rect(menu_canvas, button_color, button_rect)

                # unlock text
                if gears >= all_bots[i]["cost"]:
                    button_text_color = (255, 255, 255)
                else:
                    button_text_color = all_bots[i]["bot"].text_used_color
                draw_shop_text(menu_canvas, font_cache, "Unlock", button_text_color, 665, menu_y + 46)

                # line before unlock row
                menu_y += 90
                pygame.draw.line(menu_canvas, (255, 255, 255), (0, menu_y - 90), (760, menu_y - 90), 3)

        # draw the visible part of the shop menu onto the screen based on scroll position
        visible_rect = pygame.Rect(0, int(menu_scroll_y), 760, 560)
        screen.blit(menu_canvas, (257, 40), visible_rect)
        
        # shop menu outline
        pygame.draw.rect(screen, (255, 255, 255), (257, 40, 760, 560), 3)

    return menu_height

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

def draw_lore_box(screen, regular_font, battle_state, inspecting_character, lore_scroll_y, rounds):
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
    visible_rect = pygame.Rect(0, int(lore_scroll_y), 580, 80)
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

def draw_screen(screen, regular_font, floating_font, shop_title_font, font_cache, player_bots, enemy_goons, active_effects, battle_state, active_bot, chosen_action, inspecting_character, lore_scroll_y, menu_height, menu_scroll_y, gears, rounds):
    # background color
    screen.fill((0, 0, 0))

    # draw bots and goons with animations based on their states and actions
    draw_characters(screen, regular_font, player_bots, enemy_goons, active_bot, chosen_action, inspecting_character)

    # draw bots and goons status effects
    draw_character_status_effects(screen, regular_font, player_bots, enemy_goons, battle_state)

    # draw shop box above action box
    draw_shop_box(screen, regular_font, font_cache, battle_state, active_bot, gears, rounds)

    # draw shop bar and menu if opened
    draw_shop_bar(screen, shop_title_font, battle_state)
    menu_height = draw_shop_menu(screen, shop_title_font, font_cache, battle_state, menu_height, menu_scroll_y, gears, rounds)

    # draw action options based on active bot and chosen action
    draw_action_box(screen, font_cache, battle_state, active_bot, chosen_action)

    # draw lore box with scrolling
    lore_height = draw_lore_box(screen, regular_font, battle_state, inspecting_character, lore_scroll_y, rounds)

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

    return lore_height, menu_height

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
