import typing
from typing import Tuple

import pygame

import entities.actions.actions
import entities.creature


class Player(entities.creature.Creature):

    def __init__(self):
        super().__init__('player')
        self.action_points = 0
        self.speed = 100
        self.current_action = None

    def handle_input(self, events, pressed_keys) -> typing.Union[entities.actions.actions.BaseAction, None]:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                self.current_action = entities.actions.actions.MoveAction(self, (0, -1))
                return self.current_action
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                self.current_action = entities.actions.actions.MoveAction(self, (0, 1))
                return self.current_action
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                self.current_action = entities.actions.actions.MoveAction(self, (-1, 0))
                return self.current_action
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
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

    def move(self, direction: Tuple[int, int]):
        super(Player, self).move(direction)
        # # Keep player on the screen
        #
        # if self.rect.left < 0:
        #     self.rect.left = 0
        #
        # if self.rect.right > SCREEN_WIDTH:
        #     self.rect.right = SCREEN_WIDTH
        #
        # if self.rect.top <= 0:
        #     self.rect.top = 0
        #
        # if self.rect.bottom >= SCREEN_HEIGHT:
        #     self.rect.bottom = SCREEN_HEIGHT

    def take_turn(self) -> int:
        cost = self.current_action.perform()
        self.current_action = None
        return cost
