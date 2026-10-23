# abilities.py

# import libraries
import pygame
import math

# import game modules
from .effects import FloatingText
from .helper import render_text

class MetalObject:
    def __init__(self, rect, name, health, images_path):
        # basic metal object info
        self.rect = rect
        self.name = name
        self.health = health
        self.destroyed = False

        # images
        self.images_path = images_path
        self.images = []
        self.current_image_index = 0

        # load images for the metal object
        for path in self.images_path:
            image = pygame.image.load(path).convert_alpha()
            self.images.append(image)

    def take_damage(self, fonts, party_rect, party_selected, active_effects):
        mouse_pos = pygame.mouse.get_pos()

        # check if the bots are close enough
        distance = math.hypot(party_rect.centerx - self.rect.centerx, party_rect.centery - self.rect.centery)
        if distance > 150:
            text = "Too Far"
            text_width = fonts[24].size(text)[0]
            text_x = mouse_pos[0] - text_width // 2
            active_effects.append(FloatingText((150, 150, 150), text_x, self.rect.bottom, text))

        # check if gun bot is selected
        elif party_selected != "Gun Bot":
            text1 = "You need a bot that"
            text2 = "can destroy metal"
            text_width1 = fonts[24].size(text1)[0]
            text_width2 = fonts[24].size(text2)[0]
            text_x1 = mouse_pos[0] - text_width1 // 2
            text_x2 = mouse_pos[0] - text_width2 // 2
            active_effects.append(FloatingText((150, 150, 150), text_x1, self.rect.bottom, text1))
            active_effects.append(FloatingText((150, 150, 150), text_x2, self.rect.bottom + 20, text2))

        # break the door
        else:
            self.current_image_index += 1
            self.health -= 1
            if self.health == 0:
                self.destroyed = True

    def draw(self, screen, fonts, text_cache):
        # draw metal object if not destroyed
        if not self.destroyed:
            screen.blit(self.images[self.current_image_index], self.rect)

        # draw hover text for metal object
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos) and not self.destroyed:

            # draw metal object hover box
            text_width = fonts[15].size(self.name)[0]
            hover_rect = pygame.Rect(0, 0, text_width + 10, 14)
            hover_rect.left = mouse_pos[0]
            hover_rect.bottom = mouse_pos[1]
            pygame.draw.rect(screen, (0, 0, 0), hover_rect)
            pygame.draw.rect(screen, (255, 255, 255), hover_rect, 1)

            # draw metal object hover text
            hover_text = render_text(fonts, text_cache, 15, self.name, (255, 255, 255))
            hover_text_rect = hover_text.get_rect(center=hover_rect.center)
            screen.blit(hover_text, hover_text_rect)
