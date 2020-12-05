from collections import deque
import utilities.logsetup

log = utilities.logsetup.log()

time_deque = deque()
turns = 0


def register(obj):
    time_deque.append(obj)
    obj.action_points = 0


def release(obj):
    time_deque.remove(obj)


def tick():
    global turns
    for item in range(len(time_deque)):
        if len(time_deque) > 0:
            obj = time_deque[0]
            time_deque.rotate(1)
            obj.action_points += obj.speed
            while obj.action_points > 0:
                cost = obj.take_turn()
                obj.action_points -= cost
                # log.debug(f"{obj.name} took turn, cost: {cost}, remaining: {obj.action_points}")
    turns += 1
    log.debug(f"tick, turn:{turns}")
