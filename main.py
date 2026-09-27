import asyncio
import pygame

# initialize pygame and font module
pygame.init()
pygame.font.init()

# import game modules
from game.bots import gun_bot, rico_bot
from game.characters import enemy_catalog
from game.drawing import update_animations, draw_screen, draw_main_menu
from game.battle import handle_input, enemy_turn, spawn_initial_enemies, check_game_over
from game.shop import all_bots

# ------------------------------
# MAIN
# ------------------------------

async def main():
    # screen settings
    screen = pygame.display.set_mode((1200, 730))
    # title
    pygame.display.set_caption("Rounds")
    # setup timer to control game speed
    clock = pygame.time.Clock()

    # setup fonts
    title_font = pygame.font.SysFont(None, 120)
    regular_font = pygame.font.SysFont(None, 24)
    floating_font = pygame.font.SysFont(None, 30)
    shop_title_font = pygame.font.SysFont(None, 40)
    font_cache = {}
    for size in range(10, 31):
        font_cache[size] = pygame.font.SysFont(None, size)
    text_cache = {}

    # slots for enemies to spawn in
    enemy_slots = [
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
    player_bots = [gun_bot, rico_bot]
    enemy_goons = []
    active_effects = []

    # initial game state variables
    game_state = "Main Menu"
    previous_game_state = "Main Menu"
    battle_state = "Player Turn"
    previous_battle_state = "Player Turn"

    # initial variables for player turn
    active_bot = None
    chosen_action = None

    # initial variables related to lore box
    inspecting_character = None
    lore_height = 0
    lore_scroll_y = 0.0
    lore_target_scroll_y = 0.0

    # initial variables related to shop
    menu_height = 0
    menu_scroll_y = 0.0
    menu_target_scroll_y = 0.0

    # initial variables for game progression
    gears = 0
    rounds = 1
    max_enemies = 3
    running = True

    # load initial character images
    for char in all_bots:
        char["bot"].load_images()
    for enemy, stats in enemy_catalog.items():
        stats["idle_image"] = pygame.image.load(stats["idle_image_path"]).convert_alpha()
        stats["hurt_image"] = pygame.image.load(stats["hurt_image_path"]).convert_alpha()
        stats["dead_image"] = pygame.image.load(stats["dead_image_path"]).convert_alpha()

    while running:

        # handle input events based on game state and battle state
        running, game_state, battle_state, previous_battle_state, active_bot, chosen_action, inspecting_character, lore_scroll_y, lore_target_scroll_y, menu_scroll_y, menu_target_scroll_y, gears = handle_input(
            running, player_bots, enemy_goons, active_effects, game_state, battle_state, previous_battle_state, active_bot, chosen_action, inspecting_character, lore_height, lore_scroll_y, lore_target_scroll_y, menu_height, menu_scroll_y, menu_target_scroll_y, gears, rounds, enemy_slots)

        if game_state == "Endless Mode" and previous_game_state != "Endless Mode":
            # setup for the first round of endless mode
            spawn_initial_enemies(enemy_goons, enemy_slots)
            gun_bot.reset_gun_aiming()
            previous_game_state = "Endless Mode"

        if game_state == "Main Menu":
            # screen for main menu
            draw_main_menu(screen, title_font, regular_font, font_cache, text_cache)

        elif game_state == "Endless Mode":
            # enemy turn logic
            battle_state, gears, rounds, max_enemies = enemy_turn(player_bots, enemy_goons, active_effects, battle_state, gears, rounds, max_enemies, enemy_slots)

            # check if game is over
            battle_state, lore_scroll_y, lore_target_scroll_y = check_game_over(player_bots, battle_state, lore_scroll_y, lore_target_scroll_y)

            # update animations
            lore_scroll_y, menu_scroll_y = update_animations(player_bots, enemy_goons, active_effects, battle_state, active_bot, chosen_action, lore_scroll_y, lore_target_scroll_y, menu_scroll_y, menu_target_scroll_y)

            # drawing, animation, and rendering
            lore_height, menu_height = draw_screen(
                screen, regular_font, floating_font, shop_title_font, font_cache, text_cache, player_bots, enemy_goons, active_effects, battle_state, active_bot, chosen_action, inspecting_character, lore_scroll_y, menu_height, menu_scroll_y, gears, rounds)

        
        # makes the game run at 60 frames per second
        clock.tick(60)

        # prints the current fps for debugging purposes
        fps = clock.get_fps()
        fps_text = regular_font.render(f"FPS: {fps:.2f}", True, (255, 255, 255))
        screen.blit(fps_text, (20, 20))

        # keeps the game from flickering
        pygame.display.flip()
        # prevents freezing in the web
        await asyncio.sleep(0)
    
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())