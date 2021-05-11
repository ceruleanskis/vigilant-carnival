from abc import ABC, abstractmethod
from typing import Union

import pygame

import scenes


class Scene(ABC):
    def __init__(self):
        super().__init__()
        self.block_input = False

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
        scenes.director.push(next_scene)

    def terminate(self):
        scenes.director.pop()
