#!/usr/bin/env python3
"""Price alert engine: notify when a coin crosses a threshold."""

import json
import time
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Literal
from rich.console import Console
from tracker import fetch_prices

ALERTS_FILE = Path("alerts.json")
POLL_INTERVAL = 60  # seconds
console = Console()
logger = logging.getLogger(__name__)


@dataclass
class PriceAlert:
    coin_id: str
    threshold: float
    direction: Literal["above", "below"]
    currency: str = "usd"
    triggered: bool = False

    def check(self, current_price: float) -> bool:
        if self.triggered:
            return False
        if self.direction == "above" and current_price >= self.threshold:
            return True
        if self.direction == "below" and current_price <= self.threshold:
            return True
        return False


def load_alerts() -> list[PriceAlert]:
    if ALERTS_FILE.exists():
        with open(ALERTS_FILE) as f:
            return [PriceAlert(**a) for a in json.load(f)]
    return []


def save_alerts(alerts: list[PriceAlert]) -> None:
    with open(ALERTS_FILE, "w") as f:
        json.dump([asdict(a) for a in alerts], f, indent=2)


def add_alert(coin_id: str, threshold: float, direction: str, currency: str = "usd") -> None:
    alerts = load_alerts()
    alerts.append(PriceAlert(coin_id, threshold, direction, currency))
    save_alerts(alerts)
    console.print(
        f"[green]Alert added: {coin_id} {direction} ${threshold:,.2f} {currency.upper()}[/green]"
    )


def run_alert_loop() -> None:
    console.print("[cyan]Starting alert monitor (Ctrl+C to stop)...[/cyan]")
    while True:
        alerts = load_alerts()
        pending = [a for a in alerts if not a.triggered]
        if not pending:
            console.print("[yellow]No active alerts. Add some with add_alert().[/yellow]")
            break

        coins = list({a.coin_id for a in pending})
        try:
            prices = fetch_prices(coins)
        except Exception as e:
            logger.error(f"Price fetch failed: {e}")
            time.sleep(POLL_INTERVAL)
            continue

        changed = False
        for alert in pending:
            price = prices.get(alert.coin_id, {}).get(alert.currency, 0)
            if alert.check(price):
                alert.triggered = True
                changed = True
                console.print(
                    f"[bold yellow]🔔 ALERT: {alert.coin_id.upper()} is "
                    f"{alert.direction} ${alert.threshold:,.2f} "
                    f"(current: ${price:,.2f})[/bold yellow]"
                )

        if changed:
            save_alerts(alerts)

        time.sleep(POLL_INTERVAL)
