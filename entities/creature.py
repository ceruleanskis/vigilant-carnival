import typing
from typing import Union, Tuple

import pygame

import components.map
import entities.entity
import scenes.game_scene
import utilities.constants
import utilities.game_utils
import utilities.load_data


class Creature(entities.entity.Entity):
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
        self.action_points = 0
        self.speed = 100
        import entities.actions.actions
        self.current_action = entities.actions.actions.RandomMoveAction(self)
        self.parent_scene: scenes.game_scene.GameScene = None

    def to_json(self):
        return {
            'name': self.name,
            'x_pos': self.x_pos,
            'y_pos': self.y_pos,
            'action_points': self.action_points,
            'speed': self.speed
        }

    def move(self, direction: Tuple[int, int]):
        self.previous_x_pos = self.x_pos
        self.previous_y_pos = self.y_pos
        self.rect.move_ip((direction[0] * utilities.constants.TILE_SIZE, direction[1] * utilities.constants.TILE_SIZE))
        self.x_pos += direction[0]
        self.y_pos += direction[1]

    def moved_to_blocked(self) -> typing.Union[None, 'Creature', components.map.Tile]:
        for other_creature in self.parent_scene.creatures:
            if other_creature is not self and self.x_pos == other_creature.x_pos and self.y_pos == other_creature.y_pos:
                self.teleport(self.previous_x_pos, self.previous_y_pos)
                return other_creature

        tile = self.parent_scene.tile_map.tile_map[self.x_pos][self.y_pos]
        if tile.type != 'floor' and tile.type != 'open_door':
            if tile.type == 'door':
                tile.type = 'open_door'
                tile.image_str = utilities.load_data.TILE_DATA[tile.type]['image']
            else:
                self.teleport(self.previous_x_pos, self.previous_y_pos)
                return tile

        return None

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

    def take_turn(self) -> int:
        self.current_action = entities.actions.actions.RandomMoveAction(self)
        return self.current_action.perform()
