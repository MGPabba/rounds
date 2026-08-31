import pygame
import random

# import game modules
from .helper import FloatingText
from .projectiles import LinearProjectile
from .characters import Enemy, enemy_catalog
from .shop import all_bots, bot_upgrades
from .bots import elemental_bot, lazer_bot

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

def scroll_math(mouse_pos, event, battle_state, lore_height, lore_target_scroll_y, menu_height, menu_target_scroll_y):
    # lore rectangle
    lore_rect = pygame.Rect(600, 620, 580, 90)

    # scroll through the lore box if mouse is scrolled over it
    if lore_rect.collidepoint(mouse_pos):
        max_scroll_index = max(0, lore_height - 80)
        # scroll up (text moves down)
        if event.button == 4:
            lore_target_scroll_y = max(0, lore_target_scroll_y - 30)
        # scroll down (text moves up)
        elif event.button == 5:
            lore_target_scroll_y = min(max_scroll_index, lore_target_scroll_y + 30)

    if battle_state == "Shop":
        # menu rectangle
        menu_rect = pygame.Rect(257, 40, 760, 560)

        # scroll through the shop menu if mouse is scrolled over it
        if menu_rect.collidepoint(mouse_pos):
            max_scroll_index = max(0, menu_height - 560)
            # scroll up (text moves down)
            if event.button == 4:
                menu_target_scroll_y = max(0, menu_target_scroll_y - 60)
            # scroll down (text moves up)
            elif event.button == 5:
                menu_target_scroll_y = min(max_scroll_index, menu_target_scroll_y + 60)
    
    return lore_target_scroll_y, menu_target_scroll_y

def reset_shop_confirmations():
    # reset all unlock and upgrades confirmations
    for bot in all_bots:
        bot["confirm"] = False
        for upgrade in bot_upgrades[bot["bot"].name]:
            upgrade["confirm"] = False

def open_shop(mouse_pos, battle_state, previous_battle_state):
    # shop button rectangle
    shop_button_rect = pygame.Rect(40, 530, 100, 50)
    # open shop if button is clicked and close shop if button is clicked again
    if shop_button_rect.collidepoint(mouse_pos) and not lazer_bot.actions[0]["movement_mode"]:
        if battle_state == "Shop":
            reset_shop_confirmations()
            battle_state = previous_battle_state
        else:
            previous_battle_state = battle_state
            battle_state = "Shop"
    return battle_state, previous_battle_state

def shop_bar_navigation(mouse_pos, menu_height, menu_target_scroll_y):
    for i in range(len(all_bots)):
        # bar bot rectangle
        bar_bot_rect = pygame.Rect(180, 40 + i * 80, 80, 80)

        # scroll to the bot's section if it is unlocked
        if bar_bot_rect.collidepoint(mouse_pos) and all_bots[i]["unlocked"]:
            jump_y = 0
            for j in range(i):
                if all_bots[j]["unlocked"]:
                    jump_y += len(bot_upgrades[all_bots[j]["bot"].name]) * 90 + 100
                else:
                    jump_y += 90
            menu_target_scroll_y = min(menu_height - 560, jump_y)
            break

    return menu_target_scroll_y

def shop_upgrade(mouse_pos, player_bots, enemy_goons, active_effects, previous_battle_state, menu_scroll_y, gears, rounds):
    # ignore clicks outside of the shop menu
    menu_rect = pygame.Rect(257, 40, 760, 560)
    if menu_rect.collidepoint(mouse_pos):

        # adjust mouse position based on menu scroll
        mouse_pos = (mouse_pos[0] - 257, mouse_pos[1] - 40 + menu_scroll_y)
        menu_y = 0

        for bot in all_bots:
            if bot["unlocked"]:
                menu_y += 100
                for upgrade in bot_upgrades[bot["bot"].name]:
                    # upgrade button rectangle
                    upgrade_button_rect = pygame.Rect(590, menu_y + 20, 150, 50)
                    menu_y += 90

                    # check if valid upgrade click
                    if upgrade["level"] < len(upgrade["cost"]):
                        cost_number = upgrade["cost"][upgrade["level"]]
                        if upgrade_button_rect.collidepoint(mouse_pos) and gears >= cost_number:

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
                                gears -= cost_number
                                upgrade["level"] += 1
                                upgrade["confirm"] = False

                            # set confirm to true if not confirmed yet
                            else:
                                reset_shop_confirmations()
                                upgrade["confirm"] = True
                            
                            return previous_battle_state, gears

            # unlock bot if valid unlock click
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

                    # set confirm to true if not confirmed yet
                    else:
                        reset_shop_confirmations()
                        bot["confirm"] = True

                    return previous_battle_state, gears

    return previous_battle_state, gears

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

