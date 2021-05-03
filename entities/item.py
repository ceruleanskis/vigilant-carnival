import typing
from typing import Union

import pygame

import entities.entity
import utilities.constants
import utilities.game_utils
import utilities.load_data
import utilities.map_helpers


class Item(entities.entity.Entity):

    def __init__(self, name: str, ID: int):
        import components.component
        import scenes.game_scene

        super().__init__(name)
        self.ID = ID
        self.x_pos = 1
        self.y_pos = 1

        self.item_component = components.component.ItemComponent(self)
        self.tileset_alpha: typing.Union[None, typing.Tuple[int, int, int]] = \
            utilities.load_data.ITEM_DATA[self.name]['tileset_alpha']
        convert_alpha = True
        if self.tileset_alpha is None:
            convert_alpha = False

        self.image = utilities.game_utils.GameUtils.load_sprite(utilities.load_data.ITEM_DATA[self.name]['image'],
                                                                self.tileset_alpha, convert_alpha)
        self.image_num = 0
        # self.image = self.image[self.image_num].copy()
        self.rect = self.image.get_rect()
        self.rect.x = self.x_pos * utilities.constants.TILE_SIZE
        self.rect.y = self.y_pos * utilities.constants.TILE_SIZE
        # self.previous_x_pos = self.x_pos
        # self.previous_y_pos = self.y_pos
        self.parent_scene: scenes.game_scene.GameScene = None

    def disappear(self):
        self.image = None
        self.blocks = False
        index = self.get_index(self.parent_scene.items, self)
        self.parent_scene.items.remove(self)
        print(index)

    @staticmethod
    def get_index(item_list, item):
        for index, thing in enumerate(item_list):
            if item.ID == thing.ID:
                return index

        return -1

    def render(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        # self.teleport(self.x_pos, self.y_pos)
        self.update()
