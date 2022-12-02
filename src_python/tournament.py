from constants import *

class Tournament:
    def __init__(self, globalHistoryBits, localHistoryBits, pcIndexBits):
        self.globalMask = (1 << globalHistoryBits) - 1
        self.localMask = (1 << localHistoryBits) - 1
        self.pcMask = (1 << pcIndexBits) - 1

        self.localHist = [0] * (1 << pcIndexBits)
        self.localPHT = [WN] * (1 << localHistoryBits)
        self.globalHist = 0
        self.globalPHT = [WN] * (1 << globalHistoryBits)
        self.choicePHT = [WL] * (1 << globalHistoryBits)

    def train(self, pc, outcome):
        # Local Prediction
        pcSlide = pc & self.pcMask
        currLocalHist = self.localHist[pcSlide]
        localDecision = self.localPHT[currLocalHist]

        # Global Prediction
        globalDecision = self.globalPHT[self.globalHist]

        # Choice Prediction
        choice = self.choicePHT[self.globalHist]
        if choice == WG or choice == SG:
            decision = globalDecision
        else:
            decision = localDecision

        # Decision Updation
        if outcome:
            if localDecision != ST:
                self.localPHT[currLocalHist] += 1
            if globalDecision != ST:
                self.globalPHT[self.globalHist] += 1
            if localDecision >= 2 and globalDecision < 2 and choice != SL:
                self.choicePHT[self.globalHist] -= 1
            elif localDecision < 2 and globalDecision >= 2 and choice != SG:
                self.choicePHT[self.globalHist] += 1
        else:
            if localDecision != SN:
                self.localPHT[currLocalHist] -= 1
            if globalDecision != SN:
                self.globalPHT[self.globalHist] -= 1
            if localDecision < 2 and globalDecision >= 2 and choice != SL:
                self.choicePHT[self.globalHist] -= 1
            elif localDecision >= 2 and globalDecision < 2 and choice != SG:
                self.choicePHT[self.globalHist] += 1

        # History Updation
        self.localHist[pcSlide] = outcome | (currLocalHist << 1) & self.localMask
        self.globalHist = outcome | (self.globalHist << 1) & self.globalMask

        # Output
        return (decision >= 2) == outcome

