# SolVault: Locking in Profits on Solana

This repository contains the **SolVault Bounty project**, an advanced trading platform built on Solana, leveraging Jupiter’s liquidity to offer pro trader features like OCO (One-Cancels-the-Other) orders, percentage-based trailing stops, and risk management. SolVault integrates with Jupiter’s API (station.jup.ag/docs/old/apis/swap-api) to simulate real-time price tracking and trade execution on Solana.

## Features

- **Unified Dashboard**: Real-time tracking for spot and perpetual (perp) trading on Solana via Jupiter.
- **Advanced Orders**: Limit orders, OCO orders, percentage-based trailing stops (supports both long and short positions), and bracket orders (stop loss + take profit).
- **Risk Management**: Built-in risk-reward calculator and portfolio tracking with dynamic position updates.
- **Error Handling**: Robust validation for user inputs, API failures, and trade execution (e.g., insufficient liquidity, invalid amounts).
- **Jupiter API Integration**: Simulates Jupiter’s `/quote` and `/swap` endpoints for price quotes and trade execution, adhering to Solana’s high-speed, low-cost transactions.

## Planned Enhancements

- Real-time price feed integration with Solana oracles/Jupiter API (requires API key).
- Multi-asset support for trading different tokens (e.g. SOL, JUP, USDC) on Solana.
- Backtesting feature for historical price data and strategy testing.
- Command-line interface (CLI) or web-based dashboard for improved user experience.
- Dynamic liquidity pool simulation based on market activity.
- Secure user authentication with password hashing (e.g., bcrypt).

## Setup

1. **Clone the Repository**:

   ```sh
   git clone https://github.com/Kvngsw/solvault-bty.git
   cd solvault-bounty
   ```

2. **Create and Activate a Virtual Environment**:

   macOS/Linux:

   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   Windows:

   ```sh
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```sh
   pip install -r requirements.txt
   ```

4. **Run the Script**:

   ```sh
   python solvault.py
   ```

## Requirements

- Python 3.9 or higher
- random==3.9, 
- typing==3.7.4.3,
- requests==2.31.0 (for optional Jupiter API simulation)

## Contact

**Name:** Xerxes III\
**Email:** [dee.makindee.dev@gmail.com](mailto:dee.makindee.dev@gmail.com)

## Team Background

Developed by an experienced developer focused on Solana blockchain projects. Current works include a superfast copytrading tool, a memecoin sniping tool, a whale wallet tracking tool, a token sniffing tool, and a memecoin analyzer to scout new promising plays and lock in profits. This expertise ensures SolVault’s robust design and Jupiter/Solana integration.

## Submission Links

Slide Deck: [https://drive.google.com/file/d/1feMLn2-T9LpezMfJS8wPHX2bVIcRetzO/view?usp=drive_link]
Supplementary Doc: [https://drive.google.com/file/d/1ei9BssVsl8G5sDGOUxw581ooKmWQhlpy/view?usp=drivesdk] 

## Testing

The repository includes basic unit tests in solvault.py (run with python -c "import solvault; solvault.__test__"). These tests verify core functionality like user registration, order placement, risk-reward calculation, and trailing stop logic for both long and short positions. Expand these tests or add new ones to verify functionality under different scenarios.

```

Contribution

If you'd like to contribute, feel free to fork the repository and submit a pull request. Please follow PEP 8 and include tests for new features.

```

```

```
