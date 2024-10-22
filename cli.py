#!/usr/bin/env python3
"""Unified CLI entry-point for crypto-tracker."""

import argparse
import sys
from rich.console import Console

console = Console()


def cmd_prices(args):
    from tracker import fetch_prices, display_prices
    coins = args.coins or ["bitcoin", "ethereum", "solana"]
    data = fetch_prices(coins, args.currency)
    display_prices(data, args.currency)


def cmd_portfolio(args):
    from portfolio import show_portfolio, add_holding, remove_holding
    if args.action == "show":
        show_portfolio(args.currency)
    elif args.action == "add":
        if not args.coin or args.amount is None:
            console.print("[red]--coin and --amount are required for 'add'[/red]")
        else:
            add_holding(args.coin, args.amount)
    elif args.action == "remove":
        if not args.coin:
            console.print("[red]--coin is required for 'remove'[/red]")
        else:
            remove_holding(args.coin)


def cmd_alert(args):
    from alerts import add_alert, run_alert_loop
    if args.action == "add":
        if not all([args.coin, args.threshold, args.direction]):
            console.print("[red]--coin, --threshold, --direction required for 'add'[/red]")
        else:
            add_alert(args.coin, args.threshold, args.direction, args.currency)
    elif args.action == "run":
        run_alert_loop()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crypto-tracker",
        description="Lightweight cryptocurrency price tracker and portfolio tool",
    )
    parser.add_argument("--currency", default="usd", metavar="CCY")
    sub = parser.add_subparsers(dest="command", required=True)

    # prices
    p_prices = sub.add_parser("prices", help="Show live prices")
    p_prices.add_argument("coins", nargs="*")
    p_prices.set_defaults(func=cmd_prices)

    # portfolio
    p_port = sub.add_parser("portfolio", help="Manage your portfolio")
    p_port.add_argument("action", choices=["show", "add", "remove"])
    p_port.add_argument("--coin")
    p_port.add_argument("--amount", type=float)
    p_port.set_defaults(func=cmd_portfolio)

    # alert
    p_alert = sub.add_parser("alert", help="Set and monitor price alerts")
    p_alert.add_argument("action", choices=["add", "run"])
    p_alert.add_argument("--coin")
    p_alert.add_argument("--threshold", type=float)
    p_alert.add_argument("--direction", choices=["above", "below"])
    p_alert.set_defaults(func=cmd_alert)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/yellow]")
        sys.exit(0)


if __name__ == "__main__":
    main()
