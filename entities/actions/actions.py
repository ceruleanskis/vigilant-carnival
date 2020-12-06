import random
import typing
from abc import ABC, abstractmethod

import components.map
import entities.creature
import utilities.logsetup

log = utilities.logsetup.log()


class BaseAction(ABC):
    def __init__(self, creature: entities.creature.Creature):
        self.creature = creature
        self.action_cost = 0

    @abstractmethod
    def perform(self) -> int:
        raise NotImplementedError

    def set_current_action(self):
        pass


class MoveAction(BaseAction):
    def __init__(self, creature: entities.creature.Creature, direction: typing.Tuple[int, int]):
        super().__init__(creature)
        self.action_cost = 100
        self.direction = direction

    def perform(self) -> int:
        self.creature.move(self.direction)
        blocking_entity = self.creature.moved_to_blocked()
        if blocking_entity is None or isinstance(blocking_entity, components.map.Tile):
            return self.action_cost
        elif isinstance(blocking_entity, entities.creature.Creature):
            return MeleeAction(self.creature, melee_target=blocking_entity).perform()
        else:
            raise AttributeError


class RandomMoveAction(MoveAction):
    def __init__(self, creature: entities.creature.Creature):
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1))
        direction = random.choice(directions)
        super().__init__(creature, direction)


class MeleeAction(BaseAction):
    def __init__(self, creature: entities.creature.Creature, melee_target: entities.creature.Creature):
        super().__init__(creature)
        self.melee_target = melee_target
        self.action_cost = 100

    def perform(self) -> int:
        log.debug(f'The {self.creature.name} kicks the {self.melee_target.name}.')
        return self.action_cost
