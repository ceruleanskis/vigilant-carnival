from typing import Tuple

import pygame

import entities.creature


class Player(entities.creature.Creature):

    def __init__(self):
        super().__init__(name='player')
        self.action_points = 0
        self.speed = 100

    def handle_input(self, events, pressed_keys)-> str:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                return self.move((0, -1))
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                return self.move((0, 1))
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                return self.move((-1, 0))
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                return self.move((1, 0))
            elif event.type == pygame.JOYHATMOTION:
                if event.value == (0, 1):  # up d-pad
                    return self.move((0, -1))
                elif event.value == (0, -1):  # down d-pad
                    return self.move((0, 1))
                elif event.value == (-1, 0):  # left d-pad
                    return self.move((-1, 0))
                elif event.value == (1, 0):  # right d-pad
                    return self.move((1, 0))
                else:
                    pass

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
        return 'move'

    def take_turn(self):
        return 100
