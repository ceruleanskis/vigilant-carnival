import entities.creature
import entities.entity
import utilities.logsetup

log = utilities.logsetup.log()


class BaseComponent:
    def __init__(self, entity: entities.entity.Entity):
        self.entity = entity


class FighterComponent(BaseComponent, object):
    def __init__(self, entity: entities.creature.Creature, hp: int, strength: int):
        super().__init__(entity)
        self.entity = entity
        self.alive = True
        self.max_hp = hp
        self.hp = hp
        self.strength = strength

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))

        if self._hp <= 0:
            self.die()

    def die(self):
        log.info(f"{self.entity.name}_{self.entity.ID} died.")
        self.alive = False
        self.entity.die()
