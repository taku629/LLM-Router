import argparse
import json

from .config import RouterConfig
from .models import list_supported_models
from .tracker import CostTracker
from .selftest import run_selftest


def _print_json(payload: object) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser(prog="llmrouter")
    sub = parser.add_subparsers(dest="cmd")
    stats_parser = sub.add_parser("stats")
    stats_parser.add_argument("--json", action="store_true")
    sub.add_parser("selftest")
    sub.add_parser("config")
    sub.add_parser("models")
    args = parser.parse_args()

    if args.cmd == "stats":
        config = RouterConfig.from_env()
        t = CostTracker(str(config.db_path))
        totals = t.totals()
        breakdown = t.model_breakdown()
        if args.json:
            _print_json({"totals": totals, "models": breakdown})
            return
        print(f"Requests      : {int(totals['requests'])}")
        print(f"Priced        : {int(totals['priced_requests'])}")
        print(f"Unpriced      : {int(totals['unpriced_requests'])}")
        print(f"Routed cost   : ${totals['routed_cost']:.6f}")
        print(f"Baseline cost : ${totals['baseline_cost']:.6f}")
        print(f"Saved         : ${totals['saved_cost']:.6f}")
        print(f"Avg routed    : ${totals['average_routed_cost']:.6f}")
        print(f"Avg saved     : ${totals['average_saved_cost']:.6f}")
        print(f"Avg score     : {totals['average_complexity_score']:.2f}")
        if breakdown:
            print("")
            print("By model")
            for row in breakdown:
                print(
                    f"- {row['routed_model']}: requests={int(row['requests'])}, "
                    f"avg_score={row['average_complexity_score']:.2f}, "
                    f"cost=${row['routed_cost']:.6f}, saved=${row['saved_cost']:.6f}"
                )
    elif args.cmd == "selftest":
        run_selftest()
    elif args.cmd == "config":
        _print_json(RouterConfig.from_env().as_dict())
    elif args.cmd == "models":
        _print_json(
            [
                {
                    "name": model.name,
                    "input_per_1k": model.input_per_1k,
                    "output_per_1k": model.output_per_1k,
                }
                for model in list_supported_models()
            ]
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
