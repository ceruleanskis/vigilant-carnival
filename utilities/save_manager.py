import datetime
import glob
import json
import os
import typing

import pygame

import utilities.constants
import utilities.seed


class SaveManager:
    """
    Manages and includes useful routines for saving and loading of game data files.
    """

    @staticmethod
    def get_save_list() -> typing.List[typing.Dict]:
        """
        Get the list of saved games in SAVE_GAME_DIR
        :return: A list of dicts containing save game info.
        :rtype: dict: {
        'path': str absolute path to file,
        'modified': str last modified time represented as %c (locale datettime representation),
        'modified_timestamp': float POSIX timestamp of last modified time,
        'seed': str representing UUID game seed value
        }
        """
        save_list = []
        save_files = glob.glob(f'{utilities.constants.SAVE_GAME_DIR}/*{utilities.constants.SAVE_GAME_EXT}')
        for i in range(len(save_files)):
            path = save_files[i]
            modified = SaveManager.get_file_modified_time(path)
            json_data = SaveManager.load_game(path, import_seed=False)
            seed = json_data['seed']
            save_list.append({
                'path': path,
                'modified': modified['modified_str'],
                'modified_timestamp': modified['modified_timestamp'],
                'seed': seed
            })
        save_list = sorted(save_list, key=lambda k: datetime.datetime.fromtimestamp(k['modified_timestamp']),
                           reverse=True)

        return save_list

    @staticmethod
    def get_file_modified_time(path: str) -> dict[str, typing.Union[float]]:
        """
        Get the last modified time of a file at the given path.
        :param path: absolute path to file
        :type path: str
        :return: a dict containing str last modified time represented as %c and POSIX timestamp
        :rtype: dict[str, typing.Union[float]]
        """
        modified = {}
        timestamp = os.path.getmtime(path)
        modified['modified_timestamp'] = timestamp
        datetime_obj = datetime.datetime.fromtimestamp(timestamp)
        modified['modified_str'] = datetime_obj.strftime('%c')
        return modified

    @staticmethod
    def load_game(file_path: str, import_seed: bool = True) -> typing.Dict:
        """
        Loads JSON data from a file path into an object.
        :param file_path: absolute path to file
        :type file_path:
        :param import_seed: whether to import a seed into the game or not
        :type import_seed: bool
        :return: object containing saved game data from file
        :rtype: dict
        """
        with open(file_path) as json_file:
            json_data = json.load(json_file)
        if import_seed:
            utilities.seed.import_seed(json_data['seed'])
        return json_data

    @staticmethod
    def save_game(json_data: typing.Dict) -> str:
        """
        Saves the given JSON data to a file in SAVE_GAME_DIR.
        :param json_data: game data dict
        :type json_data: dict
        :return: the name of the file that was saved (relative to SAVE_GAME_DIR)
        :rtype: str
        """
        save_as_name = SaveManager.get_save_name()
        save_name_list = SaveManager.get_save_names_from_save_list()
        for i in range(len(save_name_list)):
            if save_as_name in save_name_list:
                save_as_name = SaveManager.get_save_name(i + 1)

        save_as_path = f'{utilities.constants.SAVE_GAME_DIR}/{save_as_name}'
        os.makedirs(os.path.dirname(save_as_path), exist_ok=True)
        with open(save_as_path, 'w') as outfile:
            json.dump(json_data, outfile)

        return save_as_name

    @staticmethod
    def get_screenshot_file_path(save_as_name: str):
        """
        Constructs the path of the file to save a screenshot of the saved game to.
        :param save_as_name: the name of the dave game data file
        :type save_as_name: str
        :return:
        :rtype:
        """
        return f'{utilities.constants.SAVE_GAME_DIR}/{save_as_name.removesuffix(".json")}.png'

    @staticmethod
    def save_screenshot(save_as_name: str, surface: pygame.Surface):  # pragma: no cover
        """
        Screenshots and saves an image to the saved game dir with the name of the saved game file
        (but instead extension of png) given a pygame surface to screenshot.
        :param save_as_name: the name of the dave game data file
        :type save_as_name: str
        :param surface: the pygame surface to screenshot
        :type surface: pygame.Surface
        """
        save_as_screenshot_name = SaveManager.get_screenshot_file_path(save_as_name)
        pygame.image.save(surface, save_as_screenshot_name) # pragma: no cover

    @staticmethod
    def get_save_names_from_save_list() -> [str]:
        """
        Returns the list of names of the saved game files relative to the SAVE_GAME_DIR.
        :return: list of save names
        :rtype: list[str]
        """
        save_list = SaveManager.get_save_list()
        return [save['path'].removeprefix(f'{utilities.constants.SAVE_GAME_DIR}/') for save in save_list]

    @staticmethod
    def get_save_name(num: int = 0) -> str:
        """
        Iterate the save game name using number given (to avoid duplicate save names)
        :param num: the index of saved games
        :type num: int
        :return: filename appended with number
        :rtype: str
        """
        if num == 0:
            return f'{utilities.constants.SAVE_GAME_PREFIX}{utilities.constants.SAVE_GAME_EXT}'
        if num > 0:
            return f'{utilities.constants.SAVE_GAME_PREFIX}_{num - 1}{utilities.constants.SAVE_GAME_EXT}'
        else:
            raise ValueError('Number to append to save file name should be greater than zero ')
