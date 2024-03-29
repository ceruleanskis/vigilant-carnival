import typing
from typing import Union, IO, Tuple

import pygame

import utilities
import utilities.constants
import utilities.logsetup

log = utilities.logsetup.log()


class GameUtils:
    """
    A class holding common game methods for use across other modules.
    """

    @staticmethod
    def get_text_center_height(screen: Union[pygame.Surface, pygame.SurfaceType],
                               text: Union[pygame.Surface, pygame.SurfaceType]) -> int:
        return screen.get_height() // 2 - text.get_height() // 2

    @staticmethod
    def get_text_center_width(screen: Union[pygame.Surface, pygame.SurfaceType],
                              text: Union[pygame.Surface, pygame.SurfaceType]) -> int:
        return screen.get_width() // 2 - text.get_width() // 2

    @staticmethod
    def get_text_center(screen: Union[pygame.Surface, pygame.SurfaceType],
                        text: Union[pygame.Surface, pygame.SurfaceType]) -> typing.Tuple[int, int]:
        return GameUtils.get_text_center_width(screen, text), GameUtils.get_text_center_height(screen, text)

    @staticmethod
    def round_to_multiple(x: int, base: int) -> int:
        """
        Rounds x to a multiple of base.
        :param x: The int to round
        :type x: int
        :param base: The base to round to multiples of
        :type base: int
        :return:
        :rtype: int
        """
        return base * round(x / base)

    @staticmethod
    def display_fps(clock: pygame.time.Clock, font: pygame.font.Font):
        fps = str(int(clock.get_fps()))
        fps_text = font.render(f'FPS: {fps}', True, pygame.Color("coral"))
        return fps_text

    @staticmethod
    def load_sprite(path_from_root: Union[str, IO], colorkey: Tuple = None,
                    convert_alpha: bool = None, tile_size: int = utilities.constants.TILE_SIZE) -> pygame.Surface:
        full_path = f'{utilities.constants.ROOT_DIR}/{path_from_root}'
        try:
            image: pygame.Surface = pygame.image.load(full_path)
            if convert_alpha:
                image = image.convert_alpha()
            if colorkey:
                image.set_colorkey(colorkey)
            image = pygame.transform.scale(image, (tile_size, tile_size))
            return image
        except FileNotFoundError as err:
            log.error(f'ERROR: {full_path} does not exist.')
            raise err
        except Exception as err:
            raise err
