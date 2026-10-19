# scenes.py

# import libraries
import pygame
import random

# import game modules
from .bots import GunBot, RicoBot, ModBot, ElementalBot, LazerBot, ChaosBot, DuploBot, HealerBot
from .goons import BasicGoon, TankyGoon, PowerfulGoon, DummyGoon
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
            for bot in self.player_bots:
                bot.acted = True
                for action in bot.actions:
                    action["used"] = True
        
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
                            return TutorialBattleScene(self.fonts, self.font_cache)
                        
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

class BattleScene():
    def __init__(self, fonts, font_cache):
        # scene texts
        self.fonts = fonts
        self.font_cache = font_cache
        self.text_cache = {}

        # create game elements
        self.action_box = ActionBox()
        self.lore_box = LoreBox()
        self.player_zone = PlayerZone()
        self.enemy_zone = EnemyZone()
        self.execution = Execution()

        # create player bots to not crash
        self.elemental_bot = ElementalBot(0, 0)

        # initial list of effects
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
    
        # initial variables for game progression
        self.gears = 0
        self.rounds = 1

    def handle_input(self, events):
        # dont allow any input if the game is over
        if self.battle_state == "Game Over":
            return self

        for event in events:

            # handles mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:

                # update target scroll based on mouse scroll
                self.lore_target_scroll = self.lore_box.handle_event(event, self.lore_height, self.lore_target_scroll)

                # handle left mouse clicks
                if event.button == 1:

                    if self.battle_state != "Lazer Movement":

                        # handle player zone, enemy zone, and action box events
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

                    # deselect action, bot, or inspected character
                    if self.battle_state != "Lazer Movement":
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
                if self.battle_state != "Lazer Movement":
                    self.battle_state, self.chosen_action, self.inspecting_character, self.lore_scroll, self.lore_target_scroll = self.action_box.handle_event(event,
                        self.battle_state, self.active_bot, self.chosen_action,
                        self.inspecting_character, self.lore_scroll, self.lore_target_scroll)

        return self

    def update(self):
        # change to game over if all enemies are dead
        if self.battle_state != "Victory":
            enemies_alive = False
            for enemy in self.enemy_goons:
                if enemy.real_health > 0:
                    enemies_alive = True
                    break
            if not enemies_alive:
                self.battle_state = "Victory"
                self.active_effects.append(FloatingText((255, 255, 255), 460, 300, "Victory!"))
                for bot in self.player_bots:
                    bot.acted = False
                    for action in bot.actions:
                        action["used"] = False

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

        # handle round end
        if self.battle_state == "Round End":
            self.battle_state, self.gears, self.rounds = self.execution.round_end(self.player_bots, self.enemy_goons, self.active_effects, self.battle_state, self.gears, self.rounds, self.gun_bot, self.elemental_bot)

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

    def draw(self, screen):
        # background color
        screen.fill((0, 0, 0))

        # draw player and enemy zones
        self.player_zone.draw(screen, self.fonts, self.text_cache, self.player_bots, self.battle_state, self.active_bot, self.chosen_action, self.inspecting_character)
        self.enemy_zone.draw(screen, self.fonts, self.text_cache, self.enemy_goons, self.battle_state, self.inspecting_character, self.elemental_bot)

        # draw bottom boxes
        self.action_box.draw(screen, self.font_cache, self.text_cache, self.battle_state, self.active_bot, self.chosen_action)
        self.lore_height = self.lore_box.draw(screen, self.fonts, self.text_cache, self.battle_state, self.inspecting_character, self.lore_height, self.lore_scroll, self.rounds)

        # draw all active effects
        for effect in self.active_effects:
            if isinstance(effect, FloatingText):
                effect.draw(screen, self.fonts, self.text_cache)
            else:
                effect.draw(screen)

        # temp box
        if self.active_bot:
            temp_box_color = self.active_bot.box_background_color
        else:
            temp_box_color = (50, 50, 50)
        pygame.draw.rect(screen, temp_box_color, (20, 620, 60, 90))
        pygame.draw.rect(screen, (255, 255, 255), (20, 620, 60, 90), 3)

