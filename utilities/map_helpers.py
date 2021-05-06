import copy
import operator
import typing

import components.map
import utilities.ship_generator


class MapHelpers:
    @staticmethod
    def is_in_map_bounds(coordinate: utilities.ship_generator.Coordinate, map_width: int, map_height: int) -> bool:
        return 0 <= coordinate.x < map_width and 0 <= coordinate.y < map_height

    @staticmethod
    def get_neighbors(current_pos: utilities.ship_generator.Coordinate, map_width: int, map_height: int) -> typing.List[
        utilities.ship_generator.Coordinate]:
        neighbors: typing.List[utilities.ship_generator.Coordinate] = []
        neighbor_candidates = [utilities.ship_generator.Coordinate(current_pos.x, current_pos.y - 1),
                               utilities.ship_generator.Coordinate(current_pos.x, current_pos.y + 1),
                               utilities.ship_generator.Coordinate(current_pos.x + 1, current_pos.y),
                               utilities.ship_generator.Coordinate(current_pos.x - 1, current_pos.y)]

        for candidate in neighbor_candidates:
            if MapHelpers.is_in_map_bounds(candidate, map_width, map_height):
                neighbors.append(candidate)

        return neighbors

    @staticmethod
    def get_index(tiles_list, tile):
        for index, item in enumerate(tiles_list):
            if tile.x == item.x and tile.y == item.y:
                return index

        return -1

    @staticmethod
    def get_distance_map(tilemap: components.map.TileMap, goal_pos: utilities.ship_generator.Coordinate):
        infinity = float('inf')
        checked_tiles = []
        unchecked_tiles = []
        for y in range(tilemap.height):
            for x in range(tilemap.height):
                tile: components.map.Tile = tilemap.tile_map[x][y]
                if x == goal_pos.x and y == goal_pos.y:
                    tile.pathfind_distance = 0
                    tile.discovered = False
                    unchecked_tiles.append(tile)
                else:
                    tile.pathfind_distance = infinity
                    tile.discovered = False
                    unchecked_tiles.append(tile)

        start_tile: components.map.Tile = copy.copy(tilemap.tile_map[goal_pos.x][goal_pos.y])
        checked_tiles = MapHelpers.bfs(tilemap, start_tile, checked_tiles, unchecked_tiles)

        root_tile_index_in_checked_tiles = MapHelpers.get_index(checked_tiles, tilemap.tile_map[goal_pos.x][goal_pos.y])
        checked_tiles[root_tile_index_in_checked_tiles].pathfind_distance = 0

        return checked_tiles

    @staticmethod
    def bfs(tilemap, root, checked_tiles, unchecked_tiles):
        infinity = float('inf')
        undiscovered_tiles = [tile for tile in unchecked_tiles if not tile.discovered]

        while len(undiscovered_tiles) > 0:
            smallest_distance_tile = min(undiscovered_tiles, key=operator.attrgetter('pathfind_distance'))
            smallest_distance_tile_index_in_unchecked_tiles = MapHelpers.get_index(undiscovered_tiles,
                                                                                   smallest_distance_tile)
            neighbors = MapHelpers.get_neighbors(
                utilities.ship_generator.Coordinate(smallest_distance_tile.x, smallest_distance_tile.y), tilemap.width,
                tilemap.height)
            for neighbor in neighbors:
                neighbor_tile: components.map.Tile = tilemap.tile_map[neighbor.x][neighbor.y]
                if neighbor_tile.type != 'wall':
                    newcalc = smallest_distance_tile.pathfind_distance + 1
                    if newcalc < neighbor_tile.pathfind_distance:
                        neighbor_tile.pathfind_distance = newcalc
                else:
                    neighbor_tile.pathfind_distance = infinity


            undiscovered_tiles[smallest_distance_tile_index_in_unchecked_tiles].discovered = True
            index_in_unchecked_tiles = MapHelpers.get_index(undiscovered_tiles, smallest_distance_tile)
            checked_tiles.append(undiscovered_tiles[index_in_unchecked_tiles])
            undiscovered_tiles = [tile for tile in undiscovered_tiles if not tile.discovered]

        return checked_tiles

    @staticmethod
    def recursive_bfs(tile, tilemap, unchecked_tiles, checked_tiles):
        if len(unchecked_tiles) == 0:
            return
        checked_tiles.append(tile)
        index_in_unchecked_tiles = MapHelpers.get_index(unchecked_tiles, tile)
        unchecked_tiles.pop(index_in_unchecked_tiles)

        neighbors = MapHelpers.get_neighbors(utilities.ship_generator.Coordinate(tile.x, tile.y), tilemap.width,
                                             tilemap.height)
        for neighbor in neighbors:
            neighbor_tile: components.map.Tile = copy.copy(tilemap.tile_map[neighbor.x][neighbor.y])
            index_in_unchecked_tiles = MapHelpers.get_index(unchecked_tiles, neighbor_tile)
            print("index_in_unchecked_tiles", index_in_unchecked_tiles)
            if index_in_unchecked_tiles == -1:
                pass
            if neighbor_tile.type == 'door':
                neighbor_tile.pathfind_distance = tile.pathfind_distance + 1
                checked_tiles.append(neighbor_tile)
                if len(unchecked_tiles) > 0:
                    unchecked_tiles.pop(index_in_unchecked_tiles)
                    MapHelpers.recursive_bfs(neighbor_tile, tilemap, unchecked_tiles, checked_tiles)
            elif neighbor_tile.blocks:
                checked_tiles.append(neighbor_tile)
                if len(unchecked_tiles) > 0:
                    unchecked_tiles.pop(index_in_unchecked_tiles)
                    MapHelpers.recursive_bfs(neighbor_tile, tilemap, unchecked_tiles, checked_tiles)
            else:
                neighbor_tile.pathfind_distance = tile.pathfind_distance + 1
                checked_tiles.append(neighbor_tile)
                if len(unchecked_tiles) > 0:
                    unchecked_tiles.pop(index_in_unchecked_tiles)
                    MapHelpers.recursive_bfs(neighbor_tile, tilemap, unchecked_tiles, checked_tiles)
