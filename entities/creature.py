from typing import Union, Tuple

import pygame

import utilities.constants
import utilities.game_utils
import utilities.load_data
from entities.entity import Entity


class Creature(Entity):
    def __init__(self, name: str):
        super().__init__()
        self.x_pos = 1
        self.y_pos = 1

        self.name = name
        image = utilities.game_utils.GameUtils.load_sprite(utilities.load_data.ENTITY_DATA[self.name]['image'],
                                                           (0, 0, 0))
        self.surface = image
        self.rect = self.surface.get_rect()
        self.rect.x = self.x_pos * utilities.constants.TILE_SIZE
        self.rect.y = self.y_pos * utilities.constants.TILE_SIZE
        self.previous_x_pos = self.x_pos
        self.previous_y_pos = self.y_pos

    def move(self, direction: Tuple[int, int]):
        self.previous_x_pos = self.x_pos
        self.previous_y_pos = self.y_pos
        self.rect.move_ip((direction[0] * utilities.constants.TILE_SIZE, direction[1] * utilities.constants.TILE_SIZE))
        self.x_pos += direction[0]
        self.y_pos += direction[1]

    def teleport(self, x_pos, y_pos):
        self.rect.x = x_pos * utilities.constants.TILE_SIZE
        self.rect.y = y_pos * utilities.constants.TILE_SIZE
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.previous_x_pos = x_pos
        self.previous_y_pos = y_pos

    def render(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        self.teleport(self.x_pos, self.y_pos)
        self.update()

    def take_turn(self):
        raise NotImplementedError
