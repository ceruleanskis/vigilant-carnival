import scenes.game_scene as game_scene
import utilities.constants
from components.scene import Scene
from utilities.game_utils import *

pygame.joystick.init()
try:
    # Setup and init joystick
    j = pygame.joystick.Joystick(0)
    j.init()

    # Check init status
    if j.get_init() == 1:
        print("Joystick is initialized")
except pygame.error as err:
    print(err)
    print("Joystick is NOT initialized")


class TitleScene(Scene):
    """
    Introductory game scene, displaying menu options.
    """

    def __init__(self):
        Scene.__init__(self)
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 48)
        self.menu_items = [0, 1, 2]
        self.selected_menu_item = self.menu_items[0]

    def traverse_menu(self, direction) -> None:
        """
        Cycles up and down the menu in the direction specified.

        :param direction: the direction to go in the menu list; up (-1) or down (1)
        :type direction: int
        :return: None
        :rtype: None
        """
        if direction == -1:
            if self.selected_menu_item == 0:
                self.selected_menu_item = len(self.menu_items) - 1
            else:
                self.selected_menu_item -= 1
        elif direction == 1:
            if self.selected_menu_item == len(self.menu_items) - 1:
                self.selected_menu_item = 0
            else:
                self.selected_menu_item += 1

    def handle_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.take_menu_action()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                self.traverse_menu(-1)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                self.traverse_menu(1)
            elif event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                self.take_menu_action()
            elif event.type == pygame.JOYHATMOTION:
                if event.value == (0, 1):
                    self.traverse_menu(-1)
                elif event.value == (0, -1):
                    self.traverse_menu(1)

    def take_menu_action(self):
        if self.selected_menu_item == 0:
            self.switch_scene(game_scene.GameScene())
        elif self.selected_menu_item == 1:
            self.switch_scene(game_scene.GameScene2())
        elif self.selected_menu_item == 2:
            self.terminate()

    def update(self):
        pass

    def get_selected_text(self,
                          start_text: Union[pygame.Surface, pygame.SurfaceType],
                          load_text: Union[pygame.Surface, pygame.SurfaceType],
                          exit_text: Union[pygame.Surface, pygame.SurfaceType]):
        if self.selected_menu_item == 0:
            selected_text = start_text
        elif self.selected_menu_item == 1:
            selected_text = load_text
        elif self.selected_menu_item == 2:
            selected_text = exit_text
        else:
            raise Exception("menu item out of bounds")

        return selected_text

    def render(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        screen.fill(utilities.constants.BLACK)

        start_text = self.font.render('Start', True, utilities.constants.GREEN)
        load_text = self.font.render('Load', True, utilities.constants.GREEN)
        exit_text = self.font.render('Exit', True, utilities.constants.GREEN)

        selected_text = self.get_selected_text(start_text, load_text, exit_text)

        rect = selected_text.get_rect()

        pygame.draw.rect(selected_text, utilities.constants.BLUE, rect, 1)

        screen.blit(start_text, (
            GameUtils.get_text_center_width(screen, start_text),
            GameUtils.get_text_center_height(screen, start_text)))
        screen.blit(load_text, (
            GameUtils.get_text_center_width(screen, load_text),
            GameUtils.get_text_center_height(screen, load_text) + 60))
        screen.blit(exit_text, (
            GameUtils.get_text_center_width(screen, exit_text),
            GameUtils.get_text_center_height(screen, exit_text) + 120))

        pygame.display.update()
