import typing

import components.component
import entities.actions.actions
import entities.creature
import entities.item
import utilities.logsetup

log = utilities.logsetup.log()


class Consumable(components.component.BaseComponent):
    def __init__(self, entity: entities.item.Item):
        super().__init__(entity)
        self.entity = entity

    def get_action(self, consumer: entities.creature.Creature) -> typing.Optional[entities.actions.actions.BaseAction]:
        """Try to return the action for this item."""
        return entities.actions.actions.ItemAction(consumer, self.entity)

    def activate(self, action: entities.actions.actions.ItemAction) -> None:
        raise NotImplementedError()


class HealingConsumable(Consumable):
    def __init__(self, amount: int, entity: entities.item.Item):
        super().__init__(entity)
        self.amount = amount

    def activate(self, action: entities.actions.actions.ItemAction) -> int:
        action_cost = 100
        consumer = action.creature
        amount_recovered = consumer.fighter_component.heal(self.amount)

        if amount_recovered > 0:
            log.info(f"You consume the {self.entity.name}, and recover {amount_recovered} HP!")
            self.entity.destroy(consumer)
            return action_cost
