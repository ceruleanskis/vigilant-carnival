import typing
from typing import Union, Tuple

import pygame

import components.map
import entities.entity
import utilities.constants
import utilities.game_utils
import utilities.load_data
import utilities.logsetup

log = utilities.logsetup.log()


class Facing:
    left = 'left'
    right = 'right'


class Creature(entities.entity.Entity):
    def __init__(self, name: str):
        import scenes.game_scene
        import components.component

        super().__init__(name)
        self.x_pos = 1
        self.y_pos = 1

        self.fighter_component = components.component.FighterComponent(self, hp=5, strength=2)

        self.tileset_alpha: typing.Union[None, typing.Tuple[int, int, int]] = \
            utilities.load_data.ENTITY_DATA[self.name]['tileset_alpha']
        convert_alpha = True
        if self.tileset_alpha is None:
            convert_alpha = False

        self.images = [
            utilities.game_utils.GameUtils.load_sprite(utilities.load_data.ENTITY_DATA[self.name]['images'][0],
                                                       self.tileset_alpha, convert_alpha),
            utilities.game_utils.GameUtils.load_sprite(utilities.load_data.ENTITY_DATA[self.name]['images'][1],
                                                       self.tileset_alpha, convert_alpha)
        ]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = self.x_pos * utilities.constants.TILE_SIZE
        self.rect.y = self.y_pos * utilities.constants.TILE_SIZE
        self.previous_x_pos = self.x_pos
        self.previous_y_pos = self.y_pos
        self.action_points = 0
        self.speed = 100
        self.current_action = entities.actions.actions.RandomMoveAction(self)
        self.parent_scene: scenes.game_scene.GameScene = None
        self.image_num = 0
        self.image = self.images[0]
        self.next_move = pygame.time.get_ticks() + 500  # 100ms = 0.1s
        self.facing = Facing.left
        self.facing_changed = False
        self.damaged = False
        self.damage_taken = 0

    def to_json(self):
        return {
            'name': self.name,
            'x_pos': self.x_pos,
            'y_pos': self.y_pos,
            'action_points': self.action_points,
            'speed': self.speed
        }

    @staticmethod
    def from_json(json_obj: typing.Dict) -> 'Creature':
        creature_name = json_obj['name']
        creature = Creature(creature_name)
        creature.x_pos = json_obj['x_pos']
        creature.y_pos = json_obj['y_pos']
        creature.action_points = json_obj['action_points']
        creature.speed = json_obj['speed']

        try:
            creature.tileset_alpha = json_obj['tileset_alpha']
        except KeyError as err:
            log.warning(f"Entity {creature.name} has no tileset alpha in JSON file.")

        return creature

    def move(self, direction: Tuple[int, int]):
        self.previous_x_pos = self.x_pos
        self.previous_y_pos = self.y_pos
        self.rect.move_ip((direction[0] * utilities.constants.TILE_SIZE, direction[1] * utilities.constants.TILE_SIZE))
        self.x_pos += direction[0]
        self.y_pos += direction[1]

        if direction == (-1, 0):
            self.facing = Facing.left
            self.facing_changed = True

        if direction == (1, 0):
            self.facing = Facing.right
            self.facing_changed = True

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

    def update(self):
        if pygame.time.get_ticks() >= self.next_move or self.facing_changed:
            self.next_move = pygame.time.get_ticks() + 500  # 100ms = 0.1s
            if self.image_num == 0:
                self.image_num = 1
                self.image = self.images[1]
            else:
                self.image_num = 0
                self.image = self.images[0]

            if self.facing == Facing.right:
                self.image = pygame.transform.flip(self.image, True, False)

            self.facing_changed = False

    def render(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        self.teleport(self.x_pos, self.y_pos)
        self.update()

    def take_turn(self) -> int:
        self.current_action = entities.actions.actions.RandomMoveAction(self)
        return self.current_action.perform()

    def die(self):
        self.fighter_component = None
        self.blocks = False
        self.current_action = None
