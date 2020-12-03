from collections import deque

time_deque = deque()
turns = 0


def register(obj):
    time_deque.append(obj)
    obj.action_points = 0


def release(obj):
    time_deque.remove(obj)


def tick():
    global turns
    if len(time_deque) > 0:
        obj = time_deque[0]
        time_deque.rotate(1)
        obj.action_points += obj.speed
        while obj.action_points > 0:
            obj.action_points -= obj.take_turn()
        turns += 1