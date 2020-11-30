from abc import ABC, abstractmethod
from typing import Union

import pygame


class Scene(ABC):
    def __init__(self):
        self.next = self
        super().__init__()

    @abstractmethod
    def handle_input(self, events, pressed_keys):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        pass

    def switch_scene(self, next_scene):
        self.next = next_scene

    def terminate(self):
        self.switch_scene(None)
