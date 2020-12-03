import random
import typing
from typing import Union, List, Dict

import pygame

import entities.entity
import utilities.constants
import utilities.dungeon_generator
import utilities.game_utils
import utilities.load_data
import utilities.seed
import utilities.ship_generator

random.seed(utilities.seed.seed_int)

pygame.font.init()
font = pygame.font.SysFont(None, 12)


class Tile(entities.entity.Entity):
    def __init__(self, x, y):
        super(Tile, self).__init__()
        self.x: int = x
        self.y: int = y
        self.surface = pygame.Surface((utilities.constants.TILE_SIZE, utilities.constants.TILE_SIZE))
        self.image_str: str = ""
        self.rect = self.surface.get_rect()
        self.type = utilities.constants.TILE_FLOOR
        self.visible = False
        self.text = font.render(f'{self.x},{self.y}', True, pygame.Color("yellow"))
        self.bitmask_value = 0
        self.blocks = False

    @staticmethod
    def from_json(json_obj: Dict, x=None, y=None) -> 'Tile':
        if x is None and y is None:
            x = json_obj['x']
            y = json_obj['y']
        tile = Tile(x, y)
        tile.type = json_obj['name']
        tile.blocks = json_obj['blocks']

        return tile

    def to_json(self):
        return {
            'x': self.x,
            'y': self.y,
            'name': self.type,
            'visible': self.visible,
            'blocks': self.blocks
        }

    def render(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        pass


class TileMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def generate_map(self):
        floor_tile = utilities.load_data.TILE_DATA['floor']
        self.tile_map: typing.List[typing.List[Tile]] = [[Tile.from_json(floor_tile, x, y)
                                                          for x in range(self.width)]
                                                         for y in range(self.height)]

        self.ship_generator: utilities.ship_generator.ShipGenerator = utilities.ship_generator.ShipGenerator(
            map_width=self.width,
            map_height=self.height,
            orientation=utilities.ship_generator.Orientation.vertical,
            bridge_width=3,
            min_room_size=4,
            max_room_size=9,
            num_rooms=50
        )
        self.ship_generator.get_ship()
        self.level_array = self.ship_generator.level_array
        self.tile_map = list(map(list, zip(*self.tile_map)))[::1]
        self.room_list = self.ship_generator.rooms
        self.set_tile_types()

        self.starting_room = random.choice(self.room_list)

        self.set_bitmask_value()
        if not utilities.constants.FOG_OF_WAR_ON:
            self.reveal_map()

        self.draw_map()

    @staticmethod
    def tile_list_to_json(tile_list: typing.List[typing.List[Tile]]) -> typing.List[typing.List[typing.Dict]]:
        json_list: typing.List[typing.List[typing.Dict]] = [[{} for y in range(len(tile_list[0]))] for x in
                                                            range(len(tile_list))]
        for y in range(len(tile_list[0])):
            for x in range(len(tile_list)):
                json_list[x][y] = tile_list[x][y].to_json()
        return json_list

    @staticmethod
    def tile_list_from_json(json_list: typing.List[typing.List[Dict]]) -> typing.List[typing.List[Tile]]:
        tile_list: typing.List[typing.List[Tile]] = [[Tile(x, y) for y in range(len(json_list[0]))] for x in
                                                     range(len(json_list))]
        for y in range(len(json_list[0])):
            for x in range(len(json_list)):
                tile_list[x][y] = Tile.from_json(json_list[x][y])
        return tile_list

    def to_json(self):
        return {
            'width': self.width,
            'height': self.height,
            'tile_map': TileMap.tile_list_to_json(self.tile_map),
            'room_list': [room.to_json() for room in self.room_list],
            'starting_room': self.starting_room.to_json()
        }

    @staticmethod
    def from_json(json_obj: typing.Dict) -> 'TileMap':
        width = json_obj['width']
        height = json_obj['height']
        tile_map = TileMap(width, height)
        tile_map.tile_map = TileMap.tile_list_from_json(json_obj['tile_map'])
        tile_map.room_list = [utilities.ship_generator.Rectangle.from_json(rect) for rect in json_obj['room_list']]
        tile_map.starting_room = utilities.ship_generator.Rectangle.from_json(json_obj['starting_room'])
        return tile_map

    def init_json_map(self):
        self.set_bitmask_value()
        if not utilities.constants.FOG_OF_WAR_ON:
            self.reveal_map()
        self.draw_map()

    def set_bitmask_value(self):
        for y in range(self.height):
            for x in range(self.width):
                current_tile: Tile = self.tile_map[x][y]
                if 'bitmask_values' in utilities.load_data.TILE_DATA[current_tile.type]:
                    self.calculate_bitmask_value(current_tile)
                    current_tile.image_str = \
                        utilities.load_data.TILE_DATA[current_tile.type]['bitmask_values'][
                            str(current_tile.bitmask_value)][
                            'image']
                else:
                    current_tile.image_str = utilities.load_data.TILE_DATA[current_tile.type]['image']

    def calculate_bitmask_value(self, tile: Tile):
        north = 2 ** 0
        east = 2 ** 2
        south = 2 ** 3
        west = 2 ** 1

        bitmask_value = 0

        if tile.y - 1 >= 0:
            north_tile: Tile = self.tile_map[tile.x][tile.y - 1]
            if north_tile.type == tile.type:
                bitmask_value += north

        if tile.x + 1 < self.width:
            east_tile: Tile = self.tile_map[tile.x + 1][tile.y]
            if east_tile.type == tile.type:
                bitmask_value += east

        if tile.y + 1 < self.height:
            south_tile: Tile = self.tile_map[tile.x][tile.y + 1]
            if south_tile.type == tile.type:
                bitmask_value += south

        if tile.x - 1 >= 0:
            west_tile: Tile = self.tile_map[tile.x - 1][tile.y]
            if west_tile.type == tile.type:
                bitmask_value += west

        tile.bitmask_value = bitmask_value

    @staticmethod
    def create_room_list(rooms: [List[int]]) -> List[utilities.ship_generator.Rectangle]:
        room_list = []
        for room in rooms:
            room_list.append(utilities.ship_generator.Rectangle(*room))
        return room_list

    def reveal_map(self):
        for y in range(self.height):
            for x in range(self.width):
                current_tile: Tile = self.tile_map[x][y]
                current_tile.visible = True

    def set_tile_types(self):
        for y in range(self.height):
            for x in range(self.width):
                current_tile: Tile = self.tile_map[x][y]
                current_tile.type = self.level_array[x][y]
                current_tile.blocks = utilities.load_data.TILE_DATA[current_tile.type]['blocks']

    def random_coord_in_room(self, room: utilities.ship_generator.Rectangle):
        coord: utilities.ship_generator.Coordinate = random.choice(room.get_room_coords(without_corners=True))
        tile: Tile = self.tile_map[coord.x][coord.y]
        if room.includes_point(coord) and tile.type != 'wall':
            return coord
        else:
            return self.random_coord_in_room(room)

    def draw_map(self):
        for y in range(self.height):
            for x in range(self.width):
                current_tile: Tile = self.tile_map[x][y]
                self.draw_tile(current_tile)

    def update(self):
        pass

    def set_tile_visibility(self, x: int, y: int, visibility: bool = True):
        tile: Tile = self.tile_map[x][y]

        tile.visible = visibility
        self.draw_tile(tile)

    def is_blocked_at_location(self, x: int, y: int) -> bool:
        tile: Tile = self.tile_map[x][y]
        return tile.blocks

    def set_room_visibility(self, room: utilities.ship_generator.Rectangle, visibility: bool, redraw: bool = False):
        for x in range(room.x, room.x + room.width):
            for y in range(room.y, room.y + room.height):
                current_tile: Tile = self.tile_map[x][y]
                current_tile.visible = visibility

        if redraw:
            self.draw_map()

    def render(self, screen: Union[pygame.Surface, pygame.SurfaceType]):
        pass

    @staticmethod
    def draw_tile(current_tile: Tile):
        if current_tile.visible:
            current_tile.surface = utilities.game_utils.GameUtils.load_sprite(
                current_tile.image_str)
        else:
            current_tile.surface.fill((0, 0, 0))

        current_tile.rect = current_tile.surface.get_rect()
        current_tile.rect.x = current_tile.x * utilities.constants.TILE_SIZE
        current_tile.rect.y = current_tile.y * utilities.constants.TILE_SIZE
        if utilities.constants.GRID_DISPLAY:
            pygame.draw.rect(
                current_tile.surface, utilities.constants.BLACK, current_tile.surface.get_rect(), 1)
