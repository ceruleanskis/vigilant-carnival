import itertools
import random
import timeit
import typing
from typing import List

import utilities.load_data


class Coordinate:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

    def to_tuple(self) -> typing.Tuple[int, int]:
        return self.x, self.y

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Coordinate):
            return self.x == other.x and self.y == other.y
        return False

    def __str__(self):
        return f'Coordinate: ({self.x}, {self.y})'

    def __repr__(self):
        return f'Coordinate: ({self.x}, {self.y})'


class Orientation:
    vertical: str = 'vertical'
    horizontal: str = 'horizontal'


class Triangle:
    def __init__(self, a: Coordinate, b: Coordinate, c: Coordinate):
        self.a = a
        self.b = b
        self.c = c

    def get_area(self) -> float:
        area = 0.5 * (
                self.a.x * (self.b.y - self.c.y) +
                self.b.x * (self.c.y - self.a.y) +
                self.c.x * (self.a.y - self.b.y)
        )
        return abs(area)


class Rectangle:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.area = w * h
        self.room_repr: typing.List[int] = [x, y, w, h]
        self.corners = [self.top_right_corner(), self.bottom_left_corner(), self.top_left_corner(),
                        self.bottom_right_corner()]
        self.wall_coordinates: typing.List[Coordinate] = list(
            itertools.chain(self.top_wall(), self.bottom_wall(), self.left_wall(),
                            self.right_wall()))
        self.center = Coordinate(
            int(self.x + (0.5 * self.width)),
            int(self.y + (0.5 * self.height))
        )

    def get_room_coords(self, without_corners=False) -> typing.List[Coordinate]:
        room_coords: typing.List[Coordinate] = []

        for y1 in range(self.y, self.y + self.height):
            for x1 in range(self.x, self.x + self.width):
                if without_corners:
                    if Coordinate(x1, y1) not in self.corners:
                        room_coords.append(Coordinate(x1, y1))
                else:
                    room_coords.append(Coordinate(x1, y1))

        return room_coords

    def includes_point(self, coord: Coordinate, without_corners=False):
        """
        Let P(x,y), and rectangle A(x1,y1),B(x2,y2),C(x3,y3),D(x4,y4)
        x1, y1 = x, y of rect
        x2, y2 = x + width, y of rect
        x3, y3 = x + width, y + height of rect
        x4, y4 = x, y + height of rect

        Calculate the sum of areas of △APD,△DPC,△CPB,△PBA
        If this sum is greater than the area of the rectangle, then P(x,y) is outside the rectangle.
        Else if this sum is equal to the area of the rectangle (observe that this sum cannot be less than the latter),
        if area of any of the triangles is 0 then P(x,y) is on the rectangle
        (in fact on that line corresponding to the triangle of area=0).
        Observe that the equality of the sum is necessary; it is not sufficient that area=0),
        else P(x,y) is is inside the rectangle.
        :param coord: 
        :type coord: 
        :return: 
        :rtype: 
        """
        return coord in self.get_room_coords(without_corners)
        # triangle_APD = Triangle(Coordinate(self.x, self.y), coord, Coordinate(self.x, self.y + self.height))
        # triangle_APD_area = triangle_APD.get_area()
        #
        # triangle_DPC = Triangle(Coordinate(self.x, self.y + self.height), coord,
        #                         Coordinate(self.x + self.width, self.y + self.height))
        # triangle_DPC_area = triangle_DPC.get_area()
        #
        # triangle_CPB = Triangle(Coordinate(self.x + self.width, self.y + self.height), coord,
        #                         Coordinate(self.x + self.width, self.y))
        # triangle_CPB_area = triangle_CPB.get_area()
        #
        # triangle_PBA = Triangle(Coordinate(self.x + self.width, self.y), coord, Coordinate(self.x, self.y))
        # triangle_PBA_area = triangle_PBA.get_area()
        #
        # sum_of_areas = triangle_APD_area + triangle_DPC_area + triangle_CPB_area + triangle_PBA_area
        # print(f'sum of areas: {sum_of_areas}, rect area: {self.area}, '
        #       f'APD area: {triangle_APD_area}, DPC area: {triangle_DPC_area}, '
        #       f'CPB area: {triangle_CPB_area}, PBA area: {triangle_PBA_area}')
        # if sum_of_areas > self.area:
        #     return False
        # # elif sum_of_areas == self.area:
        # #     pass
        #     # if triangle_APD_area == 0 or triangle_DPC_area == 0 or triangle_CPB_area == 0 or triangle_PBA_area == 0:
        #     #     # ON the rectangle
        #     #     print("on the rectangle")
        #     #     return True
        #     # else:
        #     #     # IN the rectangle
        #     #     print("in the rectangle")
        #     #     return True
        # else: #idk
        #     return True
        #     # raise Exception("calc exception?")

    def top_left_corner(self):
        return Coordinate(self.x, self.y)

    def top_right_corner(self):
        return Coordinate(self.x + self.width - 1, self.y)

    def bottom_left_corner(self):
        return Coordinate(self.x, self.y + self.height)

    def bottom_right_corner(self):
        return Coordinate(self.x + self.width - 1, self.y + self.height)

    @staticmethod
    def do_rectangles_overlap(rect1: 'Rectangle', rect2: 'Rectangle') -> bool:
        for coord in rect1.get_room_coords():
            if rect2.includes_point(coord):
                return True

        return False

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Rectangle):
            return self.x == other.x \
                   and self.y == other.y \
                   and self.height == other.height \
                   and self.width == other.width
        return False

    def top_left(self) -> List[int]:
        return [self.x - 1, self.y - 1]

    def bottom_left(self) -> List[int]:
        return [self.x - 1, self.y + self.height]

    def top_right(self) -> List[int]:
        return [self.x + self.width, self.y - 1]

    def bottom_right(self) -> List[int]:
        return [self.x + self.width, self.y + self.height]

    def left_wall(self) -> List[Coordinate]:
        wall = []
        for y in range(self.y, self.y + self.height):
            wall.append(Coordinate(self.x, y))
        return wall

    def right_wall(self) -> List[Coordinate]:
        wall = []
        for y in range(self.y, self.y + self.height):
            wall.append(Coordinate(self.x + self.width - 1, y))
        return wall

    def top_wall(self) -> List[Coordinate]:
        wall = []
        for x in range(self.x, self.x + self.width):
            wall.append(Coordinate(x, self.y))
        return wall

    def bottom_wall(self) -> List[Coordinate]:
        wall = []
        for x in range(self.x, self.x + self.width):
            wall.append(Coordinate(x, self.y + self.height - 1))
        return wall


