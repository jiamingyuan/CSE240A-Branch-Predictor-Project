from pht import PHT

class GShare:
    def __init__(self, global_history_bits):
        self.global_history_table = PHT(global_history_bits)
        self.global_hist = 0
        self.global_mask = (1 << global_history_bits) - 1

    def train(self, pc, outcome):
        # Make prediction and update
        gshare_index = (pc ^ self.global_hist) & self.global_mask
        decision, _ = self.global_history_table.train(gshare_index, outcome)

        # Update global history
        self.global_hist = outcome | (self.global_hist << 1) & self.global_mask

        # Output result
        return decision == outcome