# battle.py

# import libraries
import pygame
import random

# import game modules
from .helper import dynamic_text, render_text
from .effects import FloatingText

# ------------------------------
# BOTTOM BOXES
# ------------------------------

class ActionBox:
    def __init__(self):
        self.buttons = [
            pygame.Rect(120, 640, 150, 50), # left button
            pygame.Rect(290, 640, 150, 50)  # right button
        ]

    def handle_event(self, event, battle_state, active_bot, chosen_action, inspecting_character, lore_scroll, lore_target_scroll):
        if active_bot:
            action = None

            # correspond the mouse clicks to the action buttons
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i in range(len(active_bot.actions)):
                    if self.buttons[i].collidepoint(event.pos):
                        action = active_bot.actions[i]

            # correspond the key presses to the action buttons
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    action = active_bot.actions[0]
                elif event.key == pygame.K_2 and len(active_bot.actions) > 1:
                    action = active_bot.actions[1]

            # if action click or press is valid and not used, update states
            if action and not action["used"]:

                # action is deselected if already chosen
                if chosen_action == action["name"]:
                    chosen_action = None
                    battle_state = "Player Turn"
                
                # action is selected
                else:
                    chosen_action = action["name"]
                    battle_state = action["target_state"]
                    lore_target_scroll = action["scroll"]

                # if inspecting something else, switch inspecting to active bot when action is chosen
                if inspecting_character != active_bot:
                    inspecting_character = active_bot
                    lore_scroll = action["scroll"]
                    lore_target_scroll = action["scroll"]

        return battle_state, chosen_action, inspecting_character, lore_scroll, lore_target_scroll

    def draw(self, screen, font_cache, text_cache, battle_state, active_bot, chosen_action):
        # draw action box background
        if active_bot:
            box_color = active_bot.box_background_color
        else:
            box_color = (50, 50, 50)
        pygame.draw.rect(screen, box_color, (100, 620, 360, 90))
        pygame.draw.rect(screen, (255, 255, 255), (100, 620, 360, 90), 3)

        # draw action buttons based on active bot
        mouse_pos = pygame.mouse.get_pos()
        if active_bot:
            for i, action in enumerate(active_bot.actions):

                # draw action button
                if battle_state not in ["Shop", "Lazer Movement"]:
                    if self.buttons[i].collidepoint(mouse_pos) and chosen_action == action["name"]:
                        button_color = (255, 125, 125)
                    elif self.buttons[i].collidepoint(mouse_pos) and not action["used"]:
                        button_color = active_bot.button_hover_color
                    else:
                        button_color = active_bot.button_color
                else:
                    button_color = active_bot.button_color
                pygame.draw.rect(screen, button_color, self.buttons[i])

                # draw action button text
                if chosen_action == action["name"]:
                    text = f"Cancel {action['name']}"
                    pygame.draw.rect(screen, (0, 255, 0), self.buttons[i], 4)
                else:
                    text = action["name"]
                if not action["used"]:
                    text_color = (255, 255, 255)
                else:
                    text_color = active_bot.text_used_color
                button_text = dynamic_text(font_cache, text_cache, text, 140, 40, text_color)
                button_text_rect = button_text.get_rect(center=self.buttons[i].center)
                button_text_rect.y += 1
                screen.blit(button_text, button_text_rect)

class LoreBox:
    def __init__(self):
        self.lore_rect = pygame.Rect(600, 620, 580, 90)

    def handle_event(self, event, lore_height, lore_target_scroll):
        # scroll through the lore box if mouse is scrolled over it
        mouse_pos = pygame.mouse.get_pos()
        if self.lore_rect.collidepoint(mouse_pos):
        
            # scroll up (text moves down)
            if event.button == 4:
                lore_target_scroll = max(0, lore_target_scroll - 30)
            
            # scroll down (text moves up)
            elif event.button == 5:
                max_scroll = max(0, lore_height - 80)
                lore_target_scroll = min(max_scroll, lore_target_scroll + 30)
            
        return lore_target_scroll

    def update(self, lore_scroll, lore_target_scroll):
        # update scrolling position for lore box
        lore_scroll += (lore_target_scroll - lore_scroll) * 0.2
        if abs(lore_target_scroll - lore_scroll) < 0.1:
            lore_scroll = lore_target_scroll
        return lore_scroll

    def draw(self, screen, fonts, text_cache, battle_state, inspecting_character, lore_height, lore_scroll, rounds):
        # draw lore box background
        if inspecting_character:
            box_color = inspecting_character.box_background_color
        else:
            box_color = (50, 50, 50)
        pygame.draw.rect(screen, box_color, self.lore_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.lore_rect, 3)

        # get lore text based on battle state or inspecting character
        lore = []
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
        visible_rect = pygame.Rect(0, int(lore_scroll), 580, 80)
        screen.blit(lore_canvas, (610, 625), visible_rect)

        return lore_height