def inspect_enemy(mouse_pos, enemy_goons, inspecting_character, lore_scroll_y, lore_target_scroll_y):
    for enemy in enemy_goons:
        # inspect enemy if it's clicked and alive when its not time to target enemy
        if enemy.rect.collidepoint(mouse_pos) and enemy.real_health > 0:
            # enemy inspection is deselected if clicked again
            if inspecting_character == enemy:
                inspecting_character = None
            else:
                inspecting_character = enemy
                lore_target_scroll_y = 0
                lore_scroll_y = 0
            break
    return inspecting_character, lore_scroll_y, lore_target_scroll_y

def select_bot(mouse_pos, player_bots, battle_state, active_bot, chosen_action, inspecting_character, lore_scroll_y, lore_target_scroll_y):
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
                lore_target_scroll_y = 0
                lore_scroll_y = 0
            battle_state = "Player Turn"
            chosen_action = None
            break
    return battle_state, active_bot, chosen_action, inspecting_character, lore_scroll_y, lore_target_scroll_y

def select_action(mouse_pos, event, battle_state, active_bot, chosen_action, inspecting_character, lore_scroll_y, lore_target_scroll_y):
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
                lore_target_scroll_y = active_bot.actions[0]["scroll"]
            
            # if enemy is being inspected, switch inspecting to active bot when action is chosen
            if inspecting_character != active_bot:
                lore_target_scroll_y = active_bot.actions[0]["scroll"]
                lore_scroll_y = active_bot.actions[0]["scroll"]
                inspecting_character = active_bot

        elif (mouse_pos and (right_button_rect.collidepoint(mouse_pos)) or (event and event.key == pygame.K_2)) and not active_bot.actions[1]["used"]:
            if chosen_action == active_bot.actions[1]["name"]:
                chosen_action = None
                battle_state = "Player Turn"
            else:
                chosen_action = active_bot.actions[1]["name"]
                battle_state = active_bot.actions[1]["target_state"]
                lore_target_scroll_y = active_bot.actions[1]["scroll"]
            
            # if enemy is being inspected, switch inspecting to active bot when action is chosen
            if inspecting_character != active_bot:
                lore_target_scroll_y = active_bot.actions[1]["scroll"]
                lore_scroll_y = active_bot.actions[1]["scroll"]
                inspecting_character = active_bot
    
    return battle_state, chosen_action, inspecting_character, lore_scroll_y, lore_target_scroll_y

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

def player_turn(event, mouse_pos, player_bots, enemy_goons, active_effects, battle_state, previous_battle_state, active_bot, chosen_action, inspecting_character, lore_height, lore_scroll_y, lore_target_scroll_y, menu_height, menu_scroll_y, menu_target_scroll_y, gears, rounds, enemy_slots):
    # if game is over, dont allow any more actions
    if battle_state == "Game Over":
        return battle_state, previous_battle_state, active_bot, chosen_action, inspecting_character, lore_scroll_y, lore_target_scroll_y, menu_scroll_y, menu_target_scroll_y, gears
 
    # update target scroll based on mouse scroll
    if event.button in [4, 5]:
        lore_target_scroll_y, menu_target_scroll_y = scroll_math(mouse_pos, event, battle_state, lore_height, lore_target_scroll_y, menu_height, menu_target_scroll_y)
    
    # handle player actions based on battle state and mouse clicks
    elif event.button == 1:
        # open or close shop
        battle_state, previous_battle_state = open_shop(mouse_pos, battle_state, previous_battle_state)

        # upgrade bot actions if shop is open
        if battle_state == "Shop":
            menu_target_scroll_y = shop_bar_navigation(mouse_pos, menu_height, menu_target_scroll_y)
            previous_battle_state, gears = shop_upgrade(mouse_pos, player_bots, enemy_goons, active_effects, previous_battle_state, menu_scroll_y, gears, rounds)

        else:
            # if lazer bot is in movement mode, other actions are disabled
            if not lazer_bot.actions[0]["movement_mode"]:
                # harvest gears
                gears = harvest_gears(mouse_pos, enemy_goons, active_effects, gears, enemy_slots)

                # inspect enemy if not targeting enemy
                if battle_state not in ["Target Enemy", "Target Enemy or Self", "Target Any"]:
                    inspecting_character, lore_scroll_y, lore_target_scroll_y = inspect_enemy(mouse_pos, enemy_goons, inspecting_character, lore_scroll_y, lore_target_scroll_y)

                # select bot if not targeting bot
                if battle_state not in ["Target Bot", "Target Any"]:
                    battle_state, active_bot, chosen_action, inspecting_character, lore_scroll_y, lore_target_scroll_y = select_bot(mouse_pos, player_bots, battle_state, active_bot, chosen_action, inspecting_character, lore_scroll_y, lore_target_scroll_y)
                
                # select action if bot is selected
                battle_state, chosen_action, inspecting_character, lore_scroll_y, lore_target_scroll_y = select_action(mouse_pos, None, battle_state, active_bot, chosen_action, inspecting_character, lore_scroll_y, lore_target_scroll_y)
                
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
            reset_shop_confirmations()
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

    return battle_state, previous_battle_state, active_bot, chosen_action, inspecting_character, lore_scroll_y, lore_target_scroll_y, menu_scroll_y, menu_target_scroll_y, gears

