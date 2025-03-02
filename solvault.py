import time
from typing import Dict, List, Optional
import random
from dataclasses import dataclass


@dataclass
class Position:
    """Represents an open trading position on SolVault."""
    type: str
    amount: float
    entry_price: float
    current_value: float

    def update_value(self, current_price: float) -> None:
        """Updates the current value of the position based on market price."""
        self.current_value = self.amount * current_price


class JupiterAPI:
    """Simulates Jupiter's API for price tracking and trade execution on Solana."""
    def __init__(self) -> None:
        self.current_price = 100.0  # Starting price for the simulated asset
        self.liquidity_pool = 10000.0  # Simulated liquidity pool in USD

    def get_price(self) -> float:
        """Simulates fetching the current price from Jupiter's API."""
        # Simulate price fluctuations
        self.current_price += random.uniform(-1.5, 1.5)
        return self.current_price

    def execute_trade(self, amount: float, price: float, trade_type: str) -> bool:
        """Simulates executing a trade using Jupiter's API."""
        if not isinstance(amount, (int, float)) or amount == 0:
            raise ValueError("Trade amount must be a non-zero number.")
        if price <= 0:
            raise ValueError("Price must be positive.")
        if self.liquidity_pool < abs(amount) * price:
            raise ValueError("Insufficient liquidity in the pool.")
        self.liquidity_pool -= abs(amount) * price
        print(f"Trade executed: {amount} {trade_type} at {price}")
        return True


