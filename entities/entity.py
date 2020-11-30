from abc import abstractmethod
from typing import Union

import pygame


class Entity(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

    def handle_input(self, events, pressed_keys):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        pass