# ------------------------------
# SHOP STUFF
# ------------------------------

class ShopBox:
    def __init__(self):
        self.shop_button_rect = pygame.Rect(40, 530, 100, 50)

    def handle_event(self, event, all_bots, bot_upgrades, battle_state, previous_battle_state):
        # dont open shop during lazer movement
        if battle_state == "Lazer Movement":
            return battle_state, previous_battle_state
        
        if self.shop_button_rect.collidepoint(event.pos):

            # close shop
            if battle_state == "Shop":
                battle_state = previous_battle_state

                # reset all unlock and upgrades confirmations
                for bot in all_bots:
                    bot["confirm"] = False
                    for upgrade in bot_upgrades[bot["bot"].name]:
                        upgrade["confirm"] = False

            # open shop
            else:
                previous_battle_state = battle_state
                battle_state = "Shop"
        
        return battle_state, previous_battle_state

    def draw(self, screen, fonts, font_cache, text_cache, battle_state, active_bot, gears, rounds):
        # draw shop box background
        if active_bot:
            box_color = active_bot.box_background_color
        else:
            box_color = (50, 50, 50)
        pygame.draw.rect(screen, box_color, (20, 510, 140, 90))
        pygame.draw.rect(screen, (255, 255, 255), (20, 510, 140, 90), 3)

        # draw shop button
        mouse_pos = pygame.mouse.get_pos()
        if self.shop_button_rect.collidepoint(mouse_pos) and battle_state not in ["Game Over", "Lazer Movement"]:
            if battle_state == "Shop":
                button_color = (255, 125, 125)
            elif active_bot:
                button_color = active_bot.button_hover_color
            else:
                button_color = (200, 200, 200)
        else:
            if active_bot:
                button_color = active_bot.button_color
            else:
                button_color = (150, 150, 150)
        pygame.draw.rect(screen, button_color, self.shop_button_rect)

        # draw shop button text
        if battle_state == "Shop":
            text = "Close Shop"
        else:
            text = "Shop"
        button_text = dynamic_text(font_cache, text_cache, text, 90, 40, (255, 255, 255))
        button_text_rect = button_text.get_rect(center=(90, 555))
        screen.blit(button_text, button_text_rect)

        # draw info box background
        pygame.draw.rect(screen, box_color, (20, 453, 140, 60))
        pygame.draw.rect(screen, (255, 255, 255), (20, 453, 140, 60), 3)
    
        # draw round text
        round_text = render_text(fonts, text_cache, 24, f"Round: {rounds}", (255, 255, 255))
        round_text_rect = round_text.get_rect(center=(90, 473))
        screen.blit(round_text, round_text_rect)

        # draw gears text
        gears_text = render_text(fonts, text_cache, 24, f"Gears: {gears}", (255, 255, 255))
        gears_text_rect = gears_text.get_rect(center=(90, 493))
        screen.blit(gears_text, gears_text_rect)

