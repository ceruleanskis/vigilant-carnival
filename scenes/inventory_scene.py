import copy
import textwrap
import typing
from typing import Union

import pygame

import components.consumable
import entities.player
import scenes.director
import scenes.menu_scene
import utilities.constants
import utilities.fonts
import utilities.game_utils
import utilities.helpers
import utilities.load_data
import utilities.logsetup
from components.scene import Scene

log = utilities.logsetup.log()


class InventoryScene(Scene):
    """
    A game over screen.
    """

    def __init__(self, player: entities.player.Player):
        Scene.__init__(self)
        self.should_render_action_menu = False
        self.font = utilities.fonts.bold(20)
        self.image_files = {}
        self.player = player
        self.menu_items = copy.copy(self.player.inventory)
        self.selected_menu_item = 0
        self.action_menu_items = ["CANCEL", "CONSUME", "DROP"]
        self.selected_action_menu_item = 0
        self.inventory_rows = 8
        self.inventory_cols = 8
        self.inventory_size = 36
        self.inventory_surface = None
        self.inventory_surface_display_rect = None

        while len(self.menu_items) < self.inventory_size:
            self.menu_items.append(None)

    def handle_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.should_render_action_menu:
                    self.should_render_action_menu = False
                    self.selected_action_menu_item = 0
                else:
                    scenes.director.pop()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if self.should_render_action_menu:
                    self.take_action_menu_action()
                elif len(self.player.inventory) > self.selected_menu_item:
                    self.should_render_action_menu = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                if self.should_render_action_menu:
                    self.traverse_action_menu(-1)
                else:
                    self.traverse_menu(utilities.helpers.Direction.LEFT)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                if self.should_render_action_menu:
                    self.traverse_action_menu(1)
                else:
                    self.traverse_menu(utilities.helpers.Direction.RIGHT)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                if not self.should_render_action_menu:
                    self.traverse_menu(utilities.helpers.Direction.DOWN)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                if not self.should_render_action_menu:
                    self.traverse_menu(utilities.helpers.Direction.UP)

    def update(self):
        pass

    def take_action_menu_action(self):
        if self.selected_action_menu_item == 0:  # Cancel
            self.should_render_action_menu = False
        elif self.selected_action_menu_item == 1:  # Consume
            self.player.consume_item(self.player.inventory[self.selected_menu_item])
            scenes.director.pop()
        elif self.selected_action_menu_item == 2:  # Drop
            raise NotImplementedError

    def traverse_action_menu(self, direction) -> None:
        """
        Cycles up and down the menu in the direction specified.

        :param direction: the direction to go in the menu list; up (-1) or down (1)
        :type direction: int
        :return: None
        :rtype: None
        """
        if direction == -1:
            if self.selected_action_menu_item == 0:
                self.selected_action_menu_item = len(self.action_menu_items) - 1
            else:
                self.selected_action_menu_item -= 1
        elif direction == 1:
            if self.selected_action_menu_item == len(self.action_menu_items) - 1:
                self.selected_action_menu_item = 0
            else:
                self.selected_action_menu_item += 1

    def traverse_menu(self, direction: typing.Tuple[int, int]) -> None:
        """
        Cycles up and down the menu in the direction specified.

        :param direction: the direction to go in the menu list; left (-1, 0) or right (1, 0)
        :type direction: int
        :return: None
        :rtype: None
        """
        if direction == utilities.helpers.Direction.LEFT:
            if self.selected_menu_item % (self.inventory_cols - 2) == 0:
                self.selected_menu_item = self.selected_menu_item + (self.inventory_cols - 3)
            else:
                self.selected_menu_item -= 1
        elif direction == utilities.helpers.Direction.RIGHT:
            if self.selected_menu_item % (self.inventory_cols - 2) == (self.inventory_cols - 3):
                self.selected_menu_item = self.selected_menu_item - (self.inventory_cols - 3)
                pass
            else:
                self.selected_menu_item += 1
        elif direction == utilities.helpers.Direction.DOWN:
            if self.selected_menu_item + self.inventory_rows - 2 >= len(self.menu_items):
                self.selected_menu_item = self.selected_menu_item % (self.inventory_rows - 2)
            else:
                self.selected_menu_item += (self.inventory_cols - 2)
        elif direction == utilities.helpers.Direction.UP:
            if self.selected_menu_item - (self.inventory_rows - 2) < 0:
                self.selected_menu_item = self.selected_menu_item + (
                        (self.inventory_cols - 2) * (self.inventory_cols - 3))
            else:
                self.selected_menu_item -= (self.inventory_cols - 2)

    def load_inventory_images(self, screen):
        for interface_data_item in utilities.load_data.INTERFACE_DATA:
            self.image_files[interface_data_item] = load_and_scale_image(
                utilities.load_data.INTERFACE_DATA[interface_data_item], screen)

    def render_inventory_menu(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        self.render_box(self.inventory_surface, 'inventory', self.inventory_cols, self.inventory_rows)

        item_counter = 0
        for j in range(1, self.inventory_rows - 1):
            for i in range(1, self.inventory_cols - 1):
                # Render inventory middle images (i.e non-corners)
                self.inventory_surface.blit(self.image_files['inventory_middle'],
                                            (utilities.constants.TILE_SIZE * i,
                                             utilities.constants.TILE_SIZE * j))

                # Render outlines around inventory spaces
                rect = self.inventory_surface.blit(self.image_files['inventory_middle_outline'],
                                                   (utilities.constants.TILE_SIZE * i,
                                                    utilities.constants.TILE_SIZE * j))

                # Render inventory item image
                if len(self.player.inventory) >= item_counter + 1 and self.menu_items[item_counter] is not None:
                    self.inventory_surface.blit(self.menu_items[item_counter].image,
                                                (utilities.constants.TILE_SIZE * i, utilities.constants.TILE_SIZE * j))

                # Render border around inventory image if it is selected currently
                if self.selected_menu_item == item_counter:
                    rect = rect.inflate(-12, -12)
                    pygame.draw.rect(self.inventory_surface, utilities.constants.RED, rect, 5)

                item_counter += 1

        screen.blit(self.inventory_surface,
                    (self.inventory_surface_display_rect[0] - (utilities.constants.TILE_SIZE * 2),
                     self.inventory_surface_display_rect[1] - (utilities.constants.TILE_SIZE * 2),
                     self.inventory_surface_display_rect[0],
                     self.inventory_surface_display_rect[1]))

    def render(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        self.inventory_surface = pygame.surface.Surface(
            (utilities.constants.TILE_SIZE * self.inventory_cols, utilities.constants.TILE_SIZE * self.inventory_rows))
        self.inventory_surface_display_rect = utilities.game_utils.GameUtils.get_text_center(screen,
                                                                                             self.inventory_surface)
        self.load_inventory_images(screen)
        self.render_item_description_box(screen)
        self.render_inventory_menu(screen)
        if self.should_render_action_menu:
            self.render_action_menu(screen)

    def render_box(self, surface, box_type, num_cols, num_rows):
        # Blit the corners
        surface.blit(self.image_files[f'{box_type}_top_left'], (0, 0))
        surface.blit(self.image_files[f'{box_type}_top_right'],
                     (utilities.constants.TILE_SIZE * (num_cols - 1), 0))
        surface.blit(self.image_files[f'{box_type}_bottom_left'],
                     (0, utilities.constants.TILE_SIZE * (num_rows - 1)))
        surface.blit(self.image_files[f'{box_type}_bottom_right'], (
            utilities.constants.TILE_SIZE * (num_cols - 1),
            utilities.constants.TILE_SIZE * (num_rows - 1)))

        for i in range(0, num_cols - 2):
            # Blit the top
            surface.blit(self.image_files[f'{box_type}_top'],
                         (utilities.constants.TILE_SIZE * (i + 1), 0))

            # Blit the bottom
            surface.blit(self.image_files[f'{box_type}_bottom'], (
                utilities.constants.TILE_SIZE * (i + 1), utilities.constants.TILE_SIZE * (num_rows - 1)))

        for j in range(0, num_rows - 2):
            # Blit the sides
            surface.blit(self.image_files[f'{box_type}_left'],
                         (0, utilities.constants.TILE_SIZE * (j + 1)))
            surface.blit(self.image_files[f'{box_type}_right'], (
                utilities.constants.TILE_SIZE * (num_cols - 1), utilities.constants.TILE_SIZE * (j + 1)))

    def render_item_description_box(self, screen):
        item_description_box_cols = 4
        item_description_box_rows = self.inventory_rows
        scenes.director.prev().render(screen)

        text_surf = pygame.surface.Surface((250, utilities.constants.TILE_SIZE * item_description_box_rows))
        text_surf_rect = utilities.game_utils.GameUtils.get_text_center(screen, text_surf)

        if len(self.player.inventory) > self.selected_menu_item:
            self.render_box(text_surf, 'description', item_description_box_cols, item_description_box_rows)

            # Render middle tiles in description box
            for j in range(1, item_description_box_rows - 1):
                for i in range(1, item_description_box_cols - 1):
                    text_surf.blit(self.image_files['description_middle'],
                                   (utilities.constants.TILE_SIZE * i, utilities.constants.TILE_SIZE * j))

            self.render_item_title_text(text_surf)
            self.render_item_description_image(text_surf)
            self.render_item_type_text(text_surf)
            self.render_item_effect_text(text_surf)
            self.render_item_description_text(text_surf)

            screen.blit(text_surf, (
                self.inventory_surface_display_rect[0] + (utilities.constants.TILE_SIZE * (self.inventory_cols - 2)),
                self.inventory_surface_display_rect[1] - (utilities.constants.TILE_SIZE * 2),
                text_surf_rect[0],
                text_surf_rect[1]))

    def render_item_effect_text(self, text_surf):
        if self.player.inventory[self.selected_menu_item].consumable and isinstance(
                self.player.inventory[self.selected_menu_item].consumable,
                components.consumable.HealingConsumable):
            consumable: components.consumable.HealingConsumable = self.player.inventory[
                self.selected_menu_item].consumable
            effect_text = f'Health +{consumable.amount}'
            effect_font = self.font.render(effect_text, True, utilities.constants.GREEN)
            text_surf.blit(effect_font,
                           (utilities.game_utils.GameUtils.get_text_center(text_surf, effect_font)[0], 150))

    def render_item_type_text(self, text_surf):
        item_type_text = f'{self.player.inventory[self.selected_menu_item].type}'.title()
        item_type_font = self.font.render(item_type_text, True, utilities.constants.BLUE)
        text_surf.blit(item_type_font,
                       (utilities.game_utils.GameUtils.get_text_center(text_surf, item_type_font)[0], 125))

    def render_item_description_image(self, text_surf):
        image = self.player.inventory[self.selected_menu_item].image
        text_surf.blit(image,
                       (utilities.game_utils.GameUtils.get_text_center(text_surf, image)[0], 65))

    def render_item_title_text(self, text_surf):
        item_title_text = f'{self.player.inventory[self.selected_menu_item].name}'.title()
        item_title_font = self.font.render(item_title_text, True, utilities.constants.RED)
        text_surf.blit(item_title_font,
                       (utilities.game_utils.GameUtils.get_text_center(text_surf, item_title_font)[0], 25))

    def render_item_description_text(self, text_surf):
        item_description_text = f'{self.player.inventory[self.selected_menu_item].description}'
        item_description_lines = textwrap.wrap(item_description_text, text_surf.get_width() // 15)
        k = 0
        for line in item_description_lines:
            item_description_font = self.font.render(line, True, utilities.constants.RED)
            text_surf.blit(item_description_font,
                           (utilities.game_utils.GameUtils.get_text_center(text_surf, item_description_font)[0],
                            200 + (k * 20)))
            k += 1

    def render_action_menu(self, screen):
        action_menu_rows = 1
        action_menu_surf = pygame.surface.Surface(
            (utilities.constants.TILE_SIZE * 12, utilities.constants.TILE_SIZE * action_menu_rows))
        action_menu_surf_rect = utilities.game_utils.GameUtils.get_text_center(screen, action_menu_surf)

        for i in range(0, 3):
            action_font = self.font.render(self.action_menu_items[i], True, utilities.constants.WHITE)

            surf = pygame.surface.Surface((utilities.constants.TILE_SIZE * 2, utilities.constants.TILE_SIZE))
            button_rect = action_menu_surf.blit(self.image_files['button_left'],
                                                (i * (utilities.constants.TILE_SIZE * 3), 0))
            action_menu_surf.blit(self.image_files['button_right'],
                                  (utilities.constants.TILE_SIZE + (utilities.constants.TILE_SIZE * 3 * i), 0))

            rect = utilities.game_utils.GameUtils.get_text_center(surf, action_font)
            action_menu_surf.blit(action_font, (rect[0] + utilities.constants.TILE_SIZE * 3 * i, rect[1] - 3))
            if self.selected_action_menu_item == i:
                rect = pygame.Rect(button_rect.left, button_rect.top, utilities.constants.TILE_SIZE * 2,
                                   utilities.constants.TILE_SIZE)
                rect = rect.inflate(-12, -12)
                pygame.draw.rect(action_menu_surf, utilities.constants.RED, rect, 5)

            screen.blit(action_menu_surf, (
                self.inventory_surface_display_rect[0] - (utilities.constants.TILE_SIZE * 2),
                self.inventory_surface_display_rect[1] + (utilities.constants.TILE_SIZE * (self.inventory_rows - 2)),
                action_menu_surf_rect[0],
                action_menu_surf_rect[1]))


def load_and_scale_image(filename: str, screen):
    image = pygame.image.load(filename).convert_alpha(screen)
    image = pygame.transform.scale(image, (utilities.constants.TILE_SIZE, utilities.constants.TILE_SIZE))
    return image
