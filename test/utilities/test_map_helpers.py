import unittest

from utilities.map_helpers import MapHelpers
from utilities.ship_generator import Coordinate


class TestMapHelpers(unittest.TestCase):
    def test_is_in_map_bounds(self):
        self.assertTrue(MapHelpers.is_in_map_bounds(Coordinate(0, 0), 30, 30))
        self.assertTrue(MapHelpers.is_in_map_bounds(Coordinate(0, 29), 30, 30))
        self.assertTrue(MapHelpers.is_in_map_bounds(Coordinate(29, 29), 30, 30))
        self.assertFalse(MapHelpers.is_in_map_bounds(Coordinate(-1, 0), 30, 30))
        self.assertFalse(MapHelpers.is_in_map_bounds(Coordinate(0, -1), 30, 30))
        self.assertFalse(MapHelpers.is_in_map_bounds(Coordinate(-1, -1), 30, 30))
        self.assertFalse(MapHelpers.is_in_map_bounds(Coordinate(0, 30), 30, 30))
        self.assertFalse(MapHelpers.is_in_map_bounds(Coordinate(30, 30), 30, 30))
        self.assertFalse(MapHelpers.is_in_map_bounds(Coordinate(30, 29), 30, 30))
        self.assertFalse(MapHelpers.is_in_map_bounds(Coordinate(29, 30), 30, 30))

    def test_get_neighbors(self):
        map_width = 5
        map_height = 5

        get_neighbors = sorted(MapHelpers.get_neighbors(Coordinate(3, 3), map_width, map_height),
                               key=lambda c: [c.x, c.y])
        test_neighbors = sorted([Coordinate(2, 3), Coordinate(3, 2), Coordinate(3, 4), Coordinate(4, 3)],
                                key=lambda c: [c.x, c.y])
        self.assertEqual(get_neighbors, test_neighbors)

        get_neighbors = sorted(MapHelpers.get_neighbors(Coordinate(0, 0), map_width, map_height),
                               key=lambda c: [c.x, c.y])
        test_neighbors = sorted([Coordinate(0, 1), Coordinate(1, 0)],
                                key=lambda c: [c.x, c.y])
        self.assertEqual(get_neighbors, test_neighbors)

        get_neighbors = sorted(MapHelpers.get_neighbors(Coordinate(4, 4), map_width, map_height),
                               key=lambda c: [c.x, c.y])
        test_neighbors = sorted([Coordinate(4, 3), Coordinate(3, 4)],
                                key=lambda c: [c.x, c.y])
        self.assertEqual(get_neighbors, test_neighbors)

        get_neighbors = sorted(MapHelpers.get_neighbors(Coordinate(4, 2), map_width, map_height),
                               key=lambda c: [c.x, c.y])
        test_neighbors = sorted([Coordinate(4, 1), Coordinate(3, 2), Coordinate(4, 3)],
                                key=lambda c: [c.x, c.y])
        self.assertEqual(get_neighbors, test_neighbors)


if __name__ == '__main__':
    unittest.main()
