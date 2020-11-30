from typing import Union, Tuple

import pygame

import utilities.constants
import utilities.load_data
from entities.entity import Entity


class Player(Entity):
    def __init__(self):
        super().__init__()
        self.x_pos = 1
        self.y_pos = 1
        # self.surface = pygame.Surface((utilities.constants.TILE_SIZE,
        #                                utilities.constants.TILE_SIZE))
        # self.surface.fill((255, 255, 0))

        image = utilities.game_utils.GameUtils.load_sprite(utilities.load_data.ENTITY_DATA['player']['image'],(0,0,0))
        # image.set_alpha(128)
        self.surface = image
        self.rect = self.surface.get_rect()
        self.rect.x = self.x_pos * utilities.constants.TILE_SIZE
        self.rect.y = self.y_pos * utilities.constants.TILE_SIZE
        self.previous_x_pos = self.x_pos
        self.previous_y_pos = self.y_pos

    def handle_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                self.move((0, -1))
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                self.move((0, 1))
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                self.move((-1, 0))
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                self.move((1, 0))
            elif event.type == pygame.JOYHATMOTION:
                if event.value == (0, 1):  # up d-pad
                    self.move((0, -1))
                elif event.value == (0, -1):  # down d-pad
                    self.move((0, 1))
                elif event.value == (-1, 0):  # left d-pad
                    self.move((-1, 0))
                elif event.value == (1, 0):  # right d-pad
                    self.move((1, 0))
                else:
                    pass

    def move(self, direction: Tuple[int, int]):
        self.previous_x_pos = self.x_pos
        self.previous_y_pos = self.y_pos
        self.rect.move_ip((direction[0] * utilities.constants.TILE_SIZE, direction[1] * utilities.constants.TILE_SIZE))
        self.x_pos += direction[0]
        self.y_pos += direction[1]
        # # Keep player on the screen
        #
        # if self.rect.left < 0:
        #     self.rect.left = 0
        #
        # if self.rect.right > SCREEN_WIDTH:
        #     self.rect.right = SCREEN_WIDTH
        #
        # if self.rect.top <= 0:
        #     self.rect.top = 0
        #
        # if self.rect.bottom >= SCREEN_HEIGHT:
        #     self.rect.bottom = SCREEN_HEIGHT
        pass

    def teleport(self, x_pos, y_pos):
        self.rect.x = x_pos * utilities.constants.TILE_SIZE
        self.rect.y = y_pos * utilities.constants.TILE_SIZE
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.previous_x_pos = x_pos
        self.previous_y_pos = y_pos

    def update(self):
        self.update()
        pass

    def render(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        # self.sprite.image = pygame.Surface((self.size, self.size))

        # self.sprite.rect = self.sprite.image.get_rect()
        # self.sprite.rect.x = self.x
        # self.sprite.rect.y = self.y
        # screen.blit(self.surface, self.rect)
        pass