def handle_input(running, player_bots, enemy_goons, active_effects, game_state, battle_state, previous_battle_state, active_bot, chosen_action, inspecting_character, lore_height, lore_scroll_y, lore_target_scroll_y, menu_height, menu_scroll_y, menu_target_scroll_y, gears, rounds, enemy_slots):
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
                battle_state, previous_battle_state, active_bot, chosen_action, inspecting_character, lore_scroll_y, lore_target_scroll_y, menu_scroll_y, menu_target_scroll_y, gears = player_turn(
                    event, mouse_pos, player_bots, enemy_goons, active_effects, battle_state, previous_battle_state, active_bot, chosen_action, inspecting_character, lore_height, lore_scroll_y, lore_target_scroll_y, menu_height, menu_scroll_y, menu_target_scroll_y, gears, rounds, enemy_slots)
        
        elif event.type == pygame.KEYDOWN:
            if battle_state != "Shop" and not lazer_bot.actions[0]["movement_mode"]:
                # select action if bot is selected based on key press
                battle_state, chosen_action, inspecting_character, lore_scroll_y, lore_target_scroll_y = select_action(None, event, battle_state, active_bot, chosen_action, inspecting_character, lore_scroll_y, lore_target_scroll_y)

    return running, game_state, battle_state, previous_battle_state, active_bot, chosen_action, inspecting_character, lore_scroll_y, lore_target_scroll_y, menu_scroll_y, menu_target_scroll_y, gears

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
                    damage, reduction = target.damage_amount(enemy.damage)
                    target.real_health -= damage
                    active_effects.append(LinearProjectile((255, 0, 0), enemy, target, (-50, -50), damage, reduction, "Damage"))
        battle_state = "Enemy Turn Over"
    return battle_state

def round_end(player_bots, enemy_goons, active_effects, battle_state, gears, rounds):
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
    if max_enemies < 9 and rounds % 5 == 0:
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
        battle_state, gears, rounds = round_end(player_bots, enemy_goons, active_effects, battle_state, gears, rounds)

        # spawn new enemies based on the round and max enemies
        gears, max_enemies = spawn_state(enemy_goons, active_effects, gears, rounds, max_enemies, enemy_slots)
    
    return battle_state, gears, rounds, max_enemies

# ------------------------------
# GAME BEGINNING AND ENDING
# ------------------------------

def spawn_initial_enemies(enemy_goons, enemy_slots):
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

def check_game_over(player_bots, battle_state, lore_scroll_y, lore_target_scroll_y):
    # check if battle state is already game over
    if battle_state == "Game Over":
        return battle_state, lore_scroll_y, lore_target_scroll_y
    
    # game ends when all bots are dead
    game_end = True
    for bot in player_bots:
        if bot.real_health > 0:
            game_end = False
            break
    if game_end:
        lore_target_scroll_y = 0
        lore_scroll_y = 0
        battle_state = "Game Over"
    
    return battle_state, lore_scroll_y, lore_target_scroll_y
