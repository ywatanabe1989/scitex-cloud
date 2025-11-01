#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-30 14:08:15 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/demo/v02/compile_demo.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./demo/v02/compile_demo.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Does XYZ
  - Does XYZ
  - Does XYZ
  - Saves XYZ

Dependencies:
  - scripts:
    - /path/to/script1
    - /path/to/script2
  - packages:
    - package1
    - package2
IO:
  - input-files:
    - /path/to/input/file.xxx
    - /path/to/input/file.xxx

  - output-files:
    - /path/to/input/file.xxx
    - /path/to/input/file.xxx

(Remove me: Please fill docstrings above, while keeping the bulette point style, and remove this instruction line)
"""

"""Imports"""
import argparse
import scitex as stx
from scitex import logging

logger = logging.getLogger(__name__)

"""Warnings"""
# stx.pd.ignore_SettingWithCopyWarning()
# warnings.simplefilter("ignore", UserWarning)
# with warnings.catch_warnings():
#     warnings.simplefilter("ignore", UserWarning)

"""Parameters"""
# CONFIG = stx.io.load_configs()

"""Functions & Classes"""
def main(args):
    import scitex

    writer = scitex.writer.Writer(f"{__DIR__}/writer-project-demo")
    writer.compile_manuscript()
    # Main function to demonstrate this file
    # Avoid printing/logging functions here.
    # Instead, implement in delegated code as much as possible.
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="")
    # parser.add_argument(
    #     "--var",
    #     "-v",
    #     type=int,
    #     choices=None,
    #     default=1,
    #     help="(default: %(default)s)",
    # )
    # parser.add_argument(
    #     "--flag",
    #     "-f",
    #     action="store_true",
    #     default=False,
    #     help="(default: %%(default)s)",
    # )
    args = parser.parse_args()
    return args


def run_session() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    import sys
    import matplotlib.pyplot as plt
    import scitex as stx

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_session()

# EOF
