import entities.creature
import entities.entity
import utilities.logsetup

log = utilities.logsetup.log()


class BaseComponent:
    def __init__(self, entity: entities.entity.Entity):
        self.entity = entity


class ItemComponent(BaseComponent, object):
    import entities.item

    def __init__(self, entity: entities.item.Item):
        super().__init__(entity)


class FighterComponent(BaseComponent, object):
    def __init__(self, entity: entities.creature.Creature, hp: int, strength: int):
        super().__init__(entity)
        self.entity = entity
        self.alive = True
        self.max_hp = hp
        self.hp = hp
        self.strength = strength

    @property
    def strength(self) -> int:
        strength_modifier: int = sum(
            [self.entity.equipment[item].equippable.strength_modifier for item in self.entity.equipment if
             self.entity.equipment[item] is not None])
        return self._strength + strength_modifier

    @strength.setter
    def strength(self, value: int) -> None:
        self._strength = value

    @property
    def max_hp(self) -> int:
        hp_modifier: int = sum([self.entity.equipment[item].equippable.hp_modifier for item in self.entity.equipment if
                                self.entity.equipment[item] is not None])
        return self._max_hp + hp_modifier

    @max_hp.setter
    def max_hp(self, value: int) -> None:
        self._max_hp = value

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))

        if self._hp <= 0:
            self.die()

    def die(self):
        log.info(f"{self.entity.name.title()}-{self.entity.ID} died.")
        self.alive = False
        self.entity.die()

    def take_damage(self, damage: int):
        self.hp -= damage
        self.entity.health_modified = True
        self.entity.health_modified_amount = -damage

    def heal(self, amount: int) -> int:
        if self.hp == self.max_hp:
            return 0

        new_hp_value = self.hp + amount
        if new_hp_value > self.max_hp:
            new_hp_value = self.max_hp

        amount_recovered = new_hp_value - self.hp
        self.hp = new_hp_value
        self.entity.health_modified = True
        self.entity.health_modified_amount = amount_recovered
        return amount_recovered
