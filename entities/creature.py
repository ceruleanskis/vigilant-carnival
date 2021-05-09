import typing
from typing import Union, Tuple

import pygame

import components.map
import entities.entity
import utilities.constants
import utilities.fonts
import utilities.game_utils
import utilities.helpers
import utilities.load_data
import utilities.logsetup

font = utilities.fonts.default(24)

log = utilities.logsetup.log()


class Facing:
    left = 'left'
    right = 'right'


class Creature(entities.entity.Entity):
    def __init__(self, key: str, ID: int):
        import scenes.game_scene
        import components.component
        import entities.item
        import entities.actions.actions

        super().__init__(key)
        self.key = key
        self.name = utilities.load_data.ENTITY_DATA[key]['name']

        self.ID = ID
        self.x_pos = 1
        self.y_pos = 1

        self.tileset_alpha: typing.Union[None, typing.Tuple[int, int, int]] = \
            utilities.load_data.ENTITY_DATA[self.key]['tileset_alpha']
        convert_alpha = True
        if self.tileset_alpha is None:
            convert_alpha = False

        self.images = [
            utilities.game_utils.GameUtils.load_sprite(utilities.load_data.ENTITY_DATA[self.key]['images'][0],
                                                       self.tileset_alpha, convert_alpha),
            utilities.game_utils.GameUtils.load_sprite(utilities.load_data.ENTITY_DATA[self.key]['images'][1],
                                                       self.tileset_alpha, convert_alpha)
        ]
        self.image_num = 0
        self.image = self.images[self.image_num].copy()
        self.corpse_image = utilities.game_utils.GameUtils.load_sprite(
            utilities.load_data.ENTITY_DATA[self.key]['corpse_image'])
        self.rect = self.image.get_rect()
        self.rect.x = self.x_pos * utilities.constants.TILE_SIZE
        self.rect.y = self.y_pos * utilities.constants.TILE_SIZE
        self.previous_x_pos = self.x_pos
        self.previous_y_pos = self.y_pos
        self.action_points = 0
        self.speed = 100
        self.parent_scene: scenes.game_scene.GameScene = None
        self.next_move = pygame.time.get_ticks() + 500  # 100ms = 0.1s
        self.facing = Facing.left
        self.facing_changed = False
        self.health_modified = False
        self.health_modified_amount = 0
        self.did_set_corpse_image = False
        self.current_action = entities.actions.actions.ChasePlayerAction(self)
        self.inventory: typing.List[entities.item.Item] = []
        self.equipment: typing.Dict[utilities.helpers.EquipmentSlot, typing.Union[None, entities.item.Item]] = {
            utilities.helpers.EquipmentSlot.WEAPON: None,
            utilities.helpers.EquipmentSlot.CHEST: None,
            utilities.helpers.EquipmentSlot.HEAD: None,
            utilities.helpers.EquipmentSlot.HANDS: None,
            utilities.helpers.EquipmentSlot.LEGS: None,
            utilities.helpers.EquipmentSlot.FEET: None
        }
        self.fighter_component = components.component.FighterComponent(self, hp=5, strength=2)
        self.can_open_doors = False

    def to_json(self):
        return {
            'key': self.key,
            'name': self.name,
            'x_pos': self.x_pos,
            'y_pos': self.y_pos,
            'action_points': self.action_points,
            'speed': self.speed,
            'id': self.ID,
            'tileset_alpha': self.tileset_alpha,
            'previous_x_pos': self.previous_x_pos,
            'previous_y_pos': self.previous_y_pos
        }

    @staticmethod
    def from_json(json_obj: typing.Dict) -> 'Creature':
        creature_key = json_obj['key']
        creature = Creature(creature_key, json_obj['id'])
        creature.x_pos = json_obj['x_pos']
        creature.y_pos = json_obj['y_pos']
        creature.action_points = json_obj['action_points']
        creature.speed = json_obj['speed']
        creature.previous_x_pos = json_obj['previous_x_pos']
        creature.previous_y_pos = json_obj['previous_y_pos']

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
            if tile.type == 'door' and self.can_open_doors:
                tile.type = 'floor'
                tile.image_str = utilities.load_data.TILE_DATA[tile.type]['image']
            else:
                self.teleport(self.previous_x_pos, self.previous_y_pos)
                return tile

        return None

    def moved_to_item(self) -> typing.Union[None, 'Creature', 'Item', components.map.Tile]:
        if self.parent_scene and self.parent_scene.items:
            for item in self.parent_scene.items:
                if self.x_pos == item.x_pos and self.y_pos == item.y_pos:
                    return item
        return None

    def teleport(self, x_pos, y_pos):
        self.rect.x = x_pos * utilities.constants.TILE_SIZE
        self.rect.y = y_pos * utilities.constants.TILE_SIZE
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.previous_x_pos = x_pos
        self.previous_y_pos = y_pos

    def update(self):
        if self.fighter_component and self.fighter_component.alive:
            if pygame.time.get_ticks() >= self.next_move or self.facing_changed:
                self.next_move = pygame.time.get_ticks() + 500  # animation every 0.5s = 500ms
                self.update_facing()
                if self.health_modified:
                    self.update_damage_display()
        else:
            pass

    def update_facing(self):
        if self.image_num == 0:
            self.image_num = 1
        else:
            self.image_num = 0
        self.image = self.images[self.image_num].copy()
        if self.facing == Facing.right:
            self.image = pygame.transform.flip(self.image, True, False)
        self.facing_changed = False

    def update_damage_display(self):
        self.image = self.images[self.image_num].copy()

        if self.health_modified_amount > 0:
            color = utilities.constants.GREEN
        else:
            color = utilities.constants.RED

        self.image.fill(color, special_flags=pygame.BLEND_MULT)
        damage_text = font.render(str(abs(self.health_modified_amount)), True, color)
        self.image.blit(damage_text, self.image.get_rect())
        self.health_modified = False
        self.health_modified_amount = 0

    def render(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        self.teleport(self.x_pos, self.y_pos)
        self.update()

    def take_turn(self) -> int:
        self.current_action = entities.actions.actions.ChasePlayerAction(self)
        return self.current_action.perform()

    def die(self):
        self.image = self.corpse_image
        self.did_set_corpse_image = True
        self.fighter_component = None
        self.blocks = False
        self.current_action = None
