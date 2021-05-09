import copy
import textwrap
import typing
from typing import Union

import pygame

import components.consumable
import components.equippable
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
        if len(self.player.inventory) == 0:
            self.should_render_action_menu = False

    def update_player(self):
        self.player = self.player.parent_scene.player
        self.menu_items = copy.copy(self.player.inventory)

    def take_action_menu_action(self):
        if self.selected_action_menu_item == 0:  # Cancel
            self.should_render_action_menu = False
        elif self.selected_action_menu_item == 1:  # Consume/Equip
            if self.action_menu_items[1] == "EQUIP":
                self.player.equip_item(self.player.inventory[self.selected_menu_item])
                # todo: fix. this seems hacky as a way to update the screen after equip
                self.should_render_action_menu = False
                self.game_scene.handle_input([], None)
            elif self.action_menu_items[1] == "CONSUME":
                self.player.consume_item(self.player.inventory[self.selected_menu_item])
                scenes.director.pop()
            else:
                raise ValueError(f"Unknown action {self.action_menu_items[1]}")
        elif self.selected_action_menu_item == 2:  # Drop
            self.player.drop_item(self.player.inventory[self.selected_menu_item])

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
                if self.selected_menu_item == item_counter:
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

        # Head
        head_rect = text_surf.blit(self.image_files['inventory_middle_outline'],
                       (utilities.constants.TILE_SIZE * 2,
                        utilities.constants.TILE_SIZE))

        if self.player.equipment[utilities.helpers.EquipmentSlot.HEAD] is not None:
            image = self.player.equipment[utilities.helpers.EquipmentSlot.HEAD]
            text_surf.blit(self.shrink(image),
                           (head_rect[0] + 12, head_rect[1] + 12))

        # Weapon
        weapon_slot_pos = (utilities.constants.TILE_SIZE * 2,
                           utilities.constants.TILE_SIZE * 5)
        w_rect = text_surf.blit(self.image_files['inventory_middle_outline'], weapon_slot_pos)

        if self.selected_equipment_menu_item == utilities.helpers.EquipmentSlot.WEAPON:
            weapon_outline_rect = pygame.Rect(w_rect.left, w_rect.top, utilities.constants.TILE_SIZE,
                                              utilities.constants.TILE_SIZE)
            weapon_outline_rect = weapon_outline_rect.inflate(-12, -12)
            pygame.draw.rect(text_surf, utilities.constants.RED, weapon_outline_rect, 5)

        if self.player.equipment[utilities.helpers.EquipmentSlot.WEAPON] is not None:
            text_surf.blit(self.shrink(self.player.equipment[utilities.helpers.EquipmentSlot.WEAPON]),
                           (weapon_slot_pos[0] + 12, weapon_slot_pos[1] + 12))

        # Hands + Chest
        for i in range(1, 4):
            hands_chest_rect = text_surf.blit(self.image_files['inventory_middle_outline'],
                                              (utilities.constants.TILE_SIZE * i,
                                               utilities.constants.TILE_SIZE * 2))
            if self.player.equipment[utilities.helpers.EquipmentSlot.HANDS] is not None:
                if i == 1:
                    image = self.player.equipment[utilities.helpers.EquipmentSlot.HANDS]
                    text_surf.blit(self.shrink(image),
                                   (hands_chest_rect[0] + 12, hands_chest_rect[1] + 12))
                if i == 3:
                    image = self.player.equipment[utilities.helpers.EquipmentSlot.HANDS]
                    image = pygame.transform.flip(self.shrink(image), True, False)
                    text_surf.blit(image,
                                   (hands_chest_rect[0] + 12, hands_chest_rect[1] + 12))

            if self.player.equipment[utilities.helpers.EquipmentSlot.CHEST] is not None:
                if i == 2:
                    image = self.player.equipment[utilities.helpers.EquipmentSlot.CHEST]
                    text_surf.blit(self.shrink(image),
                                   (hands_chest_rect[0] + 12, hands_chest_rect[1] + 12))

        # Feet
        for i in range(1, 3):
            feet_rect = text_surf.blit(self.image_files['inventory_middle_outline'],
                           (utilities.constants.TILE_SIZE * (i + 0.5),
                            utilities.constants.TILE_SIZE * 3))
            if self.player.equipment[utilities.helpers.EquipmentSlot.FEET] is not None:
                if i == 1:
                    image = self.player.equipment[utilities.helpers.EquipmentSlot.FEET]
                    text_surf.blit(self.shrink(image),
                                   (feet_rect[0] + 12, feet_rect[1] + 12))
                if i == 2:
                    image = self.player.equipment[utilities.helpers.EquipmentSlot.FEET]
                    image = pygame.transform.flip(self.shrink(image), True, False)
                    text_surf.blit(image,
                                   (feet_rect[0] + 12, feet_rect[1] + 12))

        text = 'Armor'
        effect_font = self.font.render(text, True, utilities.constants.GREEN)
        text_surf.blit(effect_font,
                       (utilities.game_utils.GameUtils.get_text_center(text_surf, effect_font)[0], 30))

        text = 'Weapon'
        effect_font = self.font.render(text, True, utilities.constants.GREEN)
        text_surf.blit(effect_font,
                       (utilities.game_utils.GameUtils.get_text_center(text_surf, effect_font)[0], 285))

        screen.blit(text_surf, (
            self.inventory_surface_display_rect[0] - (utilities.constants.TILE_SIZE * (self.inventory_cols - 3)),
            self.inventory_surface_display_rect[1] - (utilities.constants.TILE_SIZE * 2),
            text_surf_rect[0],
            text_surf_rect[1]))

    def render_item_description_box(self, screen):
        item_description_box_cols = 5
        item_description_box_rows = self.inventory_rows

        text_surf = pygame.surface.Surface((item_description_box_cols * utilities.constants.TILE_SIZE,
                                            utilities.constants.TILE_SIZE * item_description_box_rows))
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
                self.inventory_surface_display_rect[0] + (utilities.constants.TILE_SIZE * (self.inventory_cols)),
                self.inventory_surface_display_rect[1] - (utilities.constants.TILE_SIZE * 2),
                text_surf_rect[0],
                text_surf_rect[1]))

    def render_item_effect_text(self, text_surf):
        if self.player.inventory[self.selected_menu_item].consumable is not None and isinstance(
                self.player.inventory[self.selected_menu_item].consumable,
                components.consumable.HealingConsumable):
            component = self.player.inventory[
                self.selected_menu_item].consumable
            effect_text = f'Health +{component.amount}'
        elif self.player.inventory[self.selected_menu_item].equippable is not None and isinstance(
                self.player.inventory[self.selected_menu_item].equippable,
                components.equippable.Equippable):
            component = self.player.inventory[
                self.selected_menu_item].equippable
            effect_text = f'Strength +{component.strength_modifier}'
        else:
            return
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
