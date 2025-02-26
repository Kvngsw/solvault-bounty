import time
from typing import Dict, List, Optional
import random


class JupiterAPI:
    
    
    """Simulates Jupiter's API for price tracking and trade execution on Solana."""
    def __init__(self):
        self.current_price = 100.0  # Starting Jupiter-based asset price on Solana
        self.liquidity_pool = 10000.0  # Simulated Jupiter liquidity in USD

    def get_price(self):
        """Simulates Jupiter price fluctuations on Solana."""
        self.current_price += random.uniform(-1.5, 1.5)
        return self.current_price

    def execute_trade(self, amount: float, price: float, trade_type: str):
        """Executes a trade if liquidity is available, simulating Jupiter on Solana."""
        if self.liquidity_pool >= amount * price:
            self.liquidity_pool -= amount * price
            return True
        return False


class SolVault:
    
    
    """SolVault trading platform, leveraging Jupiter's API on Solana for advanced trading
    features."""
    def __init__(self):
        self.users: Dict[str, Dict] = {}
        self.jupiter = JupiterAPI()
        self.orders: List[Dict] = []

    def register(self, username: str, password: str, initial_balance: float = 1000.0):
        """Registers a new user on SolVault with an initial balance."""
        if username in self.users:
            print("Error: Username already exists.")
            return False
        self.users[username] = {
            "password": password,
            "balance": initial_balance,
            "positions": [],  # List of {type: spot/perp, amount, entry_price, current_value}
            "orders": [],
            "portfolio_history": []  # Track balance and positions over time
        }
        print(f"Registered {username} with balance {initial_balance} on SolVault")
        return True

    def login(self, username: str, password: str):
        """Logs in a user to SolVault."""
        if username in self.users and self.users[username]["password"] == password:
            print(f"Logged in as {username} on SolVault")
            return True
        print("Error: Invalid credentials.")
        return False

    def calculate_risk_reward(self, entry_price: float, stop_loss: float, take_profit: float):
        """Calculates risk-reward ratio for an order on SolVault."""
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        if risk == 0:
            return 0
        return reward / risk

    def place_order(self, username: str, trade_type: str, amount: float, limit_price: float,
                    stop_loss: Optional[float] = None, take_profit: Optional[float] = None,
                    trailing_stop: bool = False, trailing_percent: float = 1.0):
        """Places an advanced order on SolVault using Jupiter's API on Solana."""
        if username not in self.users:
            print("Error: User not found.")
            return False

        user = self.users[username]
        current_price = self.jupiter.get_price()
        if user["balance"] < amount * current_price:
            print("Error: Insufficient balance.")
            return False

        rr_ratio = self.calculate_risk_reward(current_price, stop_loss or current_price,
                                            take_profit or current_price) if stop_loss and take_profit else None

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
            f"Placed {trade_type} order on SolVault via Jupiter: Amount={amount}, "
            f"Limit={limit_price}, SL={stop_loss}, TP={take_profit}, "
            f"Trailing={trailing_stop} ({trailing_percent}%)"
        )
        return True

    def update_trailing_stop(self, order: Dict, current_price: float):
        """Updates a trailing stop order on SolVault based on a percentage of the current
        price."""
        if not order["trailing_stop"] or not order["active"] or not order["entry_price"]:
            return

        trail_distance = current_price * (order["trail_percent"] / 100)  # Convert % to price distance
        max_price = max(order["entry_price"], current_price)  # Track the highest price reached

        # Adjust stop loss to trail the max price by the percentage distance
        new_stop_loss = max_price - trail_distance
        if new_stop_loss > order["stop_loss"]:  # Only move stop loss up (for long positions)
            order["stop_loss"] = new_stop_loss
            print(
                f"Trailing stop updated to {order['stop_loss']:.2f} for {order['username']} "
                f"(trail: {order['trail_percent']}%)"
            )

    def check_market_and_execute(self):
        """Checks market conditions and executes orders on SolVault via Jupiter on Solana."""
        current_price = self.jupiter.get_price()
        print(
            f"Current price on SolVault via Jupiter: {current_price:.2f} | "
            f"Liquidity: {self.jupiter.liquidity_pool:.2f}"
        )

        for order in self.orders:
            if not order["active"]:
                continue

            user = self.users[order["username"]]
            target_hit = (order["amount"] > 0 and current_price >= order["limit_price"]) or \
                        (order["amount"] < 0 and current_price <= order["limit_price"])
            stop_hit = order["stop_loss"] and current_price <= order["stop_loss"]
            profit_hit = order["take_profit"] and current_price >= order["take_profit"]

            if target_hit and self.jupiter.execute_trade(order["amount"], current_price, order["type"]):
                order["entry_price"] = current_price
                user["positions"].append({"type": order["type"], "amount": order["amount"],
                                        "entry_price": current_price,
                                        "current_value": order["amount"] * current_price})
                user["balance"] -= order["amount"] * current_price
                print(
                    f"Executed {order['type']} limit order for {order['username']} on SolVault "
                    f"at {current_price}"
                )
                if not (order["stop_loss"] or order["take_profit"]):
                    order["active"] = False

            if order["entry_price"] and order["trailing_stop"]:
                self.update_trailing_stop(order, current_price)

            if order["entry_price"] and (stop_hit or profit_hit):
                if order["oco"]:
                    action = "stop loss" if stop_hit else "take profit"
                    user["balance"] += order["amount"] * current_price
                    order["active"] = False
                    print(
                        f"OCO triggered {action} for {order['username']} on SolVault at "
                        f"{current_price}"
                    )
                elif stop_hit:
                    user["balance"] += order["amount"] * current_price
                    order["active"] = False
                    print(
                        f"Stop loss triggered for {order['username']} on SolVault at "
                        f"{current_price}"
                    )
                elif profit_hit:
                    user["balance"] += order["amount"] * current_price
                    order["active"] = False
                    print(
                        f"Take profit triggered for {order['username']} on SolVault at "
                        f"{current_price}"
                    )

            user["portfolio_history"].append({"time": time.time(), "balance": user["balance"],
                                            "positions_value": sum(p["current_value"] for p in
                                                                user["positions"])})

    def dashboard(self, username: str):
        """Displays the SolVault dashboard for a user, showing balances and orders."""
        if username not in self.users:
            print("Error: User not found.")
            return
        user = self.users[username]
        total_value = user["balance"] + sum(p["current_value"] for p in user["positions"])
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


if __name__ == "__main__":
    sol_vault = SolVault()
    sol_vault.register("protrader", "pass456", 5000.0)
    sol_vault.login("protrader", "pass456")

    # Place a Jupiter/Solana perp order with a 2% trailing stop
    sol_vault.place_order("protrader", "perp", 10.0, 102.0, stop_loss=98.0, take_profit=110.0,
                        trailing_stop=True, trailing_percent=2.0)

    for _ in range(15):
        sol_vault.check_market_and_execute()
        sol_vault.dashboard("protrader")
        time.sleep(1)
        