import random
import typing

import pygame

import components.camera
import components.map
import entities.creature
import entities.player
import scenes.death_scene
import scenes.director
import scenes.menu_scene
import systems.time_manager
import utilities.constants
import utilities.fonts
import utilities.fov
import utilities.game_utils
import utilities.load_data
import utilities.logsetup
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
        self.font = utilities.fonts.default(utilities.constants.MESSAGE_FONT_SIZE)
        self.all_sprites = pygame.sprite.Group()
        self.map_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.loaded_player_pos = None
        self.last_saved = None
        self.surface = pygame.surface.Surface((utilities.constants.DISPLAY_WIDTH, utilities.constants.DISPLAY_HEIGHT))
        self.creatures: typing.List[entities.creature.Creature] = []
        self.time_manager = systems.time_manager.TimeManager()
        background_image = pygame.image.load(utilities.load_data.BACKGROUND_IMAGE_DATA['space']['image']).convert()
        self.background_image = pygame.transform.scale(background_image, (
            utilities.constants.DISPLAY_WIDTH, utilities.constants.DISPLAY_HEIGHT))
        self.background_surface = self.surface.copy()

        self.background_rendered = False
        font_pixel_width = self.font.render("m", True, utilities.constants.BLACK).get_width()
        utilities.messages.message_log = utilities.messages.MessageLog(
            (utilities.constants.MESSAGE_LOG_WIDTH // font_pixel_width) - font_pixel_width,
            utilities.constants.MAX_MESSAGES)

        if not loaded_json:
            width = 50
            height = 50
            self.tile_map = components.map.TileMap(width, height)

            self.tile_map.generate_map()
            self.add_map_tiles_to_sprite_list()

            for i in range(20):
                creature = entities.creature.Creature('floating_eye')
                self.all_sprites.add(creature)
                self.enemy_sprites.add(creature)
                random_pos = self.tile_map.random_coord_in_room(random.choice(self.tile_map.room_list))
                creature.x_pos = random_pos.x
                creature.y_pos = random_pos.y
                self.creatures.append(creature)
        else:
            self.load(loaded_json)

        self.player = entities.player.Player()
        self.all_sprites.add(self.player)
        self.set_player_pos(self.loaded_player_pos)
        self.creatures.append(self.player)
        self.time_manager.register(self.player)

        for critter in self.creatures:
            if creature is not self.player:
                self.time_manager.register(critter)

        self.block_input = False

    def add_map_tiles_to_sprite_list(self):
        for y in range(self.tile_map.height):
            for x in range(self.tile_map.width):
                self.map_sprites.add(self.tile_map.tile_map[x][y])
                self.all_sprites.add(self.tile_map.tile_map[x][y])

    def load(self, json_data):
        self.tile_map: components.map.TileMap = components.map.TileMap.from_json(json_data['map'])
        self.tile_map.init_json_map()
        player_pos = json_data['player_pos']
        self.loaded_player_pos = utilities.ship_generator.Coordinate(player_pos[0], player_pos[1])

        self.add_map_tiles_to_sprite_list()

        if 'creatures' in json_data:
            for creature_data in json_data['creatures']:
                creature = entities.creature.Creature.from_json(creature_data)
                self.all_sprites.add(creature)
                self.creatures.append(creature)

    def save(self):
        creatures_self_copy = self.creatures.copy()
        creatures_self_copy.remove(self.player)
        creature_data = []
        for creature in creatures_self_copy:
            creature_data.append(creature.to_json())

        json_data = {
            'version': utilities.constants.VERSION,
            'seed': utilities.seed.seed.hex,
            'level': 1,
            'player_pos': [self.player.x_pos, self.player.y_pos],
            'creatures': creature_data,
            'map': self.tile_map.to_json()
        }

        self.last_saved = utilities.save_manager.SaveManager.save_game(json_data)

    def set_player_pos(self, player_pos: utilities.ship_generator.Coordinate = None):
        if player_pos is None:
            player_pos = self.tile_map.random_coord_in_room(self.tile_map.starting_room)

        self.player.x_pos = player_pos.x
        self.player.y_pos = player_pos.y
        self.player.teleport(self.player.x_pos, self.player.y_pos)

    def update_creature_parent(self):
        for creature in self.creatures:
            creature.parent_scene = self

    def handle_input(self, events, pressed_keys):
        if not self.block_input:
            for event in events:
                self.player.handle_input(events, pressed_keys)
                if self.player.current_action is not None:
                    self.update_creature_parent()
                    self.time_manager.tick()
                self.update_fov()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.switch_scene(scenes.menu_scene.MenuScene(title=False))

        if not self.player.alive:
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
        message_log_surface.fill((60, 51, 154))
        pygame.draw.rect(message_log_surface, (174, 228, 237), message_log_surface.get_rect().inflate(-10, -10), 3)

        for i in range(len(utilities.messages.message_log.messages)):
            message = utilities.messages.message_log.messages[i]
            message_display = self.font.render(message.text, True, message.color)
            message_display_rect = message_display.get_rect()
            message_log_surface.blit(message_display, (10, utilities.constants.FONT_SIZE * i + 10,
                                                       message_display_rect.width, message_display_rect.height
                                                       ))

        return message_log_surface

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

                if self.player.x_pos == start_x and self.player.y_pos == start_y:
                    self.player.render(screen)
                    self.surface.blit(self.player.image, tile_rect)

        self.surface.blit(self.render_message_log(),
                          [0, utilities.constants.DISPLAY_HEIGHT - utilities.constants.MESSAGE_LOG_HEIGHT - 60,
                           utilities.constants.MESSAGE_LOG_WIDTH,
                           utilities.constants.MESSAGE_LOG_HEIGHT
                           ])

        screen.blit(self.surface, self.surface.get_rect())
