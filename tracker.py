#!/usr/bin/env python3
"""crypto-tracker: fetch and display live crypto prices."""

import argparse
import requests
from rich.console import Console
from rich.table import Table

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
console = Console()

DEFAULT_COINS = ["bitcoin", "ethereum", "solana", "base"]


def fetch_prices(coin_ids: list[str], vs_currency: str = "usd") -> dict:
    """Fetch current prices from CoinGecko."""
    params = {
        "ids": ",".join(coin_ids),
        "vs_currencies": vs_currency,
        "include_24hr_change": "true",
    }
    resp = requests.get(COINGECKO_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def display_prices(data: dict, vs_currency: str = "usd") -> None:
    table = Table(title="Crypto Prices", show_header=True, header_style="bold cyan")
    table.add_column("Coin", style="bold white")
    table.add_column(f"Price ({vs_currency.upper()})", justify="right")
    table.add_column("24h Change", justify="right")

    for coin, info in data.items():
        price = info.get(vs_currency, 0)
        change = info.get(f"{vs_currency}_24h_change", 0) or 0
        change_str = f"{change:+.2f}%"
        color = "green" if change >= 0 else "red"
        table.add_row(
            coin.capitalize(),
            f"${price:,.2f}",
            f"[{color}]{change_str}[/{color}]",
        )
    console.print(table)


def main():
    parser = argparse.ArgumentParser(description="Fetch live crypto prices")
    parser.add_argument("coins", nargs="*", default=DEFAULT_COINS,
                        help="CoinGecko coin IDs (default: btc eth sol)")
    parser.add_argument("--currency", default="usd", help="Quote currency (default: usd)")
    args = parser.parse_args()

    try:
        data = fetch_prices(args.coins, args.currency)
        display_prices(data, args.currency)
    except requests.RequestException as e:
        console.print(f"[red]Error fetching prices: {e}[/red]")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
