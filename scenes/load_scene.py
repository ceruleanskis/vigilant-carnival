import typing
from typing import Union

import pygame

import scenes.director
import scenes.game_scene
import utilities.constants
import utilities.fonts
import utilities.game_utils as game_utils
import utilities.logsetup
import utilities.save_manager
from components.scene import Scene

log = utilities.logsetup.log()


class LoadScene(Scene):
    """
    Displays list of saved games and loads them.
    """

    def __init__(self):
        Scene.__init__(self)
        self.font = utilities.fonts.default(28)
        self.menu_items = utilities.save_manager.SaveManager.get_save_list()
        self.selected_menu_item = 0
        self.no_saves_text = self.font.render('No saved games found.', True, utilities.constants.GREEN)
        self.saves_found = True
        self.displayed_screenshot: typing.Union[pygame.surface.Surface, None] = None
        self.screenshot_width = utilities.constants.DISPLAY_WIDTH // 2
        self.screenshot_height = utilities.constants.DISPLAY_HEIGHT // 2
        self.screenshot_x = utilities.constants.DISPLAY_WIDTH - self.screenshot_width
        self.seed_text_surface = None

    def handle_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if self.saves_found:
                    self.take_menu_action()
                else:
                    self.terminate()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.terminate()
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
        json_data = self.load()
        scenes.director.replace_with(scenes.game_scene.GameScene(json_data))

    def load(self):
        file = self.menu_items[self.selected_menu_item]
        log.info(f'Loaded game from {file}.')
        return utilities.save_manager.SaveManager.load_game(file['path'])

    def update(self):
        pass

    def load_screenshot(self, index: int):
        try:
            file_name = self.menu_items[index]['path']
            screenshot = f'{utilities.constants.SAVE_GAME_DIR}/{file_name.removesuffix(".json")}.png' \
                .removeprefix(f'{utilities.constants.SAVE_GAME_DIR}/')
            self.displayed_screenshot = pygame.image.load(screenshot).convert()
            self.displayed_screenshot = pygame.transform.scale(self.displayed_screenshot, (
                self.screenshot_width, self.screenshot_height))
        except Exception as err:
            log.error(err)
            self.displayed_screenshot = pygame.surface.Surface((self.screenshot_width, self.screenshot_height))
            self.displayed_screenshot.fill(utilities.constants.DARK_BLUE)

    def render(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        screen.fill(utilities.constants.DARK_BLUE)
        file_column_text = self.font.render('File', True, utilities.constants.GREEN)
        date_column_text = self.font.render('Date', True, utilities.constants.GREEN)
        screen.blit(file_column_text, (10, 3))
        screen.blit(date_column_text, (10 + (10 * 48), 3))
        if self.menu_items:
            for i in range(len(self.menu_items)):
                file_name = self.menu_items[i]['path'].removeprefix(f'{utilities.constants.SAVE_GAME_DIR}/')
                file_modified = self.menu_items[i]['modified']
                seed = self.menu_items[i]['seed']
                save_game_file_text = self.font.render(f'{file_name}', True, utilities.constants.GREEN)
                save_game_date_text = self.font.render(f'{file_modified}', True, utilities.constants.GREEN)
                seed_text = self.font.render(f'Seed: {seed}', True, utilities.constants.GREEN)
                if self.selected_menu_item == i:
                    rect = save_game_file_text.get_rect()
                    pygame.draw.rect(save_game_file_text, utilities.constants.BLUE, rect, 1)
                    self.load_screenshot(i)
                    screenshot_rect = pygame.rect.Rect(
                        [self.screenshot_x, 3 * 48, self.screenshot_width, self.screenshot_height])
                    screen.blit(self.displayed_screenshot, screenshot_rect)
                    self.seed_text_surface = pygame.surface.Surface((25 * 48, 48))
                    self.seed_text_surface.fill(utilities.constants.DARK_BLUE)
                    self.seed_text_surface.blit(seed_text, (0, 0))

                screen.blit(save_game_file_text, (10, (2 * 48) + (i * 48)))
                screen.blit(save_game_date_text, (10 + (10 * 48), (2 * 48) + (i * 48)))
                screen.blit(self.seed_text_surface, (self.screenshot_x, (2 * 48)))
        else:
            self.saves_found = False
            screen.blit(self.no_saves_text, (
                game_utils.GameUtils.get_text_center_width(screen, self.no_saves_text),
                game_utils.GameUtils.get_text_center_height(screen, self.no_saves_text)))

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
