import glob
import os
import time
import unittest
from datetime import datetime

import utilities.constants
from utilities.save_manager import SaveManager


class TestSaveManager(unittest.TestCase):
    def setUp(self) -> None:
        utilities.constants.SAVE_GAME_DIR = f'{utilities.constants.ROOT_DIR}/test/test_data'
        utilities.constants.SAVE_GAME_PREFIX = 'test_data'
        self.save_name = 'test_data.save.json'
        self.modified_string = "Mon Dec  1 05:30:32 2025"
        # set test file to a fixed date for testing
        date = datetime(year=2025, month=12, day=1, hour=5, minute=30, second=32)
        self.timestamp = date.timestamp()
        self.file_path = f'{utilities.constants.SAVE_GAME_DIR}/{self.save_name}'
        self.test_seed = 'de96922ddb784f1c80587a5c726a799a'
        modTime = time.mktime(date.timetuple())
        os.utime(f'{utilities.constants.SAVE_GAME_DIR}/{self.save_name}', (modTime, modTime))

    def tearDown(self) -> None:
        # delete all created files in test_data except test_data.save.json
        while not os.path.exists(self.file_path):
            time.sleep(10)

        if os.path.isfile(self.file_path):
            for CleanUp in glob.glob(f'{utilities.constants.SAVE_GAME_DIR}/*'):
                if not CleanUp.endswith(self.save_name):
                    os.remove(CleanUp)

    def test_get_save_list(self):
        save_list = SaveManager.get_save_list()
        save_list_assert = [{'path': self.file_path,
                             'modified': self.modified_string,
                             'modified_timestamp': self.timestamp,
                             'seed': self.test_seed}]

        self.assertEqual(save_list, save_list_assert)

    def test_get_file_modified_time(self):
        assert_file_modified_time = {'modified_timestamp': self.timestamp, 'modified_str': self.modified_string}
        self.assertEqual(assert_file_modified_time,
                         SaveManager.get_file_modified_time(self.file_path))

    def test_load_game(self):
        import uuid
        import utilities.seed
        test_data = {"version": "0.1.0", "seed": self.test_seed}
        self.assertEqual(test_data, SaveManager.load_game(self.file_path, import_seed=False))
        self.assertEqual(test_data, SaveManager.load_game(self.file_path, import_seed=True))
        self.assertEqual(uuid.UUID(self.test_seed), utilities.seed.seed)

    def test_save_game(self):
        import uuid
        seed = uuid.uuid4()
        test_data = {"version": "0.1.0", "seed": seed.hex}
        for i in range(0, 20):
            test_save_name = f'test_data_{i}.save.json'
            self.assertEqual(test_save_name, SaveManager.save_game(test_data))

    def test_get_screenshot_file_path(self):
        screenshot_file_name = f'{utilities.constants.SAVE_GAME_DIR}/test_data.save.png'
        self.assertEqual(screenshot_file_name, SaveManager.get_screenshot_file_path(self.save_name))

    def test_get_save_names_from_save_list(self):
        test_save_names = [self.save_name]
        self.assertEqual(test_save_names, SaveManager.get_save_names_from_save_list())

    def test_get_save_name(self):
        self.assertEqual(self.save_name, SaveManager.get_save_name())
        for i in range(1, 20):
            test_save_name = f'test_data_{i - 1}.save.json'
            self.assertEqual(test_save_name, SaveManager.get_save_name(i))

if __name__ == '__main__':
    unittest.main()
