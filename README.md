# Tactical-Asset-Allocation-Crisis-Alpha
Systematic Multi-Asset Tactical Allocation strategy in Python. Features risk-adjusted momentum, regime-switching, and crisis-alpha rotation. Sharpe: 1.07.

This repository implements a Regime-Adaptive Tactical Asset Allocation (TAA) framework. The strategy utilizes risk-adjusted momentum and a systematic "Crisis-Alpha" rotation engine to outperform the S&P 500 while significantly reducing tail risk during market shocks.

Metric,             Tactical Strategy,     S&P 500 (SPY)
Annualized Return,       18.27%,               ~12.5%
Sharpe Ratio,             1.07,                 0.79
Max Drawdown,            -23.88%,             -33.72%

Methodology
1. Signal Logic (Momentum & Mean Reversion)
The core alpha is derived from a hybrid signal:
Momentum: A 12-month lookback captures persistent trends.
Reversion: A 1-month short-term reversal filter prevents "buying the top" of an overextended move.
Weighting: Assets are weighted by their Return-to-Volatility ratio, ensuring the risk budget is balanced across SPY, TLT, GLD, USO, and UUP.

2. The Crisis-Alpha Rotation
Unlike traditional "Risk-Off" strategies that move to 0% cash, this model actively seeks Convexity. When the S&P 500 falls below its 200-day Moving Average:

The model liquidates equity-heavy positions.It rotates into a 50/50 split of Long-Term Treasuries (TLT) and Gold (GLD).This creates a "Flight-to-Quality" hedge that often generates positive returns while the market bleeds.

3. Volatility Targeting
To ensure an apples-to-apples comparison with the S&P 500, the strategy utilizes dynamic scaling. Target Vol: 15% (Annualized).
Execution: The model calculates current realized volatility and applies a leverage factor (capped at 2.0x) to maintain a consistent risk profile.

🛡️ Robustness & Overfitting Check

To mitigate the risk of "backtest overfitting," a Sensitivity Analysis was performed across various lookback parameters (150-250 days).
The "bundle" effect in the chart above confirms that the strategy's edge is a result of robust structural market anomalies rather than hyper-parameter tuning.
