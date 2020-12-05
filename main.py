import pygame

import scenes.director
import utilities.constants
import utilities.game_utils
import utilities.logsetup
import utilities.seed
from components.scene import Scene
from scenes.menu_scene import MenuScene

log = utilities.logsetup.log()


def run_game(starting_scene: Scene = MenuScene()) -> None:
    """
    Initializes game window and sets starting scene.

    :param starting_scene: the scene to begin the game with
    :type starting_scene: MenuScene
    :return: None
    :rtype: None
    """
    pygame.init()

    screen = pygame.display.set_mode((utilities.constants.DISPLAY_WIDTH, utilities.constants.DISPLAY_HEIGHT))
    clock = pygame.time.Clock()
    pygame.font.init()
    font = pygame.font.SysFont(None, 48)

    active_scene: Scene = starting_scene
    scenes.director.push(active_scene)

    # Main loop
    while True:
        active_scene = scenes.director.top()
        if not active_scene:
            break
        pressed_keys = pygame.key.get_pressed()

        filtered_events = []
        for event in pygame.event.get():
            quit_attempt = False

            if event.type == pygame.QUIT:
                quit_attempt = True
            elif event.type == pygame.KEYDOWN:
                alt_pressed = pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]
                if event.key == pygame.K_F4 and alt_pressed:
                    quit_attempt = True

            if quit_attempt:
                return
            else:
                filtered_events.append(event)

        active_scene.handle_input(filtered_events, pressed_keys)
        active_scene.update()
        active_scene.render(screen)
        show_fps(screen, clock, font)
        pygame.display.flip()
        clock.tick(utilities.constants.FPS)


def show_fps(screen, clock, font):
    fps_display = utilities.game_utils.GameUtils.display_fps(clock, font)
    fps_rect = fps_display.get_rect()
    fps_rect.x = utilities.constants.DISPLAY_WIDTH - 125
    fps_rect.y = 0
    screen.blit(fps_display, fps_rect)


if __name__ == '__main__':
    run_game()
