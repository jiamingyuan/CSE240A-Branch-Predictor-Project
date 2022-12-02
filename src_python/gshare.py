from constants import *

class GShare:
    def __init__(self, ghistoryBits):
        self.ghistoryBits = ghistoryBits
        self.ghist = 0
        self.pht = [WN] * (2 ** self.ghistoryBits)

    def predict(self, pc):
        idx = (pc ^ self.ghist) & ((1 << self.ghistoryBits) - 1)
        decision = self.pht[idx]

        if decision == WT or decision == ST:
            return TAKEN
        else:
            return NOTTAKEN

    def train(self, pc, outcome):
        idx = (pc ^ self.ghist) & ((1 << self.ghistoryBits) - 1)
        decision = self.pht[idx]

        if outcome and (decision != ST):
            self.pht[idx] = decision + 1
        elif not outcome and (decision != SN):
            self.pht[idx] = decision - 1

        self.ghist = outcome | (self.ghist << 1) & ((1 << self.ghistoryBits) - 1)

        return (decision == WT or decision == ST) == outcome