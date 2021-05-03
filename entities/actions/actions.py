import operator
import random
import typing
from abc import ABC, abstractmethod

import components.map
import entities.creature
import utilities.logsetup
import utilities.map_helpers
import utilities.ship_generator

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


class TeleportAction(BaseAction):
    def __init__(self, creature: entities.creature.Creature, pos: utilities.ship_generator.Coordinate):
        super().__init__(creature)
        self.action_cost = 100
        self.pos = pos

    def perform(self) -> int:
        prev_x = self.creature.previous_x_pos
        prev_y = self.creature.previous_y_pos
        self.creature.teleport(self.pos.x, self.pos.y)
        blocking_entity = self.creature.moved_to_blocked()
        if blocking_entity is None or isinstance(blocking_entity, components.map.Tile):
            return self.action_cost
        elif isinstance(blocking_entity, entities.creature.Creature):
            if blocking_entity.fighter_component:
                self.creature.teleport(prev_x, prev_y)
                return MeleeAction(self.creature, melee_target=blocking_entity).perform()
            else:
                return self.action_cost
        else:
            raise AttributeError


class RandomMoveAction(MoveAction):
    def __init__(self, creature: entities.creature.Creature):
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1))
        direction = random.choice(directions)
        super().__init__(creature, direction)


class ChasePlayerAction(TeleportAction):
    def __init__(self, creature: entities.creature.Creature):
        if creature.parent_scene and creature.parent_scene.distance_map:
            distance_map = creature.parent_scene.distance_map

            neighbors = utilities.map_helpers.MapHelpers.get_neighbors(
                utilities.ship_generator.Coordinate(creature.x_pos, creature.y_pos),
                creature.parent_scene.tile_map.width,
                creature.parent_scene.tile_map.height)

            map_n = []
            for neighbor in neighbors:
                for tile in distance_map:
                    if tile.x == neighbor.x and tile.y == neighbor.y:
                        map_n.append(tile)

            smallest_distance_tile = min(map_n, key=operator.attrgetter('pathfind_distance'))
            super().__init__(creature,
                             utilities.ship_generator.Coordinate(smallest_distance_tile.x, smallest_distance_tile.y))
        else:
            directions = ((-1, 0), (1, 0), (0, -1), (0, 1))
            direction = random.choice(directions)
            super().__init__(creature, direction)


class MeleeAction(BaseAction):
    def __init__(self, creature: entities.creature.Creature, melee_target: entities.creature.Creature):
        super().__init__(creature)
        self.melee_target = melee_target
        self.action_cost = 100

    def perform(self) -> int:
        damage = self.creature.fighter_component.strength
        log.debug(
            f'The {self.creature.name}_{self.creature.ID} kicks the {self.melee_target.name}_{self.melee_target.ID} for {damage}.')
        self.melee_target.fighter_component.hp -= damage
        self.melee_target.damaged = True
        self.melee_target.damage_taken = damage
        return self.action_cost
