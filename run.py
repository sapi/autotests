#!/usr/bin/env python

import subprocess

from config import cfg
from shared.args import parse_args


def copy_script(args):
    """
    copy_script(Namespace) -> None

    We don't want to stuff around with importing the script, as that requires
    a proper set of modules in the directory structure (ie, __init__.py).

    So we copy the script to a known location to play with.

    """
    cmd = 'cp %s %s.py'%(args.path, cfg.TEST_SCRIPT_NAME)
    child = subprocess.Popen(cmd, shell=True)
    child.wait()

    if child.returncode:
        exit(child.returncode)


def main():
    args = parse_args()

    copy_script(args)

    # Call our test script from here
    cmd = 'python ./test.py%s %s'%(' --masters' if args.masters else '',
            args.path)
    child = subprocess.Popen(cmd, shell=True)
    child.wait()


if __name__ == '__main__':
    main()
