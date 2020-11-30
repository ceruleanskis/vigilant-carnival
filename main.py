import pygame

import utilities.constants
import utilities.game_utils
import utilities.seed
from components.scene import Scene
from scenes.title_scene import TitleScene

print(utilities.constants.ROOT_DIR)


def run_game(starting_scene: Scene = TitleScene()) -> None:
    """
    Initializes game window and sets starting scene.

    :param starting_scene: the scene to begin the game with
    :type starting_scene: TitleScene
    :return: None
    :rtype: None
    """
    pygame.init()

    screen = pygame.display.set_mode((utilities.constants.DISPLAY_WIDTH, utilities.constants.DISPLAY_HEIGHT))
    clock = pygame.time.Clock()
    pygame.font.init()
    font = pygame.font.SysFont(None, 48)

    active_scene: Scene = starting_scene

    # Main loop
    while active_scene is not None:
        pressed_keys = pygame.key.get_pressed()

        filtered_events = []
        for event in pygame.event.get():
            quit_attempt = False

            if event.type == pygame.QUIT:
                quit_attempt = True
            elif event.type == pygame.KEYDOWN:
                alt_pressed = pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]
                if event.key == pygame.K_ESCAPE:
                    quit_attempt = True
                elif event.key == pygame.K_F4 and alt_pressed:
                    quit_attempt = True

            if quit_attempt:
                active_scene.terminate()
            else:
                filtered_events.append(event)

        active_scene.handle_input(filtered_events, pressed_keys)
        # active_scene.update()
        active_scene.render(screen)
        show_fps(screen, clock, font)
        active_scene = active_scene.next
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
