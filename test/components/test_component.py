import unittest
import unittest.mock

import pygame

import components.component
import entities.actions.actions
import entities.creature


class TestFighterComponent(unittest.TestCase):

    def setUp(self) -> None:
        pygame.init()

        screen = pygame.display.set_mode((0, 0))
        self.fighter_entity = entities.creature.Creature('floating_eye', ID=0)
        self.fighter_entity_2 = entities.creature.Creature('floating_eye', ID=1)
        self.fighter_entity.current_action = entities.actions.actions.MeleeAction(self.fighter_entity,
                                                                                  self.fighter_entity_2)
        self.fighter_entity.fighter_component = components.component.FighterComponent(self.fighter_entity, hp=100,
                                                                                      strength=50)
        self.fighter_entity_2.fighter_component = components.component.FighterComponent(self.fighter_entity_2, hp=100,
                                                                                        strength=50)

    def test_hp(self):
        self.fighter_entity.fighter_component.hp += 50
        self.assertEqual(self.fighter_entity.fighter_component.hp, 100)

        self.fighter_entity.fighter_component.hp -= 50
        self.assertEqual(self.fighter_entity.fighter_component.hp, 50)

        self.fighter_entity.fighter_component.hp -= 300
        self.assertEqual(self.fighter_entity.fighter_component, None)

    def test_attack(self):
        self.fighter_entity.current_action.perform()
        self.assertEqual(self.fighter_entity_2.fighter_component.hp, 50)

        self.fighter_entity.current_action.perform()
        self.assertEqual(self.fighter_entity_2.fighter_component, None)


if __name__ == '__main__':
    unittest.main()
