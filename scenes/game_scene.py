import random
from typing import Union

import pygame
import jsonpickle

import components.map
import scenes.title_scene as title_scene
import utilities.fov
import utilities.seed
import utilities.constants
import utilities.load_data
import json
from components.scene import Scene
from entities.player import Player

random.seed(utilities.seed.seed_int)


class GameScene(Scene):
    def __init__(self):
        Scene.__init__(self)
        self.all_sprites = pygame.sprite.Group()
        self.map_sprites = pygame.sprite.Group()

        self.tile_map = components.map.TileMap(((utilities.constants.DISPLAY_WIDTH - utilities.constants.TILE_SIZE) // utilities.constants.TILE_SIZE) + 1,
                                               (utilities.constants.DISPLAY_HEIGHT - utilities.constants.TILE_SIZE) // utilities.constants.TILE_SIZE)

        for y in range(self.tile_map.height):
            for x in range(self.tile_map.width):
                self.map_sprites.add(self.tile_map.tile_map[x][y])
                self.all_sprites.add(self.tile_map.tile_map[x][y])

        self.player = Player()
        self.all_sprites.add(self.player)
        player_pos = self.tile_map.random_coord_in_room(self.tile_map.starting_room)

        self.player.x_pos = player_pos.x
        self.player.y_pos = player_pos.y
        self.player.teleport(self.player.x_pos, self.player.y_pos)

    def handle_input(self, events, pressed_keys):
        for event in events:
            self.player.handle_input(events, pressed_keys)
            self.did_move_to_blocked()
            self.update_fov()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.switch_scene(title_scene.TitleScene())

    def did_move_to_blocked(self):
        collision_list = pygame.sprite.spritecollide(self.player, self.map_sprites, False)
        for tile in collision_list:
            if tile.type != 'floor' and tile.type != 'open_door':
                # pass
                if tile.type == 'door':
                    tile.type = 'open_door'
                    tile.image_str = utilities.load_data.TILE_DATA[tile.type]['image']
                else:
                    self.player.teleport(self.player.previous_x_pos, self.player.previous_y_pos)

    def update_fov(self):
        utilities.fov.fieldOfView(self.player.x_pos,
                                  self.player.y_pos,
                                  self.tile_map.width,
                                  self.tile_map.height,
                                  10,
                                  self.tile_map.set_tile_visibility,
                                  self.tile_map.is_blocked_at_location)

    def update(self):
        # pygame.display.update()
        pass

    def render(self, screen):
        screen.fill((0, 0, 0))
        self.tile_map.render(screen)
        for entity in self.all_sprites:
            screen.blit(entity.surface, entity.rect)
            if utilities.constants.COORDINATE_DISPLAY and isinstance(entity, components.map.Tile):
                    screen.blit(entity.text, entity.rect)


class GameScene2(Scene):
    def __init__(self):
        Scene.__init__(self)

    def handle_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.switch_scene(title_scene.TitleScene())

    def update(self):
        pass

    def render(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        # The game scene is just a blank blue screen
        screen.fill((255, 0, 255))
