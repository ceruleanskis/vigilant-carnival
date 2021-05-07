import typing
from typing import Union

import pygame

import entities.entity
import utilities.constants
import utilities.game_utils
import utilities.load_data
import utilities.logsetup
import utilities.map_helpers

log = utilities.logsetup.log()


class Item(entities.entity.Entity):

    def __init__(self, key: str, ID: int):
        import components.component
        import scenes.game_scene
        import components.consumable

        super().__init__(key)
        self.name = utilities.load_data.ITEM_DATA[self.key]['name']
        self.ID = ID
        self.x_pos = 1
        self.y_pos = 1

        self.item_component = components.component.ItemComponent(self)
        self.tileset_alpha: typing.Union[None, typing.Tuple[int, int, int]] = \
            utilities.load_data.ITEM_DATA[self.key]['tileset_alpha']
        convert_alpha = True
        if self.tileset_alpha is None:
            convert_alpha = False

        self.image = utilities.game_utils.GameUtils.load_sprite(utilities.load_data.ITEM_DATA[self.key]['image'],
                                                                self.tileset_alpha, convert_alpha)
        self.type = utilities.load_data.ITEM_DATA[self.key]['type']
        self.description = utilities.load_data.ITEM_DATA[self.key]['description']
        self.image_num = 0
        self.rect = self.image.get_rect()
        self.rect.x = self.x_pos * utilities.constants.TILE_SIZE
        self.rect.y = self.y_pos * utilities.constants.TILE_SIZE
        self.parent_scene: scenes.game_scene.GameScene = None
        self.consumable = None
        self.load_consumables()

    def to_json(self) -> typing.Dict:
        return {
            'name': self.name,
            'key': self.key,
            'x_pos': self.x_pos,
            'y_pos': self.y_pos,
            'id': self.ID,
            'tileset_alpha': self.tileset_alpha
        }

    @staticmethod
    def from_json(json_obj: typing.Dict) -> 'Item':
        item_key = json_obj['key']
        item = Item(item_key, json_obj['id'])
        item.x_pos = json_obj['x_pos']
        item.y_pos = json_obj['y_pos']

        try:
            item.tileset_alpha = json_obj['tileset_alpha']
        except KeyError as err:
            log.warning(f"Entity {item.name} has no tileset alpha in JSON file.")

        return item

    def disappear(self):
        self.blocks = False
        self.parent_scene.items.remove(self)
        self.parent_scene.item_sprites.remove(self)
        self.parent_scene.all_sprites.remove(self)

    def destroy(self, consumer: entities.creature.Creature):
        if self in consumer.inventory:
            consumer.inventory.remove(self)
        else:
            log.warning(f"Could not remove {self.name} from inventory.")

    @staticmethod
    def get_index(item_list, item):
        for index, thing in enumerate(item_list):
            if item.ID == thing.ID:
                return index

        return -1

    def render(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        # self.teleport(self.x_pos, self.y_pos)
        self.update()

    def load_consumables(self):
        import components.consumable

        if "consumable" in utilities.load_data.ITEM_DATA[self.key]:
            consumable_type = None
            if "type" in utilities.load_data.ITEM_DATA[self.key]["consumable"][0]:
                consumable_type = utilities.load_data.ITEM_DATA[self.key]["consumable"][0]['type']
            else:
                log.debug(f'No type found for {self.key} {["consumable"][0]} in items.json.')

            if consumable_type == "HealingConsumable":
                if "amount" in utilities.load_data.ITEM_DATA[self.key]["consumable"][0]:
                    amount = utilities.load_data.ITEM_DATA[self.key]["consumable"][0]["amount"]
                    self.consumable = components.consumable.HealingConsumable(amount, entity=self)
                else:
                    log.debug(f'No amount found for HealingConsumable {self.key} in items.json.')
            else:
                log.debug(f'Consumable type {consumable_type} not found.')
        else:
            log.info("None type consumable")
            self.consumable = None
