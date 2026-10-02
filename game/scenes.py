import pygame

# import game modules
from .battle import spawn_initial_enemies, player_turn, select_action, enemy_turn, check_game_over
from .bots import gun_bot, rico_bot, lazer_bot
from .drawing import update_animations, draw_screen
from .helper import dynamic_text, render_text

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
                            return self
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

class EndlessModeScene():
    def __init__(self, fonts, font_cache):
        # scene texts
        self.fonts = fonts
        self.font_cache = font_cache
        self.text_cache = {}

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

        # initial list of characters and effects
        self.player_bots = [gun_bot, rico_bot]
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
        self.lore_scroll_y = 0.0
        self.lore_target_scroll_y = 0.0
    
        # initial variables related to shop
        self.menu_height = 0
        self.menu_scroll_y = 0.0
        self.menu_target_scroll_y = 0.0
    
        # initial variables for game progression
        self.gears = 0
        self.rounds = 1
        self.max_enemies = 3

        # setup for the first round of endless mode
        spawn_initial_enemies(self.enemy_goons, self.enemy_slots)
        gun_bot.reset_gun_aiming()

    def handle_input(self, events):
        for event in events:

            # handles mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.battle_state, self.previous_battle_state, self.active_bot, self.chosen_action, self.inspecting_character, self.lore_scroll_y, self.lore_target_scroll_y, self.menu_scroll_y, self.menu_target_scroll_y, self.gears = player_turn(
                    event, mouse_pos,
                    self.player_bots, self.enemy_goons, self.active_effects,
                    self.battle_state, self.previous_battle_state, self.active_bot, self.chosen_action,
                    self.inspecting_character, self.lore_height, self.lore_scroll_y, self.lore_target_scroll_y,
                    self.menu_height, self.menu_scroll_y, self.menu_target_scroll_y,
                    self.gears, self.rounds, self.enemy_slots)

            # handles key presses
            elif event.type == pygame.KEYDOWN:
                if self.battle_state != "Shop" and not lazer_bot.actions[0]["movement_mode"]:
                    # select action if bot is selected based on key press
                    self.battle_state, self.chosen_action, self.inspecting_character, self.lore_scroll_y, self.lore_target_scroll_y = select_action(None, event,
                        self.battle_state, self.active_bot, self.chosen_action,
                        self.inspecting_character, self.lore_scroll_y, self.lore_target_scroll_y)

        return self

    def update(self):
        # enemy turn logic
        self.battle_state, self.gears, self.rounds, self.max_enemies = enemy_turn(
            self.player_bots, self.enemy_goons, self.active_effects, self.battle_state, self.gears, self.rounds, self.max_enemies, self.enemy_slots)

        # check if game is over
        self.battle_state, self.lore_scroll_y, self.lore_target_scroll_y = check_game_over(self.player_bots, self.battle_state, self.lore_scroll_y, self.lore_target_scroll_y)

        # update animations
        self.lore_scroll_y, self.menu_scroll_y = update_animations(
            self.player_bots, self.enemy_goons, self.active_effects,
            self.battle_state, self.active_bot, self.chosen_action,
            self.lore_scroll_y, self.lore_target_scroll_y,
            self.menu_scroll_y, self.menu_target_scroll_y)

    def draw(self, screen):
        # drawing and animation
        self.lore_height, self.menu_height = draw_screen(screen,
            self.fonts, self.font_cache, self.text_cache,
            self.player_bots, self.enemy_goons, self.active_effects,
            self.battle_state, self.active_bot, self.chosen_action,
            self.inspecting_character, self.lore_scroll_y,
            self.menu_height, self.menu_scroll_y,
            self.gears, self.rounds)
