import typing
from typing import Tuple

import pygame

import components.component
import entities.actions.actions
import entities.creature
import entities.item
import utilities.logsetup
import utilities.ship_generator

log = utilities.logsetup.log()


class Player(entities.creature.Creature):

    def __init__(self):
        super().__init__('player', ID=0)
        self.visible = True
        self.action_points = 0
        self.speed = 101
        self.current_action = None
        self.fighter_component = components.component.FighterComponent(self, hp=100, strength=3)
        self.alive = True
        self.can_open_doors = True

    def handle_input(self, events, pressed_keys) -> typing.Union[entities.actions.actions.BaseAction, None]:
        for event in events:
            if self.fighter_component:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                    self.current_action = entities.actions.actions.MoveAction(self, (0, -1))
                    return self.current_action
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                    self.current_action = entities.actions.actions.MoveAction(self, (0, 1))
                    return self.current_action
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                    self.facing = entities.creature.Facing.left
                    self.facing_changed = True
                    self.current_action = entities.actions.actions.MoveAction(self, (-1, 0))
                    return self.current_action
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                    self.facing = entities.creature.Facing.right
                    self.facing_changed = True
                    self.current_action = entities.actions.actions.MoveAction(self, (1, 0))
                    return self.current_action
                elif event.type == pygame.JOYHATMOTION:
                    if event.value == (0, 1):  # up d-pad
                        self.current_action = entities.actions.actions.MoveAction(self, (0, -1))
                        return self.current_action
                    elif event.value == (0, -1):  # down d-pad
                        self.current_action = entities.actions.actions.MoveAction(self, (0, 1))
                        return self.current_action
                    elif event.value == (-1, 0):  # left d-pad
                        self.current_action = entities.actions.actions.MoveAction(self, (-1, 0))
                        return self.current_action
                    elif event.value == (1, 0):  # right d-pad
                        self.current_action = entities.actions.actions.MoveAction(self, (1, 0))
                        return self.current_action
                    else:
                        return None
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    item = self.moved_to_item()
                    if item is not None and isinstance(item, entities.item.Item):
                        self.current_action = entities.actions.actions.PickUpItemAction(self, item)
                        return self.current_action
                    else:
                        return None
            else:
                self.alive = False

    def move(self, direction: Tuple[int, int]):
        super(Player, self).move(direction)

    def consume_item(self, item: entities.item.Item):
        if item is not None and item in self.inventory and item.consumable and isinstance(item, entities.item.Item):
            if isinstance(item.consumable, components.consumable.HealingConsumable) \
                    and self.fighter_component.hp >= self.fighter_component.max_hp:
                log.info("Your health is already full.")
                return None
            self.current_action = entities.actions.actions.ItemAction(self, item)
        else:
            # raise err
            return None

    def equip_item(self, item: entities.item.Item):
        if item is not None and item in self.inventory and item.equippable and isinstance(
                item.equippable,
                components.equippable.Equippable):
            self.equipment[item.equippable.slot] = item
            self.current_action = entities.actions.actions.ItemAction(self, item)
        else:
            # raise err
            return None

    def drop_item(self, item: entities.item.Item):
        if item is not None and item in self.inventory and isinstance(item, entities.item.Item):
            self.parent_scene.place_item(item,
                                         utilities.ship_generator.Coordinate(self.x_pos, self.y_pos))
            item.destroy(self)

    def take_turn(self) -> int:
        cost = self.current_action.perform()
        self.current_action = None
        return cost

    def unequip_item(self, item: entities.item.Item):
        if item is not None and item.equippable and isinstance(item.equippable,components.equippable.Equippable):
            self.equipment[item.equippable.slot] = None
            self.inventory.append(item)
            self.current_action = entities.actions.actions.ItemAction(self, item)
        else:
            # raise err
            return None
