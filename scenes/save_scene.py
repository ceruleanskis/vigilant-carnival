from typing import Union

import pygame

import scenes.director
import utilities.constants
import utilities.fonts
import utilities.game_utils
from components.scene import Scene


class SaveScene(Scene):
    """
    Saves the game.
    """

    def __init__(self, last_saved: str):
        Scene.__init__(self)
        pygame.font.init()
        self.font = utilities.fonts.default(48)
        self.last_saved_text = self.font.render(f'Saved game to {last_saved}', True, utilities.constants.GREEN)

    def handle_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                scenes.director.pop()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                scenes.director.pop()
            else:
                pass

    def update(self):
        pass

    def render(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        screen.fill(utilities.constants.DARK_BLUE)
        screen.blit(self.last_saved_text, (
            utilities.game_utils.GameUtils.get_text_center_width(screen, self.last_saved_text),
            utilities.game_utils.GameUtils.get_text_center_height(screen, self.last_saved_text)))
