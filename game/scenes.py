# scenes.py

# import libraries
import pygame
import random

# import game modules
from .bots import GunBot, RicoBot, ModBot, ElementalBot, LazerBot, ChaosBot, DuploBot
from .goons import BasicGoon, TankyGoon, PowerfulGoon
from .helper import wrap_text, dynamic_text, render_text
from .battle import ActionBox, LoreBox, ShopBox, ShopBar, ShopMenu, PlayerZone, EnemyZone, Execution
from .effects import FloatingText, BounceProjectile, LaserProjectile, GlitchyBlockProjectile, ShieldProjectile

# ------------------------------
# MAIN MENU
# ------------------------------

class MainMenuScene():
    def __init__(self, fonts, font_cache):
        # scene texts
        self.fonts = fonts
        self.font_cache = font_cache
        self.text_cache = {}

        # scene buttons
        self.buttons = [
            {
                "text": "Story Mode",
                "rect": pygame.Rect(500, 335, 200, 80),
            },
            {
                "text": "Endless Mode",
                "rect": pygame.Rect(500, 500, 200, 80),
            }
        ]
    
    def handle_input(self, events):
        # enters the selected game mode based on button click
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in self.buttons:
                    if button["rect"].collidepoint(event.pos):
                        if button["text"] == "Story Mode":
                            return Chapter1CutScene(self.fonts, self.font_cache)
                        elif button["text"] == "Endless Mode":
                            return EndlessModeScene(self.fonts, self.font_cache)
        return self

    def update(self):
        pass

    def draw(self, screen):
        # draw main menu background
        screen.fill((10, 10, 25))

        # draw title text
        welcome_text = render_text(self.fonts, self.text_cache, 24, "Welcome to", (255, 255, 255))
        title_text = render_text(self.fonts, self.text_cache, 120, "Rounds", (255, 255, 255))
        welcome_text_rect = welcome_text.get_rect(center=(600, 160))
        title_text_rect = title_text.get_rect(center=(600, 200))
        screen.blit(welcome_text, welcome_text_rect)
        screen.blit(title_text, title_text_rect)

        # button rectangles
        story_button_rect = self.buttons[0]["rect"]
        endless_button_rect = self.buttons[1]["rect"]

        # change button color based on hover
        mouse_pos = pygame.mouse.get_pos()
        if story_button_rect.collidepoint(mouse_pos):
            story_button_color = (150, 150, 255)
        else:
            story_button_color = (100, 100, 255)
        if endless_button_rect.collidepoint(mouse_pos):
            endless_button_color = (150, 150, 255)
        else:
            endless_button_color = (100, 100, 255)

        # draw story mode button
        pygame.draw.rect(screen, story_button_color, story_button_rect)
        story_text = dynamic_text(self.font_cache, self.text_cache, "Story Mode", 180, 30, (255, 255, 255))
        story_text_rect = story_text.get_rect(center=(600, 375))
        screen.blit(story_text, story_text_rect)

        # draw endless mode button
        pygame.draw.rect(screen, endless_button_color, endless_button_rect)
        endless_text = dynamic_text(self.font_cache, self.text_cache, "Endless Mode", 180, 80, (255, 255, 255))
        endless_text_rect = endless_text.get_rect(center=(600, 540))
        screen.blit(endless_text, endless_text_rect)

# ------------------------------
# ENDLESS MODE
# ------------------------------

