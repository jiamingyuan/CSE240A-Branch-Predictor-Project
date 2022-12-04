from constants import *

class PHT:
    def __init__(self, bit_length, init_value=WF):
        self.table = [init_value] * (1 << bit_length)

    def get(self, idx):
        return self.table[idx]

    def update(self, idx, value):
        self.table[idx] = value

    def train(self, idx, outcome):
        decision = self.get(idx)

        if outcome and (decision != ST):
            self.table[idx] += 1
        elif not outcome and (decision != SF):
            self.table[idx] -= 1

        return decision == WT or decision == ST, decision == WT or decision == WF