class ShopBar:
    def handle_event(self, event, all_bots, bot_upgrades, menu_height, menu_target_scroll):
        for i in range(len(all_bots)):
            bar_bot_rect = pygame.Rect(180, 40 + i * 80, 80, 80)
    
            # scroll to the bot's section if it is unlocked
            if bar_bot_rect.collidepoint(event.pos) and all_bots[i]["unlocked"]:
                jump_y = 0
                for j in range(i):
                    if all_bots[j]["unlocked"]:
                        jump_y += len(bot_upgrades[all_bots[j]["bot"].name]) * 90 + 100
                    else:
                        jump_y += 90
                menu_target_scroll = min(menu_height - 560, jump_y)
                break
    
        return menu_target_scroll

    def draw(self, screen, fonts, text_cache, all_bots, battle_state):
        if battle_state == "Shop":
            for i in range(len(all_bots)):

                # draw bot button if unlocked
                if all_bots[i]["unlocked"]:
    
                    # draw bot button
                    mouse_pos = pygame.mouse.get_pos()
                    button_rect = pygame.Rect(180, 40 + i * 80, 80, 80)
                    if button_rect.collidepoint(mouse_pos):
                        button_color = all_bots[i]["bot"].button_color
                    else:
                        button_color = all_bots[i]["bot"].box_background_color
                    pygame.draw.rect(screen, button_color, button_rect)
    
                    # draw bot's first letter of name
                    bot_letter_text = render_text(fonts, text_cache, 40, all_bots[i]["bot"].name[0], (255, 255, 255))
                    bot_letter_rect = bot_letter_text.get_rect(center=(220, 80 + i * 80))
                    screen.blit(bot_letter_text, bot_letter_rect)
    
                # draw empty box if not unlocked
                else:
                    pygame.draw.rect(screen, all_bots[i]["bot"].box_background_color, (180, 40 + i * 80, 80, 80))
    
                # draw line between buttons
                if i != 0:
                    pygame.draw.line(screen, (255, 255, 255), (180, 40 + i * 80), (260, 40 + i * 80), 3)
    
            # draw shop nav bar outline
            pygame.draw.rect(screen, (255, 255, 255), (180, 40, 80, 560), 3)

