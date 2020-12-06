import random
import typing

import pygame

import components.map
import scenes.menu_scene
import systems.time_manager
import utilities.constants
import utilities.fov
import utilities.load_data
import utilities.logsetup
import utilities.messages
import utilities.save_manager
import utilities.seed
import utilities.ship_generator
from components.scene import Scene
from entities.creature import Creature
from entities.player import Player

log = utilities.logsetup.log()
random.seed(utilities.seed.seed_int)
pygame.font.init()


class GameScene(Scene):
    def __init__(self, loaded_json=None):
        Scene.__init__(self)
        self.block_input = True
        self.font = pygame.font.SysFont(None, 48)
        self.all_sprites = pygame.sprite.Group()
        self.map_sprites = pygame.sprite.Group()
        self.loaded_player_pos = None
        self.last_saved = None
        self.surface = pygame.surface.Surface((utilities.constants.DISPLAY_WIDTH, utilities.constants.DISPLAY_HEIGHT))
        self.creatures: typing.List[Creature] = []

        if not loaded_json:
            width = ((utilities.constants.DISPLAY_WIDTH - utilities.constants.TILE_SIZE)
                     // utilities.constants.TILE_SIZE) + 1
            height = (utilities.constants.DISPLAY_HEIGHT - utilities.constants.TILE_SIZE) \
                     // utilities.constants.TILE_SIZE
            self.tile_map = components.map.TileMap(width, height)

            self.tile_map.generate_map()
            self.add_map_tiles_to_sprite_list()

            # creature = Creature('floating_eye')
            # self.all_sprites.add(creature)
            # random_pos = self.tile_map.random_coord_in_room(random.choice(self.tile_map.room_list))
            # creature.x_pos = random_pos.x
            # creature.y_pos = random_pos.y
            # self.creatures.extend([creature])
        else:
            self.load(loaded_json)

        self.player = Player()
        self.all_sprites.add(self.player)
        self.set_player_pos(self.loaded_player_pos)
        self.creatures.append(self.player)

        for critter in self.creatures:
            systems.time_manager.register(critter)

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
                creature = Creature.from_json(creature_data)
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
                    systems.time_manager.tick()
                self.update_fov()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.switch_scene(scenes.menu_scene.MenuScene(title=False))

    def update_fov(self):
        utilities.fov.fieldOfView(self.player.x_pos,
                                  self.player.y_pos,
                                  self.tile_map.width,
                                  self.tile_map.height,
                                  10,
                                  self.tile_map.set_tile_visibility,
                                  self.tile_map.is_blocked_at_location)

    def update(self):
        pass

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
        self.surface.fill((0, 0, 0))
        self.tile_map.render(screen)
        for entity in self.all_sprites:
            entity.render(screen)
            self.surface.blit(entity.surface, entity.rect)
            if utilities.constants.COORDINATE_DISPLAY and isinstance(entity, components.map.Tile):
                self.surface.blit(entity.text, entity.rect)

        self.surface.blit(self.render_message_log(),
                          [0, utilities.constants.DISPLAY_HEIGHT - utilities.constants.MESSAGE_LOG_HEIGHT - 60,
                           utilities.constants.MESSAGE_LOG_WIDTH,
                           utilities.constants.MESSAGE_LOG_HEIGHT
                           ])

        screen.blit(self.surface, self.surface.get_rect())
