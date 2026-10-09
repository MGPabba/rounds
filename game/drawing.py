# drawing.py

import pygame

# import game modules
from .helper import FloatingText, dynamic_text, render_text
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

def update_animations(player_bots, enemy_goons, active_effects, battle_state, active_bot, chosen_action, lore_scroll_y, lore_target_scroll_y, menu_scroll_y, menu_target_scroll_y, gun_bot):
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

    # update gun bot aiming marker if it is unlocked and chosen
    if active_bot and active_bot.name == "Gun Bot" and chosen_action == "Left Gun" and active_bot.actions[0]["aiming_unlocked"]:
        gun_bot.update_gun_aiming()

    return lore_scroll_y, menu_scroll_y

# ------------------------------
# DRAWING CHARACTERS AND STATUS EFFECTS
# ------------------------------

def draw_characters(screen, fonts, text_cache, player_bots, enemy_goons, active_bot, chosen_action, inspecting_character):
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

        # draw character name and health
        name_text = render_text(fonts, text_cache, 24, char.name, (255, 255, 255))
        screen.blit(name_text, (char.rect.x, char.rect.y - 40))
        health_text = render_text(fonts, text_cache, 24, f"HP: {char.visual_health}", (255, 255, 255))
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

def draw_character_status_effects(screen, mouse_pos, fonts, text_cache, player_bots, enemy_goons, battle_state, elemental_bot, lazer_bot):
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
                fire_text = render_text(fonts, text_cache, 24, f"{char.fire_rounds}", (255, 0, 0))
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
                mark_text = render_text(fonts, text_cache, 24, "M", (255, 255, 0))
                screen.blit(mark_text, (char.rect.x - 16, char.rect.y - 20))

            # draw block barrier
            if char.block > 0:
                pygame.draw.rect(screen, (255, 155, 0), (char.rect.x -10, char.rect.y, 110, 110), 3)
                pygame.draw.rect(screen, (255, 155, 0), (char.rect.x, char.rect.y - 5, 105, 105), 3)
                pygame.draw.rect(screen, (255, 155, 0), (char.rect.x, char.rect.y, 120, 120), 3)

            # draw shield
            if char.shield > 0:
                pygame.draw.circle(screen, (200, 200, 200), (char.rect.centerx, char.rect.centery), 55, 3)

            # highlight character if hovering and valid target
            if char.rect.collidepoint(mouse_pos) and char.real_health > 0:
                if char in enemy_goons and battle_state in ["Target Enemy", "Target Enemy or Self", "Target Any"]:
                    pygame.draw.rect(screen, (255, 0, 0), char.rect, 3)
                elif (char in player_bots and battle_state in ["Target Bot", "Target Any"]) or (char.name == "Lazer Bot" and battle_state == "Target Line") or (char.name == "Duplo Bot" and battle_state == "Target Enemy or Self"):
                    pygame.draw.rect(screen, (0, 255, 0), char.rect, 3)
                elif char in player_bots and battle_state not in ["Game Over", "Shop"] and not char.acted and not lazer_bot.actions[0]["movement_mode"]:
                    pygame.draw.rect(screen, (0, 0, 255), char.rect, 3)

