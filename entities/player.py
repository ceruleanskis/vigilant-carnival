from typing import Tuple

import pygame

import entities.creature


class Player(entities.creature.Creature):

    def __init__(self):
        super().__init__(name='player')

    def handle_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                self.move((0, -1))
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                self.move((0, 1))
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                self.move((-1, 0))
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                self.move((1, 0))
            elif event.type == pygame.JOYHATMOTION:
                if event.value == (0, 1):  # up d-pad
                    self.move((0, -1))
                elif event.value == (0, -1):  # down d-pad
                    self.move((0, 1))
                elif event.value == (-1, 0):  # left d-pad
                    self.move((-1, 0))
                elif event.value == (1, 0):  # right d-pad
                    self.move((1, 0))
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

    def take_turn(self):
        pass
