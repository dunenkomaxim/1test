#!/usr/bin/env python3
"""Portfolio manager: track token holdings and compute total value."""

import json
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from tracker import fetch_prices

PORTFOLIO_FILE = Path(os.getenv("PORTFOLIO_PATH", "portfolio.json"))
console = Console()


def load_portfolio() -> dict:
    if PORTFOLIO_FILE.exists():
        with open(PORTFOLIO_FILE) as f:
            return json.load(f)
    return {}


def save_portfolio(portfolio: dict) -> None:
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=2)
    console.print(f"[green]Portfolio saved to {PORTFOLIO_FILE}[/green]")


def add_holding(coin_id: str, amount: float) -> None:
    portfolio = load_portfolio()
    portfolio[coin_id] = portfolio.get(coin_id, 0) + amount
    save_portfolio(portfolio)
    console.print(f"[cyan]Added {amount} {coin_id} to portfolio[/cyan]")


def remove_holding(coin_id: str) -> None:
    portfolio = load_portfolio()
    if coin_id in portfolio:
        del portfolio[coin_id]
        save_portfolio(portfolio)
    else:
        console.print(f"[yellow]{coin_id} not found in portfolio[/yellow]")


def show_portfolio(vs_currency: str = "usd") -> None:
    portfolio = load_portfolio()
    if not portfolio:
        console.print("[yellow]Portfolio is empty. Use 'add' to track coins.[/yellow]")
        return

    prices = fetch_prices(list(portfolio.keys()), vs_currency)

    table = Table(title="My Portfolio", header_style="bold magenta")
    table.add_column("Coin", style="bold white")
    table.add_column("Holdings", justify="right")
    table.add_column(f"Price ({vs_currency.upper()})", justify="right")
    table.add_column("Value", justify="right", style="bold")
    table.add_column("24h Change", justify="right")

    total = 0.0
    for coin, amount in portfolio.items():
        info = prices.get(coin, {})
        price = info.get(vs_currency, 0)
        change = info.get(f"{vs_currency}_24h_change", 0) or 0
        value = amount * price
        total += value
        color = "green" if change >= 0 else "red"
        table.add_row(
            coin.capitalize(),
            f"{amount:.4f}",
            f"${price:,.2f}",
            f"${value:,.2f}",
            f"[{color}]{change:+.2f}%[/{color}]",
        )

    console.print(table)
    console.print(f"\n[bold]Total portfolio value: ${total:,.2f} {vs_currency.upper()}[/bold]")