class ShopMenu:
    def __init__(self):
        self.menu_rect = pygame.Rect(257, 40, 760, 560)

    def handle_event_scroll(self, event, battle_state, menu_height, menu_target_scroll):
        if battle_state == "Shop":
        
            # scroll through the shop menu if mouse is scrolled over it
            mouse_pos = pygame.mouse.get_pos()
            if self.menu_rect.collidepoint(mouse_pos):
            
                # scroll up (text moves down)
                if event.button == 4:
                    menu_target_scroll = max(0, menu_target_scroll - 60)
                
                # scroll down (text moves up)
                elif event.button == 5:
                    max_scroll_index = max(0, menu_height - 560)
                    menu_target_scroll = min(max_scroll_index, menu_target_scroll + 60)
        
        return menu_target_scroll

    def handle_event_click(self, event, all_bots, bot_upgrades, player_bots, enemy_goons, active_effects, previous_battle_state, menu_scroll, gears, rounds):
        # adjust mouse position based on menu scroll
        mouse_pos = (event.pos[0] - 257, event.pos[1] - 40 + menu_scroll)

        menu_y = 0
        for bot in all_bots:

            # handle bot upgrades
            if bot["unlocked"]:
                menu_y += 100
                for upgrade in bot_upgrades[bot["bot"].name]:

                    # upgrade button rectangle
                    upgrade_button_rect = pygame.Rect(590, menu_y + 20, 150, 50)
                    menu_y += 90

                    if upgrade_button_rect.collidepoint(mouse_pos) and upgrade["level"] < len(upgrade["cost"]) and gears >= upgrade["cost"][upgrade["level"]]:

                        # upgrade bot action if confirmed
                        if upgrade["confirm"]:
                            i = upgrade["action_number"]
                            bot["bot"].actions[i][upgrade["stat"]] = upgrade["amount"][upgrade["level"]]

                            # if the upgrade is for barrage, check if barrage can be used with the new charge needed value
                            if upgrade["stat"] == "barrage_charge_needed" and bot["bot"].actions[i]["barrage_charge"] >= bot["bot"].actions[i]["barrage_charge_needed"] and bot["bot"].actions[i]["used"]:
                                bot["bot"].actions[i]["used"] = False
                                active_effects.append(FloatingText((255, 50, 255), bot["bot"].rect.x, bot["bot"].rect.top - 20, "Barrage Ready!"))
                            
                            # if the upgrade is for ice hits needed, freeze the enemies if they have enough ice hits with the new ice hits needed value
                            if upgrade["stat"] == "ice_hits_needed":
                                for enemy in enemy_goons:
                                    if enemy.real_health > 0 and enemy.ice_hits >= bot["bot"].actions[i]["ice_hits_needed"]:
                                        enemy.frozen = True
                                        enemy.ice_hits = 0
                                        text = "Frozen!"
                                        text_width = len(text) * 10
                                        text_x = random.randint(enemy.rect.left, enemy.rect.right - text_width)
                                        active_effects.append(FloatingText((0, 255, 255), text_x, enemy.rect.top + 10, text))

                            # if the upgrade is for mark hits needed, mark the enemies if they have enough mark hits with the new mark hits needed value
                            if upgrade["stat"] == "mark_hits_needed":
                                for enemy in enemy_goons:
                                    if enemy.real_health > 0 and enemy.mark_hits >= bot["bot"].actions[i]["mark_hits_needed"]:
                                        enemy.marked = True
                                        enemy.mark_hits = 0
                                        text = "Marked!"
                                        text_width = len(text) * 10
                                        text_x = random.randint(enemy.rect.left, enemy.rect.right - text_width)
                                        active_effects.append(FloatingText((255, 255, 0), text_x, enemy.rect.top + 10, text))

                            # update data
                            gears -= upgrade["cost"][upgrade["level"]]
                            upgrade["level"] += 1
                            upgrade["confirm"] = False

                        # set confirm to true if not confirmed yet and reset all other confirmations
                        else:
                            for b in all_bots:
                                b["confirm"] = False
                                for u in bot_upgrades[b["bot"].name]:
                                    u["confirm"] = False
                            upgrade["confirm"] = True
                        
                        return previous_battle_state, gears

            # handle bot unlock
            else:

                # unlock button rectangle
                unlock_button_rect = pygame.Rect(590, menu_y + 20, 150, 50)
                menu_y += 90

                if unlock_button_rect.collidepoint(mouse_pos) and rounds >= bot["round"] and gears >= bot["cost"]:

                    # unlock bot if confirmed
                    if bot["confirm"]:
                        gears -= bot["cost"]
                        bot["unlocked"] = True
                        player_bots.append(bot["bot"])
                        if previous_battle_state == "Player Turn Over":
                            previous_battle_state = "Player Turn"

                    # set confirm to true if not confirmed yet and reset all other confirmations
                    else:
                        for b in all_bots:
                            b["confirm"] = False
                            for u in bot_upgrades[b["bot"].name]:
                                u["confirm"] = False
                        bot["confirm"] = True

                    return previous_battle_state, gears

        return previous_battle_state, gears

    def update(self, menu_scroll, menu_target_scroll):
        # update scrolling position for shop menu
        menu_scroll += (menu_target_scroll - menu_scroll) * 0.2
        if abs(menu_target_scroll - menu_scroll) < 0.1:
            menu_scroll = menu_target_scroll
        return menu_scroll

    def draw_text(self, menu_canvas, font_cache, text_cache, text, max_width, color, center_x, center_y):
        # draw text on the shop menu
        text_label = dynamic_text(font_cache, text_cache, text, max_width, 40, color)
        text_rect = text_label.get_rect(center=(center_x, center_y))
        menu_canvas.blit(text_label, text_rect)

    def draw(self, screen, fonts, font_cache, text_cache, all_bots, bot_upgrades, battle_state, menu_height, menu_scroll, gears, rounds):
        if battle_state == "Shop":

            # get mouse position relative to shop menu
            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = (mouse_pos[0] - 257, mouse_pos[1] - 40 + menu_scroll)

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

                    # draw background box for each bot and its upgrades
                    pygame.draw.rect(menu_canvas, bot["bot"].box_background_color, (0, menu_y, 760, len(bot_upgrades[bot["bot"].name]) * 90 + 100))

                    # draw bot name title
                    bot_name_text = render_text(fonts, text_cache, 40, bot["bot"].name, (255, 255, 255))
                    bot_name_rect = bot_name_text.get_rect(center=(380, menu_y + 26))
                    menu_canvas.blit(bot_name_text, bot_name_rect)

                    # draw line under bot name row
                    menu_y += 50
                    pygame.draw.line(menu_canvas, (255, 255, 255), (0, menu_y), (760, menu_y), 3)
                    column_top_y = menu_y

                    # draw heading row
                    self.draw_text(menu_canvas, font_cache, text_cache, "Action", 180, (255, 255, 255), 95, menu_y + 26)
                    self.draw_text(menu_canvas, font_cache, text_cache, "Buff", 180, (255, 255, 255), 285, menu_y + 26)
                    self.draw_text(menu_canvas, font_cache, text_cache, "Cost", 180, (255, 255, 255), 475, menu_y + 26)
                    self.draw_text(menu_canvas, font_cache, text_cache, "Upgrade", 180, (255, 255, 255), 665, menu_y + 26)

                    # draw line under heading row
                    menu_y += 50
                    pygame.draw.line(menu_canvas, (255, 255, 255), (0, menu_y), (760, menu_y), 3)

                    # draw each upgrade row
                    for upgrade in bot_upgrades[bot["bot"].name]:

                        # draw upgrade action name
                        self.draw_text(menu_canvas, font_cache, text_cache, upgrade["action"], 180, (255, 255, 255), 95, menu_y + 46)

                        # draw upgrade row if not max level
                        if upgrade["level"] < len(upgrade["cost"]):
                            cost_number = upgrade["cost"][upgrade["level"]]

                            # draw upgrade buff and cost
                            self.draw_text(menu_canvas, font_cache, text_cache, upgrade["buff_desc_1"], 180, (255, 255, 255), 285, menu_y + 31)
                            self.draw_text(menu_canvas, font_cache, text_cache, upgrade["buff_desc_2"][upgrade["level"]], 180, (255, 255, 255), 285, menu_y + 61)
                            self.draw_text(menu_canvas, font_cache, text_cache, f"{cost_number} Gears", 180, (255, 255, 255), 475, menu_y + 46)

                            # draw upgrade button
                            button_rect = pygame.Rect(590, menu_y + 20, 150, 50)
                            if gears >= cost_number and button_rect.collidepoint(mouse_pos):
                                button_color = bot["bot"].button_hover_color
                            else:
                                button_color = bot["bot"].button_color
                            pygame.draw.rect(menu_canvas, button_color, button_rect)
                            if upgrade["confirm"]:
                                pygame.draw.rect(menu_canvas, (0, 255, 0), button_rect, 4)

                            # draw upgrade button text
                            if gears >= cost_number:
                                button_text_color = (255, 255, 255)
                            else:
                                button_text_color = bot["bot"].text_used_color
                            if upgrade["confirm"]:
                                button_text = "Confirm Upgrade"
                            else:
                                button_text = "Upgrade"
                            self.draw_text(menu_canvas, font_cache, text_cache, button_text, 140, button_text_color, 665, menu_y + 46)

                        # draw upgrade row if max level
                        else:
                            self.draw_text(menu_canvas, font_cache, text_cache, "Max Level", 180, (255, 255, 255), 285, menu_y + 46)
                            self.draw_text(menu_canvas, font_cache, text_cache, "Max Level", 180, (255, 255, 255), 475, menu_y + 46)
                            self.draw_text(menu_canvas, font_cache, text_cache, "Max Level", 180, (255, 255, 255), 665, menu_y + 46)

                        # draw line under upgrade row
                        menu_y += 90
                        pygame.draw.line(menu_canvas, (255, 255, 255), (0, menu_y), (760, menu_y), 3)

                    # draw column lines
                    pygame.draw.line(menu_canvas, (255, 255, 255), (190, column_top_y), (190, menu_y), 3)
                    pygame.draw.line(menu_canvas, (255, 255, 255), (380, column_top_y), (380, menu_y), 3)
                    pygame.draw.line(menu_canvas, (255, 255, 255), (570, column_top_y), (570, menu_y), 3)

                    # draw line before bot name row
                    if i != 0:
                        pygame.draw.line(menu_canvas, (255, 255, 255), (0, column_top_y - 50), (760, column_top_y - 50), 3)

                # draw locked bots
                else:

                    # draw background box for locked bot
                    pygame.draw.rect(menu_canvas, bot["bot"].box_background_color, (0, menu_y, 760, 90))

                    # draw bot name title
                    bot_name_text = render_text(fonts, text_cache, 40, bot["bot"].name, (255, 255, 255))
                    bot_name_rect = bot_name_text.get_rect(center=(190, menu_y + 46))
                    menu_canvas.blit(bot_name_text, bot_name_rect)

                    # draw unlock round if not available yet
                    if bot["round"] > rounds:
                        self.draw_text(menu_canvas, font_cache, text_cache, f"Available after round {bot['round'] - 1}", 380, (255, 255, 255), 475, menu_y + 46)

                    # draw unlock option if available
                    else:

                        # draw bot unlock cost
                        self.draw_text(menu_canvas, font_cache, text_cache, "Unlock Cost:", 180, (255, 255, 255), 475, menu_y + 31)
                        self.draw_text(menu_canvas, font_cache, text_cache, f"{bot['cost']} Gears", 180, (255, 255, 255), 475, menu_y + 61)

                        # draw unlock button
                        button_rect = pygame.Rect(590, menu_y + 20, 150, 50)
                        if gears >= bot["cost"] and button_rect.collidepoint(mouse_pos):
                            button_color = bot["bot"].button_hover_color
                        else:
                            button_color = bot["bot"].button_color
                        pygame.draw.rect(menu_canvas, button_color, button_rect)
                        if bot["confirm"]:
                            pygame.draw.rect(menu_canvas, (0, 255, 0), button_rect, 4)

                        # draw unlock button text
                        if gears >= bot["cost"]:
                            button_text_color = (255, 255, 255)
                        else:
                            button_text_color = bot["bot"].text_used_color
                        if bot["confirm"]:
                            button_text = "Confirm Unlock"
                        else:
                            button_text = "Unlock"
                        self.draw_text(menu_canvas, font_cache, text_cache, button_text, 140, button_text_color, 665, menu_y + 46)

                    # draw line before unlock row
                    menu_y += 90
                    pygame.draw.line(menu_canvas, (255, 255, 255), (0, menu_y - 90), (760, menu_y - 90), 3)

            # draw the visible part of the shop menu onto the screen based on scroll position
            visible_rect = pygame.Rect(0, int(menu_scroll), 760, 560)
            screen.blit(menu_canvas, (257, 40), visible_rect)
            
            # draw shop menu outline
            pygame.draw.rect(screen, (255, 255, 255), self.menu_rect, 3)

        return menu_height

