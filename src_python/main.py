import argparse
from tqdm import *

from gshare import GShare
from constants import *

def params():
    parser = argparse.ArgumentParser()

    parser.add_argument("--bptype", default=1, type=int)
    parser.add_argument("--file", default="../traces/fp_1", type=str)
    parser.add_argument('--ghistoryBits', default=10, type=int)

    args = parser.parse_args()
    return args

def line_parser(line):
    pc, outcome = line.split(' ')
    pc = int(pc, base=16)
    outcome = int(outcome[:-1])

    return pc, outcome

if __name__ == '__main__':
    args = params()

    if args.bptype == GSHARE:
        predictor = GShare(args.ghistoryBits)

    num_branches = 0
    mispredictions = 0
    with open(args.file, 'r') as file:
        for line in tqdm(file.readlines()):
            pc, outcome = line_parser(line)

            if not predictor.train(pc, outcome):
                mispredictions += 1
            num_branches += 1

    print('Branches:               ', num_branches)
    print('Incorrect:              ', mispredictions)
    print('Misprediction Rate:     ', mispredictions / num_branches)