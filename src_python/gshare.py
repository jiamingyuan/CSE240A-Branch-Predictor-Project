from constants import *

class GShare:
    def __init__(self, globalHistoryBits):
        self.globalMask = (1 << globalHistoryBits) - 1
        self.globalHist = 0
        self.pht = [WN] * (1 << globalHistoryBits)

    def predict(self, pc):
        idx = (pc ^ self.globalHist) & self.globalMask
        decision = self.pht[idx]

        if decision == WT or decision == ST:
            return TAKEN
        else:
            return NOTTAKEN

    def train(self, pc, outcome):
        idx = (pc ^ self.globalHist) & self.globalMask
        decision = self.pht[idx]

        if outcome and (decision != ST):
            self.pht[idx] += 1
        elif not outcome and (decision != SN):
            self.pht[idx] -= 1

        self.globalHist = outcome | (self.globalHist << 1) & self.globalMask

        return (decision == WT or decision == ST) == outcome