# ------------------------------
# CHARACTER ZONES
# ------------------------------

class PlayerZone:
    def handle_event(self, event, player_bots, battle_state, active_bot, chosen_action, inspecting_character, lore_scroll, lore_target_scroll):
        # dont allow selecting or deselecting bots if targeting a bot or if the battle is over
        if battle_state in ["Target Bot", "Target Any", "Victory"]:
            return battle_state, active_bot, chosen_action, inspecting_character, lore_scroll, lore_target_scroll

        # handle valid bot selection or deselection
        for bot in player_bots:
            if bot.rect.collidepoint(event.pos) and bot.real_health > 0 and not bot.acted:

                # bot is deselected if already active
                if active_bot == bot:

                    # if lazer bot or duplo bot is active and their first action is chosen, that bot can't be deselected by clicking on itself
                    if (active_bot.name == "Lazer Bot" and chosen_action == "Pierce") or (active_bot.name == "Duplo Bot" and chosen_action == "Charge"):
                        break

                    # bot is deselected
                    active_bot = None
                    inspecting_character = None

                # bot is selected
                else:
                    active_bot = bot
                    inspecting_character = bot
                    lore_scroll = 0
                    lore_target_scroll = 0

                # reset states
                battle_state = "Player Turn"
                chosen_action = None
                break

        return battle_state, active_bot, chosen_action, inspecting_character, lore_scroll, lore_target_scroll

    def update(self, player_bots, battle_state, active_bot, chosen_action):
        # update bot animations
        for bot in player_bots:
            bot.hurt_animations()
            bot.update_idle_animation()

        # update gun aiming if active
        player_bots[0].update_gun_aiming(active_bot, chosen_action)

        # update lazer bot position if in movement mode
        if battle_state == "Lazer Movement":
            mouse_pos_y = pygame.mouse.get_pos()[1]
            active_bot.rect.centery = max(1, min(730, mouse_pos_y))

    def draw(self, screen, fonts, text_cache, player_bots, battle_state, active_bot, chosen_action, inspecting_character):
        # draw player bots
        for bot in player_bots:
            bot.draw(screen, fonts, text_cache, battle_state, active_bot, chosen_action, inspecting_character)

