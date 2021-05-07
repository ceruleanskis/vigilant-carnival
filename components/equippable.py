import typing

import components.component
import entities.actions.actions
import entities.creature
import entities.item
import utilities.helpers
import utilities.logsetup

log = utilities.logsetup.log()


class Equippable(components.component.BaseComponent):
    def __init__(self, entity: entities.item.Item, slot: utilities.helpers.EquipmentSlot, strength_modifier=0, hp_modifier=0):
        super().__init__(entity)
        self.hp_modifier = hp_modifier
        self.strength_modifier = strength_modifier
        self.entity = entity
        self.slot = slot

    def get_action(self, equipper: entities.creature.Creature) -> typing.Optional[entities.actions.actions.BaseAction]:
        """Try to return the action for this item."""
        return entities.actions.actions.ItemAction(equipper, self.entity)

    def activate(self, action: entities.actions.actions.ItemAction) -> int:
        action_cost = 100
        equipper = action.creature

        self.entity.destroy(equipper)
        log.info(f"You equip the {self.entity.name}.")
        return action_cost