class SolVault:
    """SolVault trading platform, leveraging Jupiter's API on Solana."""
    def __init__(self) -> None:
        self.users: Dict[str, Dict] = {}
        self.jupiter = JupiterAPI()
        self.orders: List[Dict] = []

    def register(self, username: str, password: str, initial_balance: float = 1000.0) -> None:
        """Registers a new user on SolVault."""
        self._validate_username(username)
        self._validate_password(password)
        self._validate_balance(initial_balance)

        if username in self.users:
            raise ValueError("Username already exists.")

        self.users[username] = {
            "password": password,  # Note: In production, use hashing (e.g., bcrypt)
            "balance": initial_balance,
            "positions": [],  # List of Position objects
            "orders": [],
            "portfolio_history": []  # Track balance and positions over time
        }
        print(f"Registered {username} with balance {initial_balance} on SolVault")

    def login(self, username: str, password: str) -> bool:
        """Logs in a user to SolVault."""
        self._validate_username(username)
        self._validate_password(password)

        if username not in self.users or self.users[username]["password"] != password:
            raise ValueError("Invalid credentials.")

        print(f"Logged in as {username} on SolVault")
        return True

    def calculate_risk_reward(self, entry_price: float, stop_loss: float, take_profit: float) -> float:
        """Calculates the risk-reward ratio for a trade."""
        self._validate_prices(entry_price, stop_loss, take_profit)

        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        if risk == 0:
            raise ValueError("Risk cannot be zero.")
        return reward / risk

    def place_order(self, username: str, trade_type: str, amount: float, limit_price: float,
                stop_loss: Optional[float] = None, take_profit: Optional[float] = None,
                trailing_stop: bool = False, trailing_percent: float = 1.0) -> bool:
        """Places an advanced order on SolVault."""
        self._validate_username(username)
        self._validate_trade_type(trade_type)
        self._validate_amount(amount)
        self._validate_limit_price(limit_price)
        self._validate_stop_loss(stop_loss)
        self._validate_take_profit(take_profit)
        self._validate_trailing_stop(trailing_stop, trailing_percent)

        user = self.users[username]
        current_price = self.jupiter.get_price()

        if user["balance"] < abs(amount) * current_price:
            raise ValueError("Insufficient balance for the order.")

        rr_ratio = None
        if stop_loss and take_profit:
            rr_ratio = self.calculate_risk_reward(current_price, stop_loss, take_profit)

        order = {
            "username": username,
            "type": trade_type,
            "amount": amount,
            "limit_price": limit_price,
            "stop_loss": stop_loss,
            "trailing_stop": trailing_stop,
            "trail_percent": trailing_percent if trailing_stop else None,
            "take_profit": take_profit,
            "oco": stop_loss is not None and take_profit is not None,
            "active": True,
            "entry_price": None,
            "rr_ratio": rr_ratio
        }
        self.orders.append(order)
        user["orders"].append(order)
        print(
            f"Placed {trade_type} order on SolVault: Amount={amount}, "
            f"Limit={limit_price}, SL={stop_loss}, TP={take_profit}, "
            f"Trailing={trailing_stop} ({trailing_percent}%)"
        )
        return True

    def close_position(self, username: str, position_index: int) -> bool:
        """Closes a position for a user."""
        self._validate_username(username)
        user = self.users[username]

        if not 0 <= position_index < len(user["positions"]):
            raise ValueError("Invalid position index.")

        position = user["positions"][position_index]
        current_price = self.jupiter.get_price()
        position.update_value(current_price)
        profit_loss = position.current_value - (position.amount * position.entry_price)
        user["balance"] += position.current_value
        del user["positions"][position_index]
        print(f"Closed position for {username}: Profit/Loss = {profit_loss:.2f}")
        return True

    def update_positions(self) -> None:
        """Updates the current value of all open positions based on the latest market price."""
        current_price = self.jupiter.get_price()
        for user in self.users.values():
            for position in user["positions"]:
                position.update_value(current_price)

    def update_trailing_stop(self, order: Dict, current_price: float) -> None:
        """Updates a trailing stop order based on the current price."""
        if not order["trailing_stop"] or not order["active"] or not order["entry_price"]:
            return

        trail_distance = current_price * (order["trail_percent"] / 100)
        if order["amount"] > 0:  # Long position
            max_price = max(order["entry_price"], current_price)
            new_stop_loss = max_price - trail_distance
            if new_stop_loss > order["stop_loss"] or order["stop_loss"] is None:
                order["stop_loss"] = new_stop_loss
                print(f"Trailing stop updated to {order['stop_loss']:.2f} (long)")
        else:  # Short position
            min_price = min(order["entry_price"], current_price)
            new_stop_loss = min_price + trail_distance
            if new_stop_loss < order["stop_loss"] or order["stop_loss"] is None:
                order["stop_loss"] = new_stop_loss
                print(f"Trailing stop updated to {order['stop_loss']:.2f} (short)")

    def check_market_and_execute(self) -> None:
        """Checks market conditions and executes orders."""
        current_price = self.jupiter.get_price()
        self.update_positions()
        print(f"Current price: {current_price:.2f} | Liquidity: {self.jupiter.liquidity_pool:.2f}")

        for order in self.orders:
            if not order["active"]:
                continue

            user = self.users[order["username"]]
            target_hit = (order["amount"] > 0 and current_price >= order["limit_price"]) or \
                        (order["amount"] < 0 and current_price <= order["limit_price"])
            stop_hit = order["stop_loss"] and current_price <= order["stop_loss"]
            profit_hit = order["take_profit"] and current_price >= order["take_profit"]

            if target_hit:
                try:
                    if self.jupiter.execute_trade(order["amount"], current_price, order["type"]):
                        order["entry_price"] = current_price
                        user["positions"].append(Position(
                            type=order["type"],
                            amount=order["amount"],
                            entry_price=current_price,
                            current_value=order["amount"] * current_price
                        ))
                        user["balance"] -= abs(order["amount"] * current_price)
                        print(f"Executed {order['type']} order for {order['username']} at {current_price}")
                        if not (order["stop_loss"] or order["take_profit"]):
                            order["active"] = False
                except ValueError as e:
                    print(f"Order execution failed: {e}")
                    order["active"] = False

            if order["entry_price"] and order["trailing_stop"]:
                self.update_trailing_stop(order, current_price)

            if order["entry_price"] and (stop_hit or profit_hit):
                if order["oco"]:
                    action = "stop loss" if stop_hit else "take profit"
                    user["balance"] += abs(order["amount"] * current_price)
                    order["active"] = False
                    print(f"OCO triggered {action} for {order['username']} at {current_price}")
                elif stop_hit:
                    user["balance"] += abs(order["amount"] * current_price)
                    order["active"] = False
                    print(f"Stop loss triggered for {order['username']} at {current_price}")
                elif profit_hit:
                    user["balance"] += abs(order["amount"] * current_price)
                    order["active"] = False
                    print(f"Take profit triggered for {order['username']} at {current_price}")

            user["portfolio_history"].append({
                "time": time.time(),
                "balance": user["balance"],
                "positions_value": sum(p.current_value for p in user["positions"])
            })

    def dashboard(self, username: str) -> None:
        """Displays the SolVault dashboard for a user."""
        self._validate_username(username)

        if username not in self.users:
            raise ValueError("User not found.")

        user = self.users[username]
        total_value = user["balance"] + sum(p.current_value for p in user["positions"])
        print(f"\n=== SolVault Dashboard for {username} ===")
        print(f"Balance: {user['balance']:.2f}")
        print(f"Positions: {user['positions']}")
        print(f"Active Orders: {len(user['orders'])}")
        print(f"Portfolio Value: {total_value:.2f}")
        if user["portfolio_history"]:
            print(
                f"Latest Portfolio Update: Balance={user['portfolio_history'][-1]['balance']:.2f}, "
                f"Positions Value={user['portfolio_history'][-1]['positions_value']:.2f}"
            )
        print("====================\n")

    def _validate_username(self, username: str) -> None:
        """Validates the username."""
        if not isinstance(username, str) or not username.strip():
            raise ValueError("Username must be a non-empty string.")

    def _validate_password(self, password: str) -> None:
        """Validates the password."""
        if not isinstance(password, str) or not password.strip():
            raise ValueError("Password must be a non-empty string.")

    def _validate_balance(self, balance: float) -> None:
        """Validates the initial balance."""
        if not isinstance(balance, (int, float)) or balance < 0:
            raise ValueError("Initial balance must be a non-negative number.")

    def _validate_trade_type(self, trade_type: str) -> None:
        """Validates the trade type."""
        if trade_type not in ["spot", "perp"]:
            raise ValueError("Trade type must be 'spot' or 'perp'.")

    def _validate_amount(self, amount: float) -> None:
        """Validates the trade amount."""
        if not isinstance(amount, (int, float)) or amount == 0:
            raise ValueError("Amount must be a non-zero number.")

    def _validate_limit_price(self, limit_price: float) -> None:
        """Validates the limit price."""
        if not isinstance(limit_price, (int, float)) or limit_price <= 0:
            raise ValueError("Limit price must be a positive number.")

    def _validate_stop_loss(self, stop_loss: Optional[float]) -> None:
        """Validates the stop loss."""
        if stop_loss is not None and (not isinstance(stop_loss, (int, float)) or stop_loss <= 0):
            raise ValueError("Stop loss, if provided, must be a positive number.")

    def _validate_take_profit(self, take_profit: Optional[float]) -> None:
        """Validates the take profit."""
        if take_profit is not None and (not isinstance(take_profit, (int, float)) or take_profit <= 0):
            raise ValueError("Take profit, if provided, must be a positive number.")

    def _validate_trailing_stop(self, trailing_stop: bool, trailing_percent: float) -> None:
        """Validates the trailing stop parameters."""
        if not isinstance(trailing_stop, bool):
            raise ValueError("Trailing stop must be a boolean.")
        if not isinstance(trailing_percent, (int, float)) or trailing_percent <= 0:
            raise ValueError("Trailing percent must be a positive number.")

    def _validate_prices(self, entry_price: float, stop_loss: float, take_profit: float) -> None:
        """Validates the prices for risk-reward calculation."""
        if not all(isinstance(x, (int, float)) for x in [entry_price, stop_loss, take_profit]):
            raise ValueError("Prices must be numbers.")
        if entry_price <= 0 or stop_loss <= 0 or take_profit <= 0:
            raise ValueError("Prices must be positive.")


if __name__ == "__main__":
    try:
        sol_vault = SolVault()
        sol_vault.register("protrader", "pass456", 5000.0)
        sol_vault.login("protrader", "pass456")

        # Place a long position with a trailing stop
        sol_vault.place_order("protrader", "perp", 10.0, 102.0, stop_loss=98.0,
                            take_profit=110.0, trailing_stop=True, trailing_percent=2.0)

        # Place a short position
        sol_vault.place_order("protrader", "perp", -5.0, 98.0, stop_loss=102.0,
                            take_profit=95.0, trailing_stop=True, trailing_percent=2.0)

        for _ in range(15):
            sol_vault.check_market_and_execute()
            sol_vault.dashboard("protrader")
            time.sleep(1)

        # Close a position (e.g., first position)
        sol_vault.close_position("protrader", 0)
    except ValueError as e:
        print(f"Error: {e}")
