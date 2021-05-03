import pygame.font

import utilities.constants
import utilities.load_data

pygame.font.init()

fonts = utilities.load_data.FONT_DATA


class FontWeightString:
    default = 'default'
    bold = 'bold'
    italic = 'italic'
    bold_italic = 'bold_italic'


def get_font(font_weight_str: str, font_size: int = utilities.constants.FONT_SIZE):
    font_path = fonts[font_weight_str]
    return pygame.font.Font(font_path, font_size)


def default(font_size: int = utilities.constants.FONT_SIZE):
    return get_font(FontWeightString.default, font_size)


def bold(font_size: int = utilities.constants.FONT_SIZE):
    return get_font(FontWeightString.bold, font_size)


def italic(font_size: int = utilities.constants.FONT_SIZE):
    return get_font(FontWeightString.italic, font_size)


def bold_italic(font_size: int = utilities.constants.FONT_SIZE):
    return get_font(FontWeightString.bold_italic, font_size)
