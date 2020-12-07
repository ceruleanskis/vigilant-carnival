import utilities.constants
import utilities.ship_generator


def track_camera(player_x_pos, player_y_pos, map_width, map_height):
    MAP_DISPLAY_WIDTH = utilities.constants.MAP_DISPLAY_WIDTH
    MAP_DISPLAY_HEIGHT = utilities.constants.MAP_DISPLAY_HEIGHT
    x = player_x_pos - MAP_DISPLAY_WIDTH // 2
    y = player_y_pos - MAP_DISPLAY_HEIGHT // 2

    if x < 0:
        x = 0

    if y < 0:
        y = 0

    if x > map_width - MAP_DISPLAY_WIDTH - 1:
        x = map_width - MAP_DISPLAY_WIDTH - 1

    if y > map_height - MAP_DISPLAY_HEIGHT - 1:
        y = map_height - MAP_DISPLAY_HEIGHT - 1

    return utilities.ship_generator.Coordinate(x, y)