class EnemyZone:
    def handle_event(self, event, enemy_slots, enemy_goons, active_effects, battle_state, inspecting_character, lore_scroll, lore_target_scroll, gears):
        # handle valid goon selection or deselection
        for i in range(len(enemy_goons) - 1, -1, -1):
            goon = enemy_goons[i]
            if goon.rect.collidepoint(event.pos):

                # if goon alive and not being targeted, inspect
                if goon.real_health > 0 and battle_state not in ["Target Enemy", "Target Enemy or Self", "Target Any"]:

                    # goon inspection is deselected if already being inspected
                    if inspecting_character == goon:
                        inspecting_character = None

                    # goon inspection is selected
                    else:
                        inspecting_character = goon
                        lore_scroll = 0
                        lore_target_scroll = 0
                    break

                # if goon dead, harvest
                elif goon.visual_health == 0:

                    # harvest gears from dead goons
                    enemy_gears = random.randint(goon.min_gears, goon.max_gears)
                    gears += enemy_gears
                    active_effects.append(FloatingText((100, 100, 100), goon.rect.left, goon.rect.centery, f"+{enemy_gears} gears"))
                    
                    # remove goon from the game
                    enemy_slots[goon.slot_id]["occupied"] = False
                    enemy_goons.pop(i)
                    break

        return inspecting_character, lore_scroll, lore_target_scroll, gears

    def spawn_goons(self, enemy_slots, enemy_types, enemy_goons, active_effects, gears, rounds, max_enemies):
        # determine how many enemies to spawn based on the round
        spawns = 0
        if rounds <= 10:
            spawns = 1
        else:
            spawns = 2
        
        # increase the max number of enemies every 5 rounds, up to a maximum of 9
        if max_enemies < 9 and rounds % 5 == 0:
            max_enemies += 1
        
        for _ in range(spawns):
            
            # auto harvest gears and remove dead goons if there are max number of enemies on the field
            if len(enemy_goons) == max_enemies:
                for i in range(len(enemy_goons) - 1, -1, -1):
                    enemy = enemy_goons[i]
                    if enemy.visual_health == 0:

                        # harvest gears from dead goons
                        enemy_gears = random.randint(enemy.min_gears, enemy.max_gears)
                        gears += enemy_gears
                        active_effects.append(FloatingText((100, 100, 100), enemy.rect.left, enemy.rect.centery, f"+{enemy_gears} gears"))
                        
                        # remove goon from the game
                        enemy_slots[enemy.slot_id]["occupied"] = False
                        enemy_goons.pop(i)
                        break
            
            # spawn new enemies if there are empty slots
            if len(enemy_goons) < max_enemies:
    
                # find empty slots
                empty_slots = []
                for i, slot in enumerate(enemy_slots):
                    if not slot["occupied"]:
                        empty_slots.append(i)
                
                if empty_slots:

                    # choose a random empty slot
                    slot_id = random.choice(empty_slots)
                    slot = enemy_slots[slot_id]
                    slot["occupied"] = True
    
                    # random offsets for the goon spawn position
                    x_offset = random.randint(0, 100)
                    y_offset = random.randint(40, 100)
    
                    # spawn a random goon
                    random_type = random.randint(0, len(enemy_types) - 1)
                    enemy_type = enemy_types[random_type]
                    new_enemy = enemy_type(
                        slot["x"] + x_offset,
                        slot["y"] + y_offset,
                        slot_id)
                    enemy_goons.append(new_enemy)
        
        return gears, max_enemies

    def update(self, enemy_goons):
        # update goon animations
        for goon in enemy_goons:
            goon.hurt_animations()
            goon.update_idle_animation()

    def draw(self, screen, fonts, text_cache, enemy_goons, battle_state, inspecting_character, elemental_bot):
        # draw enemy goons
        for goon in enemy_goons:
            goon.draw(screen, fonts, text_cache, battle_state, inspecting_character, elemental_bot)

