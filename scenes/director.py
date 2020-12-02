import typing

import components.scene

scene_list: typing.List[components.scene.Scene] = []


def push(scene: typing.Union[components.scene.Scene, None]):
    scene_list.append(scene)


def replace_with(scene: components.scene.Scene):
    index = scene_list.index(top())
    scene_list[index] = scene


def pop():
    scene_list.pop()


def prev():
    try:
        return scene_list[-2]
    except Exception:
        raise IndexError('director.py: Scene out of range in scene list.')


def top():
    try:
        return scene_list[-1]
    except IndexError:
        return None
