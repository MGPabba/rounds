import asyncio
import pygame

# initialize pygame and font module
pygame.init()
pygame.font.init()

# import game modules
from game.scenes import MainMenuScene

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
    fonts = {
        24: pygame.font.SysFont(None, 24),
        30: pygame.font.SysFont(None, 30),
        40: pygame.font.SysFont(None, 40),
        120: pygame.font.SysFont(None, 120)
    }
    font_cache = {}
    for size in range(10, 31):
        font_cache[size] = pygame.font.SysFont(None, size)

    # initalize the first scene
    current_scene = MainMenuScene(fonts, font_cache)
    running = True

    while running:
        events = pygame.event.get()
        
        # quit game if window is closed or escape key is pressed
        for event in events:
            if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
                break

        # handle input, update, and draw for the current scene
        current_scene = current_scene.handle_input(events)
        current_scene.update()
        current_scene.draw(screen)
        
        # makes the game run at 60 frames per second
        clock.tick(60)

        # draws the current fps for debugging purposes
        fps = clock.get_fps()
        fps_text = fonts[24].render(f"FPS: {fps:.2f}", True, (255, 255, 255))
        screen.blit(fps_text, (20, 20))

        # keeps the game from flickering
        pygame.display.flip()
        # prevents freezing in the web
        await asyncio.sleep(0)
    
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())