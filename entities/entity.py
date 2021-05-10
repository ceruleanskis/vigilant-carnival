import typing
from abc import abstractmethod
from typing import Union

import pygame


class Entity(pygame.sprite.Sprite):
    def __init__(self, key: str = "None"):
        super().__init__()
        self.key = key
        self.name = key
        self.blocks = True
        self.visible = False

    def update(self):
        super().update()

    @abstractmethod
    def render(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        pass

    @abstractmethod
    def to_json(self) -> typing.Dict:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def from_json(json_obj: typing.Dict) -> 'Entity':
        raise NotImplementedError


class EntityGroup(pygame.sprite.Group):
    def __init__(self, *entities: typing.Union[Entity, typing.Sequence[Entity]]):
        super().__init__(*entities)
