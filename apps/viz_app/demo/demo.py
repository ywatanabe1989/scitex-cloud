#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SciTeX Code Framework Demo
Demonstrates the complete research workflow with automatic session management.
"""

import sys
import matplotlib.pyplot as plt
import scitex as stx

def main(args):
    """Demo of SciTeX capabilities."""

    # 1. Universal I/O - Load data
    print("📂 Loading data...")
    # data = stx.io.load("data.csv")  # Auto-detects format

    # 2. Session management creates organized structure
    print(f"📁 Session directory: {CONFIG['SDIR']}")
    print(f"   ├── logs/ (stdout.log, stderr.log)")
    print(f"   ├── CONFIGS/ (CONFIG.yaml, CONFIG.pkl)")
    print(f"   └── figs/")

    # 3. Statistical testing (23 tests available)
    print("\n📊 Statistical testing...")
    # result = stx.stats.ttest_ind(control, treatment, plot=True)
    print("   - Parametric & non-parametric tests")
    print("   - Effect sizes & power analysis")
    print("   - Export to 9 formats")

    # 4. Machine Learning
    print("\n🧠 ML & AI capabilities...")
    print("   - PyTorch training utilities")
    print("   - GenAI: 7 providers (OpenAI, Anthropic, Google...)")
    print("   - Cost tracking enabled")

    # 5. Publication plots
    print("\n📈 Creating publication-ready plots...")
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    ax.set_title("Sample Plot")
    stx.io.save(fig, "demo_plot.png")  # Auto-saves data as CSV
    print("   ✓ Saved: demo_plot.png + data CSV")

    return 0


def parse_args():
    """Parse command line arguments."""
    import argparse
    parser = argparse.ArgumentParser(description='SciTeX Demo')
    return parser.parse_args()


def run_main():
    """Initialize SciTeX framework, run main, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    args = parse_args()

    # Start session - creates organized directory structure
    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__file__,
        verbose=True,
    )

    print("\n" + "="*60)
    print("SciTeX Framework Demo - Reproducible Research Pipeline")
    print("="*60 + "\n")

    # Run main
    exit_status = main(args)

    # Close session - organizes outputs to FINISHED_SUCCESS/ERROR
    stx.session.close(
        CONFIG,
        verbose=True,
        exit_status=exit_status,
    )

    print("\n" + "="*60)
    print(f"Session organized: {CONFIG['SDIR']}")
    print("All outputs automatically tracked and saved!")
    print("="*60)


if __name__ == "__main__":
    run_main()

# EOF
