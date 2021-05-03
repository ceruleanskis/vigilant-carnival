from typing import Union

import pygame

import scenes.director
import scenes.menu_scene
import utilities.constants
import utilities.fonts
import utilities.game_utils
from components.scene import Scene


class DeathScene(Scene):
    """
    A game over screen.
    """

    def __init__(self):
        Scene.__init__(self)
        self.font = utilities.fonts.bold(80)

    def handle_input(self, events, pressed_keys):
        for event in events:
            if hasattr(event, 'type') and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                scenes.director.replace_with(scenes.menu_scene.MenuScene())
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                scenes.director.replace_with(scenes.menu_scene.MenuScene())
            else:
                pass

    def update(self):
        pass

    def render(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        screen.fill(utilities.constants.BLACK)
        died_text = self.font.render("YOU DIED", True, utilities.constants.RED)
        screen.blit(died_text, utilities.game_utils.GameUtils.get_text_center(screen, died_text))
