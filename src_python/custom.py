from constants import *
from pht import PHT

class Custom:
    def __init__(self, global_history_bits, local_history_bits, pc_index_bits):
        # Initialize masks
        self.global_mask = (1 << global_history_bits) - 1
        self.local_mask = (1 << local_history_bits) - 1
        self.pc_mask = (1 << pc_index_bits) - 1

        # Initialize histories
        self.local_history = PHT(pc_index_bits, init_value=0)
        self.global_history = 0

        # Initialize tabels
        self.local_history_table = PHT(local_history_bits)
        self.global_history_table = PHT(global_history_bits)
        self.gshare_history_table = PHT(global_history_bits)
        self.choice_table = PHT(global_history_bits)

    def train(self, pc, outcome):
        # Local prediction
        local_hist_idx = pc & self.pc_mask
        local_index = self.local_history.get(local_hist_idx)
        local_decision, _ = self.local_history_table.train(local_index, outcome)

        # Global prediction
        global_decision, _ = self.global_history_table.train(self.global_history, outcome)

        # Gshare prediction
        gshare_idx = (pc ^ self.global_history) & self.global_mask
        gshare_decision, _ = self.gshare_history_table.train(gshare_idx, outcome)

        # Make decision
        if local_decision == gshare_decision:
            decision = local_decision
        else:
            choice, neutral = self.choice_table.train(self.global_history, gshare_decision == outcome)
            if choice:
                decision = gshare_decision
            else:
                decision = local_decision

        # History updation
        local_history_new = outcome | (self.local_history.get(local_hist_idx) << 1) & self.local_mask
        self.local_history.update(local_hist_idx, local_history_new)
        self.global_history = outcome | (self.global_history << 1) & self.global_mask

        # Output
        return decision == outcome
