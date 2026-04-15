import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

# ==========================================
# 1. DATA ACQUISITION & SETUP
# ==========================================
# Assets: Stocks (SPY), Long Bonds (TLT), Gold (GLD), Commodities (USO), Dollar (UUP)
tickers = ["SPY", "TLT", "GLD", "USO", "UUP"]
data = yf.download(tickers, start="2010-01-01")["Close"]
data = data.ffill().dropna()
returns = data.pct_change().dropna()

# ==========================================
# 2. SIGNAL GENERATION
# ==========================================
# 12-month momentum (252 days) adjusted for 1-month reversal (21 days)
momentum = data.pct_change(252) - data.pct_change(21)
# 60-day rolling volatility for risk-weighting
vol_rolling = returns.rolling(60).std() * np.sqrt(252)

# Risk-Adjusted Momentum Score
score = (momentum / vol_rolling).clip(lower=0)

# ==========================================
# 3. MONTHLY TACTICAL REBALANCING
# ==========================================
rebalance_dates = data.resample("ME").last().index
weights_list = []

for date in rebalance_dates:
    score_slice = score.loc[:date]
    if len(score_slice) < 1: continue
    
    # Get latest scores and normalize to weights
    latest_score = score_slice.iloc[-1]
    if latest_score.sum() > 0:
        w = latest_score / latest_score.sum()
    else:
        # Default to equal weight if no positive momentum
        w = pd.Series(1/len(tickers), index=tickers)
    weights_list.append((date, w))

weights = pd.DataFrame([w for _, w in weights_list], index=[d for d, _ in weights_list])
weights = weights.reindex(data.index, method="ffill").fillna(0)

# ==========================================
# 4. CRISIS-AWARE REGIME FILTER
# ==========================================
# If SPY is below 200MA, we exit risky assets and rotate to "Crisis Alpha" (TLT/GLD)
spy_ma200 = data["SPY"].rolling(200).mean()
is_risk_on = data["SPY"] > spy_ma200

# Define defensive rotation (50/50 Gold and Treasuries)
crisis_weights = pd.Series(0, index=tickers)
crisis_weights["TLT"] = 0.5
crisis_weights["GLD"] = 0.5

# Apply the regime switch
final_weights = weights.copy()
for i in range(len(final_weights)):
    if not is_risk_on.iloc[i]:
        final_weights.iloc[i] = crisis_weights

# ==========================================
# 5. VOLATILITY TARGETING (THE GAP CLOSER)
# ==========================================
# Calculate base strategy returns (with 1-day lag for execution realism)
raw_strategy_returns = (final_weights.shift(1) * returns).sum(axis=1)

# Target 15% Volatility (matches long-term S&P 500 risk)
target_vol = 0.15 
strat_vol_now = raw_strategy_returns.rolling(22).std() * np.sqrt(252)
leverage = (target_vol / strat_vol_now).fillna(1.0).clip(0.5, 2.0)

# Apply dynamic scaling
leveraged_returns = raw_strategy_returns * leverage.shift(1)

# ==========================================
# 6. PERFORMANCE CALCULATIONS
# ==========================================
def calculate_metrics(rets):
    cum_rets = (1 + rets).cumprod()
    ann_return = (1 + rets.mean())**252 - 1
    ann_vol = rets.std() * np.sqrt(252)
    sharpe = (ann_return - 0.02) / ann_vol  # 2% Risk-free rate assumption
    drawdown = (cum_rets / cum_rets.cummax() - 1)
    return cum_rets, ann_return, ann_vol, sharpe, drawdown

strat_cum, strat_ret, strat_v, strat_s, strat_dd = calculate_metrics(leveraged_returns)
spy_cum, spy_ret, spy_v, spy_s, spy_dd = calculate_metrics(returns["SPY"])

# ==========================================
# 7. FINAL VISUALIZATION
# ==========================================
plt.style.use('seaborn-v0_8-muted')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True, gridspec_kw={'height_ratios': [3, 1]})

# Main Equity Curve
ax1.plot(strat_cum, label=f"Crisis-Aware Strategy (Sharpe: {strat_s:.2f})", color='#1f77b4', lw=2)
ax1.plot(spy_cum, label=f"S&P 500 (Sharpe: {spy_s:.2f})", color='#ff7f0e', alpha=0.6)
ax1.set_title("Tactical Crisis Alpha vs. S&P 500 Buy & Hold", fontsize=14, fontweight='bold')
ax1.set_ylabel("Growth of $1")
ax1.legend(loc='upper left')
ax1.grid(alpha=0.3)

# Drawdown Shading
ax2.fill_between(strat_dd.index, strat_dd * 100, 0, color='#1f77b4', alpha=0.4, label="Strategy Drawdown")
ax2.fill_between(spy_dd.index, spy_dd * 100, 0, color='#ff7f0e', alpha=0.2, label="SPY Drawdown")
ax2.set_title("Drawdown Intensity (%)", fontsize=12)
ax2.set_ylabel("Depth (%)")
ax2.set_ylim(-40, 0)
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.show()

print(f"--- STRATEGY PERFORMANCE ---")
print(f"Ann. Return: {strat_ret:.2%}")
print(f"Max Drawdown: {strat_dd.min():.2%}")
print(f"Sharpe Ratio: {strat_s:.2f}")