class EndlessModeScene():
    def __init__(self, fonts, font_cache):
        # scene texts
        self.fonts = fonts
        self.font_cache = font_cache
        self.text_cache = {}

        # create game elements
        self.action_box = ActionBox()
        self.lore_box = LoreBox()
        self.shop_box = ShopBox()
        self.shop_bar = ShopBar()
        self.shop_menu = ShopMenu()
        self.player_zone = PlayerZone()
        self.enemy_zone = EnemyZone()
        self.execution = Execution()

        # create player bots
        self.gun_bot = GunBot(200, 100)
        self.rico_bot = RicoBot(200, 275)
        self.mod_bot = ModBot(350, 100)
        self.elemental_bot = ElementalBot(200, 450)
        self.lazer_bot = LazerBot(480, 300)
        self.chaos_bot = ChaosBot(350, 275)
        self.duplo_bot = DuploBot(350, 450)

        # all bots and their unlock conditions
        self.all_bots = [
            {"bot": self.gun_bot,        "cost": 0,  "round": 1, "confirm": False, "unlocked": True},
            {"bot": self.rico_bot,       "cost": 0,  "round": 1, "confirm": False, "unlocked": True},
            {"bot": self.mod_bot,        "cost": 10, "round": 3, "confirm": False, "unlocked": False},
            {"bot": self.elemental_bot,  "cost": 20, "round": 4, "confirm": False, "unlocked": False},
            {"bot": self.lazer_bot,      "cost": 30, "round": 5, "confirm": False, "unlocked": False},
            {"bot": self.chaos_bot,      "cost": 40, "round": 6, "confirm": False, "unlocked": False},
            {"bot": self.duplo_bot,      "cost": 50, "round": 7, "confirm": False, "unlocked": False}
        ]

        # all bot upgrades and their costs
        self.bot_upgrades = {
            "Gun Bot": [
                {
                    "action": "Left Gun",
                    "action_number": 0,
                    "stat": "aiming_unlocked",
                    "level": 0,
                    "buff_desc_1": "Unlock Aiming",
                    "buff_desc_2": ["Locked -> Unlocked"],
                    "amount": [True],
                    "cost": [100],
                    "confirm": False
                },
                {
                    "action": "Right Gun",
                    "action_number": 1,
                    "stat": "damage",
                    "level": 0,
                    "buff_desc_1": "+1 damage",
                    "buff_desc_2": ["Damage: 1 -> 2", "Damage: 2 -> 3", "Damage: 3 -> 4", "Damage: 4 -> 5"],
                    "amount": [2, 3, 4, 5],
                    "cost": [5, 10, 15, 20],
                    "confirm": False
                }
            ],
            "Rico Bot": [
                {
                    "action": "Heal",
                    "action_number": 0,
                    "stat": "heal",
                    "level": 0,
                    "buff_desc_1": "+1 heal",
                    "buff_desc_2": ["Heal: 1 -> 2", "Heal: 2 -> 3", "Heal: 3 -> 4", "Heal: 4 -> 5"],
                    "amount": [2, 3, 4, 5],
                    "cost": [5, 10, 15, 20],
                    "confirm": False
                },
                {
                    "action": "Bounce",
                    "action_number": 1,
                    "stat": "damage",
                    "level": 0,
                    "buff_desc_1": "+1 damage",
                    "buff_desc_2": ["Damage: 1 -> 2", "Damage: 2 -> 3", "Damage: 3 -> 4", "Damage: 4 -> 5"],
                    "amount": [2, 3, 4, 5],
                    "cost": [5, 10, 15, 20],
                    "confirm": False
                },
                {
                    "action": "Bounce",
                    "action_number": 1,
                    "stat": "bounce_amount",
                    "level": 0,
                    "buff_desc_1": "+1 bounce",
                    "buff_desc_2": ["Bounces: 2 -> 3", "Bounces: 3 -> 4", "Bounces: 4 -> 5", "Bounces: 5 -> 6"],
                    "amount": [3, 4, 5, 6],
                    "cost": [10, 25, 40, 55],
                    "confirm": False
                }
            ],
            "Mod Bot": [
                {
                    "action": "Percentage",
                    "action_number": 0,
                    "stat": "damage",
                    "level": 0,
                    "buff_desc_1": "+10% damage",
                    "buff_desc_2": ["Damage: 10% -> 20%", "Damage: 20% -> 30%", "Damage: 30% -> 40%", "Damage: 40% -> 50%"],
                    "amount": [0.2, 0.3, 0.4, 0.5],
                    "cost": [20, 30, 40, 50],
                    "confirm": False
                },
                {
                    "action": "Shield",
                    "action_number": 1,
                    "stat": "shield",
                    "level": 0,
                    "buff_desc_1": "+10% reduction",
                    "buff_desc_2": ["Reduction: 10% -> 20%", "Reduction: 20% -> 30%", "Reduction: 30% -> 40%", "Reduction: 40% -> 50%"],
                    "amount": [0.8, 0.7, 0.6, 0.5],
                    "cost": [20, 30, 40, 50],
                    "confirm": False
                }
            ],
            "Elemental Bot": [
                {
                    "action": "Fire",
                    "action_number": 0,
                    "stat": "damage",
                    "level": 0,
                    "buff_desc_1": "+1 damage",
                    "buff_desc_2": ["Damage: 1 -> 2", "Damage: 2 -> 3", "Damage: 3 -> 4", "Damage: 4 -> 5"],
                    "amount": [2, 3, 4, 5],
                    "cost": [10, 20, 30, 40],
                    "confirm": False
                },
                {
                    "action": "Fire",
                    "action_number": 0,
                    "stat": "fire_rounds_amount",
                    "level": 0,
                    "buff_desc_1": "+1 round",
                    "buff_desc_2": ["Round: 2 -> 3", "Round: 3 -> 4", "Round: 4 -> 5"],
                    "amount": [3, 4, 5],
                    "cost": [10, 20, 30],
                    "confirm": False
                },
                {
                    "action": "Ice",
                    "action_number": 1,
                    "stat": "ice_hits_needed",
                    "level": 0,
                    "buff_desc_1": "-1 freeze hit needed",
                    "buff_desc_2": ["Hits Needed: 3 -> 2", "Hits Needed: 2 -> 1"],
                    "amount": [2, 1],
                    "cost": [25, 50],
                    "confirm": False
                }
            ],
            "Lazer Bot": [
                {
                    "action": "Pierce",
                    "action_number": 0,
                    "stat": "damage",
                    "level": 0,
                    "buff_desc_1": "+1 damage",
                    "buff_desc_2": ["Damage: 1 -> 2", "Damage: 2 -> 3", "Damage: 3 -> 4", "Damage: 4 -> 5"],
                    "amount": [2, 3, 4, 5],
                    "cost": [10, 20, 30, 40],
                    "confirm": False
                },
                {
                    "action": "Barrage",
                    "action_number": 1,
                    "stat": "damage",
                    "level": 0,
                    "buff_desc_1": "+1 damage",
                    "buff_desc_2": ["Damage: 1 -> 2", "Damage: 2 -> 3", "Damage: 3 -> 4", "Damage: 4 -> 5"],
                    "amount": [2, 3, 4, 5],
                    "cost": [10, 20, 30, 40],
                    "confirm": False
                },
                {
                    "action": "Barrage",
                    "action_number": 1,
                    "stat": "barrage_charge_needed",
                    "level": 0,
                    "buff_desc_1": "-5 barrage charge",
                    "buff_desc_2": ["Charge Needed: 20 -> 15", "Charge Needed: 15 -> 10", "Charge Needed: 10 -> 5"],
                    "amount": [15, 10, 5],
                    "cost": [10, 30, 50],
                    "confirm": False
                }
            ],
            "Chaos Bot": [
                {
                    "action": "Random",
                    "action_number": 0,
                    "stat": "min_power",
                    "level": 0,
                    "buff_desc_1": "+1 min power",
                    "buff_desc_2": ["Min Power: 1 -> 2", "Min Power: 2 -> 3", "Min Power: 3 -> 4", "Min Power: 4 -> 5"],
                    "amount": [2, 3, 4, 5],
                    "cost": [10, 20, 30, 40],
                    "confirm": False
                },
                {
                    "action": "Random",
                    "action_number": 0,
                    "stat": "max_power",
                    "level": 0,
                    "buff_desc_1": "+1 max power",
                    "buff_desc_2": ["Max Power: 5 -> 6", "Max Power: 6 -> 7", "Max Power: 7 -> 8", "Max Power: 8 -> 9", "Max Power: 9 -> 10"],
                    "amount": [6, 7, 8, 9, 10],
                    "cost": [10, 20, 30, 40, 50],
                    "confirm": False
                },
                {
                    "action": "Barrier",
                    "action_number": 1,
                    "stat": "block",
                    "level": 0,
                    "buff_desc_1": "+10% block",
                    "buff_desc_2": ["Block: 10% -> 20%", "Block: 20% -> 30%", "Block: 30% -> 40%", "Block: 40% -> 50%"],
                    "amount": [20, 30, 40, 50],
                    "cost": [20, 30, 40, 50],
                    "confirm": False
                }
            ],
            "Duplo Bot": [
                {
                    "action": "Mark",
                    "action_number": 1,
                    "stat": "mark_hits_needed",
                    "level": 0,
                    "buff_desc_1": "-1 mark hit needed",
                    "buff_desc_2": ["Hits Needed: 2 -> 1"],
                    "amount": [1],
                    "cost": [50],
                    "confirm": False
                }
            ]
        }

        # slots for enemies to spawn in
        self.enemy_slots = [
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

        # different types of enemy
        self.enemy_types = [BasicGoon, TankyGoon, PowerfulGoon]

        # initial list of characters and effects
        self.player_bots = [self.gun_bot, self.rico_bot]
        self.enemy_goons = []
        self.active_effects = []
    
        # initial variables for player turn
        self.battle_state = "Player Turn"
        self.previous_battle_state = "Player Turn"
        self.active_bot = None
        self.chosen_action = None
    
        # initial variables related to lore box
        self.inspecting_character = None
        self.lore_height = 0
        self.lore_scroll = 0.0
        self.lore_target_scroll = 0.0
    
        # initial variables related to shop
        self.menu_height = 0
        self.menu_scroll = 0.0
        self.menu_target_scroll = 0.0
    
        # initial variables for game progression
        self.gears = 0
        self.rounds = 1
        self.max_enemies = 3

        # load initial character images
        for char in self.all_bots:
            char["bot"].load_images()
        for enemy in self.enemy_types:
            enemy.load_images()

        # inital gun bot aiming setup
        self.gun_bot.reset_gun_aiming()

        # spawn two basic goons at the start of the game in random empty slots
        for _ in range(2):

            # find empty slots
            empty_slots = []
            for i, slot in enumerate(self.enemy_slots):
                if not slot["occupied"]:
                    empty_slots.append(i)

            # choose a random empty slot
            slot_id = random.choice(empty_slots)
            slot = self.enemy_slots[slot_id]
            slot["occupied"] = True

            # random offsets for the goon spawn position
            x_offset = random.randint(0, 100)
            y_offset = random.randint(40, 100)

            # spawn a basic goon
            new_enemy = self.enemy_types[0](
                slot["x"] + x_offset,
                slot["y"] + y_offset,
                slot_id)
            self.enemy_goons.append(new_enemy)

    def handle_input(self, events):
        # dont allow any input if the game is over
        if self.battle_state == "Game Over":
            return self

        for event in events:

            # handles mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:

                # update target scroll based on mouse scroll
                self.lore_target_scroll = self.lore_box.handle_event(event, self.lore_height, self.lore_target_scroll)
                self.menu_target_scroll = self.shop_menu.handle_event_scroll(event, self.battle_state, self.menu_height, self.menu_target_scroll)

                # handle left mouse clicks
                if event.button == 1:

                    # handle shop box events
                    self.battle_state, self.previous_battle_state = self.shop_box.handle_event(event, self.all_bots, self.bot_upgrades, self.battle_state, self.previous_battle_state)

                    # handle shop bar and menu events when shop is open
                    if self.battle_state == "Shop":
                        self.menu_target_scroll = self.shop_bar.handle_event(event, self.all_bots, self.bot_upgrades, self.menu_height, self.menu_target_scroll)
                        self.previous_battle_state, self.gears = self.shop_menu.handle_event_click(event,
                            self.all_bots, self.bot_upgrades,
                            self.player_bots, self.enemy_goons, self.active_effects,
                            self.previous_battle_state,
                            self.menu_scroll,
                            self.gears, self.rounds)

                    # handle other events when shop is closed
                    else:

                        # handle player zone, enemy zone, and action box events
                        if self.battle_state != "Lazer Movement":
                            self.inspecting_character, self.lore_scroll, self.lore_target_scroll, self.gears = self.enemy_zone.handle_event(event,
                                self.enemy_slots,
                                self.enemy_goons, self.active_effects,
                                self.battle_state,
                                self.inspecting_character, self.lore_scroll, self.lore_target_scroll,
                                self.gears)
                            self.battle_state, self.active_bot, self.chosen_action, self.inspecting_character, self.lore_scroll, self.lore_target_scroll = self.player_zone.handle_event(event,
                                self.player_bots,
                                self.battle_state, self.active_bot, self.chosen_action,
                                self.inspecting_character, self.lore_scroll, self.lore_target_scroll)
                            self.battle_state, self.chosen_action, self.inspecting_character, self.lore_scroll, self.lore_target_scroll = self.action_box.handle_event(event,
                                self.battle_state, self.active_bot, self.chosen_action,
                                self.inspecting_character, self.lore_scroll, self.lore_target_scroll)

                        # execute the chosen action
                        self.battle_state, self.active_bot, self.chosen_action, self.inspecting_character = self.execution.execute_action(event,
                            self.player_bots, self.enemy_goons, self.active_effects,
                            self.battle_state, self.active_bot, self.chosen_action,
                            self.inspecting_character)
                        self.battle_state, self.active_bot, self.chosen_action, self.inspecting_character = self.execution.execute_laser_action(event,
                            self.player_bots, self.enemy_goons, self.active_effects,
                            self.battle_state, self.active_bot, self.chosen_action,
                            self.inspecting_character)

                # handle right mouse clicks
                elif event.button == 3:

                    # close shop
                    if self.battle_state == "Shop":
                        self.battle_state = self.previous_battle_state

                        # reset all unlock and upgrades confirmations
                        for b in self.all_bots:
                            b["confirm"] = False
                            for u in self.bot_upgrades[b["bot"].name]:
                                u["confirm"] = False

                    # deselect action, bot, or inspected character
                    elif self.battle_state != "Lazer Movement":
                        if self.chosen_action:
                            self.chosen_action = None
                            self.battle_state = "Player Turn"
                        elif self.active_bot:
                            self.inspecting_character = None
                            self.active_bot = None
                        elif self.inspecting_character:
                            self.inspecting_character = None

            # handles key presses
            elif event.type == pygame.KEYDOWN:

                # handle action box events
                if self.battle_state not in ["Shop", "Lazer Movement"]:
                    self.battle_state, self.chosen_action, self.inspecting_character, self.lore_scroll, self.lore_target_scroll = self.action_box.handle_event(event,
                        self.battle_state, self.active_bot, self.chosen_action,
                        self.inspecting_character, self.lore_scroll, self.lore_target_scroll)

        return self

    def update(self):
        # change to player turn over if all enemies are dead
        enemies_alive = False
        for enemy in self.enemy_goons:
            if enemy.real_health > 0:
                enemies_alive = True
                break
        if not enemies_alive:
            self.battle_state = "Player Turn Over"
        
        # change to enemy turn if player turn is over and all projectiles have reached their target
        if self.battle_state == "Player Turn Over":
            projectiles_effects_active = False
            for effect in self.active_effects:
                if not isinstance(effect, FloatingText):
                    projectiles_effects_active = True
                    break
            if not projectiles_effects_active:
                self.battle_state = "Enemy Turn"

        # execute enemy attacks
        self.battle_state = self.execution.execute_enemy_attacks(self.player_bots, self.enemy_goons, self.active_effects, self.battle_state)

        # change to round end if enemy turn is over and all projectiles have reached their target
        if self.battle_state == "Enemy Turn Over":
            projectiles_effects_active = False
            for effect in self.active_effects:
                if not isinstance(effect, FloatingText):
                    projectiles_effects_active = True
                    break
            if not projectiles_effects_active:
                self.battle_state = "Round End"

        # handle round end and spawn new goons
        if self.battle_state == "Round End":
            self.battle_state, self.gears, self.rounds = self.execution.round_end(self.player_bots, self.enemy_goons, self.active_effects, self.battle_state, self.gears, self.rounds, self.gun_bot, self.elemental_bot)
            self.gears, self.max_enemies = self.enemy_zone.spawn_goons(self.enemy_slots, self.enemy_types, self.enemy_goons, self.active_effects, self.gears, self.rounds, self.max_enemies)

        # check if game is over
        game_end = True
        for bot in self.player_bots:
            if bot.real_health > 0:
                game_end = False
                break
        if game_end:
            self.lore_target_scroll = 0
            self.lore_scroll = 0
            self.battle_state = "Game Over"

        # update character animations
        self.player_zone.update(self.player_bots, self.battle_state, self.active_bot, self.chosen_action)
        self.enemy_zone.update(self.enemy_goons)

        # update and remove effects
        for effect in self.active_effects[:]:
            if isinstance(effect, FloatingText) or isinstance(effect, LaserProjectile) or isinstance(effect, GlitchyBlockProjectile) or isinstance(effect, ShieldProjectile):
                effect.update()
            elif isinstance(effect, BounceProjectile):
                effect.update(self.enemy_goons, self.active_effects)
            else:
                effect.update(self.active_effects)
            if not effect.active:
                self.active_effects.remove(effect)

        # update scrolling positions
        self.lore_scroll = self.lore_box.update(self.lore_scroll, self.lore_target_scroll)
        self.menu_scroll = self.shop_menu.update(self.menu_scroll, self.menu_target_scroll)

    def draw(self, screen):
        # background color
        screen.fill((0, 0, 0))

        # draw player and enemy zones
        self.player_zone.draw(screen, self.fonts, self.text_cache, self.player_bots, self.battle_state, self.active_bot, self.chosen_action, self.inspecting_character)
        self.enemy_zone.draw(screen, self.fonts, self.text_cache, self.enemy_goons, self.battle_state, self.inspecting_character, self.elemental_bot)

        # draw shop stuff
        self.shop_box.draw(screen, self.fonts, self.font_cache, self.text_cache, self.battle_state, self.active_bot, self.gears, self.rounds)
        self.shop_bar.draw(screen, self.fonts, self.text_cache, self.all_bots, self.battle_state)
        self.menu_height = self.shop_menu.draw(screen, self.fonts, self.font_cache, self.text_cache, self.all_bots, self.bot_upgrades, self.battle_state, self.menu_height, self.menu_scroll, self.gears, self.rounds)

        # draw bottom boxes
        self.action_box.draw(screen, self.font_cache, self.text_cache, self.battle_state, self.active_bot, self.chosen_action)
        self.lore_height = self.lore_box.draw(screen, self.fonts, self.text_cache, self.battle_state, self.inspecting_character, self.lore_height, self.lore_scroll, self.rounds)

        # draw all active effects
        for effect in self.active_effects:
            if isinstance(effect, FloatingText):
                effect.draw(screen, self.fonts, self.text_cache)
            else:
                effect.draw(screen)

        # draw bot action indicators if active
        self.gun_bot.draw_gun_aiming(screen, self.font_cache, self.text_cache, self.active_bot, self.chosen_action)
        self.lazer_bot.draw_laser(screen, self.enemy_goons, self.battle_state)

        # temp box
        if self.active_bot:
            temp_box_color = self.active_bot.box_background_color
        else:
            temp_box_color = (50, 50, 50)
        pygame.draw.rect(screen, temp_box_color, (20, 620, 60, 90))
        pygame.draw.rect(screen, (255, 255, 255), (20, 620, 60, 90), 3)

# ------------------------------
# STORY MODE
# ------------------------------

class Chapter1CutScene():
    def __init__(self, fonts, font_cache):
        # scene texts
        self.fonts = fonts
        self.font_cache = font_cache
        self.text_cache = {}

        # scene buttons
        self.next_button_rect = pygame.Rect(920, 620, 100, 60)

        # script for the cutscene with images and dialogue lines
        self.script = [
            {
                "image_path": "assets/chapter1/cutscenes/scene1.png",
                "lines": [
                    "Long ago ... ",
                    "... like two months ago ...",
                    "... the earth was just there."
                ]
            },
            {
                "image_path": "assets/chapter1/cutscenes/scene2.png",
                "lines": [
                    "But then the aliens attacked!",
                    "Aliens robots with technology much more advanced than humans."
                ]
            },
            {
                "image_path": "assets/chapter1/cutscenes/scene3.png",
                "lines": [
                    "They destroyed many cities and caused much chaos.",
                    "But all hope was not lost ..."
                ]
            },
            {
                "image_path": "assets/chapter1/cutscenes/scene4.png",
                "lines": [
                    "... as the humans have discovered magic!"
                ]
            },
            {
                "image_path": "assets/chapter1/cutscenes/scene5.png",
                "lines": [
                    "Scientists and engineers have studied and discovered how to infuse magic into technology.",
                    "With this new technology, humans can create something powerful to fight back!"
                ]
            }
        ]

        # initial variables for cutscene progression
        self.current_image = 0
        self.current_line = 0

        # load and scale images for the cutscene
        self.images = []
        for scene in self.script:
            image = pygame.image.load(scene["image_path"]).convert_alpha()
            scaled_image = pygame.transform.scale_by(image, 2)
            self.images.append(scaled_image)

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.next_button_rect.collidepoint(event.pos):

                    # advance to the next image if the lines for this image are done
                    if self.current_line >= len(self.script[self.current_image]["lines"])-1:
                        self.current_image += 1
                        self.current_line = 0

                        # advance to the next scene if the cutscene is done
                        if self.current_image >= len(self.script):
                            return BlankScene(self.fonts, self.font_cache)
                        
                    # advance to the next line
                    else:
                        self.current_line += 1
        return self

    def update(self):
        pass

    def draw(self, screen):
        # draw background
        screen.fill((0, 0, 0))
        screen.blit(self.images[self.current_image], (0, 0))

        # draw dialogue box
        pygame.draw.rect(screen, (100, 100, 255), (300, 620, 600, 60))
        pygame.draw.rect(screen, (255, 255, 255), (300, 620, 600, 60), 3)

        # draw dialogue text
        dialogue_lines = wrap_text(self.script[self.current_image]["lines"][self.current_line], self.fonts, 580)
        for i, line in enumerate(dialogue_lines):
            dialogue_text = render_text(self.fonts, self.text_cache, 24, line, (255, 255, 255))
            screen.blit(dialogue_text, (310, 630 + i * 25))

        # draw next button
        mouse_pos = pygame.mouse.get_pos()
        if self.next_button_rect.collidepoint(mouse_pos):
            button_color = (150, 150, 255)
        else:
            button_color = (100, 100, 255)
        pygame.draw.rect(screen, button_color, self.next_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.next_button_rect, 3)

        # draw next button text
        next_text = dynamic_text(self.font_cache, self.text_cache, "Next", 90, 50, (255, 255, 255))
        next_text_rect = next_text.get_rect(center=self.next_button_rect.center)
        screen.blit(next_text, next_text_rect)

# ------------------------------
# BLANK SCENE
# ------------------------------

class BlankScene():
    def __init__(self, fonts, font_cache):
        # scene texts
        self.fonts = fonts
        self.font_cache = font_cache
        self.text_cache = {}

    def handle_input(self, events):
        return self

    def update(self):
        pass

    def draw(self, screen):
        # blank background with text saying more to be added
        screen.fill((0, 0, 0))
        text = render_text(self.fonts, self.text_cache, 24, "More To Be Added", (255, 255, 255))
        screen.blit(text, (200, 200))
