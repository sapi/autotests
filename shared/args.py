import argparse


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('path', type=str)
    parser.add_argument('--masters', action='store_true', default=False)

    return parser.parse_args()