class Execution:
    def execute_action(self, event, player_bots, enemy_goons, active_effects, battle_state, active_bot, chosen_action, inspecting_character):
        # find who can be targeted
        if battle_state == "Target Bot":
            characters = player_bots
        elif battle_state == "Target Enemy":
            characters = enemy_goons
        elif battle_state in ["Target Enemy or Self", "Target Any"]:
            characters = player_bots + enemy_goons
        else:
            return battle_state, active_bot, chosen_action, inspecting_character
        
        for char in characters:
            if char.rect.collidepoint(event.pos) and char.real_health > 0:
                
                # perform the action chosen on the target character
                if chosen_action == "Barrage":
                    active_bot.perform_action(active_effects, enemy_goons, chosen_action, None)
                else:
                    active_bot.perform_action(active_effects, char, chosen_action)
                
                # reset for next action
                active_bot.check_actions(chosen_action)
                active_bot = None
                chosen_action = None
                inspecting_character = None

                # check if all bots finished their actions
                battle_state = "Player Turn Over"
                for bot in player_bots:
                    if bot.real_health > 0 and not bot.acted:
                        battle_state = "Player Turn"
                        break
                break

        return battle_state, active_bot, chosen_action, inspecting_character

    def execute_laser_action(self, event, player_bots, enemy_goons, active_effects, battle_state, active_bot, chosen_action, inspecting_character):
        # bot enters and exits movement mode when clicked on
        if battle_state == "Target Line" and active_bot.rect.collidepoint(event.pos):
            battle_state = "Lazer Movement"
        elif battle_state == "Lazer Movement" and active_bot.rect.collidepoint(event.pos):
            battle_state = "Target Line"
        
        # perform pierce action if lazer bot is not moving and mouse is clicked to the right of lazer bot
        elif battle_state == "Target Line" and event.pos[0] > active_bot.rect.centerx + active_bot.actions[0]["projectile_offset"][0]:

            # calculate the start position, end position, and direction of the laser beam based on the mouse position and lazer bot's position
            start_x = active_bot.rect.centerx + active_bot.actions[0]["projectile_offset"][0]
            start_y = active_bot.rect.centery + active_bot.actions[0]["projectile_offset"][1]
            direction_x = event.pos[0] - start_x
            direction_y = event.pos[1] - start_y
            length = (direction_x ** 2 + direction_y ** 2) ** 0.5
            end_x = start_x + direction_x / length * 1000
            end_y = start_y + direction_y / length * 1000

            # find all enemies hit by the laser beam
            enemies_hit = []
            for enemy in enemy_goons:
                if enemy.real_health > 0 and enemy.rect.clipline(start_x, start_y, end_x, end_y):
                    enemies_hit.append(enemy)
            active_bot.perform_action(active_effects, enemies_hit, chosen_action, (end_x, end_y))

            # reset for next action
            active_bot.check_actions(chosen_action)
            active_bot = None
            chosen_action = None
            inspecting_character = None

            # check if all bots finished their actions
            battle_state = "Player Turn Over"
            for bot in player_bots:
                if bot.real_health > 0 and not bot.acted:
                    battle_state = "Player Turn"
                    break

        return battle_state, active_bot, chosen_action, inspecting_character

    def execute_enemy_attacks(self, player_bots, enemy_goons, active_effects, battle_state):
        if battle_state == "Enemy Turn":
            for goon in enemy_goons:
                if goon.real_health > 0:

                    # skip the enemy turn if frozen
                    if goon.frozen:
                        continue
                    
                    # attack a random alive bot
                    bots_alive = []
                    for bot in player_bots:
                        if bot.real_health > 0:
                            bots_alive.append(bot)
                    if bots_alive:
                        target = random.choice(bots_alive)
                        goon.perform_attack(active_effects, target)

            battle_state = "Enemy Turn Over"
        return battle_state

    def round_end(self, player_bots, enemy_goons, active_effects, battle_state, gears, rounds, gun_bot, elemental_bot):
        # does fire damage to characters on fire
        for char in player_bots + enemy_goons:
            if char.real_health > 0 and char.fire_rounds > 0:
                char.fire_rounds -= 1
                if char in player_bots:
                    damage, reduction = char.damage_amount(1)
                    char.real_health -= damage
                    char.take_damage(active_effects, damage, reduction)
                elif char in enemy_goons:
                    damage, reduction = char.damage_amount(elemental_bot.actions[0]["damage"])
                    char.real_health -= damage
                    char.take_damage(active_effects, damage, reduction)
        
        # resets for next turn
        for bot in player_bots:
            bot.reset_actions()
        for char in player_bots + enemy_goons:
            char.frozen = False
            char.marked = False
            char.block = 0
            char.shield = 0
        gun_bot.reset_gun_aiming()
        battle_state = "Player Turn"
        rounds += 1

        # bonus gears every 10 rounds
        if rounds % 10 == 0:
            if rounds <= 50:
                gears += 10
                bonus_text = "Bonus Gears: 10"
            else:
                gears += 20
                bonus_text = "Bonus Gears: 20"
            active_effects.append(FloatingText((255, 255, 255), 460, 350, bonus_text))

        # display round number for new round
        active_effects.append(FloatingText((255, 255, 255), 460, 300, f"Round: {rounds}"))

        return battle_state, gears, rounds
