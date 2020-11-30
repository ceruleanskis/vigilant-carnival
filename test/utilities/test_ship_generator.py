import unittest

from utilities.ship_generator import Coordinate, Rectangle, Triangle


class TestCoordinate(unittest.TestCase):
    def test_equality(self):
        self.assertEqual(Coordinate(0, 0) == Coordinate(0, 0), True)
        self.assertEqual(Coordinate(323, 45) == Coordinate(323, 45),
                         True)
        self.assertEqual(Coordinate(323, 45) == (323, 45), False)


class TestTriangle(unittest.TestCase):
    def test_area(self):
        triangle_1 = Triangle(Coordinate(2, 4), Coordinate(3, -6), Coordinate(7, 8))
        triangle_2 = Triangle(Coordinate(1, 8), Coordinate(8, 9), Coordinate(2, 1))
        triangle_3 = Triangle(Coordinate(-10, 5), Coordinate(15, 5), Coordinate(10, 12))
        self.assertEqual(triangle_1.get_area(), 27)
        self.assertEqual(triangle_2.get_area(), 25)
        self.assertEqual(triangle_3.get_area(), 87.5)


class TestRectangle(unittest.TestCase):
    def test_get_room_coords(self):
        rect_1 = Rectangle(0, 0, 2, 2)
        rect_1_room_coords = rect_1.get_room_coords()

        # Test size of room
        self.assertEqual(len(rect_1_room_coords), 4)

        # Test value of room coords
        rect_1_room_coords_sorted = sorted(rect_1_room_coords, key=lambda c: [c.x, c.y])

        expected_room_coords = [Coordinate(0, 0), Coordinate(1, 0), Coordinate(0, 1), Coordinate(1, 1)]
        expected_room_coords_sorted = sorted(expected_room_coords, key=lambda c: [c.x, c.y])

        self.assertEqual(rect_1_room_coords_sorted,
                         expected_room_coords_sorted)

    def test_includes_point(self):
        rect_1 = Rectangle(2, 2, 2, 2)

        self.assertTrue(rect_1.includes_point(Coordinate(2, 2)))
        self.assertTrue(rect_1.includes_point(Coordinate(2, 3)))
        self.assertTrue(rect_1.includes_point(Coordinate(3, 2)))
        self.assertTrue(rect_1.includes_point(Coordinate(3, 3)))

        self.assertFalse(rect_1.includes_point(Coordinate(1, 1)))
        self.assertFalse(rect_1.includes_point(Coordinate(2, 1)))
        self.assertFalse(rect_1.includes_point(Coordinate(3, 1)))
        self.assertFalse(rect_1.includes_point(Coordinate(4, 1)))
        self.assertFalse(rect_1.includes_point(Coordinate(1, 2)))
        self.assertFalse(rect_1.includes_point(Coordinate(4, 2)))
        self.assertFalse(rect_1.includes_point(Coordinate(1, 3)))
        self.assertFalse(rect_1.includes_point(Coordinate(4, 3)))
        self.assertFalse(rect_1.includes_point(Coordinate(1, 4)))
        self.assertFalse(rect_1.includes_point(Coordinate(2, 4)))
        self.assertFalse(rect_1.includes_point(Coordinate(3, 4)))
        self.assertFalse(rect_1.includes_point(Coordinate(4, 4)))


if __name__ == '__main__':
    unittest.main()
