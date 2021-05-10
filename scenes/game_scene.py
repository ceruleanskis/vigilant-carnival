import random
import typing

import pygame

import components.camera
import components.consumable
import components.map
import entities.creature
import entities.item
import entities.player
import scenes.death_scene
import scenes.director
import scenes.inventory_scene
import scenes.menu_scene
import systems.time_manager
import utilities.constants
import utilities.fonts
import utilities.fov
import utilities.game_utils
import utilities.load_data
import utilities.logsetup
import utilities.map_helpers
import utilities.messages
import utilities.save_manager
import utilities.seed
import utilities.ship_generator
from components.scene import Scene

log = utilities.logsetup.log()
random.seed(utilities.seed.seed_int)


class GameScene(Scene):
    def __init__(self, loaded_json=None):
        Scene.__init__(self)
        self.block_input = True
        self.message_font = utilities.fonts.default(utilities.constants.MESSAGE_FONT_SIZE)
        self.pathfind_font = utilities.fonts.default(12)
        self.stats_display_font = utilities.fonts.default(32)
        self.all_sprites = pygame.sprite.Group()
        self.map_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()
        self.loaded_player_pos = None
        self.loaded_player_hp = None
        self.last_saved = None
        self.surface = pygame.surface.Surface((utilities.constants.DISPLAY_WIDTH, utilities.constants.DISPLAY_HEIGHT))
        self.creatures: typing.List[entities.creature.Creature] = []
        self.items: typing.List[entities.item.Item] = []
        self.time_manager = systems.time_manager.TimeManager()
        background_image = pygame.image.load(utilities.load_data.BACKGROUND_IMAGE_DATA['space']['image']).convert()
        self.background_image = pygame.transform.scale(background_image, (
            utilities.constants.DISPLAY_WIDTH, utilities.constants.DISPLAY_HEIGHT))
        self.background_surface = self.surface.copy()
        self.distance_map = []
        self.tile_map = None

        self.background_rendered = False
        font_pixel_width = self.message_font.render("m", True, utilities.constants.BLACK).get_width()
        utilities.messages.message_log = utilities.messages.MessageLog(
            (utilities.constants.MESSAGE_LOG_WIDTH // font_pixel_width) - font_pixel_width,
            utilities.constants.MAX_MESSAGES)

        self.player = entities.player.Player()

        if not loaded_json:
            self.set_up_new_game()
            self.set_player_pos(None)
        else:
            self.load(loaded_json)

        self.all_sprites.add(self.player)
        self.creatures.append(self.player)
        self.time_manager.register(self.player)

        for critter in self.creatures:
            if critter is not self.player:
                self.time_manager.register(critter)

        self.block_input = False

        self.update_parent()
        self.update_distance_map()

    def get_random_unoccupied_coord_in_room(self,
                                            room: utilities.ship_generator.Rectangle) -> utilities.ship_generator.Coordinate:
        random_pos = self.tile_map.random_coord_in_room(room)
        passes = 1

        while self.is_tile_occupied(random_pos):
            passes += 1
            if passes > 10:
                return None
            else:
                random_pos = self.tile_map.random_coord_in_room(room)
        return random_pos

    def is_tile_occupied(self, coord: utilities.ship_generator.Coordinate) -> bool:
        tile: components.map.Tile = self.tile_map.tile_map[coord.x][coord.y]
        if tile.type == 'door':
            return True

        if coord.x == self.player.x_pos and coord.y == self.player.y_pos:
            return True

        for enemy in self.enemy_sprites:
            if coord.x == enemy.x_pos and coord.y == enemy.y_pos:
                return True

        for item in self.item_sprites:
            if coord.x == item.x_pos and coord.y == item.y_pos:
                return True

        return False

    def set_up_new_game(self):
        width = 20
        height = 20
        self.tile_map = components.map.TileMap(width, height)
        self.tile_map.generate_map()
        self.add_map_tiles_to_sprite_list()
        random_pos = self.get_random_unoccupied_coord_in_room(random.choice(self.tile_map.room_list))
        if random_pos:
            item = entities.item.Item('rusty_knife', ID=2)
            self.place_item(item, random_pos)
            item = entities.item.Item('ceramic_boots', ID=2)
            self.place_item(item, random_pos)
            item = entities.item.Item('ceramic_gloves', ID=2)
            self.place_item(item, random_pos)
            item = entities.item.Item('ceramic_chest', ID=2)
            self.place_item(item, random_pos)
            item = entities.item.Item('ceramic_helmet', ID=2)
            self.place_item(item, random_pos)
            item = entities.item.Item('ceramic_leggings', ID=2)
            self.place_item(item, random_pos)
        else:
            log.warning("Item placement timed out.")
        for i in range(10):
            creature = entities.creature.Creature('floating_eye', ID=i + 3)
            self.all_sprites.add(creature)
            self.enemy_sprites.add(creature)
            random_pos = self.get_random_unoccupied_coord_in_room(random.choice(self.tile_map.room_list))
            if random_pos:
                creature.x_pos = random_pos.x
                creature.y_pos = random_pos.y
                self.creatures.append(creature)
            else:
                log.warning("Enemy placement timed out.")

    def place_item(self, item: entities.item.Item, pos: utilities.ship_generator.Coordinate):
        item.x_pos = pos.x
        item.y_pos = pos.y
        self.all_sprites.add(item)
        self.item_sprites.add(item)
        self.items.append(item)

    def add_map_tiles_to_sprite_list(self):
        for y in range(self.tile_map.height):
            for x in range(self.tile_map.width):
                self.map_sprites.add(self.tile_map.tile_map[x][y])
                self.all_sprites.add(self.tile_map.tile_map[x][y])

    def load(self, json_data):
        self.tile_map: components.map.TileMap = components.map.TileMap.from_json(json_data['map'])
        self.tile_map.init_json_map()
        self.player = entities.player.Player.from_json(json_data['player'], creature_type='Player')
        self.set_player_pos(utilities.ship_generator.Coordinate(self.player.x_pos, self.player.y_pos))
        self.add_map_tiles_to_sprite_list()

        if 'creatures' in json_data:
            for creature_data in json_data['creatures']:
                creature = entities.creature.Creature.from_json(creature_data)
                self.all_sprites.add(creature)
                self.enemy_sprites.add(creature)
                self.creatures.append(creature)

        if 'items' in json_data:
            for item_data in json_data['items']:
                item = entities.item.Item.from_json(item_data)
                self.all_sprites.add(item)
                self.item_sprites.add(item)
                self.items.append(item)

    def save(self):
        creatures_self_copy = self.creatures.copy()
        creatures_self_copy.remove(self.player)
        items_self_copy = self.items.copy()
        item_data = []
        creature_data = []
        for creature in creatures_self_copy:
            creature_data.append(creature.to_json())

        for item in items_self_copy:
            item_data.append(item.to_json())

        json_data = {
            'version': utilities.constants.VERSION,
            'seed': utilities.seed.seed.hex,
            'level': 1,
            'player': self.player.to_json(),
            'creatures': creature_data,
            'items': item_data,
            'map': self.tile_map.to_json()
        }

        self.last_saved = utilities.save_manager.SaveManager.save_game(json_data)

    def set_player_pos(self, player_pos: utilities.ship_generator.Coordinate = None):
        if player_pos is None:
            player_pos = self.get_random_unoccupied_coord_in_room(self.tile_map.starting_room)
            log.warning("Player placement timed out.")

        while player_pos is None:
            player_pos = self.get_random_unoccupied_coord_in_room(random.choice(self.tile_map.room_list))

        self.player.x_pos = player_pos.x
        self.player.y_pos = player_pos.y
        self.player.teleport(self.player.x_pos, self.player.y_pos)

    def update_parent(self):
        for creature in self.creatures:
            creature.parent_scene = self

        for item in self.items:
            item.parent_scene = self

    def update_distance_map(self):
        self.distance_map = utilities.map_helpers.MapHelpers.get_distance_map(
            self.tile_map,
            goal_pos=utilities.ship_generator.Coordinate(self.player.x_pos, self.player.y_pos))

    def handle_input(self, events, pressed_keys):
        if not self.block_input:
            self.player.handle_input(events, pressed_keys)
            if self.player.current_action is not None:
                self.update_parent()
                self.time_manager.tick()
                self.update_distance_map()

            self.update_fov()
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.switch_scene(scenes.menu_scene.MenuScene(title=False))
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                    self.look()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                    self.switch_scene(scenes.inventory_scene.InventoryScene(self.player, self))
                    return None

        if not self.player.alive:
            log.debug('DEAD')
            scenes.director.replace_with(scenes.death_scene.DeathScene())

    def update_fov(self):
        utilities.fov.fieldOfView(self.player.x_pos,
                                  self.player.y_pos,
                                  self.tile_map.width,
                                  self.tile_map.height,
                                  10,
                                  self.tile_map.set_tile_visibility,
                                  self.tile_map.is_blocked_at_location)

    def update(self):
        for creature in self.creatures:
            if not creature.fighter_component or not creature.fighter_component.alive:
                self.time_manager.release(creature)
                self.creatures.remove(creature)

    def render_message_log(self) -> pygame.surface.Surface:
        message_log_surface = pygame.surface.Surface((utilities.constants.MESSAGE_LOG_WIDTH,
                                                      utilities.constants.MESSAGE_LOG_HEIGHT))
        message_log_surface.fill(utilities.constants.DARK_BLUE)
        pygame.draw.rect(message_log_surface, utilities.constants.LIGHT_BLUE,
                         message_log_surface.get_rect().inflate(-10, -10), 3)

        for i in range(len(utilities.messages.message_log.messages)):
            message = utilities.messages.message_log.messages[i]
            message_display = self.message_font.render(message.text, True, message.color)
            message_display_rect = message_display.get_rect()
            message_log_surface.blit(message_display, (10, utilities.constants.FONT_SIZE * i + 10,
                                                       message_display_rect.width, message_display_rect.height
                                                       ))

        return message_log_surface

    def render_stats_display(self) -> pygame.surface.Surface:
        stats_display_surface = pygame.surface.Surface((utilities.constants.STATS_DISPLAY_WIDTH,
                                                        utilities.constants.MESSAGE_LOG_HEIGHT))
        stats_display_surface.fill(utilities.constants.DARK_BLUE)

        self.render_health_display(stats_display_surface)

        self.render_strength_display(stats_display_surface)

        pygame.draw.rect(stats_display_surface, utilities.constants.LIGHT_BLUE,
                         stats_display_surface.get_rect().inflate(-10, -10), 3)

        return stats_display_surface

    def render_strength_display(self, stats_display_surface, order: int = 1):
        strength_icon_path = utilities.load_data.INTERFACE_DATA["strength"]
        strength_icon = utilities.game_utils.GameUtils.load_sprite(strength_icon_path,
                                                                   colorkey=utilities.constants.BLACK,
                                                                   convert_alpha=True)
        stats_display_surface.blit(strength_icon,
                                   [10, 10 + ((utilities.constants.TILE_SIZE * order) + (order * 5)),
                                    strength_icon.get_width(),
                                    strength_icon.get_height()])
        strength_text = "STR:"
        strength_text_color = utilities.constants.YELLOW
        if self.player.fighter_component:
            strength_text = f'STR: {self.player.fighter_component.strength}'
        self.render_stat(order, stats_display_surface, strength_icon, strength_text, strength_text_color)

    def render_stat(self, order, stats_display_surface, icon, text, text_color):
        strength_display = self.stats_display_font.render(text, True, text_color)
        stats_display_surface.blit(strength_display,
                                   [icon.get_width() + 20,
                                    (icon.get_height() // 2) + (order * 5) + (
                                            utilities.constants.TILE_SIZE * order) - 15,
                                    strength_display.get_width(),
                                    strength_display.get_height()])

    def render_health_display(self, stats_display_surface, order: int = 0):
        health_icon_path = utilities.load_data.INTERFACE_DATA["health"]
        health_icon = utilities.game_utils.GameUtils.load_sprite(health_icon_path)
        stats_display_surface.blit(health_icon,
                                   [10, 10 + ((utilities.constants.TILE_SIZE * order) + (order * 5)),
                                    health_icon.get_width(),
                                    health_icon.get_height()])
        health_text = 'DEAD'
        health_text_color = utilities.constants.GREEN
        if self.player.fighter_component:
            health_text = f'{self.player.fighter_component.hp}/{self.player.fighter_component.max_hp}'
            if self.player.fighter_component.hp <= self.player.fighter_component.max_hp * 0.6:
                health_text_color = utilities.constants.YELLOW
            if self.player.fighter_component.hp <= self.player.fighter_component.max_hp * 0.4:
                health_text_color = utilities.constants.ORANGE
            if self.player.fighter_component.hp <= self.player.fighter_component.max_hp * 0.2:
                health_text_color = utilities.constants.LIGHT_RED
        self.render_stat(order, stats_display_surface, health_icon, health_text, health_text_color)

    def render_turn_display(self) -> pygame.surface.Surface:
        fps_display = self.stats_display_font.render(f'Turns: {self.time_manager.turns}', True, pygame.Color("blue"))
        fps_rect = fps_display.get_rect()
        fps_rect.x = utilities.constants.DISPLAY_WIDTH - 125
        fps_rect.y = 0

        return fps_display

    def render(self, screen):

        if not self.background_rendered:
            self.background_surface.blit(self.background_image, self.background_image.get_rect())
            self.background_rendered = True

        screen.blit(self.background_surface, (0, 0))

        self.surface.blit(self.background_image, self.background_image.get_rect())

        # self.all_sprites.clear(screen, self.surface)
        coord = components.camera.track_camera(self.player.x_pos, self.player.y_pos, self.tile_map.width,
                                               self.tile_map.height)

        for y in range(utilities.constants.MAP_DISPLAY_HEIGHT):
            for x in range(utilities.constants.MAP_DISPLAY_WIDTH):
                start_x = x + coord.x
                start_y = y + coord.y

                if start_x < 0:
                    start_x = 0

                if start_y < 0:
                    start_y = 0

                tile: components.map.Tile = self.tile_map.tile_map[start_x][start_y]
                tile_rect = ((x * utilities.constants.TILE_SIZE),
                             (y * utilities.constants.TILE_SIZE),
                             utilities.constants.TILE_SIZE, utilities.constants.TILE_SIZE)
                if tile.type != 'stone':
                    tile.render(screen)
                    self.surface.blit(tile.image, tile_rect)

                for enemy in self.enemy_sprites:
                    enemy.visible = self.tile_map.tile_map[start_x][start_y].visible
                    if enemy.visible and enemy.x_pos == start_x and enemy.y_pos == start_y:
                        enemy.render(screen)
                        self.surface.blit(enemy.image, tile_rect)

                for item in self.item_sprites:
                    item.visible = self.tile_map.tile_map[start_x][start_y].visible
                    if item.image is not None and item.visible and item.x_pos == start_x and item.y_pos == start_y:
                        item.render(screen)
                        self.surface.blit(item.image, tile_rect)

                if self.player.x_pos == start_x and self.player.y_pos == start_y:
                    self.player.render(screen)
                    self.surface.blit(self.player.image, tile_rect)

                if utilities.constants.PATHFINDING_DISPLAY:
                    self.display_pathfinding(tile, tile_rect)

        self.surface.blit(self.render_message_log(),
                          [0, utilities.constants.DISPLAY_HEIGHT - utilities.constants.MESSAGE_LOG_HEIGHT - 60,
                           utilities.constants.MESSAGE_LOG_WIDTH,
                           utilities.constants.MESSAGE_LOG_HEIGHT
                           ])

        self.surface.blit(self.render_stats_display(),
                          [utilities.constants.DISPLAY_WIDTH - utilities.constants.STATS_DISPLAY_WIDTH,
                           utilities.constants.DISPLAY_HEIGHT - utilities.constants.MESSAGE_LOG_HEIGHT - 60,
                           utilities.constants.STATS_DISPLAY_WIDTH,
                           utilities.constants.MESSAGE_LOG_HEIGHT
                           ])

        if utilities.constants.TURN_COUNT_DISPLAY:
            turn_display = self.render_turn_display()
            self.surface.blit(turn_display,
                              [0, 0,
                               utilities.constants.STATS_DISPLAY_WIDTH,
                               utilities.constants.MESSAGE_LOG_HEIGHT
                               ])

        screen.blit(self.surface, self.surface.get_rect())

    def display_pathfinding(self, tile, tile_rect: pygame.Rect):
        index_in_distance_map = utilities.map_helpers.MapHelpers.get_index(self.distance_map, tile)
        distance_map_tile = self.distance_map[index_in_distance_map]
        distance = str(distance_map_tile.pathfind_distance)
        distance_text = self.pathfind_font.render(distance, True, utilities.constants.RED)
        self.surface.blit(distance_text, [tile_rect[0] + utilities.constants.TILE_SIZE // 2,
                                          tile_rect[1],
                                          tile_rect[2],
                                          tile_rect[3]
                                          ])

    def look(self):
        looked_at_item = False
        for item in self.items:
            if self.player.x_pos == item.x_pos and self.player.y_pos == item.y_pos:
                log.info(item.name.capitalize())
                looked_at_item = True
        if not looked_at_item:
            tile = self.tile_map.tile_map[self.player.x_pos][self.player.y_pos]
            log.info(tile.name.capitalize())
