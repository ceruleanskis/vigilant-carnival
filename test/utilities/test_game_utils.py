import unittest

import utilities.game_utils


class TestGameUtils(unittest.TestCase):
    def setUp(self) -> None:
        self.game_utils = utilities.game_utils.GameUtils()

    def test_round_to_multiple(self):
        self.assertEqual(utilities.game_utils.GameUtils.round_to_multiple(36, 50), 50)
        self.assertEqual(utilities.game_utils.GameUtils.round_to_multiple(13421542, 3), 13421541)


if __name__ == '__main__':
    unittest.main()
