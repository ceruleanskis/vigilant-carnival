import typing
from abc import abstractmethod
from typing import Union

import pygame


class Entity(pygame.sprite.Sprite):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.blocks = True

    def update(self):
        super().update()

    @abstractmethod
    def render(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        pass


class EntityGroup(pygame.sprite.Group):
    def __init__(self, *entities: typing.Union[Entity, typing.Sequence[Entity]]):
        super().__init__(*entities)
