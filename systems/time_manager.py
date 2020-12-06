from collections import deque

import utilities.logsetup

log = utilities.logsetup.log()


class TimeManager:
    def __init__(self):
        self.time_deque = deque()
        self.turns = 0

    def register(self, obj):
        self.time_deque.append(obj)
        obj.action_points = 0

    def release(self, obj):
        self.time_deque.remove(obj)

    def tick(self):
        for item in range(len(self.time_deque)):
            if len(self.time_deque) > 0:
                obj = self.time_deque[0]
                self.time_deque.rotate(1)
                obj.action_points += obj.speed
                while obj.action_points > 0:
                    cost = obj.take_turn()
                    obj.action_points -= cost
        self.turns += 1
        log.debug(f"tick, turn:{self.turns}")