class TutorialBattleScene(BattleScene):
    def __init__(self, fonts, font_cache):
        super().__init__(fonts, font_cache)

        # create player bots
        self.gun_bot = GunBot(250, 150)
        self.healer_bot = HealerBot(250, 350)

        # create enemy goons
        self.dummy_goon = DummyGoon(700, 250, 0)

        # slots for enemies to spawn in
        self.enemy_slots = [
            {"x": 600, "y": 0, "occupied": False}
        ]

        # initial list of characters
        self.player_bots = [self.gun_bot, self.healer_bot]
        self.enemy_goons = [self.dummy_goon]

        # load initial character images
        for bot in self.player_bots:
            bot.load_images()
        for goon in self.enemy_goons:
            goon.load_images()

        # load sciengineer image
        self.sciengineer_image = pygame.image.load("assets/chapter1/tutorial/sciengineer.png").convert_alpha()

        # tutorial steps with instructions
        self.current_step = 0
        self.current_line = 0
        self.tutorial_steps = [
            {
                "lines": [
                    "Hello there! Welcome to the world my fellow bots!",
                    "I am a scientist and a engineer, or sciengineer I guess.",
                    "I've been working with magic infused technology trying to make something to help defend our world.",
                    "And I think you bots are it!",
                    "And the fact that you can hear me now means that I think I have succeeded in my creation!",
                    "With the power you have that I think you have, we might be able to finally have a chance!",
                    "Lets test you out to see if you are completely working.",
                    "Here is a dummy robot I made.",
                    "If you can destroy this, then you are ready!"
                ],
                "draw_box": pygame.Rect(480, 60, 500, 60),
                "input_box": pygame.Rect(990, 60, 100, 60),
                "next": "next"
            },
            {
                "lines": [
                    "Click on a bot to select it. Start by clicking on gun bot"
                ],
                "draw_box": pygame.Rect(30, 150, 200, 90),
                "input_box": self.gun_bot.rect,
                "next": "select_gun_bot",
            },
            {
                "lines": [
                    "Each bot will have unique actions you can perform.",
                    "Some will start with 2, some with 1.",
                    "Some are for attacking and some are for support.",
                    "You can use each action once per round."
                ],
                "draw_box": pygame.Rect(100, 540, 360, 60),
                "input_box": pygame.Rect(470, 540, 100, 60),
                "next": "next"
            },
            {
                "lines": [
                    "Click on any action to select it.."
                ],
                "draw_box": pygame.Rect(100, 540, 360, 60),
                "input_box": [pygame.Rect(120, 640, 150, 50), pygame.Rect(290, 640, 150, 50)],
                "next": "select_gun"
            },
            {
                "lines": [
                    "Now click on the dummy goon to attack it."
                ],
                "draw_box": pygame.Rect(650, 130, 250, 60),
                "input_box": self.dummy_goon.rect,
                "next": "select_dummy_goon_attack"
            },
            {
                "lines": [
                    "Now lets see what Healer Bot can do."
                ],
                "draw_box": pygame.Rect(30, 350, 200, 60),
                "input_box": self.healer_bot.rect,
                "next": "select_healer_bot"
            },
            {
                "lines": [
                    "You can see the description and stats of each bot and their actions here.",
                    "You can scroll up and down to see more."
                ],
                "draw_box": pygame.Rect(600, 540, 400, 60),
                "input_box": pygame.Rect(1010, 540, 100, 60),
                "next": "next"
            },
            {
                "lines": [
                    "Select the heal action."
                ],
                "draw_box": pygame.Rect(100, 540, 360, 60),
                "input_box": pygame.Rect(120, 640, 150, 50),
                "next": "select_heal"
            },
            {
                "lines": [
                    "Click on any bot to heal it."
                ],
                "draw_box": pygame.Rect(30, 250, 200, 60),
                "input_box": [self.gun_bot.rect, self.healer_bot.rect],
                "next": "select_bot"
            },
            {
                "lines": [
                    "When not targeting an enemy, you can click on them to see their description and stats."
                ],
                "draw_box": pygame.Rect(650, 130, 500, 60),
                "input_box": self.dummy_goon.rect,
                "next": "select_dummy_goon_inspect"
            },
            {
                "lines": [
                    "I think you got it! Now finish the round by using gun bot's other action"
                ],
                "draw_box": pygame.Rect(480, 60, 500, 60),
                "input_box": pygame.Rect(0, 0, 1200, 730),
                "next": "finish_round"
            },
            {
                "lines": [
                    "Now the enemy will attack you.",
                    "Now a new round starts and you can use your actions again.",
                    "Once you select a bot or an action, you can click on the same bot or action to deselect it.",
                    "You can also right click to deselect an action, bot, or inspected character."
                ],
                "draw_box": pygame.Rect(480, 60, 500, 60),
                "input_box": pygame.Rect(990, 60, 100, 60),
                "next": "next"
            },
            {
                "lines": [
                    "Continue fighting to destroy the dummy goon."
                ],
                "draw_box": pygame.Rect(480, 60, 500, 60),
                "input_box": pygame.Rect(0, 0, 1200, 730),
                "next": "free_play"
            },
            {
                "lines": [
                    "Nice, you got it!",
                    "I'm so happy that you are working properly."
                ],
                "draw_box": pygame.Rect(480, 60, 500, 60),
                "input_box": pygame.Rect(990, 60, 100, 60),
                "next": "next"
            },
            {
                "lines": [
                    "After destroying an enemy, you can click on them to get some gears."
                ],
                "draw_box": pygame.Rect(650, 130, 500, 60),
                "input_box": self.dummy_goon.rect,
                "next": "harvest_gears"
            },
            {
                "lines": [
                    "Gears can be used in many ways like upgrading your bots for example.",
                    "How exactly? I don't know, but I'm sure other sciengineers will help you out there.",
                    "I think you are ready!"
                ],
                "draw_box": pygame.Rect(480, 60, 500, 60),
                "input_box": pygame.Rect(990, 60, 100, 60),
                "next": "next"
            }
        ]

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                step = self.tutorial_steps[self.current_step]

                # update target scroll based on mouse scroll
                self.lore_target_scroll = self.lore_box.handle_event(event, self.lore_height, self.lore_target_scroll)

                # handle left mouse clicks
                if event.button == 1:

                    # handle tutorial steps for steps with multiple input boxes
                    if isinstance(step["input_box"], list):
                        for box in step["input_box"]:
                            if box.collidepoint(event.pos):

                                # handle action box events for action selecting step
                                if step["next"] == "select_gun":
                                    self.current_step += 1
                                    self.battle_state, self.chosen_action, self.inspecting_character, self.lore_scroll, self.lore_target_scroll = self.action_box.handle_event(event,
                                        self.battle_state, self.active_bot, self.chosen_action,
                                        self.inspecting_character, self.lore_scroll, self.lore_target_scroll)

                                # handle player zone events for bot healing step
                                if step["next"] == "select_bot":
                                    self.current_step += 1
                                    self.battle_state, self.active_bot, self.chosen_action, self.inspecting_character = self.execution.execute_action(event,
                                        self.player_bots, self.enemy_goons, self.active_effects,
                                        self.battle_state, self.active_bot, self.chosen_action,
                                        self.inspecting_character)

                    # handle tutorial steps for steps with a single input box
                    elif step["input_box"].collidepoint(event.pos):

                        # handle tutorial steps based on the next action
                        if step["next"] == "next":

                            # advance to the next line
                            self.current_line += 1

                            # advance to the next step if the lines for this step are done
                            if self.current_line >= len(step["lines"]):
                                self.current_line = 0
                                self.current_step += 1

                            # advance to the next scene if tutorial is done
                            if self.current_step >= len(self.tutorial_steps):
                                return BlankScene(self.fonts, self.font_cache)

                        # handle player zone events for bot selecting steps
                        elif step["next"] in ["select_gun_bot", "select_healer_bot"]:
                            self.current_step += 1
                            self.battle_state, self.active_bot, self.chosen_action, self.inspecting_character, self.lore_scroll, self.lore_target_scroll = self.player_zone.handle_event(event,
                                self.player_bots,
                                self.battle_state, self.active_bot, self.chosen_action,
                                self.inspecting_character, self.lore_scroll, self.lore_target_scroll)

                        # handle action box events for action selecting step
                        elif step["next"] == "select_heal":
                            self.current_step += 1
                            self.battle_state, self.chosen_action, self.inspecting_character, self.lore_scroll, self.lore_target_scroll = self.action_box.handle_event(event,
                                self.battle_state, self.active_bot, self.chosen_action,
                                self.inspecting_character, self.lore_scroll, self.lore_target_scroll)

                        # handle action execution events for attacking step
                        elif step["next"] == "select_dummy_goon_attack":
                            self.current_step += 1
                            self.battle_state, self.active_bot, self.chosen_action, self.inspecting_character = self.execution.execute_action(event,
                                self.player_bots, self.enemy_goons, self.active_effects,
                                self.battle_state, self.active_bot, self.chosen_action,
                                self.inspecting_character)

                        # handle enemy zone events for inspecting and harvesting steps
                        elif step["next"] in ["select_dummy_goon_inspect", "harvest_gears"]:
                            self.current_step += 1
                            self.inspecting_character, self.lore_scroll, self.lore_target_scroll, self.gears = self.enemy_zone.handle_event(event,
                                self.enemy_slots,
                                self.enemy_goons, self.active_effects,
                                self.battle_state,
                                self.inspecting_character, self.lore_scroll, self.lore_target_scroll,
                                self.gears)

                        # handle all events for finish round and free play steps
                        elif step["next"] in ["finish_round", "free_play"]:
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
                            self.battle_state, self.active_bot, self.chosen_action, self.inspecting_character = self.execution.execute_action(event,
                                self.player_bots, self.enemy_goons, self.active_effects,
                                self.battle_state, self.active_bot, self.chosen_action,
                                self.inspecting_character)

                # handle right mouse clicks
                elif event.button == 3:

                    # deselect action, bot, or inspected character once in free play step
                    if step["next"] == "free_play":
                        if self.chosen_action:
                            self.chosen_action = None
                            self.battle_state = "Player Turn"
                        elif self.active_bot:
                            self.inspecting_character = None
                            self.active_bot = None
                        elif self.inspecting_character:
                            self.inspecting_character = None

        return self

    def update(self):
        super().update()

        step = self.tutorial_steps[self.current_step]

        # advance to the next step if the round is finished in the finish round step
        if step["next"] == "finish_round" and self.battle_state == "Player Turn Over":
            self.current_step += 1

        # advance to the next step if the dummy goon is destroyed in the free play step
        if step["next"] == "free_play" and self.dummy_goon.visual_health <= 0:
            self.current_step += 1

    def draw(self, screen):
        # draw everything once in free play step
        if self.current_step >= 12:
            super().draw(screen)

        # introduce the drawings based on the tutorial steps
        else:
            screen.fill((0, 0, 0))

            # draw player zone
            self.player_zone.draw(screen, self.fonts, self.text_cache, self.player_bots, self.battle_state, self.active_bot, self.chosen_action, self.inspecting_character)

            # draw all active effects
            for effect in self.active_effects:
                if isinstance(effect, FloatingText):
                    effect.draw(screen, self.fonts, self.text_cache)
                else:
                    effect.draw(screen)

            # draw enemy zone after its introduced
            if (self.current_step >= 1) or (self.current_step == 0 and self.current_line >= 7):
                self.enemy_zone.draw(screen, self.fonts, self.text_cache, self.enemy_goons, self.battle_state, self.inspecting_character, self.elemental_bot)

            # draw action box after its introduced
            if self.current_step >= 2:
                self.action_box.draw(screen, self.font_cache, self.text_cache, self.battle_state, self.active_bot, self.chosen_action)

            # draw lore box after its introduced
            if self.current_step >= 6:
                self.lore_height = self.lore_box.draw(screen, self.fonts, self.text_cache, self.battle_state, self.inspecting_character, self.lore_height, self.lore_scroll, self.rounds)

        # draw the sciengineer image
        screen.blit(self.sciengineer_image, (400, 80))

        step = self.tutorial_steps[self.current_step]

        # draw dialogue box
        pygame.draw.rect(screen, (100, 100, 255), step["draw_box"])
        pygame.draw.rect(screen, (255, 255, 255), step["draw_box"], 3)

        # draw dialogue text
        dialogue_lines = wrap_text(step["lines"][self.current_line], self.fonts, step["draw_box"].width - 20)
        for i, line in enumerate(dialogue_lines):
            dialogue_text = render_text(self.fonts, self.text_cache, 24, line, (255, 255, 255))
            screen.blit(dialogue_text, (step["draw_box"].x + 10, step["draw_box"].y + 10 + i * 25))

        # draw next button if the step is a next step
        if step["next"] == "next":

            # draw next button
            mouse_pos = pygame.mouse.get_pos()
            if step["input_box"].collidepoint(mouse_pos):
                button_color = (150, 150, 255)
            else:
                button_color = (100, 100, 255)
            pygame.draw.rect(screen, button_color, step["input_box"])
            pygame.draw.rect(screen, (255, 255, 255), step["input_box"], 3)

            # draw next button text
            next_text = dynamic_text(self.font_cache, self.text_cache, "Next", 90, 50, (255, 255, 255))
            next_text_rect = next_text.get_rect(center=step["input_box"].center)
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
