# abilities.py

# import libraries
import pygame
import math
import random

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

class CheckpointRunes:
    def __init__(self, rect):
        # basic checkpoint runes info
        self.rect = rect

        # checkpoint runes state
        self.open = False
        self.completed = False

        # runes corners
        self.corners = [
            { # top-left corner
                "rect": pygame.Rect(400, 165, 50, 50),
                "line_offset": (-10, -10),
                "orientation": random.choice([1, 2, 3]),
                "target": 0
            },
            { # top-right corner
                "rect": pygame.Rect(750, 165, 50, 50),
                "line_offset": (10, 10),
                "orientation": random.choice([0, 2, 3]),
                "target": 1
            },
            { # bottom-right corner
                "rect": pygame.Rect(750, 515, 50, 50),
                "line_offset": (-10, -10),
                "orientation": random.choice([0, 1, 3]),
                "target": 2
            },
            { # bottom-left corner
                "rect": pygame.Rect(400, 515, 50, 50),
                "line_offset": (10, 10),
                "orientation": random.choice([0, 1, 2]),
                "target": 3
            }
        ]

    def handle_input(self, event, fonts, active_effects, party_rect, party_selected, moving):
        # handle input for opening the puzzle window
        if self.rect.collidepoint(event.pos) and not self.open and not self.completed:
            mouse_pos = pygame.mouse.get_pos()
            
            # check if the bots are close enough
            distance = math.hypot(party_rect.centerx - self.rect.centerx, party_rect.centery - self.rect.centery)
            if distance > 150:
                text = "Too Far"
                text_width = fonts[24].size(text)[0]
                text_x = mouse_pos[0] - text_width // 2
                active_effects.append(FloatingText((255, 255, 255), text_x, self.rect.bottom, text))

            # check if healer bot is selected
            elif party_selected != "Healer Bot":
                text1 = "You need a bot that"
                text2 = "can activate runes"
                text_width1 = fonts[24].size(text1)[0]
                text_width2 = fonts[24].size(text2)[0]
                text_x1 = mouse_pos[0] - text_width1 // 2
                text_x2 = mouse_pos[0] - text_width2 // 2
                active_effects.append(FloatingText((255, 255, 255), text_x1, self.rect.bottom, text1))
                active_effects.append(FloatingText((255, 255, 255), text_x2, self.rect.bottom + 20, text2))

            # open puzzle window
            else:
                self.open = True
                moving = False

        # handle input for interacting with the puzzle window
        elif self.open and not self.completed:
            for corner in self.corners:
                if corner["rect"].collidepoint(event.pos):

                    # rotate the corner orientation
                    corner["orientation"] = (corner["orientation"] + 1) % 4

                    # check if all corners are correctly oriented
                    for corner in self.corners:
                        if corner["orientation"] != corner["target"]:
                            break
                    else:
                        self.completed = True
                        text = "Checkpoint Activated!"
                        text_width = fonts[24].size(text)[0]
                        text_x = 580 - text_width // 2
                        active_effects.append(FloatingText((0, 255, 0), text_x, 365, text))

        return moving, self.completed

    def update(self, active_effects, moving):
        # close the puzzle window once its completed and the text has disappeared
        if self.open and self.completed and not active_effects:
            self.open = False
            moving = True

        return moving

    def draw(self, screen, fonts, text_cache):
        # draw a indicator that the rune has been activated
        if self.completed:
            pygame.draw.rect(screen, (0, 255, 0), (self.rect.centerx - 10, self.rect.centery - 10, 20, 20))

        # draw puzzle window when its open
        if self.open:

            # draw puzzle window box
            pygame.draw.rect(screen, (0, 0, 0), (350, 115, 500, 500), 0, 10)
            pygame.draw.rect(screen, (55, 255, 20), (350, 115, 500, 500), 3, 10)

            # draw the lines connecting the corners based on their orientation
            for corner in self.corners:
                start_pos = (corner["rect"].centerx + corner["line_offset"][0], corner["rect"].centery + corner["line_offset"][1])
                if corner["orientation"] == corner["target"]:
                    line_color = (0, 255, 0)
                else:
                    line_color = (255, 255, 255)
                if corner["orientation"] == 0:
                    pygame.draw.line(screen, line_color, start_pos, (corner["rect"].centerx + 350 + corner["line_offset"][0], corner["rect"].centery + corner["line_offset"][1]), 10)
                    pygame.draw.line(screen, line_color, start_pos, (corner["rect"].centerx + corner["line_offset"][0], corner["rect"].centery + 350 + corner["line_offset"][1]), 10)
                elif corner["orientation"] == 1:
                    pygame.draw.line(screen, line_color, start_pos, (corner["rect"].centerx - 350 + corner["line_offset"][0], corner["rect"].centery + corner["line_offset"][1]), 10)
                    pygame.draw.line(screen, line_color, start_pos, (corner["rect"].centerx + corner["line_offset"][0], corner["rect"].centery + 350 + corner["line_offset"][1]), 10)
                elif corner["orientation"] == 2:
                    pygame.draw.line(screen, line_color, start_pos, (corner["rect"].centerx - 350 + corner["line_offset"][0], corner["rect"].centery + corner["line_offset"][1]), 10)
                    pygame.draw.line(screen, line_color, start_pos, (corner["rect"].centerx + corner["line_offset"][0], corner["rect"].centery - 350 + corner["line_offset"][1]), 10)  
                elif corner["orientation"] == 3:
                    pygame.draw.line(screen, line_color, start_pos, (corner["rect"].centerx + 350 + corner["line_offset"][0], corner["rect"].centery + corner["line_offset"][1]), 10)
                    pygame.draw.line(screen, line_color, start_pos, (corner["rect"].centerx + corner["line_offset"][0], corner["rect"].centery - 350 + corner["line_offset"][1]), 10)

            # draw the corners
            for corner in self.corners:
                if corner["orientation"] == corner["target"]:
                    corner_color = (0, 255, 0)
                else:
                    corner_color = (255, 255, 255)
                pygame.draw.rect(screen, corner_color, corner["rect"])

        # draw hover text for the checkpoint runes
        else:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                text = "Checkpoint Runes"

                # draw checkpoint runes hover box
                text_width = fonts[15].size(text)[0]
                hover_rect = pygame.Rect(0, 0, text_width + 10, 14)
                hover_rect.left = mouse_pos[0]
                hover_rect.bottom = mouse_pos[1]
                pygame.draw.rect(screen, (0, 0, 0), hover_rect)
                pygame.draw.rect(screen, (255, 255, 255), hover_rect, 1)

                # draw checkpoint runes hover text
                hover_text = render_text(fonts, text_cache, 15, text, (255, 255, 255))
                hover_text_rect = hover_text.get_rect(center=hover_rect.center)
                screen.blit(hover_text, hover_text_rect)
