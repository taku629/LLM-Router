import argparse

from .tracker import CostTracker


def main() -> None:
    parser = argparse.ArgumentParser(prog="llmrouter")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("stats")
    args = parser.parse_args()

    if args.cmd == "stats":
        t = CostTracker()
        totals = t.totals()
        print(f"Requests      : {int(totals['requests'])}")
        print(f"Routed cost   : ${totals['routed_cost']:.6f}")
        print(f"Baseline cost : ${totals['baseline_cost']:.6f}")
        print(f"Saved         : ${totals['saved_cost']:.6f}")
    else:
        parser.print_help()
