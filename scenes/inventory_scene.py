import copy
import textwrap
import typing
from typing import Union

import pygame

import components.consumable
import components.equippable
import entities.item
import entities.player
import scenes.director
import scenes.menu_scene
import utilities.constants
import utilities.fonts
import utilities.game_utils
import utilities.helpers
import utilities.helpers
import utilities.load_data
import utilities.logsetup
from components.scene import Scene

log = utilities.logsetup.log()


class InventoryScene(Scene):
    """
    A game over screen.
    """

    def __init__(self, player: entities.player.Player, game_scene):
        Scene.__init__(self)
        self.game_scene = game_scene
        self.should_render_action_menu = False
        self.should_traverse_equipment_menu = False
        self.font = utilities.fonts.bold(20)
        self.image_files = {}
        self.player = player
        self.menu_items = copy.copy(self.player.inventory)
        self.selected_menu_item = 0
        self.action_menu_items = ["CANCEL", "CONSUME", "DROP"]
        self.selected_action_menu_item = 0
        self.equipment_menu_items = [utilities.helpers.EquipmentSlot.HEAD, utilities.helpers.EquipmentSlot.CHEST,
                                     utilities.helpers.EquipmentSlot.HANDS, utilities.helpers.EquipmentSlot.LEGS,
                                     utilities.helpers.EquipmentSlot.FEET,
                                     utilities.helpers.EquipmentSlot.WEAPON]
        self.selected_equipment_menu_item: typing.Union[0, utilities.helpers.EquipmentSlot] = 0
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
                elif self.should_traverse_equipment_menu:
                    self.traverse_equipment_menu(utilities.helpers.Direction.LEFT)
                else:
                    self.traverse_menu(utilities.helpers.Direction.LEFT)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                if self.should_render_action_menu:
                    self.traverse_action_menu(1)
                elif self.should_traverse_equipment_menu:
                    self.traverse_equipment_menu(utilities.helpers.Direction.RIGHT)
                else:
                    self.traverse_menu(utilities.helpers.Direction.RIGHT)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                if not self.should_render_action_menu:
                    if self.should_traverse_equipment_menu:
                        self.traverse_equipment_menu(utilities.helpers.Direction.DOWN)
                    else:
                        self.traverse_menu(utilities.helpers.Direction.DOWN)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                if not self.should_render_action_menu:
                    if self.should_traverse_equipment_menu:
                        self.traverse_equipment_menu(utilities.helpers.Direction.UP)
                    else:
                        self.traverse_menu(utilities.helpers.Direction.UP)

    def update(self):
        self.update_player()
        if len(self.player.inventory) == 0:
            self.should_render_action_menu = False

    def update_player(self):
        self.player = self.player.parent_scene.player
        self.menu_items = copy.copy(self.player.inventory)
        while len(self.menu_items) < self.inventory_size:
            self.menu_items.append(None)

    def take_action_menu_action(self):
        if self.selected_action_menu_item == 0:  # Cancel
            self.should_render_action_menu = False
        elif self.selected_action_menu_item == 1:  # Consume/Equip
            if self.action_menu_items[1] == "EQUIP":
                self.player.equip_item(self.player.inventory[self.selected_menu_item])
                # todo: fix. this seems hacky as a way to update the screen after equip
                self.should_render_action_menu = False
                self.game_scene.handle_input([], None)
                self.update()
            elif self.action_menu_items[1] == "CONSUME":
                self.player.consume_item(self.player.inventory[self.selected_menu_item])
                scenes.director.pop()
            else:
                raise ValueError(f"Unknown action {self.action_menu_items[1]}")
        elif self.selected_action_menu_item == 2:  # Drop
            self.player.drop_item(self.player.inventory[self.selected_menu_item])

    def traverse_action_menu(self, direction) -> None:
        """
        Cycles action menu up and down the menu in the direction specified.

        :param direction: the direction to go in the action menu list; up (-1) or down (1)
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

    def traverse_equipment_menu(self, direction: typing.Tuple[int, int]) -> None:
        if direction == utilities.helpers.Direction.LEFT:
            selected_equipment_menu_item = self.equipment_menu_items.index(self.selected_equipment_menu_item)
            self.selected_menu_item = ((selected_equipment_menu_item + 1) * (self.inventory_rows - 2)) - 1
            self.selected_equipment_menu_item = None
            self.should_traverse_equipment_menu = False
        elif direction == utilities.helpers.Direction.RIGHT:
            selected_equipment_menu_item = self.equipment_menu_items.index(self.selected_equipment_menu_item)
            self.selected_menu_item = ((selected_equipment_menu_item) * (self.inventory_rows - 2))
            self.selected_equipment_menu_item = None
            self.should_traverse_equipment_menu = False
        elif direction == utilities.helpers.Direction.UP:
            selected_equipment_menu_item = self.equipment_menu_items.index(self.selected_equipment_menu_item) - 1
            if selected_equipment_menu_item < 0:
                self.selected_equipment_menu_item = self.equipment_menu_items[len(self.equipment_menu_items) - 1]
            else:
                self.selected_equipment_menu_item = self.equipment_menu_items[selected_equipment_menu_item]
        elif direction == utilities.helpers.Direction.DOWN:
            selected_equipment_menu_item = self.equipment_menu_items.index(self.selected_equipment_menu_item) + 1
            if selected_equipment_menu_item >= len(self.equipment_menu_items):
                self.selected_equipment_menu_item = self.equipment_menu_items[0]
            else:
                self.selected_equipment_menu_item = self.equipment_menu_items[selected_equipment_menu_item]

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
                self.should_traverse_equipment_menu = True
                self.selected_equipment_menu_item = self.equipment_menu_items[
                    self.selected_menu_item // (self.inventory_cols - 2)]
            else:
                self.selected_menu_item -= 1
        elif direction == utilities.helpers.Direction.RIGHT:
            if self.selected_menu_item % (self.inventory_cols - 2) == (self.inventory_cols - 3):
                self.should_traverse_equipment_menu = True
                equipment_index = (self.selected_menu_item // (self.inventory_cols - 3)) - 1
                if equipment_index >= len(self.equipment_menu_items):
                    equipment_index = len(self.equipment_menu_items) - 1
                self.selected_equipment_menu_item = self.equipment_menu_items[equipment_index]
            else:
                self.selected_menu_item += 1
        elif direction == utilities.helpers.Direction.DOWN:
            if self.selected_menu_item + (self.inventory_rows - 2) >= self.inventory_size:
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
                rect = self.inventory_surface.blit(self.image_files['inventory_middle'],
                                                   (utilities.constants.TILE_SIZE * i,
                                                    utilities.constants.TILE_SIZE * j))

                # Render inventory item image
                if len(self.player.inventory) >= item_counter + 1 and self.menu_items[item_counter] is not None:
                    self.inventory_surface.blit(self.shrink(self.menu_items[item_counter]),
                                                ((utilities.constants.TILE_SIZE * i) + 12,
                                                 (utilities.constants.TILE_SIZE * j) + 12))
                    self.update_action_menu_items()
                else:
                    # Render outlines around inventory spaces
                    self.inventory_surface.blit(self.image_files['inventory_middle_outline'],
                                                (utilities.constants.TILE_SIZE * i,
                                                 utilities.constants.TILE_SIZE * j))

                # Render border around inventory image if it is selected currently
                if self.selected_menu_item == item_counter and not self.should_traverse_equipment_menu:
                    rect = rect.inflate(-12, -12)
                    pygame.draw.rect(self.inventory_surface, utilities.constants.RED, rect, 5)

                item_counter += 1

        screen.blit(self.inventory_surface,
                    (self.inventory_surface_display_rect[0],
                     self.inventory_surface_display_rect[1] - (utilities.constants.TILE_SIZE * 2),
                     self.inventory_surface_display_rect[0],
                     self.inventory_surface_display_rect[1]))

    @staticmethod
    def shrink(item: entities.item.Item):
        image = utilities.game_utils.GameUtils.load_sprite(utilities.load_data.ITEM_DATA[item.key]['image'],
                                                           item.tileset_alpha, convert_alpha=True,
                                                           tile_size=utilities.constants.TILE_SIZE - (12 * 2))
        return image

    def render(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        self.inventory_surface = pygame.surface.Surface(
            (utilities.constants.TILE_SIZE * self.inventory_cols, utilities.constants.TILE_SIZE * self.inventory_rows))
        self.inventory_surface_display_rect = utilities.game_utils.GameUtils.get_text_center(screen,
                                                                                             self.inventory_surface)
        self.load_inventory_images(screen)
        scenes.director.prev().render(screen)
        if self.should_traverse_equipment_menu:
            self.render_item_description_box(screen, equipped=True)
        else:
            self.render_item_description_box(screen)
        self.render_equipment_box(screen)
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

    def render_equipment_item(self, text_surf, equipment_menu_item: utilities.helpers.EquipmentSlot):
        tile_y = utilities.constants.TILE_SIZE * (self.equipment_menu_items.index(equipment_menu_item) + 1)
        if equipment_menu_item == utilities.helpers.EquipmentSlot.WEAPON:
            tile_y += 30

        equipment_rect = text_surf.blit(self.image_files['inventory_middle_outline'],
                                        (utilities.constants.TILE_SIZE * 2, tile_y))

        if self.selected_equipment_menu_item == equipment_menu_item:
            outline_rect = pygame.Rect(equipment_rect.left, equipment_rect.top, utilities.constants.TILE_SIZE,
                                       utilities.constants.TILE_SIZE)
            outline_rect = outline_rect.inflate(-12, -12)
            pygame.draw.rect(text_surf, utilities.constants.RED, outline_rect, 5)

        if self.player.equipment[equipment_menu_item] is not None:
            image = self.player.equipment[equipment_menu_item]
            text_surf.blit(self.shrink(image),
                           (equipment_rect[0] + 12, equipment_rect[1] + 12))

    def render_hands_feet(self, text_surf, equipment_menu_item: utilities.helpers.EquipmentSlot):
        tile_y = utilities.constants.TILE_SIZE * (self.equipment_menu_items.index(equipment_menu_item) + 1)
        list_items = [1, 3]

        for i in list_items:
            equipment_rect = text_surf.blit(self.image_files['inventory_middle_outline'],
                                            (utilities.constants.TILE_SIZE * i,
                                             tile_y))
            if self.player.equipment[equipment_menu_item] is not None:
                if i == list_items[0]:
                    image = self.player.equipment[equipment_menu_item]
                    text_surf.blit(self.shrink(image),
                                   (equipment_rect[0] + 12, equipment_rect[1] + 12))
                if i == list_items[1]:
                    image = self.player.equipment[equipment_menu_item]
                    image = pygame.transform.flip(self.shrink(image), True, False)
                    text_surf.blit(image,
                                   (equipment_rect[0] + 12, equipment_rect[1] + 12))

            if self.selected_equipment_menu_item == equipment_menu_item:
                outline_rect = pygame.Rect(equipment_rect.left, equipment_rect.top, utilities.constants.TILE_SIZE,
                                           utilities.constants.TILE_SIZE)
                outline_rect = outline_rect.inflate(-12, -12)
                pygame.draw.rect(text_surf, utilities.constants.RED, outline_rect, 5)

    def render_equipment_box(self, screen):
        item_description_box_cols = 5
        item_description_box_rows = self.inventory_rows

        text_surf = pygame.surface.Surface((item_description_box_cols * utilities.constants.TILE_SIZE,
                                            utilities.constants.TILE_SIZE * item_description_box_rows))
        text_surf_rect = utilities.game_utils.GameUtils.get_text_center(screen, text_surf)

        self.render_box(text_surf, 'description', item_description_box_cols, item_description_box_rows)

        # Render middle tiles in description box
        for j in range(1, item_description_box_rows - 1):
            for i in range(1, item_description_box_cols - 1):
                text_surf.blit(self.image_files['description_middle'],
                               (utilities.constants.TILE_SIZE * i, utilities.constants.TILE_SIZE * j))

        self.render_equipment_item(text_surf, utilities.helpers.EquipmentSlot.HEAD)
        self.render_equipment_item(text_surf, utilities.helpers.EquipmentSlot.CHEST)
        self.render_equipment_item(text_surf, utilities.helpers.EquipmentSlot.LEGS)
        self.render_equipment_item(text_surf, utilities.helpers.EquipmentSlot.WEAPON)
        self.render_hands_feet(text_surf, utilities.helpers.EquipmentSlot.HANDS)
        self.render_hands_feet(text_surf, utilities.helpers.EquipmentSlot.FEET)

        text = 'Armor'
        effect_font = self.font.render(text, True, utilities.constants.GREEN)
        text_surf.blit(effect_font,
                       (utilities.game_utils.GameUtils.get_text_center(text_surf, effect_font)[0], 30))

        text = 'Weapon'
        effect_font = self.font.render(text, True, utilities.constants.GREEN)
        text_surf.blit(effect_font,
                       (utilities.game_utils.GameUtils.get_text_center(text_surf, effect_font)[0], 385))

        screen.blit(text_surf, (
            self.inventory_surface_display_rect[0] - (utilities.constants.TILE_SIZE * (self.inventory_cols - 3)),
            self.inventory_surface_display_rect[1] - (utilities.constants.TILE_SIZE * 2),
            text_surf_rect[0],
            text_surf_rect[1]))

    def render_item_description_box(self, screen, equipped: bool = False):
        item_description_box_cols = 5
        item_description_box_rows = self.inventory_rows

        text_surf = pygame.surface.Surface((item_description_box_cols * utilities.constants.TILE_SIZE,
                                            utilities.constants.TILE_SIZE * item_description_box_rows))
        text_surf_rect = utilities.game_utils.GameUtils.get_text_center(screen, text_surf)

        check_to_render = len(self.player.inventory) > self.selected_menu_item
        if equipped:
            check_to_render = self.player.equipment[self.selected_equipment_menu_item] is not None

        if check_to_render:
            self.render_box(text_surf, 'description', item_description_box_cols, item_description_box_rows)

            # Render middle tiles in description box
            for j in range(1, item_description_box_rows - 1):
                for i in range(1, item_description_box_cols - 1):
                    text_surf.blit(self.image_files['description_middle'],
                                   (utilities.constants.TILE_SIZE * i, utilities.constants.TILE_SIZE * j))

            if not equipped:
                item = self.player.inventory[self.selected_menu_item]
            else:
                item = self.player.equipment[self.selected_equipment_menu_item]

            self.render_item_title_text(text_surf, item)
            self.render_item_description_image(text_surf, item)
            self.render_item_type_text(text_surf, item)
            self.render_item_effect_text(text_surf, item)
            self.render_item_description_text(text_surf, item)

            screen.blit(text_surf, (
                self.inventory_surface_display_rect[0] + (utilities.constants.TILE_SIZE * (self.inventory_cols)),
                self.inventory_surface_display_rect[1] - (utilities.constants.TILE_SIZE * 2),
                text_surf_rect[0],
                text_surf_rect[1]))

    def render_item_effect_text(self, text_surf, item: entities.item.Item):
        if item.consumable is not None and isinstance(
                item.consumable,
                components.consumable.HealingConsumable):
            component = item.consumable
            effect_text = f'Health +{component.amount}'
        elif item.equippable is not None and isinstance(
                item.equippable,
                components.equippable.Equippable):
            component = item.equippable
            effect_text = f'Strength +{component.strength_modifier}'
        else:
            return
        effect_font = self.font.render(effect_text, True, utilities.constants.GREEN)
        text_surf.blit(effect_font,
                       (utilities.game_utils.GameUtils.get_text_center(text_surf, effect_font)[0], 150))

    def render_item_type_text(self, text_surf, item: entities.item.Item):
        item_type_text = f'{item.type}'.title()
        item_type_font = self.font.render(item_type_text, True, utilities.constants.BLUE)
        text_surf.blit(item_type_font,
                       (utilities.game_utils.GameUtils.get_text_center(text_surf, item_type_font)[0], 125))

    def render_item_description_image(self, text_surf, item: entities.item.Item):
        image = item.image
        text_surf.blit(image,
                       (utilities.game_utils.GameUtils.get_text_center(text_surf, image)[0], 65))

    def render_item_title_text(self, text_surf, item: entities.item.Item):
        item_title_text = f'{item.name}'.title()
        item_title_font = self.font.render(item_title_text, True, utilities.constants.RED)
        text_surf.blit(item_title_font,
                       (utilities.game_utils.GameUtils.get_text_center(text_surf, item_title_font)[0], 25))

    def render_item_description_text(self, text_surf, item: entities.item.Item):
        item_description_text = f'{item.description}'
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

    def update_action_menu_items(self):
        if len(self.player.inventory) > self.selected_menu_item:
            if self.player.inventory[self.selected_menu_item].type == 'equippable':
                self.action_menu_items[1] = "EQUIP"
            elif self.player.inventory[self.selected_menu_item].type == 'consumable':
                self.action_menu_items[1] = "CONSUME"


def load_and_scale_image(filename: str, screen):
    image = pygame.image.load(filename).convert_alpha(screen)
    image = pygame.transform.scale(image, (utilities.constants.TILE_SIZE, utilities.constants.TILE_SIZE))
    return image