class ShipGenerator:
    def __init__(self, map_width: int, map_height: int,
                 orientation: typing.Union[Orientation.vertical, Orientation.horizontal], bridge_width: int,
                 min_room_size: int, max_room_size: int, num_rooms: int):
        self.rooms: typing.List[Rectangle] = []
        self.map_width: int = map_width
        self.map_height: int = map_height
        self.orientation: str = orientation
        self.bridge_width: int = bridge_width
        if bridge_width < 3:
            self.bridge_width = 3
        self.min_room_size = min_room_size
        self.max_room_size = max_room_size
        self.num_rooms = num_rooms
        self.room_centers: typing.List[typing.Tuple[int, int]] = []
        self.level_array = [[' ' for _ in range(map_height)] for _ in range(map_width)]
        self.bridge: Rectangle = self.create_bridge()
        # self.level_array = list(map(list, zip(*self.level_array)))[::1]

    def create_bridge(self) -> Rectangle:
        center_x = self.map_width // 2
        center_y = self.map_height // 2
        if self.orientation == Orientation.vertical:
            bridge_x = center_x - (self.bridge_width // 2)
            bridge_y = 0
            bridge = Rectangle(bridge_x, bridge_y, self.bridge_width, self.map_height)
        else:  # Orientation.horizontal
            bridge_x = 0
            bridge_y = center_y - (self.bridge_width // 2)
            bridge = Rectangle(bridge_x, bridge_y, self.map_width, self.bridge_width)

        return bridge

    def overlaps_existing_room(self, room: Rectangle, border: int = 0):
        for existing_room in self.rooms:
            x = existing_room.x - border
            if x < 0:
                x = 0

            y = existing_room.y - border
            if y < 0:
                y = 0

            # veritcal
            # TODO: horizontal
            w = existing_room.width + border
            h = existing_room.height + border

            room_with_border = Rectangle(
                x,
                y,
                w, h
            )
            if Rectangle.do_rectangles_overlap(room_with_border, room):
                return True
        return False

    def slide_room_to_center(self, room: Rectangle, direction: str = 'right') -> Rectangle:
        if self.orientation == Orientation.vertical:
            if direction == 'right':
                room_right = room.top_right_corner().x
                steps_to_bridge = self.bridge.x - room_right - 1
                new_room: Rectangle = room
                old_room = room
                for x in range(steps_to_bridge + 1):
                    new_room = Rectangle(new_room.x + 1, new_room.y, new_room.width, new_room.height)
                    for existing_room in self.rooms:
                        if Rectangle.do_rectangles_overlap(new_room, existing_room):
                            return old_room
                        else:
                            old_room = new_room

                return new_room
            elif direction == 'left':
                room_left = room.x
                steps_to_bridge = room_left - self.bridge.top_right_corner().x
                new_room: Rectangle = room
                old_room = room
                for x in range(steps_to_bridge):
                    new_room = Rectangle(new_room.x - 1, new_room.y, new_room.width, new_room.height)
                    for existing_room in self.rooms:
                        if Rectangle.do_rectangles_overlap(new_room, existing_room):
                            return old_room
                        else:
                            old_room = new_room

                return old_room
            else:
                print('slide direction not implemented')
                pass

    def create_room(self):
        # vertical
        room_width = random.randrange(self.min_room_size, self.max_room_size)
        room_height = random.randrange(self.min_room_size, self.max_room_size)
        room_x = random.randrange(0, self.bridge.x - room_width)
        room_y = random.randrange(0, self.map_height - room_height)

        room = Rectangle(room_x, room_y, room_width, room_height)

        # TODO: horizontal

        return room

    def reflect_coord(self, coord: Coordinate):
        x = coord.x
        y = coord.y
        if self.orientation == Orientation.vertical:
            x = (self.map_width - x) - self.bridge_width + 1
            pass
        else:  # if orientation == Orientation.ho(rizontal
            x = self.map_width - x

        return Coordinate(x, y)

    # run_times = 100
    # success_run_times = 0

    def get_ship(self):
        for coord in self.bridge.get_room_coords():
            self.level_array[coord.x][coord.y] = '#'
        self.paint_room_floor(self.bridge)

        for i in range(self.num_rooms):
            room = self.try_create_room(5)
            if room is not None:
                new_room = self.slide_room_to_center(room)
                self.rooms.append(new_room)

                reflected_room = self.reflect_room(new_room)
                reflected_room = self.slide_room_to_center(reflected_room, 'left')
                self.rooms.append(reflected_room)

                for coord in new_room.get_room_coords():
                    self.level_array[coord.x][coord.y] = '#'
                for coord in reflected_room.get_room_coords():
                    self.level_array[coord.x][coord.y] = '#'
            else:
                pass

        for room in self.rooms:
            self.paint_room_floor(room)
        self.paint_corridors()

        self.print_map()
        self.ascii_to_tile_type()

    def try_create_room(self, num_tries: int = 100):
        for i in range(num_tries):
            room = self.create_room()
            if not self.overlaps_existing_room(room, border=3):
                return room
            else:
                continue
        return None

    def paint_room_floor(self, room: Rectangle):
        for y in range(room.y + 1, room.y + room.height - 1):
            for x in range(room.x + 1, room.x + room.width - 1):
                self.level_array[x][y] = '.'

    def print_map(self):
        for y in range(0, self.map_height):
            row = []
            for x in range(0, self.map_width):
                row.append(self.level_array[x][y])
            print(*row, sep=' ')

    def paint_corridors(self):
        for room in self.rooms:
            center = room.center
            for room_2 in self.rooms:
                center_2 = room_2.center
                if center == center_2:
                    continue
                if center.y == center_2.y:
                    min_x = min(center.x, center_2.x)
                    max_x = max(center.x, center_2.x)
                    for x in range(min_x, max_x):
                        if Coordinate(x, center.y) in room.wall_coordinates \
                                or Coordinate(x, center.y) in room_2.wall_coordinates \
                                or Coordinate(x, center.y) in self.bridge.wall_coordinates:
                            if self.level_array[x][center.y - 1] == '.' and \
                                    self.level_array[x][center.y + 1] == '.' and \
                                    self.level_array[x + 1][center.y] == '.' and \
                                    self.level_array[x - 1][center.y] == '.':
                                pass
                            else:
                                self.level_array[x][center.y] = '+'
                        elif self.level_array[x][center.y] == '+':
                            pass
                        else:
                            self.level_array[x][center.y] = '.'

                        if self.level_array[x][center.y - 1] == ' ':
                            self.level_array[x][center.y - 1] = '#'
                        if self.level_array[x][center.y + 1] == ' ':
                            self.level_array[x][center.y + 1] = '#'
                elif center.x == center_2.x:
                    min_y = min(center.y, center_2.y)
                    max_y = max(center.y, center_2.y)
                    for y in range(min_y, max_y):
                        check_coord = Coordinate(center.x, y)
                        if check_coord in room.wall_coordinates \
                                or check_coord in room_2.wall_coordinates \
                                or check_coord in self.bridge.wall_coordinates:

                            if self.level_array[center.x][y - 1] == '.' and \
                                    self.level_array[center.x][y + 1] == '.' and \
                                    self.level_array[center.x + 1][y] == '.' and \
                                    self.level_array[center.x - 1][y] == '.':
                                pass
                            else:
                                self.level_array[center.x][y] = '+'
                        elif self.level_array[center.x][y] == '+':
                            pass
                        else:
                            self.level_array[center.x][y] = '.'

                        if self.level_array[center.x - 1][y] == ' ':
                            self.level_array[center.x - 1][y] = '#'
                        if self.level_array[center.x + 1][y] == ' ':
                            self.level_array[center.x + 1][y] = '#'
                else:  # ???
                    pass

    @staticmethod
    def get_tile_type(json_object, ascii_char: str):
        for obj in json_object:
            if json_object[obj]['ascii'] == ascii_char:
                return obj
        raise Exception("ascii not found; check tiles.json")

    def ascii_to_tile_type(self):
        tile_data = utilities.load_data.TILE_DATA
        for y in range(self.map_height):
            for x in range(self.map_width):
                self.level_array[x][y] = self.get_tile_type(tile_data, self.level_array[x][y])

    def reflect_room(self, room):
        reflected_coord = self.reflect_coord(Coordinate(room.x, room.y))
        return Rectangle(reflected_coord.x, reflected_coord.y, room.width, room.height)


if __name__ == '__main__':
    start = timeit.default_timer()
    ShipGenerator(
        map_width=48,
        map_height=28,
        orientation=Orientation.vertical,
        bridge_width=4,
        min_room_size=4,
        max_room_size=12,
        num_rooms=20
    ).get_ship()
    stop = timeit.default_timer()
    execution_time = stop - start
    print(f"Ship generation Executed in {str(execution_time * 1000)}ms")  # It returns time in milliseconds

    rect = Rectangle(0, 0, 3, 3)
    rect_2 = Rectangle(0, 0, 3, 3)
