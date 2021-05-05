import typing
from typing import Union

import pygame

import entities.entity
import utilities.constants
import utilities.game_utils
import utilities.load_data
import utilities.map_helpers

log = utilities.logsetup.log()


class Item(entities.entity.Entity):

    def __init__(self, name: str, ID: int):
        import components.component
        import scenes.game_scene
        import components.consumable

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
        self.type = utilities.load_data.ITEM_DATA[self.name]['type']
        self.description = utilities.load_data.ITEM_DATA[self.name]['description']
        self.image_num = 0
        self.rect = self.image.get_rect()
        self.rect.x = self.x_pos * utilities.constants.TILE_SIZE
        self.rect.y = self.y_pos * utilities.constants.TILE_SIZE
        self.parent_scene: scenes.game_scene.GameScene = None
        self.consumable = None
        self.load_consumables()

    def disappear(self):
        self.blocks = False
        self.parent_scene.items.remove(self)
        self.parent_scene.item_sprites.remove(self)
        self.parent_scene.all_sprites.remove(self)

    def destroy(self, consumer: entities.creature.Creature):
        if self in consumer.inventory:
            self.consumable = None
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

        if "consumable" in utilities.load_data.ITEM_DATA[self.name]:
            consumable_type = None
            if "type" in utilities.load_data.ITEM_DATA[self.name]["consumable"][0]:
                consumable_type = utilities.load_data.ITEM_DATA[self.name]["consumable"][0]['type']
            else:
                log.debug(f'No type found for {self.name} {["consumable"][0]} in items.json.')

            if consumable_type == "HealingConsumable":
                if "amount" in utilities.load_data.ITEM_DATA[self.name]["consumable"][0]:
                    amount = utilities.load_data.ITEM_DATA[self.name]["consumable"][0]["amount"]
                    self.consumable = components.consumable.HealingConsumable(amount, entity=self)
                else:
                    log.debug(f'No amount found for HealingConsumable {self.name} in items.json.')
            else:
                log.debug(f'Consumable type {consumable_type} not found.')
        else:
            log.info("None type consumable")
            self.consumable = None
