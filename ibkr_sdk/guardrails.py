import json
import os
import logging

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "max_order_value_usd": 5000,
    "max_daily_drawdown_pct": -4.0,
    "allowed_symbols": ["AAPL", "MSFT", "GOOG", "VOO", "SPY", "TSLA", "VRT"]
}

class Guardrails:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            with open(self.config_path, "w") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            return DEFAULT_CONFIG
        
        with open(self.config_path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                logger.error("Failed to parse config.json, using defaults.")
                return DEFAULT_CONFIG

    def validate_order(self, symbol, action, quantity, price):
        # 1. Symbol whitelist check
        allowed_symbols = self.config.get("allowed_symbols", [])
        if allowed_symbols and symbol not in allowed_symbols:
            return False, f"Guardrail Violation: Symbol {symbol} is not in the allowed list."

        # 2. Max Order Value check
        max_value = self.config.get("max_order_value_usd", 5000)
        order_value = quantity * price
        if order_value > max_value:
            return False, f"Guardrail Violation: Order value ${order_value:.2f} exceeds maximum allowed (${max_value})."

        return True, "Order passed local guardrails."

    def check_daily_drawdown(self, net_liq, day_pnl):
        max_drawdown = self.config.get("max_daily_drawdown_pct", -4.0)
        if net_liq <= 0:
            return True, "No drawdown check possible."

        drawdown_pct = (day_pnl / net_liq) * 100
        if drawdown_pct < max_drawdown:
            return False, f"Kill-Switch Triggered: Daily Drawdown ({drawdown_pct:.2f}%) exceeds limit ({max_drawdown}%)."
        
        return True, "Drawdown is within safe limits."