def draw_gun_aiming(screen, font_cache, text_cache, active_bot, chosen_action, gun_bot):
    if active_bot and active_bot.name == "Gun Bot" and chosen_action == "Left Gun" and active_bot.actions[0]["aiming_unlocked"]:
        # gun bot aiming box background
        pygame.draw.rect(screen, gun_bot.box_background_color, (20, 20, 105, 413))
        pygame.draw.rect(screen, (255, 255, 255), (20, 20, 105, 413), 3)

        # colors for each damage zone
        zone_colors = {
            1: (150, 200, 255),
            2: (125, 175, 255),
            3: (100, 150, 255),
            4: (75, 125, 255),
            5: (50, 100, 255)
        }

        # draw each damage zone
        for zone in gun_bot.actions[0]["zones"]:
            pygame.draw.rect(screen, zone_colors[zone["damage"]], (40, zone["position"], 50, zone["height"]))
            zone_text = dynamic_text(font_cache, text_cache, f"{zone['damage']}", 50, zone["height"], (255, 255, 255))
            zone_text_rect = zone_text.get_rect(center=(100, (zone["position"] + zone["height"] // 2) + 1))
            screen.blit(zone_text, zone_text_rect)
        pygame.draw.rect(screen, (255, 255, 255), (40, 40, 50, 373), 1)

        # draw marker line
        pygame.draw.line(screen, (255, 255, 255), (40, gun_bot.actions[0]["marker_y"]), (89, gun_bot.actions[0]["marker_y"]), 3)

# ------------------------------
# DRAWING SHOP BOX AND MENU
# ------------------------------

def draw_shop_box(screen, mouse_pos, fonts, font_cache, text_cache, battle_state, active_bot, gears, rounds, lazer_bot):
    # draw shop box background
    if active_bot:
        box_color = active_bot.box_background_color
    else:
        box_color = (50, 50, 50)
    pygame.draw.rect(screen, box_color, (20, 510, 140, 90))
    pygame.draw.rect(screen, (255, 255, 255), (20, 510, 140, 90), 3)

    # draw shop button with hover effect
    button_rect = pygame.Rect(40, 530, 100, 50)
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
    shop_text = dynamic_text(font_cache, text_cache, text, 90, 40, (255, 255, 255))
    shop_text_rect = shop_text.get_rect(center=(90, 555))
    screen.blit(shop_text, shop_text_rect)

    # draw info box background
    pygame.draw.rect(screen, box_color, (20, 453, 140, 60))
    pygame.draw.rect(screen, (255, 255, 255), (20, 453, 140, 60), 3)

    # draw round and gears text
    round_text = render_text(fonts, text_cache, 24, f"Round: {rounds}", (255, 255, 255))
    round_text_rect = round_text.get_rect(center=(90, 473))
    screen.blit(round_text, round_text_rect)
    gears_text = render_text(fonts, text_cache, 24, f"Gears: {gears}", (255, 255, 255))
    gears_text_rect = gears_text.get_rect(center=(90, 493))
    screen.blit(gears_text, gears_text_rect)

def draw_shop_bar(screen, mouse_pos, fonts, text_cache, all_bots, battle_state):
    if battle_state == "Shop":
        for i in range(len(all_bots)):
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
                bot_letter_text = render_text(fonts, text_cache, 40, all_bots[i]["bot"].name[0], (255, 255, 255))
                bot_letter_rect = bot_letter_text.get_rect(center=(220, 80 + i * 80))
                screen.blit(bot_letter_text, bot_letter_rect)

            # draw empty box if not unlocked
            else:
                pygame.draw.rect(screen, all_bots[i]["bot"].box_background_color, (180, 40 + i * 80, 80, 80))

            # line between buttons
            if i != 0:
                pygame.draw.line(screen, (255, 255, 255), (180, 40 + i * 80), (260, 40 + i * 80), 3)

        # shop nav bar outline
        pygame.draw.rect(screen, (255, 255, 255), (180, 40, 80, 560), 3)

def draw_shop_text(menu_canvas, font_cache, text_cache, text, max_width, color, center_x, center_y):
    # draw text on the shop menu
    text_label = dynamic_text(font_cache, text_cache, text, max_width, 40, color)
    text_rect = text_label.get_rect(center=(center_x, center_y))
    menu_canvas.blit(text_label, text_rect)

def draw_shop_menu(screen, mouse_pos, fonts, font_cache, text_cache, all_bots, bot_upgrades, battle_state, menu_height, menu_scroll_y, gears, rounds):
    if battle_state == "Shop":
        # get mouse position relative to shop menu
        mouse_pos = (mouse_pos[0] - 257, mouse_pos[1] - 40 + menu_scroll_y)

        # calculate the shop menu height
        menu_height = 0
        for bot in all_bots:
            if bot["unlocked"]:
                menu_height += len(bot_upgrades[bot["bot"].name]) * 90 + 100
            else:
                menu_height += 90

        # create a surface for the shop menu
        menu_canvas = pygame.Surface((760, menu_height))

        menu_y = 0
        for i, bot in enumerate(all_bots):
            # draw bot and its upgrades if unlocked
            if bot["unlocked"]:
                # background box for each bot and its upgrades
                pygame.draw.rect(menu_canvas, bot["bot"].box_background_color, (0, menu_y, 760, len(bot_upgrades[bot["bot"].name]) * 90 + 100))

                # bot name title
                bot_name_text = render_text(fonts, text_cache, 40, bot["bot"].name, (255, 255, 255))
                bot_name_rect = bot_name_text.get_rect(center=(380, menu_y + 26))
                menu_canvas.blit(bot_name_text, bot_name_rect)

                # line under bot name row
                menu_y += 50
                pygame.draw.line(menu_canvas, (255, 255, 255), (0, menu_y), (760, menu_y), 3)
                column_top_y = menu_y

                # heading row
                draw_shop_text(menu_canvas, font_cache, text_cache, "Action", 180, (255, 255, 255), 95, menu_y + 26)
                draw_shop_text(menu_canvas, font_cache, text_cache, "Buff", 180, (255, 255, 255), 285, menu_y + 26)
                draw_shop_text(menu_canvas, font_cache, text_cache, "Cost", 180, (255, 255, 255), 475, menu_y + 26)
                draw_shop_text(menu_canvas, font_cache, text_cache, "Upgrade", 180, (255, 255, 255), 665, menu_y + 26)

                # line under heading row
                menu_y += 50
                pygame.draw.line(menu_canvas, (255, 255, 255), (0, menu_y), (760, menu_y), 3)

                for upgrade in bot_upgrades[bot["bot"].name]:
                    # upgrade action
                    draw_shop_text(menu_canvas, font_cache, text_cache, upgrade["action"], 180, (255, 255, 255), 95, menu_y + 46)

                    # upgrade row if not max level
                    if upgrade["level"] < len(upgrade["cost"]):
                        cost_number = upgrade["cost"][upgrade["level"]]

                        # upgrade buff and cost
                        draw_shop_text(menu_canvas, font_cache, text_cache, upgrade["buff_desc_1"], 180, (255, 255, 255), 285, menu_y + 31)
                        draw_shop_text(menu_canvas, font_cache, text_cache, upgrade["buff_desc_2"][upgrade["level"]], 180, (255, 255, 255), 285, menu_y + 61)
                        draw_shop_text(menu_canvas, font_cache, text_cache, f"{cost_number} Gears", 180, (255, 255, 255), 475, menu_y + 46)

                        # upgrade button
                        button_rect = pygame.Rect(590, menu_y + 20, 150, 50)
                        if gears >= cost_number and button_rect.collidepoint(mouse_pos):
                            button_color = bot["bot"].button_hover_color
                        else:
                            button_color = bot["bot"].button_color
                        pygame.draw.rect(menu_canvas, button_color, button_rect)
                        if upgrade["confirm"]:
                            pygame.draw.rect(menu_canvas, (0, 255, 0), button_rect, 4)

                        # upgrade text
                        if gears >= cost_number:
                            button_text_color = (255, 255, 255)
                        else:
                            button_text_color = bot["bot"].text_used_color
                        if upgrade["confirm"]:
                            button_text = "Confirm Upgrade"
                        else:
                            button_text = "Upgrade"
                        draw_shop_text(menu_canvas, font_cache, text_cache, button_text, 140, button_text_color, 665, menu_y + 46)

                    # upgrade row if max level
                    else:
                        draw_shop_text(menu_canvas, font_cache, text_cache, "Max Level", 180, (255, 255, 255), 285, menu_y + 46)
                        draw_shop_text(menu_canvas, font_cache, text_cache, "Max Level", 180, (255, 255, 255), 475, menu_y + 46)
                        draw_shop_text(menu_canvas, font_cache, text_cache, "Max Level", 180, (255, 255, 255), 665, menu_y + 46)

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

            # draw locked bot
            else:
                # background box for locked bot
                pygame.draw.rect(menu_canvas, bot["bot"].box_background_color, (0, menu_y, 760, 90))

                # bot name title
                bot_name_text = render_text(fonts, text_cache, 40, bot["bot"].name, (255, 255, 255))
                bot_name_rect = bot_name_text.get_rect(center=(190, menu_y + 46))
                menu_canvas.blit(bot_name_text, bot_name_rect)

                # show unlock round if not available yet
                if bot["round"] > rounds:
                    draw_shop_text(menu_canvas, font_cache, text_cache, f"Available after round {bot['round'] - 1}", 380, (255, 255, 255), 475, menu_y + 46)

                # show unlock option if available
                else:
                    # bot unlock cost
                    draw_shop_text(menu_canvas, font_cache, text_cache, "Unlock Cost:", 180, (255, 255, 255), 475, menu_y + 31)
                    draw_shop_text(menu_canvas, font_cache, text_cache, f"{bot['cost']} Gears", 180, (255, 255, 255), 475, menu_y + 61)

                    # unlock button
                    button_rect = pygame.Rect(590, menu_y + 20, 150, 50)
                    if gears >= bot["cost"] and button_rect.collidepoint(mouse_pos):
                        button_color = bot["bot"].button_hover_color
                    else:
                        button_color = bot["bot"].button_color
                    pygame.draw.rect(menu_canvas, button_color, button_rect)
                    if bot["confirm"]:
                        pygame.draw.rect(menu_canvas, (0, 255, 0), button_rect, 4)

                    # unlock text
                    if gears >= bot["cost"]:
                        button_text_color = (255, 255, 255)
                    else:
                        button_text_color = bot["bot"].text_used_color
                    if bot["confirm"]:
                        button_text = "Confirm Unlock"
                    else:
                        button_text = "Unlock"
                    draw_shop_text(menu_canvas, font_cache, text_cache, button_text, 140, button_text_color, 665, menu_y + 46)

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

def draw_action_button(screen, mouse_pos, font_cache, text_cache, battle_state, active_bot, x, y, text, used, chosen, lazer_bot):
    # button rectangle
    button_rect = pygame.Rect(x, y, 150, 50)
    
    # change button color based on hover and chosen state
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
    button_text = dynamic_text(font_cache, text_cache, text, 140, 40, text_color)

    # center the text on the button
    button_text_rect = button_text.get_rect(center=button_rect.center)
    button_text_rect.y += 1

    # draw button text
    screen.blit(button_text, button_text_rect)

def draw_action_box(screen, mouse_pos, font_cache, text_cache, battle_state, active_bot, chosen_action, lazer_bot):
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
            draw_action_button(screen, mouse_pos, font_cache, text_cache, battle_state, active_bot, x, 640, action["name"], action["used"], chosen_action == action["name"], lazer_bot)

# ------------------------------
# DRAWING LORE BOX AND TEXT
# ------------------------------

def draw_lore_box(screen, fonts, text_cache, battle_state, inspecting_character, lore_scroll_y, rounds):
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
        inspecting_character.lore_text(fonts, lore)

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
        lore_text = render_text(fonts, text_cache, 24, line, (255, 255, 255))
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

def draw_laser(screen, mouse_pos, enemy_goons, battle_state, active_bot):
    if battle_state == "Target Line" and not active_bot.actions[0]["movement_mode"]:
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

def draw_effects(screen, fonts, text_cache, active_effects):
    # draw animation based on its type
    for effect in active_effects:
        # draw floating text
        if isinstance(effect, FloatingText):
            floating_text = render_text(fonts, text_cache, 30, effect.text, effect.color)
            screen.blit(floating_text, (effect.x, effect.y))

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
# DRAWING SCREEN
# ------------------------------

def draw_screen(screen, fonts, font_cache, text_cache, all_bots, bot_upgrades, player_bots, enemy_goons, active_effects, battle_state, active_bot, chosen_action, inspecting_character, lore_scroll_y, menu_height, menu_scroll_y, gears, rounds, gun_bot, elemental_bot, lazer_bot):
    # background color
    screen.fill((0, 0, 0))

    # get mouse position for hover effects
    mouse_pos = pygame.mouse.get_pos()

    # draw bots and goons with animations based on their states and actions
    draw_characters(screen, fonts, text_cache, player_bots, enemy_goons, active_bot, chosen_action, inspecting_character)

    # draw bots and goons status effects
    draw_character_status_effects(screen, mouse_pos, fonts, text_cache, player_bots, enemy_goons, battle_state, elemental_bot, lazer_bot)

    # draw gun bot aiming box if it is unlocked and chosen
    draw_gun_aiming(screen, font_cache, text_cache, active_bot, chosen_action, gun_bot)

    # draw shop box above action box
    draw_shop_box(screen, mouse_pos, fonts, font_cache, text_cache, battle_state, active_bot, gears, rounds, lazer_bot)

    # draw shop bar and menu if opened
    draw_shop_bar(screen, mouse_pos, fonts, text_cache, all_bots, battle_state)
    menu_height = draw_shop_menu(screen, mouse_pos, fonts, font_cache, text_cache, all_bots, bot_upgrades, battle_state, menu_height, menu_scroll_y, gears, rounds)

    # draw action options based on active bot and chosen action
    draw_action_box(screen, mouse_pos, font_cache, text_cache, battle_state, active_bot, chosen_action, lazer_bot)

    # draw lore box with scrolling
    lore_height = draw_lore_box(screen, fonts, text_cache, battle_state, inspecting_character, lore_scroll_y, rounds)

    # draw laser beam if lazer bot is using its pierce
    draw_laser(screen, mouse_pos, enemy_goons, battle_state, active_bot)
    
    # draw effects damage or heal numbers or projectiles
    draw_effects(screen, fonts, text_cache, active_effects)

    # temp box
    if active_bot:
        temp_box_color = active_bot.box_background_color
    else:
        temp_box_color = (50, 50, 50)
    pygame.draw.rect(screen, temp_box_color, (20, 620, 60, 90))
    pygame.draw.rect(screen, (255, 255, 255), (20, 620, 60, 90), 3)

    return lore_height, menu_height
