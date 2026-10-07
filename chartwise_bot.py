#!/usr/bin/env python3
"""
Chartwise Bot v10.1  Crypto-Only High-Probability SMC/ICT + EMA Signal Bot
Pairs: BTC/USD, SOL/USD, XRP/USD only.
v9.0 milestone upgrades:
  1. Multi-timeframe signal consensus (5m/15m/1H) with +2/+3 bonus scoring
  2. Signal confidence decay  auto-expire stale setups after 2 cooldown period
  3. !stats command  comprehensive performance dashboard
  4. Score normalization display  "Score: X / ~Y potential" in signal embeds
  5. !sensitivity [1-5] command  dynamic signal strictness control
  6. Circuit breaker auto-recovery  lifts pause early on confirmed WIN
  7. All footers, docstring, and version references updated to v9.0
v9.1 milestone upgrades:
  1. Premium signal watchlist  near-miss signals stored, alerts when entry price touched
  2. !targets [pair]  key price targets above/below (S/R, Fib, pivot, OB)
  3. Trade journal embed  comprehensive entry/exit summary sent on trade close
  4. !pa [pair]  pure price action summary (candle colors, swing H/L, structure)
  5. Adaptive SL multiplier  1.2 Trending, 0.8 Ranging, 1.5 BB squeeze
  6. !debug [pair]  developer scoring breakdown (raw score, penalties, patterns)
  7. All footers, docstring, and version references updated to v9.1
v9.2 milestone upgrades:
  1. !pairs add validation  Coinbase candle-fetch check before adding pair; input normalization
  2. Candle pattern streak tracking   "on fire" bonus when same pattern fires 3 in a row
  3. !patterns command  win rates for all pattern groups in formatted embed
  4. !hours command  performance broken down by UTC hour with emoji bars
  5. Liquidity sweep clean/dirty detection  clean sweep (wick only) = +2, dirty = +1
  6. !edge command  statistical edge calculator with expectancy and significance guidance
  7. All footers, docstring, and version references updated to v9.2
v9.4 milestone upgrades:
  1. !calendar [week|month] command  trading activity calendar view (Mon-Sun or full month)
  2. Volatility regime detection  detect_volatility_regime() helper, shown in !brief + signal embeds
  3. !scoretable command  reference card of all scoring factors and point values
  4. Multi-pair signal coordination   Wave Alert when 2+ pairs signal within 30 seconds
  5. !copy [pair] [ratio] command  copy trading size calculator at a fraction of bot's sizing
  6. Better !help organization  commands grouped into 5 categories with bold headers
  7. All footers, docstring, and version references updated to v9.4
v9.4 milestone upgrades:
  1. !correlation command  Pearson rolling correlation BTC/SOL and BTC/XRP (20 4H candles)
  2. Price alert system  !alert [pair] [price] [above|below] with PRICE_ALERTS store + auto-trigger
  3. Enhanced !status  comprehensive bot health dashboard (scan interval, signals today/yesterday, win rate, alerts count, circuit breaker)
  4. !close [pair] command  manually close an active trade with confirmation, PnL calc, log_outcome()
  5. OB stacking detection  +2 bonus when two OBs within 1% of each other (20c and 50c lookback)
  6. !top [n] command  N highest-scoring signals from SIGNAL_LOG with outcome info
  7. All footers, docstring, and version references updated to v9.4
v9.5 milestone upgrades:
  1. !backtest2 [pair] [days]  enhanced backtest on real 15m candles: Sharpe ratio, profit factor, max consec wins/losses
  2. TWAP display  calc_twap() helper; shown in !snapshot and !brief alongside VWAP with bullish/bearish context
  3. !montecarlo [n_sims]  Monte Carlo simulation of next 50 trades from TRADE_HISTORY stats
  4. Choppiness Index scoring  calc_choppiness_index() in analyze(); CI>61.8  penalty, CI<38.2  bonus; shown in !brief
  5. !add [pair] [entry] [sl] [t1] [t2] [direction]  manually add a trade to active_trades
  6. Signal score percentile  shows where current signal ranks vs last 50 in SIGNAL_LOG
  7. All footers, docstring, and version references updated to v9.5
v9.6 milestone upgrades:
  1. !optimize command  automated MIN_SCORE threshold optimizer; tests values 6-14, shows EV table, recommends optimal
  2. Donchian Channel scoring  calc_donchian_channel() helper; breakout above upper (long) or below lower (short) = +1
  3. !levels enhancement  adds Donchian Channel, Keltner Channel, VWAP/TWAP, and today's H/L
  4. Range expansion scoring  detect_range_expansion() helper; expansion in signal direction = +1, against = -1
  5. !volatility [pair]  comprehensive volatility breakdown: ATR on all TFs, CI, BB width, squeeze, regime, hist vol
  6. EMA ribbon scoring  calc_ema_ribbon() with EMA5/8/13/21; fully aligned = +2, partial (3/4) = +1
  7. !ema [pair]  EMA ribbon status across all 4 timeframes with visual alignment indicators
  8. All footers, docstring, and version references updated to v9.6
v9.7 milestone upgrades:
  1. ICT Optimal Trade Entry (OTE) detection  detect_ote_zone() helper; +2 score in 61.8-79% Fib zone after MSS
  2. !ote [pair] command  shows OTE zone for each pair on 15m/1H; green embed when price is inside OTE
  3. Power of Three (PO3) detection  detect_power_of_three() helper; +2 score on confirmed distribution phase
  4. !po3 [pair] command  shows PO3 phase (accumulation/manipulation/distribution) per pair on 15m/1H
  5. NWOG/NDOG opening gap tracking  DAILY_OPENS/WEEKLY_OPENS stores; recorded at 00:00 UTC; +1 score within 0.3%
  6. !opens command  shows last 7 daily opens and last 4 weekly opens per pair with % distance
  7. All footers, docstring, and version references updated to v9.7
v9.8 milestone upgrades:
  1. ICT Dealing Range detection  detect_dealing_range() helper; zones: Premium/Equilibrium/Discount/Deep Discount
  2. ICT Breaker Block detection  detect_breaker_block() helper; mitigated OBs now acting as S/R
  3. Dealing Range scoring  Deep Discount +2 long, Discount +1 long, Premium +1 short (1 long)
  4. ICT Consequent Encroachment (CE) scoring  price within 0.2% of FVG midpoint = +1 in FVG direction
  5. !dr [pair] command  Dealing Range across 4 timeframes with zone + key Fibonacci levels
  6. !bb2 [pair] command  ICT Breaker Blocks on 15m & 1H for both LONG and SHORT (NOT Bollinger Bands)
  7. !ce [pair] command  FVG Consequent Encroachment levels across all 4 timeframes
  8. All footers, docstring, and version references updated to v9.8
"""

import asyncio
import json
import os
import statistics
import time
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

import aiohttp
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

# Monkey-patch discord.Embed.add_field to auto-truncate values to 1024 chars
_orig_add_field = discord.Embed.add_field
def _safe_add_field(self, *, name, value, inline=True):
    value = str(value)
    if len(value) > 1024:
        value = value[:1021] + "..."
    name = str(name)
    if len(name) > 256:
        name = name[:253] + "..."
    return _orig_add_field(self, name=name, value=value, inline=inline)
discord.Embed.add_field = _safe_add_field

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

#  Rating thresholds 
RATING_A = 7
RATING_B = 5
MIN_SCORE = RATING_A  # A-grade only  higher probability trades only

# Confidence tiers based on score relative to min threshold
CONFIDENCE_HIGH   = MIN_SCORE + 5   # 12+: elite confluence
CONFIDENCE_MEDIUM = MIN_SCORE + 2   # 9+: strong confluence


def confidence_tier(score: int) -> tuple[str, str]:
    """Return (label, emoji) for a signal score's confidence tier."""
    if score >= CONFIDENCE_HIGH:
        return " High Confidence", ""
    elif score >= CONFIDENCE_MEDIUM:
        return "Medium Confidence", ""
    else:
        return "Low Confidence", ""


def next_tier_display(score: int) -> str:
    """Return a string showing the current score tier and how many points to the next tier.
    E.g. 'Score: 9  Medium | Next tier at 12 (3 more pts)'
    Used in signal embeds (v8.5 Feature 1).
    """
    if score >= CONFIDENCE_HIGH:
        return f"Score: **{score}**  High Confidence  (top tier)"
    elif score >= CONFIDENCE_MEDIUM:
        gap = CONFIDENCE_HIGH - score
        return f"Score: **{score}**  Medium | Next tier at {CONFIDENCE_HIGH} ({gap} more pt{'s' if gap != 1 else ''})"
    else:
        gap = CONFIDENCE_MEDIUM - score
        return f"Score: **{score}**  Low | Next tier at {CONFIDENCE_MEDIUM} ({gap} more pt{'s' if gap != 1 else ''})"


def count_directional_candles(candles: list, direction: str, lookback: int = 5) -> tuple[int, int]:
    """Count how many of the last `lookback` candles closed in `direction`.
    Returns (count, bonus_score) where bonus_score is +2 if all 5 align, +1 if >=4/5, else 0.
    Used in scoring engines (v8.5 Feature 6).
    """
    recent = candles[-lookback:] if len(candles) >= lookback else candles
    if direction == "long":
        aligned = sum(1 for c in recent if c["close"] > c["open"])
    else:
        aligned = sum(1 for c in recent if c["close"] < c["open"])
    total = len(recent)
    if total == 0:
        return 0, 0
    if aligned == total:
        return aligned, 2
    elif aligned >= total - 1:
        return aligned, 1
    return aligned, 0


#  Pairs  crypto only 
PAIRS = [
    {"label": "BTC/USD",  "source": "coinbase", "product_id": "BTC-USD",  "yahoo": None},
    {"label": "SOL/USD",  "source": "coinbase", "product_id": "SOL-USD",  "yahoo": None},
    {"label": "XRP/USD",  "source": "coinbase", "product_id": "XRP-USD",  "yahoo": None},
]

# Runtime-mutable copy of PAIRS for !pairs add/remove/reset (v8.4)
DYNAMIC_PAIRS: list[dict] = list(PAIRS)

# Per-pair asyncio locks  prevents duplicate signals when gather() fires all pairs simultaneously
pair_locks: dict[str, asyncio.Lock] = {}

#  Global state 
active_trades: dict[str, dict] = {}   # pair_label -> trade dict
last_signal_time: dict[str, float] = {}  # pair_label -> epoch
last_signal_dir: dict[str, str] = {}    # pair_label -> "LONG" | "SHORT" of last fired signal
last_win_time: dict[str, float] = {}    # pair_label -> epoch of last WIN close
last_loss_time: dict[str, float] = {}   # pair_label -> epoch of last LOSS close
last_trade_result: dict[str, str] = {}  # pair_label -> "WIN" | "LOSS" of most recent closed trade

# Cooldown rules:
#   Base cooldown between any signals on same pair: 90 min
#   After a WIN: 3h cooldown before next signal same pair (market just moved hard)
#   Same-direction re-entry within 30 min of previous signal: blocked
#   Dynamic cooldown scaling: +50% cooldown after a loss, -20% after a win (floor: 45 min)
SIGNAL_COOLDOWN     = 5400   # 90 min base
POST_WIN_COOLDOWN   = 10800  # 3 hr after a win
SAME_DIR_BLOCK      = 1800   # 30 min block on same-direction repeat
MIN_COOLDOWN        = 2700   # 45 min absolute floor for dynamic scaling

#  Consecutive loss circuit breaker 
# After 3 SL hits in a row across all pairs, halt scanning for 4h
CIRCUIT_BREAKER_LOSSES   = 3      # number of consecutive losses to trip
CIRCUIT_BREAKER_COOLDOWN = 14400  # 4 hours in seconds
_consecutive_losses: int = 0
_circuit_tripped_at: float = 0.0  # epoch when last tripped

#  v9.0 Feature 5: Sensitivity level (1=strict, 3=default, 5=loose) 
_sensitivity_level: int = 3  # default; adjusts MIN_SCORE, CONFIDENCE_HIGH, CONFIDENCE_MEDIUM

session_pnl = {
    "wins": 0,
    "losses": 0,
    "t1_hits": 0,
    "total_pnl_pct": 0.0,
    # Per-engine breakdown
    "premium_wins": 0,
    "premium_losses": 0,
    "standard_wins": 0,
    "standard_losses": 0,
    # Per-pair breakdown
    "pair_wins": {},    # pair_label -> win count
    "pair_losses": {},  # pair_label -> loss count
    # Per-session breakdown
    "session_wins": {},   # session_label -> wins
    "session_losses": {}, # session_label -> losses
}

#  User risk settings (persisted per session; reset on bot restart) 
# Users can customize with !risk command: account size and risk % per trade
_user_risk_settings: dict[int, dict] = {}   # discord_user_id -> {"account": float, "risk_pct": float}
DEFAULT_ACCOUNT_SIZE = 10000.0
DEFAULT_RISK_PCT     = 0.01  # 1%

#  Global account size (set via !account command, v8.7) 
# Used by position sizing calculations throughout the bot.
ACCOUNT_SIZE: float = 10000.0

#  Persistence paths 
SIGNALS_FILE  = Path(__file__).parent / "chartwise_signals.json"
STATE_FILE    = Path(__file__).parent / "chartwise_state.json"
LEARNING_FILE = Path(__file__).parent / "chartwise_learning.json"
WEIGHTS_FILE  = Path(__file__).parent / "chartwise_weights.json"

#  v10.0: Dynamic score multipliers (rebalanced from pattern_performance outcomes)
SCORE_MULTIPLIERS: dict = {}
RESOLVED_OUTCOMES_COUNT: int = 0

#  In-memory notepad for !notes command (v8.4) 
NOTES: list[str] = []

#  In-memory signal log (last 50 fired signals, deque-style) 
from collections import deque
SIGNAL_LOG: deque = deque(maxlen=50)

#  Filtered signal log (v8.1)  signals generated but not fired 
# Populated when a signal is rejected by score filter or circuit breaker.
# Useful for debugging why signals were blocked.
FILTERED_LOG: deque = deque(maxlen=30)

#  Trade history log (v8.1)  closed trades for !streak and !export 
# Appended whenever a trade closes (stop or t2). Each entry is a dict.
TRADE_HISTORY: deque = deque(maxlen=200)

#  Score history per pair (v8.8)  rolling last-10 scores per pair 
# Key = pair_label (e.g. "BTC/USD"), value = deque(maxlen=10) of int scores.
SCORE_HISTORY: dict[str, deque] = {}

#  v9.4 Feature 4: Multi-pair wave detection 
# Tracks timestamp of the most recent fired signal per pair.
# When 2+ pairs signal within WAVE_WINDOW seconds, a Wave Alert embed is sent.
WAVE_WINDOW: float = 30.0   # seconds
_recent_signal_ts: dict[str, float] = {}   # pair_label -> epoch of last fired signal
_recent_signal_info: dict[str, dict] = {}  # pair_label -> {direction, score}

#  Watchlist (v9.1 Feature 1)  near-miss signals waiting for price touch 
# Key = pair_label, value = list of dicts with near-miss signal info.
# Near-miss = signals that scored MIN_SCORE-1 or MIN_SCORE-2 (almost qualified).
# When a watchlist signal's entry price is touched in a subsequent scan, a
# "Watchlist Alert" embed is posted.
WATCHLIST: dict[str, list[dict]] = {}

#  v9.4 Feature 2: Price Alert System 
# Each alert dict: {pair, price, direction ("above"|"below"), set_time, user_id}
# Checked each scan cycle after fetching candles for each pair.
PRICE_ALERTS: list[dict] = []

#  v9.7 Feature 5: NWOG/NDOG Opening Gap tracking 
# Daily/Weekly opening prices recorded at 00:00 UTC (daily) and Monday 00:00 (weekly).
# Each entry: {"pair": str, "price": float, "time_utc": str, "type": "daily"|"weekly"}
DAILY_OPENS:  dict[str, deque] = {}   # pair_label -> deque(maxlen=7) of {price, time_utc}
WEEKLY_OPENS: dict[str, deque] = {}   # pair_label -> deque(maxlen=4) of {price, time_utc}

#  Daily PnL counters (reset at midnight UTC by daily_summary task) 
_daily_opened: int = 0   # trades opened today
_daily_closed: int = 0   # trades closed today
_daily_pnl_pct: float = 0.0   # sum of closed trade pnl_pct for today
_daily_wins: int = 0     # wins today
_daily_losses: int = 0   # losses today

#  Time-in-trade helper 
def format_trade_duration(opened_at_iso: str) -> str:
    """Parse ISO timestamp and return elapsed time as 'Xh Ym' string."""
    try:
        opened = datetime.fromisoformat(opened_at_iso)
        if opened.tzinfo is None:
            opened = opened.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - opened
        total_minutes = int(delta.total_seconds() // 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    except Exception:
        return "?"

#  Adaptive learning: confluence reason -> SL hit count 
# Loaded from disk on startup; updated whenever a stop is hit.
_adaptive_sl_counts: dict[str, int]  = {}
_adaptive_win_counts: dict[str, int] = {}  # confluence reason -> WIN occurrences
_ADAPTIVE_PENALTY_THRESHOLD = 3   # hits before we penalize this reason
_ADAPTIVE_PENALTY_SCORE     = 1   # score points subtracted per degraded reason

#  Candle pattern win rate tracking (v8.6 Feature 5) 
# Tracks wins/losses per named candle pattern. Keys: pattern name (str).
# Each value: {"wins": int, "losses": int}
# Updated in log_outcome() when trades close.
_CANDLE_PATTERNS = ["engulfing", "hammer", "pin_bar", "three_line_strike", "inside_bar"]
pattern_performance: dict[str, dict] = {p: {"wins": 0, "losses": 0} for p in _CANDLE_PATTERNS}

#  v9.2 Feature 2: Pattern streak tracking 
# Expanded pattern performance dict to include all grouped patterns for !patterns command
_ALL_PATTERNS = [
    # Candle patterns
    "engulfing", "hammer", "pin_bar", "three_line_strike", "inside_bar", "doji",
    # ICT/SMC patterns
    "mss", "sfp", "order_block", "fvg", "liquidity_sweep",
    # Momentum patterns
    "rsi_divergence", "macd_cross", "consecutive_candles", "ha_streak",
    # Multi-TF
    "mtf_consensus_2", "mtf_consensus_3", "bb_kc_squeeze",
]

def _extract_pattern_from_reason(reason: str) -> str | None:
    """Map a reason string to a canonical pattern key. Returns None if no match."""
    r = reason.lower()
    mapping = {
        "engulfing": "engulfing",
        "hammer": "hammer",
        "pin bar": "pin_bar",
        "pin_bar": "pin_bar",
        "three-line strike": "three_line_strike",
        "three_line_strike": "three_line_strike",
        "inside bar": "inside_bar",
        "inside_bar": "inside_bar",
        "doji": "doji",
        "market structure shift": "mss",
        "mss": "mss",
        "sfp": "sfp",
        "swing failure": "sfp",
        "order block": "order_block",
        "fair value gap": "fvg",
        "fvg": "fvg",
        "liquidity sweep": "liquidity_sweep",
        "rsi divergence": "rsi_divergence",
        "rsi div": "rsi_divergence",
        "macd": "macd_cross",
        "consecutive bull": "consecutive_candles",
        "consecutive bear": "consecutive_candles",
        "ha streak": "ha_streak",
        "heikin ashi": "ha_streak",
        "3/3 timeframe": "mtf_consensus_3",
        "consensus 3": "mtf_consensus_3",
        "2/3 timeframe": "mtf_consensus_2",
        "consensus 2": "mtf_consensus_2",
        "bb/kc squeeze": "bb_kc_squeeze",
        "bb squeeze": "bb_kc_squeeze",
        "keltner": "bb_kc_squeeze",
    }
    for keyword, pattern_key in mapping.items():
        if keyword in r:
            return pattern_key
    return None


def check_pattern_streak(pair_label: str, pattern_key: str, lookback: int = 3) -> bool:
    """
    v9.2 Feature 2: Return True if `pattern_key` appears in each of the last `lookback`
    SIGNAL_LOG entries for `pair_label`. Used to add the  'on fire' bonus.
    """
    pair_signals = [e for e in SIGNAL_LOG if e.get("pair") == pair_label]
    if len(pair_signals) < lookback:
        return False
    recent = pair_signals[-lookback:]
    for entry in recent:
        reasons = entry.get("reasons", [])
        if not any(_extract_pattern_from_reason(r) == pattern_key for r in reasons):
            return False
    return True


def apply_pattern_streak_bonus(pair_label: str, reasons: list[str], score: int) -> tuple[list[str], int]:
    """
    v9.2 Feature 2: Check if any pattern in the current reasons is on a 3-signal streak.
    If so, add +1 score and a  reason. Returns (updated_reasons, updated_score).
    """
    for reason in reasons:
        pk = _extract_pattern_from_reason(reason)
        if pk and check_pattern_streak(pair_label, pk, lookback=3):
            bonus_reason = f" {pk.replace('_', ' ').title()} on fire (3 signals in a row)  pattern in strong form"
            if bonus_reason not in reasons:
                reasons = list(reasons) + [bonus_reason]
                score += 1
                break  # only one streak bonus per signal
    return reasons, score


def _load_learning():
    global _adaptive_sl_counts, _adaptive_win_counts, pattern_performance
    try:
        data = json.loads(LEARNING_FILE.read_text())
        _adaptive_sl_counts  = data.get("sl_counts",  {})
        _adaptive_win_counts = data.get("win_counts", {})
        # Load pattern_performance, preserving any keys from disk
        saved_pp = data.get("pattern_performance", {})
        for p in _CANDLE_PATTERNS:
            if p in saved_pp:
                pattern_performance[p] = saved_pp[p]
    except Exception:
        _adaptive_sl_counts  = {}
        _adaptive_win_counts = {}

def _save_learning():
    try:
        LEARNING_FILE.write_text(json.dumps(
            {
                "sl_counts":  _adaptive_sl_counts,
                "win_counts": _adaptive_win_counts,
                "pattern_performance": pattern_performance,
            },
            indent=2
        ))
    except Exception as e:
        print(f"[WARN] Could not save learning file: {e}")

def get_adaptive_penalty(reasons: list[str]) -> int:
    """Return score penalty for reasons that have degraded (hit SL too often)."""
    penalty = 0
    for reason in reasons:
        # Match on prefix of the reason string (reason text can include numbers)
        for key, count in _adaptive_sl_counts.items():
            if reason.startswith(key[:40]):
                if count >= _ADAPTIVE_PENALTY_THRESHOLD:
                    penalty += _ADAPTIVE_PENALTY_SCORE
    return penalty

#  Signal logging helpers 

def _read_signals() -> list:
    try:
        return json.loads(SIGNALS_FILE.read_text())
    except Exception:
        return []

def _write_signals(signals: list):
    try:
        SIGNALS_FILE.write_text(json.dumps(signals, indent=2))
    except Exception as e:
        print(f"[WARN] Could not write signals file: {e}")

def log_signal(pair_label: str, signal: dict, engine: str, htf_trend: str) -> str:
    """Log a new signal to the JSON file. Returns the signal ID."""
    sig_id = str(uuid.uuid4())[:8]
    record = {
        "id": sig_id,
        "ts": time.time(),
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "pair": pair_label,
        "engine": engine,
        "direction": signal["direction"].upper(),
        "score": signal["score"],
        "rating": signal.get("rating", "B"),
        "entry": signal["entry"],
        "sl": signal["sl"],
        "t1": signal["t1"],
        "t2": signal["t2"],
        "htf_trend": htf_trend,
        "reasons": signal.get("reasons", []),
        "outcome": "PENDING",
        "exit_price": None,
        "exit_type": None,
        "pnl_r": None,
    }
    signals = _read_signals()
    signals.append(record)
    # Keep up to 500 signals on disk
    if len(signals) > 500:
        signals = signals[-500:]
    _write_signals(signals)
    return sig_id

def log_outcome(sig_id: str, exit_type: str, exit_price: float, entry: float, sl: float):
    """Update a signal's outcome after it closes (stop/t2/t1 final)."""
    signals = _read_signals()
    sl_dist = abs(entry - sl)
    pnl_r = 0.0
    outcome = "PENDING"

    if exit_type == "stop":
        outcome = "LOSS"
        pnl_r = -1.0
    elif exit_type == "t2":
        outcome = "WIN"
        pnl_r = abs(exit_price - entry) / max(sl_dist, 1e-9)
    elif exit_type == "t1":
        outcome = "WIN"
        pnl_r = abs(exit_price - entry) / max(sl_dist, 1e-9)

    updated_reasons = []
    for s in reversed(signals):
        if s["id"] == sig_id:
            s["outcome"] = outcome
            s["exit_price"] = exit_price
            s["exit_type"] = exit_type
            s["pnl_r"] = round(pnl_r, 2)
            updated_reasons = s.get("reasons", [])
            break
    _write_signals(signals)

    # Adaptive learning: track which reasons appear on losses (SL) and wins (T2)
    if updated_reasons:
        if exit_type == "stop":
            for reason in updated_reasons:
                key = reason[:40]  # normalize key
                _adaptive_sl_counts[key] = _adaptive_sl_counts.get(key, 0) + 1
                if _adaptive_sl_counts[key] == _ADAPTIVE_PENALTY_THRESHOLD:
                    print(f"[LEARN] Confluence degraded after {_ADAPTIVE_PENALTY_THRESHOLD} SL hits: '{reason[:60]}'")
        elif exit_type == "t2":
            for reason in updated_reasons:
                key = reason[:40]
                _adaptive_win_counts[key] = _adaptive_win_counts.get(key, 0) + 1

        # v8.6 Feature 5: track candle pattern performance
        # Map reason keywords to pattern_performance keys
        _pattern_keyword_map = {
            "engulfing": "engulfing",
            "hammer": "hammer",
            "pin bar": "pin_bar",
            "pin_bar": "pin_bar",
            "three-line strike": "three_line_strike",
            "three_line_strike": "three_line_strike",
            "inside bar": "inside_bar",
            "inside_bar": "inside_bar",
        }
        for reason in updated_reasons:
            reason_lower = reason.lower()
            for keyword, pattern_key in _pattern_keyword_map.items():
                if keyword in reason_lower:
                    if exit_type == "stop":
                        pattern_performance[pattern_key]["losses"] += 1
                    elif exit_type in ("t2", "t1"):
                        pattern_performance[pattern_key]["wins"] += 1
                    break  # only credit once per reason

        _save_learning()

def write_state_file():
    """Write current bot state to disk for the API server to read."""
    try:
        STATE_FILE.write_text(json.dumps({
            "last_scan_ts": time.time(),
            "active_trades": active_trades,
            "session_pnl": session_pnl,
            "circuit_breaker": {
                "tripped": _circuit_tripped_at > 0,
                "consecutive_losses": _consecutive_losses,
                "tripped_at": _circuit_tripped_at if _circuit_tripped_at > 0 else None,
            },
        }, indent=2))
    except Exception as e:
        print(f"[WARN] Could not write state file: {e}")

#  Bot setup 
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


# 
# DATA FETCHING
# 

async def fetch_coinbase_candles(product_id: str, granularity: int = 300, limit: int = 100) -> list[dict] | None:
    """Fetch OHLCV candles from Coinbase Advanced Trade API."""
    url = f"https://api.exchange.coinbase.com/products/{product_id}/candles"
    params = {"granularity": granularity}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                # data is list of [time, low, high, open, close, volume] newest first
                candles = []
                for row in reversed(data[:limit]):
                    candles.append({
                        "time": row[0],
                        "low": float(row[1]),
                        "high": float(row[2]),
                        "open": float(row[3]),
                        "close": float(row[4]),
                        "volume": float(row[5]),
                    })
                return candles if len(candles) >= 20 else None
    except Exception as e:
        print(f"[ERROR] fetch_coinbase_candles({product_id}): {e}")
        return None


async def fetch_yahoo_candles(ticker: str, interval: str = "5m", period: str = "5d") -> list[dict] | None:
    """Fetch OHLCV candles from Yahoo Finance."""
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + ticker
    params = {"interval": interval, "range": period}
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                result = data["chart"]["result"]
                if not result:
                    return None
                r = result[0]
                timestamps = r["timestamp"]
                q = r["indicators"]["quote"][0]
                candles = []
                for i, ts in enumerate(timestamps):
                    try:
                        candles.append({
                            "time": ts,
                            "open": float(q["open"][i]),
                            "high": float(q["high"][i]),
                            "low": float(q["low"][i]),
                            "close": float(q["close"][i]),
                            "volume": float(q["volume"][i]) if q["volume"][i] else 0.0,
                        })
                    except (TypeError, KeyError):
                        continue
                return candles[-100:] if len(candles) >= 20 else None
    except Exception as e:
        print(f"[ERROR] fetch_yahoo_candles({ticker}): {e}")
        return None


async def fetch_candles(pair: dict, timeframe: str = "5m") -> list[dict] | None:
    """Route to correct data source."""
    if pair["source"] == "coinbase":
        gran_map = {"5m": 300, "15m": 900, "1h": 3600, "4h": 14400}
        gran = gran_map.get(timeframe, 300)
        return await fetch_coinbase_candles(pair["product_id"], granularity=gran)
    elif pair["source"] == "yahoo":
        interval_map = {"5m": "5m", "15m": "15m", "1h": "1h"}
        interval = interval_map.get(timeframe, "5m")
        return await fetch_yahoo_candles(pair["yahoo"], interval=interval)
    return None


# 
# MATH UTILITIES
# 

def calc_atr(candles: list[dict], period: int = 14) -> float | None:
    """Average True Range."""
    if len(candles) < period + 1:
        return None
    trs = []
    for i in range(1, len(candles)):
        h = candles[i]["high"]
        l = candles[i]["low"]
        pc = candles[i - 1]["close"]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    return statistics.mean(trs[-period:])


def ema(values: list[float], period: int) -> float | None:
    """Exponential moving average  returns last value."""
    if len(values) < period:
        return None
    k = 2 / (period + 1)
    result = statistics.mean(values[:period])
    for v in values[period:]:
        result = v * k + result * (1 - k)
    return result


def rsi(closes: list[float], period: int = 14) -> float | None:
    """Relative Strength Index."""
    if len(closes) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, len(closes)):
        delta = closes[i] - closes[i - 1]
        gains.append(max(delta, 0))
        losses.append(max(-delta, 0))
    avg_gain = statistics.mean(gains[-period:])
    avg_loss = statistics.mean(losses[-period:])
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def pearson_correlation(x: list[float], y: list[float]) -> float | None:
    """Pearson correlation coefficient between two equal-length lists. Returns None on error."""
    n = len(x)
    if n < 3 or len(y) != n:
        return None
    try:
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)
        dx = [v - mean_x for v in x]
        dy = [v - mean_y for v in y]
        num = sum(a * b for a, b in zip(dx, dy))
        den = (sum(a ** 2 for a in dx) ** 0.5) * (sum(b ** 2 for b in dy) ** 0.5)
        if den == 0:
            return None
        return round(num / den, 4)
    except Exception:
        return None


def corr_label(r: float) -> str:
    """Human-readable label for a Pearson correlation coefficient."""
    abs_r = abs(r)
    if abs_r >= 0.8:
        return "High"
    elif abs_r >= 0.6:
        return "Moderate"
    elif abs_r >= 0.4:
        return "Low"
    else:
        return "Very Low"


def detect_rsi_divergence(candles: list[dict], direction: str, lookback: int = 10) -> int:
    """
    Detect RSI divergence  price makes new extreme but RSI doesn't.
    Returns divergence strength: 0 = none, 1 = weak, 2 = strong (large gap).
    Bullish divergence: price makes lower low, RSI makes higher low.
    Bearish divergence: price makes higher high, RSI makes lower high.
    """
    if len(candles) < lookback + 15:
        return 0
    closes = [c["close"] for c in candles]
    rsi_series = []
    for i in range(lookback + 14, len(candles)):
        r = rsi(closes[:i+1], 14)
        if r is not None:
            rsi_series.append(r)

    if len(rsi_series) < 4:
        return 0

    half = len(rsi_series) // 2

    if direction == "long":
        recent_lows = [c["low"] for c in candles[-lookback:]]
        if len(recent_lows) < 4:
            return 0
        mid = len(recent_lows) // 2
        prior_low_price = min(recent_lows[:mid])
        recent_low_price = min(recent_lows[mid:])
        prior_rsi = min(rsi_series[:half])
        recent_rsi = min(rsi_series[half:])
        if recent_low_price < prior_low_price and recent_rsi > prior_rsi:
            # Grade by RSI gap: large gap = strong divergence
            rsi_gap = recent_rsi - prior_rsi
            return 2 if rsi_gap >= 5 else 1
    else:
        recent_highs = [c["high"] for c in candles[-lookback:]]
        if len(recent_highs) < 4:
            return 0
        mid = len(recent_highs) // 2
        prior_high_price = max(recent_highs[:mid])
        recent_high_price = max(recent_highs[mid:])
        prior_rsi = max(rsi_series[:half])
        recent_rsi = max(rsi_series[half:])
        if recent_high_price > prior_high_price and recent_rsi < prior_rsi:
            rsi_gap = prior_rsi - recent_rsi
            return 2 if rsi_gap >= 5 else 1
    return 0


def detect_rsi_divergence_type(candles: list[dict], rsi_values: list[float], direction: str) -> str | None:
    """
    Detect RSI divergence using provided rsi_values over the last 10 candles.
    Returns "bullish", "bearish", or None.
    Bullish divergence (supporting longs): price makes lower low, RSI makes higher low.
    Bearish divergence (opposing longs / supporting shorts): price makes higher high, RSI makes lower high.
    """
    lookback = min(10, len(candles), len(rsi_values))
    if lookback < 4:
        return None
    price_recent = candles[-lookback:]
    rsi_recent = rsi_values[-lookback:]
    mid = lookback // 2
    if direction == "long":
        prior_low_price = min(c["low"] for c in price_recent[:mid])
        recent_low_price = min(c["low"] for c in price_recent[mid:])
        prior_rsi_low = min(rsi_recent[:mid])
        recent_rsi_low = min(rsi_recent[mid:])
        if recent_low_price < prior_low_price and recent_rsi_low > prior_rsi_low:
            return "bullish"
        prior_high_price = max(c["high"] for c in price_recent[:mid])
        recent_high_price = max(c["high"] for c in price_recent[mid:])
        prior_rsi_high = max(rsi_recent[:mid])
        recent_rsi_high = max(rsi_recent[mid:])
        if recent_high_price > prior_high_price and recent_rsi_high < prior_rsi_high:
            return "bearish"
    else:  # short
        prior_high_price = max(c["high"] for c in price_recent[:mid])
        recent_high_price = max(c["high"] for c in price_recent[mid:])
        prior_rsi_high = max(rsi_recent[:mid])
        recent_rsi_high = max(rsi_recent[mid:])
        if recent_high_price > prior_high_price and recent_rsi_high < prior_rsi_high:
            return "bearish"
        prior_low_price = min(c["low"] for c in price_recent[:mid])
        recent_low_price = min(c["low"] for c in price_recent[mid:])
        prior_rsi_low = min(rsi_recent[:mid])
        recent_rsi_low = min(rsi_recent[mid:])
        if recent_low_price < prior_low_price and recent_rsi_low > prior_rsi_low:
            return "bullish"
    return None


def calc_fibonacci_levels(candles: list[dict], lookback: int = 50) -> dict | None:
    """
    Calculate Fibonacci retracement levels from the most recent significant swing.
    Returns levels: 0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0
    Works by finding the most recent swing high and swing low within lookback candles.
    """
    if len(candles) < lookback:
        return None
    recent = candles[-lookback:]
    swing_high = max(c["high"] for c in recent)
    swing_low  = min(c["low"]  for c in recent)
    rng = swing_high - swing_low
    if rng <= 0:
        return None
    levels = {}
    for ratio in (0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0):
        # Bullish fib: levels measured from low up
        levels[ratio] = swing_low + rng * ratio
    return {
        "swing_high": swing_high,
        "swing_low": swing_low,
        "range": rng,
        "levels": levels,  # ratio -> price
    }


def ichimoku(candles: list[dict]) -> dict | None:
    """
    Compute Ichimoku Cloud components.
    Tenkan-sen (conversion line): (9-period high + low) / 2
    Kijun-sen (base line): (26-period high + low) / 2
    Senkou Span A: (Tenkan + Kijun) / 2
    Senkou Span B: (52-period high + low) / 2
    Cloud: between Span A and Span B
    """
    if len(candles) < 52:
        return None

    def period_hl(n: int) -> tuple[float, float]:
        sub = candles[-n:]
        return max(c["high"] for c in sub), min(c["low"] for c in sub)

    h9,  l9  = period_hl(9)
    h26, l26 = period_hl(26)
    h52, l52 = period_hl(52)

    tenkan = (h9  + l9)  / 2
    kijun  = (h26 + l26) / 2
    span_a = (tenkan + kijun) / 2
    span_b = (h52 + l52) / 2

    price = candles[-1]["close"]

    # Determine cloud color and price position
    cloud_top    = max(span_a, span_b)
    cloud_bottom = min(span_a, span_b)
    cloud_bullish = span_a >= span_b  # green cloud = bullish

    above_cloud = price > cloud_top
    below_cloud = price < cloud_bottom
    in_cloud    = cloud_bottom <= price <= cloud_top

    return {
        "tenkan": tenkan,
        "kijun": kijun,
        "span_a": span_a,
        "span_b": span_b,
        "cloud_top": cloud_top,
        "cloud_bottom": cloud_bottom,
        "cloud_bullish": cloud_bullish,
        "above_cloud": above_cloud,
        "below_cloud": below_cloud,
        "in_cloud": in_cloud,
        "price": price,
    }


# 
# SMC STRUCTURE DETECTION
# 

def find_swing_highs_lows(candles: list[dict], lookback: int = 5) -> dict:
    """Find recent swing highs and lows."""
    highs, lows = [], []
    for i in range(lookback, len(candles) - lookback):
        h = candles[i]["high"]
        l = candles[i]["low"]
        if all(h >= candles[j]["high"] for j in range(i - lookback, i + lookback + 1) if j != i):
            highs.append({"index": i, "price": h})
        if all(l <= candles[j]["low"] for j in range(i - lookback, i + lookback + 1) if j != i):
            lows.append({"index": i, "price": l})
    return {"highs": highs, "lows": lows}


def find_fvg(candles: list[dict]) -> list[dict]:
    """Find Fair Value Gaps (FVG)  3-candle imbalance."""
    fvgs = []
    for i in range(2, len(candles)):
        c0, c1, c2 = candles[i - 2], candles[i - 1], candles[i]
        # Bullish FVG: gap between c0 high and c2 low
        if c2["low"] > c0["high"]:
            fvgs.append({"type": "bullish", "top": c2["low"], "bottom": c0["high"], "index": i})
        # Bearish FVG: gap between c0 low and c2 high
        if c2["high"] < c0["low"]:
            fvgs.append({"type": "bearish", "top": c0["low"], "bottom": c2["high"], "index": i})
    return fvgs


def find_ifvg(candles: list[dict]) -> list[dict]:
    """Find Inverse FVGs (filled/mitigated FVGs acting as support/resistance)."""
    fvgs = find_fvg(candles)
    ifvgs = []
    for fvg in fvgs:
        filled = False
        for i in range(fvg["index"] + 1, len(candles)):
            c = candles[i]
            if fvg["type"] == "bullish" and c["low"] < fvg["bottom"]:
                filled = True
                break
            if fvg["type"] == "bearish" and c["high"] > fvg["top"]:
                filled = True
                break
        if filled:
            ifvgs.append(fvg)
    return ifvgs


def find_order_block(candles: list[dict], direction: str) -> dict | None:
    """Find the last significant order block before a strong move.
    Also validates the OB has proper body origin: displacement candle must be 1.5 avg range."""
    if len(candles) < 10:
        return None
    avg_range = statistics.mean([(c["high"] - c["low"]) for c in candles[-20:-1]]) if len(candles) >= 20 else None

    for i in range(len(candles) - 3, 5, -1):
        c = candles[i]
        next_c = candles[i + 1]
        displacement_range = next_c["high"] - next_c["low"]

        # Validate displacement: the candle after OB must be a strong move (1.5 avg range)
        # This filters weak OBs where price drifted out rather than displaced aggressively
        if avg_range and displacement_range < avg_range * 1.3:
            continue  # not a true displacement  skip this OB candidate

        # Bullish OB: last bearish candle before upward displacement
        if direction == "long":
            if c["close"] < c["open"]:  # bearish candle
                if next_c["close"] > c["high"]:  # displacement up
                    ob_body = abs(c["open"] - c["close"])
                    ob_range = c["high"] - c["low"]
                    # OB quality: body must be at least 40% of range (real candle, not doji)
                    if ob_range > 0 and ob_body / ob_range >= 0.4:
                        return {"top": c["high"], "bottom": c["low"], "index": i,
                                "type": "bullish", "body_pct": ob_body / ob_range}
        # Bearish OB: last bullish candle before downward displacement
        elif direction == "short":
            if c["close"] > c["open"]:  # bullish candle
                if next_c["close"] < c["low"]:  # displacement down
                    ob_body = abs(c["close"] - c["open"])
                    ob_range = c["high"] - c["low"]
                    if ob_range > 0 and ob_body / ob_range >= 0.4:
                        return {"top": c["high"], "bottom": c["low"], "index": i,
                                "type": "bearish", "body_pct": ob_body / ob_range}
    return None


def calc_volume_poc(candles: list[dict], bins: int = 20) -> float | None:
    """Approximate Volume Point of Control (POC)  the price level with the most volume.
    Splits the price range into bins and sums volume at each level.
    POC acts as a magnet: price tends to gravitate back toward it."""
    if not candles or len(candles) < 10:
        return None
    valid = [c for c in candles if c.get("volume") and c["volume"] > 0]
    if not valid:
        return None
    price_min = min(c["low"] for c in valid)
    price_max = max(c["high"] for c in valid)
    if price_max <= price_min:
        return None
    bin_size = (price_max - price_min) / bins
    vol_at_bin = [0.0] * bins
    for c in valid:
        # Distribute volume uniformly across the candle's price range
        lo, hi, vol = c["low"], c["high"], c["volume"]
        for b in range(bins):
            bin_lo = price_min + b * bin_size
            bin_hi = bin_lo + bin_size
            overlap = max(0.0, min(hi, bin_hi) - max(lo, bin_lo))
            if overlap > 0 and (hi - lo) > 0:
                vol_at_bin[b] += vol * overlap / (hi - lo)
    poc_bin = vol_at_bin.index(max(vol_at_bin))
    return price_min + (poc_bin + 0.5) * bin_size  # midpoint of highest-volume bin


def calc_volume_profile(candles: list[dict], lookback: int = 20, bins: int = 20) -> dict | None:
    """
    Compute a basic volume profile over the last `lookback` candles.
    Returns {"poc_price": float, "vah": float, "val": float, "bins": list}.
    POC = Point of Control (price level with highest volume).
    VAH = Value Area High (top of the 70% volume zone).
    VAL = Value Area Low (bottom of the 70% volume zone).
    The 'value area' covers 70% of total volume centred on the POC.
    """
    if not candles or len(candles) < lookback:
        return None
    recent = candles[-lookback:]
    valid = [c for c in recent if c.get("volume") and c["volume"] > 0]
    if len(valid) < 5:
        return None

    price_min = min(c["low"] for c in valid)
    price_max = max(c["high"] for c in valid)
    if price_max <= price_min:
        return None

    bin_size = (price_max - price_min) / bins
    vol_at_bin = [0.0] * bins
    bin_prices = [price_min + (b + 0.5) * bin_size for b in range(bins)]

    for c in valid:
        lo, hi, vol = c["low"], c["high"], c["volume"]
        for b in range(bins):
            bin_lo = price_min + b * bin_size
            bin_hi = bin_lo + bin_size
            overlap = max(0.0, min(hi, bin_hi) - max(lo, bin_lo))
            if overlap > 0 and (hi - lo) > 0:
                vol_at_bin[b] += vol * overlap / (hi - lo)

    poc_bin = vol_at_bin.index(max(vol_at_bin))
    poc_price = bin_prices[poc_bin]

    # Value area: expand from POC bin outward until 70% of total volume captured
    total_vol = sum(vol_at_bin)
    target_vol = total_vol * 0.70
    included_vol = vol_at_bin[poc_bin]
    lo_idx = poc_bin
    hi_idx = poc_bin

    while included_vol < target_vol:
        expand_lo = (lo_idx - 1 >= 0)
        expand_hi = (hi_idx + 1 < bins)
        if not expand_lo and not expand_hi:
            break
        vol_lo = vol_at_bin[lo_idx - 1] if expand_lo else -1
        vol_hi = vol_at_bin[hi_idx + 1] if expand_hi else -1
        if vol_lo >= vol_hi and expand_lo:
            lo_idx -= 1
            included_vol += vol_at_bin[lo_idx]
        elif expand_hi:
            hi_idx += 1
            included_vol += vol_at_bin[hi_idx]
        else:
            break

    vah = price_min + (hi_idx + 1) * bin_size
    val = price_min + lo_idx * bin_size

    return {
        "poc_price": poc_price,
        "vah": vah,
        "val": val,
        "bins": list(zip(bin_prices, vol_at_bin)),
    }


def calc_fib_levels(candles: list[dict], lookback: int = 50) -> dict | None:
    """
    Compute Fibonacci retracement levels from the last `lookback` candles' high/low range.
    Returns dict with key levels at 0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0
    measured from swing_low (0%) up to swing_high (100%).
    Also returns swing_high, swing_low, and range.
    """
    if len(candles) < lookback:
        return None
    recent = candles[-lookback:]
    swing_high = max(c["high"] for c in recent)
    swing_low  = min(c["low"]  for c in recent)
    rng = swing_high - swing_low
    if rng <= 0:
        return None
    levels = {}
    for ratio in (0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0):
        levels[ratio] = swing_low + rng * ratio
    return {
        "swing_high": swing_high,
        "swing_low":  swing_low,
        "range":      rng,
        "levels":     levels,  # ratio -> price (measured from low)
    }


def detect_market_structure_shift(candles: list[dict], direction: str, lookback: int = 30) -> bool:
    """
    Detect a Market Structure Shift (MSS)  the early sign of a trend reversal.

    Bullish MSS (for LONG signals):
      - Prior downtrend: series of lower highs and lower lows
      - Then: price makes a HIGHER HIGH, breaking the downtrend structure
      - This is the first sign of bullish reversal, before a full BOS

    Bearish MSS (for SHORT signals):
      - Prior uptrend: series of higher highs and higher lows
      - Then: price makes a LOWER LOW, breaking the uptrend structure

    Returns True if MSS detected in signal direction.
    """
    if len(candles) < lookback:
        return False

    recent = candles[-lookback:]

    if direction == "long":
        # Look for downtrend (lower highs) that then breaks with a higher high
        highs = [c["high"] for c in recent]
        # Check first half is downtrend (falling highs)
        half = len(highs) // 2
        prior_highs = highs[:half]
        recent_highs = highs[half:]
        if not prior_highs or not recent_highs:
            return False
        prior_max = max(prior_highs)
        recent_max = max(recent_highs)
        # Check prior half shows declining highs (downtrend)
        declining = sum(1 for i in range(1, len(prior_highs)) if prior_highs[i] < prior_highs[i-1])
        if declining < len(prior_highs) // 2:
            return False
        # MSS: recent half breaks above the prior trend's peak
        return recent_max > prior_max

    else:  # short
        # Look for uptrend (higher lows) that then breaks with a lower low
        lows = [c["low"] for c in recent]
        half = len(lows) // 2
        prior_lows = lows[:half]
        recent_lows = lows[half:]
        if not prior_lows or not recent_lows:
            return False
        prior_min = min(prior_lows)
        recent_min = min(recent_lows)
        rising = sum(1 for i in range(1, len(prior_lows)) if prior_lows[i] > prior_lows[i-1])
        if rising < len(prior_lows) // 2:
            return False
        return recent_min < prior_min


def detect_displacement(candles: list[dict]) -> dict | None:
    """Detect a displacement candle (strong momentum candle)."""
    if len(candles) < 5:
        return None
    avg_range = statistics.mean([(c["high"] - c["low"]) for c in candles[-20:-1]])
    for i in range(len(candles) - 1, max(len(candles) - 6, 0), -1):
        c = candles[i]
        candle_range = c["high"] - c["low"]
        if candle_range > avg_range * 1.8:  # 1.8 avg = displacement
            direction = "up" if c["close"] > c["open"] else "down"
            return {"index": i, "direction": direction, "range": candle_range, "avg_range": avg_range}
    return None


def check_liquidity_sweep(candles: list[dict], swings: dict) -> dict | None:
    """Check if recent candles swept a swing high or low.

    v9.2: adds clean/dirty sweep detection.
    Clean sweep = wick dipped through the level but candle body did NOT close through it.
    Dirty sweep = candle body closed through the swept level.
    clean=True  score +2, clean=False  score +1 (handled in calling engine).
    """
    if not candles:
        return None
    last = candles[-1]
    prev = candles[-2] if len(candles) >= 2 else None

    def _body_close_below(candle: dict, level: float) -> bool:
        """True if the candle's close (body) is below the swept level."""
        return candle["close"] < level

    def _body_close_above(candle: dict, level: float) -> bool:
        """True if the candle's close (body) is above the swept level."""
        return candle["close"] > level

    # Check for sell-side sweep (swept lows  potential long)
    for low in reversed(swings["lows"][-5:]):
        if last["low"] < low["price"] and last["close"] > low["price"]:
            # Wick went below, close is above  CLEAN sweep
            clean = not _body_close_below(last, low["price"])
            return {"type": "sell_side", "level": low["price"], "direction": "long", "cidx": -1, "clean": clean}

    # Check for buy-side sweep (swept highs  potential short)
    for high in reversed(swings["highs"][-5:]):
        if last["high"] > high["price"] and last["close"] < high["price"]:
            clean = not _body_close_above(last, high["price"])
            return {"type": "buy_side", "level": high["price"], "direction": "short", "cidx": -1, "clean": clean}

    # Also check prev candle
    if prev:
        for low in reversed(swings["lows"][-5:]):
            if prev["low"] < low["price"] and prev["close"] > low["price"]:
                clean = not _body_close_below(prev, low["price"])
                return {"type": "sell_side", "level": low["price"], "direction": "long", "cidx": -2, "clean": clean}
        for high in reversed(swings["highs"][-5:]):
            if prev["high"] > high["price"] and prev["close"] < high["price"]:
                clean = not _body_close_above(prev, high["price"])
                return {"type": "buy_side", "level": high["price"], "direction": "short", "cidx": -2, "clean": clean}
    return None


def check_bos(candles: list[dict], direction: str, swings: dict) -> dict | None:
    """Check for Break of Structure in the given direction."""
    last_close = candles[-1]["close"]
    if direction == "long":
        # BOS: close above a recent swing high
        for high in reversed(swings["highs"][-5:]):
            if last_close > high["price"]:
                return {"level": high["price"], "direction": "long"}
    elif direction == "short":
        # BOS: close below a recent swing low
        for low in reversed(swings["lows"][-5:]):
            if last_close < low["price"]:
                return {"level": low["price"], "direction": "short"}
    return None


def is_trading_into_liquidity(candles: list[dict], direction: str, swings: dict) -> bool:
    """Check if price is trading toward liquidity (equal highs/lows or session levels)."""
    price = candles[-1]["close"]
    if direction == "long":
        # Trading up toward buy-side liquidity
        for high in swings["highs"][-3:]:
            if price < high["price"] < price * 1.02:
                return True
    elif direction == "short":
        for low in swings["lows"][-3:]:
            if price * 0.98 < low["price"] < price:
                return True
    return False


def calc_fib_79(swing_low: float, swing_high: float) -> dict:
    """Calculate 79% Fibonacci OTE zone."""
    diff = swing_high - swing_low
    return {
        "ote_high": swing_high - diff * 0.705,
        "ote_low": swing_high - diff * 0.79,
        "fib_50": swing_high - diff * 0.5,
    }


def find_session_liquidity(candles: list[dict]) -> dict:
    """Find session high/low (last 24 hours of candles)."""
    if not candles:
        return {"high": None, "low": None}
    session_high = max(c["high"] for c in candles[-288:])  # ~24h at 5m
    session_low = min(c["low"] for c in candles[-288:])
    return {"high": session_high, "low": session_low}




def calc_vwap(candles: list[dict]) -> float | None:
    """Session VWAP: cumulative(price  volume) / cumulative(volume).
    Uses last 24 candles as a rolling session window."""
    window = candles[-24:]
    cum_pv = 0.0
    cum_v  = 0.0
    for c in window:
        typ_price = (c["high"] + c["low"] + c["close"]) / 3
        vol = c.get("volume") or 0
        cum_pv += typ_price * vol
        cum_v  += vol
    if cum_v == 0:
        return None
    return cum_pv / cum_v

def calc_twap(candles: list[dict], lookback: int = 20) -> float | None:
    """
    v9.5 Feature 2: Time-Weighted Average Price (TWAP).
    TWAP = sum(typical_price * volume) / sum(volume) over last `lookback` candles.
    Unlike VWAP (cumulative session), TWAP uses a fixed rolling window.
    If all volumes are zero, falls back to simple mean of typical prices.
    """
    window = candles[-lookback:] if len(candles) >= lookback else candles
    if not window:
        return None
    cum_pv = 0.0
    cum_v  = 0.0
    for c in window:
        typ_price = (c["high"] + c["low"] + c["close"]) / 3
        vol = c.get("volume") or 0
        cum_pv += typ_price * vol
        cum_v  += vol
    if cum_v == 0:
        # Fallback: simple mean of typical prices
        return statistics.mean((c["high"] + c["low"] + c["close"]) / 3 for c in window)
    return cum_pv / cum_v


def calc_choppiness_index(candles: list[dict], period: int = 14) -> float | None:
    """
    v9.5 Feature 4: Choppiness Index.
    CI = 100 * log10(sum_of_ATR1s_over_period / (period_high - period_low)) / log10(period)
    CI > 61.8  choppy/ranging market (avoid breakout trades).
    CI < 38.2  trending market (follow-through likely).
    Range 38.261.8  indeterminate.
    """
    import math
    if len(candles) < period + 1:
        return None
    recent = candles[-(period + 1):]
    # Sum of individual ATR1 values (each candle's true range)
    atr1_sum = 0.0
    for i in range(1, len(recent)):
        h = recent[i]["high"]
        l = recent[i]["low"]
        pc = recent[i - 1]["close"]
        tr = max(h - l, abs(h - pc), abs(l - pc))
        atr1_sum += tr
    # Highest high and lowest low over the period
    period_high = max(c["high"] for c in recent[-period:])
    period_low  = min(c["low"]  for c in recent[-period:])
    price_range = period_high - period_low
    if price_range <= 0 or atr1_sum <= 0:
        return None
    try:
        ci = 100 * math.log10(atr1_sum / price_range) / math.log10(period)
    except (ValueError, ZeroDivisionError):
        return None
    return round(ci, 2)


#  v9.7 Helper: ICT Optimal Trade Entry (OTE) 

def detect_ote_zone(candles: list[dict], direction: str) -> dict | None:
    """
    v9.7 Feature 1: ICT Optimal Trade Entry (OTE) zone detection.
    OTE = 61.8% to 79% Fibonacci retracement of the last major swing.
    For a bullish move (direction="long"): find last swing low  swing high,
    OTE buy zone is a pullback to 61.8%79% of that impulse.
    For a bearish move (direction="short"): find last swing high  swing low,
    OTE sell zone is a pullback to 61.8%79% of that impulse.
    Returns dict with keys: swing_low, swing_high, ote_low, ote_high,
    current_price, in_ote (bool), candles_ago (int of swing origin).
    Returns None if insufficient candles or no clear swing found.
    """
    if len(candles) < 20:
        return None
    current_price = candles[-1]["close"]
    lookback = min(50, len(candles))
    recent = candles[-lookback:]

    # Find the most recent significant swing high and swing low
    highs = [(i, c["high"]) for i, c in enumerate(recent)]
    lows  = [(i, c["low"])  for i, c in enumerate(recent)]

    # Pick the absolute swing high and low from the lookback window
    swing_high_idx, swing_high = max(highs, key=lambda x: x[1])
    swing_low_idx,  swing_low  = min(lows,  key=lambda x: x[1])

    if swing_high <= swing_low:
        return None

    total_range = swing_high - swing_low

    if direction == "long":
        # Bullish impulse: swing_low formed before swing_high
        # OTE retracement: price pulls back 61.879% from the high
        ote_high = swing_high - total_range * 0.618
        ote_low  = swing_high - total_range * 0.79
        in_ote   = ote_low <= current_price <= ote_high
        candles_ago = len(recent) - 1 - swing_low_idx
    else:
        # Bearish impulse: swing_high formed before swing_low
        # OTE retracement: price pulls back 61.879% from the low
        ote_low  = swing_low + total_range * 0.618
        ote_high = swing_low + total_range * 0.79
        in_ote   = ote_low <= current_price <= ote_high
        candles_ago = len(recent) - 1 - swing_high_idx

    return {
        "swing_low":     swing_low,
        "swing_high":    swing_high,
        "ote_low":       ote_low,
        "ote_high":      ote_high,
        "current_price": current_price,
        "in_ote":        in_ote,
        "candles_ago":   max(0, candles_ago),
        "direction":     direction,
    }


#  v9.7 Helper: ICT Power of Three (PO3) 

def detect_power_of_three(candles: list[dict]) -> dict:
    """
    v9.7 Feature 3: ICT Power of Three (Accumulation  Manipulation  Distribution).
    Simplified detection:
      1. Accumulation: price consolidates in a tight range for >= 5 candles.
      2. Manipulation: price breaks below (bullish PO3) or above (bearish PO3) the range.
      3. Distribution: price closes back inside (or above/below) the range confirming reversal.
    Returns dict: {
        "detected": bool,
        "phase": "accumulation" | "manipulation" | "distribution" | None,
        "direction": "long" | "short" | None,   # long = bullish setup, short = bearish
        "range_high": float | None,
        "range_low":  float | None,
        "confidence": "high" | "medium" | "low",
        "description": str,
    }
    """
    if len(candles) < 15:
        return {"detected": False, "phase": None, "direction": None,
                "range_high": None, "range_low": None,
                "confidence": "low", "description": "Insufficient candles"}

    result = {
        "detected": False, "phase": None, "direction": None,
        "range_high": None, "range_low": None, "confidence": "low",
        "description": "No PO3 pattern detected",
    }

    # Look for consolidation in candles[-15:-5] (10 candle lookback window)
    consol_candles = candles[-15:-5]
    if len(consol_candles) < 5:
        return result

    consol_highs  = [c["high"]  for c in consol_candles]
    consol_lows   = [c["low"]   for c in consol_candles]
    consol_closes = [c["close"] for c in consol_candles]
    range_high = max(consol_highs)
    range_low  = min(consol_lows)
    range_size = range_high - range_low
    range_mid  = (range_high + range_low) / 2

    if range_mid <= 0:
        return result

    # Tight consolidation = range < 1.5% of mid price
    tight = (range_size / range_mid) < 0.015

    result["range_high"] = range_high
    result["range_low"]  = range_low

    if not tight:
        result["phase"] = "accumulation"
        result["description"] = (
            f"Potential accumulation zone ({range_low:.4f}{range_high:.4f})  "
            "waiting for manipulation signal"
        )
        result["confidence"] = "low"
        return result

    # Tight range found  now check the next candles[-5:-1] for manipulation + distribution
    manip_candles = candles[-5:-1]
    recent_c      = candles[-1]  # most recent (potential distribution)

    for i, mc in enumerate(manip_candles):
        # Bullish PO3: manipulation = break below range_low, then close back above
        if mc["low"] < range_low and mc["close"] >= range_low:
            # Candle dipped below and recovered  manipulation confirmed
            # Check if current candle closed above mid  distribution up
            if recent_c["close"] > range_mid:
                result.update({
                    "detected":    True,
                    "phase":       "distribution",
                    "direction":   "long",
                    "confidence":  "high",
                    "description": (
                        f"Bullish PO3 complete  consolidated {range_low:.4f}{range_high:.4f}, "
                        f"faked below {range_low:.4f} then reversed above range midpoint  long distribution"
                    ),
                })
                return result
            else:
                result.update({
                    "detected":    True,
                    "phase":       "manipulation",
                    "direction":   "long",
                    "confidence":  "medium",
                    "description": (
                        f"Bullish manipulation in progress  swept below {range_low:.4f}, "
                        "watching for close back above range mid"
                    ),
                })
                return result

        # Bearish PO3: manipulation = break above range_high, then close back below
        if mc["high"] > range_high and mc["close"] <= range_high:
            if recent_c["close"] < range_mid:
                result.update({
                    "detected":    True,
                    "phase":       "distribution",
                    "direction":   "short",
                    "confidence":  "high",
                    "description": (
                        f"Bearish PO3 complete  consolidated {range_low:.4f}{range_high:.4f}, "
                        f"faked above {range_high:.4f} then reversed below range midpoint  short distribution"
                    ),
                })
                return result
            else:
                result.update({
                    "detected":    True,
                    "phase":       "manipulation",
                    "direction":   "short",
                    "confidence":  "medium",
                    "description": (
                        f"Bearish manipulation in progress  swept above {range_high:.4f}, "
                        "watching for close back below range mid"
                    ),
                })
                return result

    # Tight range but no manipulation yet
    result["phase"]       = "accumulation"
    result["confidence"]  = "medium"
    result["description"] = (
        f"Tight accumulation range ({range_low:.4f}{range_high:.4f}, "
        f"{range_size/range_mid*100:.2f}% range)  waiting for manipulation sweep"
    )
    return result


#  v9.6 Helper: Donchian Channel 

def calc_donchian_channel(candles: list[dict], period: int = 20) -> dict | None:
    """
    v9.6 Feature 2: Donchian Channel over `period` candles.
    Returns {"upper": float, "lower": float, "middle": float}.
    Upper = highest high in period, Lower = lowest low, Middle = (upper+lower)/2.
    """
    if len(candles) < period:
        return None
    recent = candles[-period:]
    upper  = max(c["high"] for c in recent)
    lower  = min(c["low"]  for c in recent)
    middle = (upper + lower) / 2
    return {"upper": upper, "lower": lower, "middle": middle}


#  v9.8 Helper: ICT Dealing Range 

def detect_dealing_range(candles: list[dict], lookback: int = 50) -> dict:
    """
    v9.8 Feature 1: ICT Dealing Range  divide the lookback range into premium/discount zones.
    Premium:      above 61.8% of range
    Equilibrium:  38.2%61.8% of range
    Discount:     below 38.2% of range
    Deep Discount: below 23.6% of range
    Returns dict with key levels and current_zone.
    """
    if len(candles) < lookback:
        recent = candles
    else:
        recent = candles[-lookback:]
    if not recent:
        return {
            "high": 0, "low": 0, "range": 0,
            "equilibrium": 0, "premium_threshold": 0,
            "discount_threshold": 0, "deep_discount_threshold": 0,
            "current_zone": "unknown",
        }
    rng_high = max(c["high"] for c in recent)
    rng_low  = min(c["low"]  for c in recent)
    rng_size = rng_high - rng_low
    current_price = candles[-1]["close"]

    premium_threshold      = rng_low + rng_size * 0.618
    equilibrium            = rng_low + rng_size * 0.500
    discount_threshold     = rng_low + rng_size * 0.382
    deep_discount_threshold = rng_low + rng_size * 0.236

    if rng_size == 0:
        current_zone = "unknown"
    elif current_price >= premium_threshold:
        current_zone = "premium"
    elif current_price >= discount_threshold:
        current_zone = "equilibrium"
    elif current_price >= deep_discount_threshold:
        current_zone = "discount"
    else:
        current_zone = "deep_discount"

    return {
        "high": rng_high,
        "low": rng_low,
        "range": rng_size,
        "equilibrium": equilibrium,
        "premium_threshold": premium_threshold,
        "discount_threshold": discount_threshold,
        "deep_discount_threshold": deep_discount_threshold,
        "current_zone": current_zone,
    }


#  v9.8 Helper: ICT Breaker Block 

def detect_breaker_block(candles: list[dict], direction: str) -> dict:
    """
    v9.8 Feature 2: A breaker block is a mitigated order block that now acts
    as support/resistance in the opposite direction.
    For LONG:  find a bearish OB (down candle) that price has since traded through
               and closed above  now acts as support.
    For SHORT: find a bullish OB (up candle) that price has since traded through
               and closed below  now acts as resistance.
    Returns dict: {found, level, zone_high, zone_low, type}
    """
    result = {"found": False, "level": 0.0, "zone_high": 0.0, "zone_low": 0.0, "type": None}
    if len(candles) < 10:
        return result

    n = len(candles)
    # Scan candles from oldest to newest (excluding last few) looking for mitigated OBs
    for i in range(n - 8, 0, -1):
        ob_candle = candles[i]
        if direction == "long":
            # Bearish OB: down candle (close < open)
            if ob_candle["close"] >= ob_candle["open"]:
                continue
            ob_high = ob_candle["high"]
            ob_low  = ob_candle["low"]
            # Check if any subsequent candle closed ABOVE the OB high (price swept through it)
            swept = False
            for j in range(i + 1, n):
                if candles[j]["close"] > ob_high:
                    swept = True
                    break
            if swept:
                # This bearish OB is now a breaker block acting as support
                result = {
                    "found": True,
                    "level": (ob_high + ob_low) / 2,
                    "zone_high": ob_high,
                    "zone_low": ob_low,
                    "type": "support",
                }
                return result  # return most recent one found
        elif direction == "short":
            # Bullish OB: up candle (close > open)
            if ob_candle["close"] <= ob_candle["open"]:
                continue
            ob_high = ob_candle["high"]
            ob_low  = ob_candle["low"]
            # Check if any subsequent candle closed BELOW the OB low (price swept through it)
            swept = False
            for j in range(i + 1, n):
                if candles[j]["close"] < ob_low:
                    swept = True
                    break
            if swept:
                result = {
                    "found": True,
                    "level": (ob_high + ob_low) / 2,
                    "zone_high": ob_high,
                    "zone_low": ob_low,
                    "type": "resistance",
                }
                return result
    return result


#  v9.6 Helper: Range Expansion 

def detect_range_expansion(candles: list[dict], lookback: int = 10) -> dict:
    """
    v9.6 Feature 4: Detect if the most recent candle's range is >2 the average
    range of the last `lookback` candles (excluding the most recent).
    Returns {"expansion": bool, "ratio": float, "direction": "bullish"|"bearish"|None}.
    direction is "bullish" if the expanding candle closed up, "bearish" if down.
    """
    if len(candles) < lookback + 1:
        return {"expansion": False, "ratio": 1.0, "direction": None}
    prev_candles = candles[-(lookback + 1):-1]
    ranges = [c["high"] - c["low"] for c in prev_candles]
    avg_range = statistics.mean(ranges) if ranges else 0
    last = candles[-1]
    last_range = last["high"] - last["low"]
    if avg_range <= 0:
        return {"expansion": False, "ratio": 1.0, "direction": None}
    ratio = last_range / avg_range
    if ratio > 2.0:
        candle_dir = "bullish" if last["close"] >= last["open"] else "bearish"
        return {"expansion": True, "ratio": ratio, "direction": candle_dir}
    return {"expansion": False, "ratio": ratio, "direction": None}


#  v9.6 Helper: EMA Ribbon (EMA5/8/13/21) 

def calc_ema_ribbon(candles: list[dict]) -> dict | None:
    """
    v9.6 Feature 5/6: Compute EMA 5, 8, 13, 21 ribbon for trend alignment.
    Returns {
        "ema5": float, "ema8": float, "ema13": float, "ema21": float,
        "aligned_bull": bool,   # EMA5 > EMA8 > EMA13 > EMA21
        "aligned_bear": bool,   # EMA5 < EMA8 < EMA13 < EMA21
        "partial_bull": int,    # count of consecutive bull orderings (top-down)
        "partial_bear": int,    # count of consecutive bear orderings (top-down)
    }
    """
    if len(candles) < 21:
        return None
    closes = [c["close"] for c in candles]
    e5  = ema(closes, 5)
    e8  = ema(closes, 8)
    e13 = ema(closes, 13)
    e21 = ema(closes, 21)
    if any(v is None for v in (e5, e8, e13, e21)):
        return None
    aligned_bull = e5 > e8 > e13 > e21
    aligned_bear = e5 < e8 < e13 < e21
    # Partial: count consecutive ordered pairs from top
    bull_pairs = [(e5, e8), (e8, e13), (e13, e21)]
    bear_pairs = [(e5, e8), (e8, e13), (e13, e21)]
    partial_bull = sum(1 for a, b in bull_pairs if a > b)
    partial_bear = sum(1 for a, b in bear_pairs if a < b)
    return {
        "ema5": e5, "ema8": e8, "ema13": e13, "ema21": e21,
        "aligned_bull": aligned_bull,
        "aligned_bear": aligned_bear,
        "partial_bull": partial_bull,
        "partial_bear": partial_bear,
    }


def is_momentum_candle(candles: list[dict], direction: str, body_ratio: float = 0.6) -> bool:
    """Check if the most recent candle is a strong-bodied momentum candle (not a doji/spinning top).
    body_ratio: body must be at least this fraction of the total candle range.
    A doji or indecision candle is a weak signal  we want conviction behind the move."""
    if not candles:
        return False
    last = candles[-1]
    total_range = last["high"] - last["low"]
    if total_range == 0:
        return False
    body = abs(last["close"] - last["open"])
    ratio = body / total_range
    if ratio < body_ratio:
        return False  # doji / indecision
    # Also check direction: bull candle for long, bear candle for short
    if direction == "long" and last["close"] <= last["open"]:
        return False  # bearish candle  no momentum
    if direction == "short" and last["close"] >= last["open"]:
        return False  # bullish candle  no momentum
    return True


def stoch_rsi(closes: list[float], period: int = 14, smooth_k: int = 3) -> float | None:
    """Stochastic RSI  RSI smoothed via stochastic formula. Returns %K (0-100).
    Oversold < 20, overbought > 80."""
    if len(closes) < period * 2:
        return None
    rsi_series = []
    for i in range(period, len(closes)):
        r = rsi(closes[:i+1], period)
        if r is not None:
            rsi_series.append(r)
    if len(rsi_series) < period:
        return None
    recent_rsi = rsi_series[-period:]
    rsi_min = min(recent_rsi)
    rsi_max = max(recent_rsi)
    if rsi_max == rsi_min:
        return 50.0
    raw_k = (rsi_series[-1] - rsi_min) / (rsi_max - rsi_min) * 100
    # Smooth %K over smooth_k periods
    if len(rsi_series) >= smooth_k:
        smooth_vals = [(rsi_series[i] - min(rsi_series[i-period+1:i+1])) / max(1e-9, max(rsi_series[i-period+1:i+1]) - min(rsi_series[i-period+1:i+1])) * 100
                       for i in range(period - 1, len(rsi_series)) if len(rsi_series[i-period+1:i+1]) == period]
        if smooth_vals and len(smooth_vals) >= smooth_k:
            return statistics.mean(smooth_vals[-smooth_k:])
    return raw_k


def detect_bb_squeeze(candles: list[dict], period: int = 20, squeeze_pct: float = 0.015) -> bool:
    """Bollinger Band squeeze  bands within squeeze_pct of price  volatility contraction  breakout imminent.
    Returns True if bands are compressed (good entry timing)."""
    if len(candles) < period:
        return False
    closes = [c["close"] for c in candles[-period:]]
    mean_price = statistics.mean(closes)
    stdev = statistics.stdev(closes)
    upper = mean_price + 2 * stdev
    lower = mean_price - 2 * stdev
    band_width = (upper - lower) / mean_price  # normalized bandwidth
    return band_width < squeeze_pct  # tight bands = squeeze


def calc_bb_width_trend(candles: list[dict], period: int = 20, lookback: int = 5) -> dict | None:
    """
    Calculate Bollinger Band width and its trend (expanding vs contracting).
    Returns dict: {width, width_prev, expanding, contracting, squeeze_pct}
    """
    if len(candles) < period + lookback:
        return None

    def band_width(subset: list[dict]) -> float:
        closes = [c["close"] for c in subset[-period:]]
        if len(closes) < period:
            return 0.0
        mean_p = statistics.mean(closes)
        stdev = statistics.stdev(closes)
        if mean_p <= 0:
            return 0.0
        return (mean_p + 2 * stdev - (mean_p - 2 * stdev)) / mean_p

    width_now  = band_width(candles)
    width_prev = band_width(candles[:-lookback])

    expanding   = width_now > width_prev * 1.05   # bands growing 5%+
    contracting = width_now < width_prev * 0.95   # bands shrinking 5%+

    return {
        "width":       width_now,
        "width_prev":  width_prev,
        "expanding":   expanding,
        "contracting": contracting,
        "squeeze":     width_now < 0.015,  # tight band
    }


#  v9.0: Heikin Ashi conversion 

def to_heikin_ashi(candles: list[dict]) -> list[dict]:
    """Convert standard OHLC candles to Heikin Ashi candles.
    HA_Close = (O+H+L+C)/4
    HA_Open  = (prev_HA_Open + prev_HA_Close)/2  (first bar: same as first regular open)
    HA_High  = max(H, HA_Open, HA_Close)
    HA_Low   = min(L, HA_Open, HA_Close)
    """
    if not candles:
        return []
    ha = []
    prev_ha_open  = candles[0]["open"]
    prev_ha_close = (candles[0]["open"] + candles[0]["high"] + candles[0]["low"] + candles[0]["close"]) / 4
    for c in candles:
        ha_close = (c["open"] + c["high"] + c["low"] + c["close"]) / 4
        ha_open  = (prev_ha_open + prev_ha_close) / 2
        ha_high  = max(c["high"], ha_open, ha_close)
        ha_low   = min(c["low"],  ha_open, ha_close)
        ha.append({
            "time":   c["time"],
            "open":   ha_open,
            "high":   ha_high,
            "low":    ha_low,
            "close":  ha_close,
            "volume": c.get("volume", 0),
        })
        prev_ha_open  = ha_open
        prev_ha_close = ha_close
    return ha


def count_consecutive_ha_candles(candles: list[dict]) -> tuple[int, str]:
    """Count how many consecutive same-colored HA candles are at the end of the series.
    Returns (count, 'green'|'red'|'none').
    A green HA candle: close > open. A red HA candle: close < open."""
    if not candles:
        return 0, "none"
    last = candles[-1]
    color = "green" if last["close"] >= last["open"] else "red"
    count = 0
    for c in reversed(candles):
        c_color = "green" if c["close"] >= c["open"] else "red"
        if c_color == color:
            count += 1
        else:
            break
    return count, color


#  v9.0: Keltner Channel 

def calc_keltner_channel(candles: list[dict], ema_period: int = 20, atr_period: int = 14, multiplier: float = 1.5) -> dict | None:
    """Compute Keltner Channel: middle=EMA(close, 20), upper/lower = middle  1.5*ATR.
    Returns {"upper": float, "middle": float, "lower": float} or None."""
    if len(candles) < max(ema_period, atr_period) + 2:
        return None
    closes = [c["close"] for c in candles]
    mid = ema(closes, ema_period)
    atr_val = calc_atr(candles, atr_period)
    if mid is None or atr_val is None:
        return None
    return {
        "upper":  mid + multiplier * atr_val,
        "middle": mid,
        "lower":  mid - multiplier * atr_val,
    }


def detect_keltner_squeeze(candles: list[dict]) -> bool:
    """Return True if BB(20,2) is narrower than Keltner Channel(20,14,1.5)  confirmed squeeze."""
    if len(candles) < 22:
        return False
    closes = [c["close"] for c in candles[-20:]]
    bb_mean = statistics.mean(closes)
    bb_std  = statistics.stdev(closes)
    bb_upper = bb_mean + 2 * bb_std
    bb_lower = bb_mean - 2 * bb_std
    kc = calc_keltner_channel(candles)
    if kc is None:
        return False
    # BB is inside KC when BB upper < KC upper AND BB lower > KC lower
    return bb_upper < kc["upper"] and bb_lower > kc["lower"]


#  v9.0: Gap / FVG detection 

def detect_gap(candles: list[dict], gap_pct: float = 0.003) -> dict | None:
    """Detect a simple price gap: current open vs previous close > gap_pct.
    Returns {"type": "up"|"down", "size_pct": float} or None."""
    if len(candles) < 2:
        return None
    prev_close = candles[-2]["close"]
    curr_open  = candles[-1]["open"]
    if prev_close == 0:
        return None
    gap = (curr_open - prev_close) / prev_close
    if abs(gap) >= gap_pct:
        return {"type": "up" if gap > 0 else "down", "size_pct": gap}
    return None


def detect_fvg_zones(candles: list[dict]) -> list[dict]:
    """Detect Fair Value Gaps (ICT FVG): 3-candle imbalance.
    Bullish FVG:  candle[i-2].high < candle[i].low   gap above between them
    Bearish FVG:  candle[i-2].low  > candle[i].high  gap below between them
    Returns list of {"type","top","bottom","index","candles_ago"} most recent first."""
    fvgs = []
    n = len(candles)
    for i in range(2, n):
        c0, c2 = candles[i - 2], candles[i]
        candles_ago = n - 1 - i
        if c2["low"] > c0["high"]:   # bullish FVG
            fvgs.append({"type": "bullish", "top": c2["low"], "bottom": c0["high"],
                         "index": i, "candles_ago": candles_ago})
        elif c2["high"] < c0["low"]: # bearish FVG
            fvgs.append({"type": "bearish", "top": c0["low"], "bottom": c2["high"],
                         "index": i, "candles_ago": candles_ago})
    fvgs.sort(key=lambda x: x["index"], reverse=True)
    return fvgs


def detect_market_regime(candles_4h: list[dict], lookback: int = 20) -> str:
    """
    Detect the current market regime from 4H candles.
    Returns one of: "Trending Up", "Trending Down", "Ranging".

    Rules:
      Trending Up:   price > 20-period SMA AND SMA is sloping up (last SMA > prior SMA)
      Trending Down: price < 20-period SMA AND SMA is sloping down
      Ranging:       price crossing SMA frequently (crossings >= 4 in lookback) OR BB width very low

    v8.8 Feature 4.
    """
    if not candles_4h or len(candles_4h) < lookback + 5:
        return "Ranging"

    recent = candles_4h[-lookback:]
    closes = [c["close"] for c in recent]

    # 20-period SMA of the most recent candle vs the prior SMA (5 candles back)
    sma_now  = sum(closes) / len(closes)
    prior_closes = [c["close"] for c in candles_4h[-(lookback + 5):-5]]
    sma_prior = sum(prior_closes) / len(prior_closes) if prior_closes else sma_now
    price = closes[-1]

    sma_slope_up   = sma_now > sma_prior
    sma_slope_down = sma_now < sma_prior

    # Count crossings of price vs SMA within the lookback window
    crossings = 0
    for i in range(1, len(closes)):
        sma_i = sum(closes[:i+1]) / (i + 1)
        sma_prev = sum(closes[:i]) / i if i > 0 else sma_i
        if (closes[i] > sma_i and closes[i-1] < sma_prev) or \
           (closes[i] < sma_i and closes[i-1] > sma_prev):
            crossings += 1

    # BB width on recent 4H
    if len(closes) >= 20:
        import statistics as _stats
        _bb_std = _stats.stdev(closes[-20:])
        _bb_mean = _stats.mean(closes[-20:])
        bb_width_pct = (4 * _bb_std / _bb_mean) if _bb_mean > 0 else 1.0
    else:
        bb_width_pct = 1.0

    if crossings >= 4 or bb_width_pct < 0.03:
        return "Ranging"
    if price > sma_now and sma_slope_up:
        return "Trending Up"
    if price < sma_now and sma_slope_down:
        return "Trending Down"
    return "Ranging"


def detect_volatility_regime(candles_1h: list[dict], lookback: int = 20) -> str:
    """
    v9.4 Feature 2: Detect the current volatility regime from 1H candles.
    Uses ATR as a percentage of price over the last `lookback` candles.
    Returns one of: "High" (ATR > 2% of price), "Normal" (0.5-2%), "Low" (<0.5%).
    """
    if not candles_1h or len(candles_1h) < lookback + 1:
        return "Normal"
    atr_val = calc_atr(candles_1h[-lookback - 1:], period=min(14, lookback))
    if atr_val is None:
        return "Normal"
    price = candles_1h[-1]["close"]
    if price <= 0:
        return "Normal"
    atr_pct = atr_val / price * 100
    if atr_pct > 2.0:
        return "High"
    elif atr_pct < 0.5:
        return "Low"
    return "Normal"


def detect_swing_failure_pattern(candles: list[dict], direction: str, lookback: int = 20) -> bool:
    """
    Swing Failure Pattern (SFP)  high-probability reversal signal.

    Bullish SFP (for LONG signals):
      - Candle wicks BELOW a prior swing low (sweeping sell-side liquidity)
      - But the candle CLOSES above that swing low
      -  Trapped shorts, smart money bought the dip

    Bearish SFP (for SHORT signals):
      - Candle wicks ABOVE a prior swing high (sweeping buy-side liquidity)
      - But the candle CLOSES below that swing high
      -  Trapped longs, smart money sold the rally

    Returns True if SFP detected on the most recent candle.
    """
    if len(candles) < lookback + 1:
        return False

    recent = candles[-(lookback + 1):-1]   # prior candles for swing reference
    last   = candles[-1]                    # current (most recent) candle

    if direction == "long":
        # Find the lowest swing low in the recent window
        swing_low = min(c["low"] for c in recent)
        # SFP: current wick went below the swing low but closed above it
        return last["low"] < swing_low and last["close"] > swing_low

    else:  # short
        # Find the highest swing high in the recent window
        swing_high = max(c["high"] for c in recent)
        # SFP: current wick went above the swing high but closed below it
        return last["high"] > swing_high and last["close"] < swing_high


def find_equal_highs_lows(candles: list[dict], tolerance: float = 0.001) -> dict:
    """Find equal highs and equal lows (liquidity pools)."""
    swings = find_swing_highs_lows(candles)
    equal_highs = []
    equal_lows = []

    highs = [s["price"] for s in swings["highs"]]
    lows = [s["price"] for s in swings["lows"]]

    for i, h in enumerate(highs):
        for j, h2 in enumerate(highs):
            if i != j and abs(h - h2) / h < tolerance:
                if h not in equal_highs:
                    equal_highs.append(h)

    for i, l in enumerate(lows):
        for j, l2 in enumerate(lows):
            if i != j and abs(l - l2) / l < tolerance:
                if l not in equal_lows:
                    equal_lows.append(l)

    return {"equal_highs": equal_highs, "equal_lows": equal_lows}


def calc_macd(prices: list[float], fast: int = 12, slow: int = 26, signal: int = 9) -> dict | None:
    """
    Compute MACD line, signal line, and histogram.
    MACD = EMA(fast) - EMA(slow)
    Signal = EMA(signal) of MACD series
    Histogram = MACD - Signal
    Returns dict with macd, signal_line, histogram, and series lists, or None if insufficient data.
    """
    if len(prices) < slow + signal + 5:
        return None

    # Build EMA fast and slow series across all prices
    k_fast = 2 / (fast + 1)
    k_slow = 2 / (slow + 1)

    ema_fast = sum(prices[:fast]) / fast
    ema_slow = sum(prices[:slow]) / slow

    macd_series = []
    for i in range(slow, len(prices)):
        ema_fast = prices[i] * k_fast + ema_fast * (1 - k_fast)
        ema_slow = prices[i] * k_slow + ema_slow * (1 - k_slow)
        macd_series.append(ema_fast - ema_slow)

    if len(macd_series) < signal:
        return None

    # Signal line = EMA(signal) of MACD series
    k_sig = 2 / (signal + 1)
    sig_val = sum(macd_series[:signal]) / signal
    signal_series = [sig_val]
    for m in macd_series[signal:]:
        sig_val = m * k_sig + sig_val * (1 - k_sig)
        signal_series.append(sig_val)

    macd_val = macd_series[-1]
    sig_last = signal_series[-1]
    hist = macd_val - sig_last

    return {
        "macd": macd_val,
        "signal_line": sig_last,
        "histogram": hist,
        "macd_series": macd_series,
        "signal_series": signal_series,
    }


def detect_doji(candle: dict, threshold: float = 0.1) -> bool:
    """
    Detect a doji candle: body <= threshold * total_range (high - low).
    A doji has a very small body relative to total candle range  indecision.
    """
    total_range = candle["high"] - candle["low"]
    if total_range <= 0:
        return False
    body = abs(candle["close"] - candle["open"])
    return body <= threshold * total_range


def detect_hammer_or_star(candle: dict) -> str | None:
    """
    Detect a hammer or shooting star candle.
    Hammer: lower wick >= 2x body, upper wick <= 0.5x body, small body.
    Shooting Star: upper wick >= 2x body, lower wick <= 0.5x body, small body.
    Returns "hammer", "shooting_star", or None.
    """
    high  = candle["high"]
    low   = candle["low"]
    open_ = candle["open"]
    close = candle["close"]
    total_range = high - low
    if total_range <= 0:
        return None
    body_top    = max(open_, close)
    body_bottom = min(open_, close)
    body        = body_top - body_bottom
    upper_wick  = high - body_top
    lower_wick  = body_bottom - low

    if body <= 0:
        return None

    # Hammer: long lower wick, small upper wick
    if lower_wick >= 2 * body and upper_wick <= 0.5 * body:
        return "hammer"
    # Shooting star: long upper wick, small lower wick
    if upper_wick >= 2 * body and lower_wick <= 0.5 * body:
        return "shooting_star"
    return None


def detect_engulfing(candles: list[dict], direction: str) -> bool:
    """Detect a bullish or bearish engulfing candle pattern.
    Bullish engulfing: current candle is bullish and its body fully engulfs the prior bearish candle body.
    Bearish engulfing: current candle is bearish and its body fully engulfs the prior bullish candle body.
    Strong reversal signal when at a key level (POI, swept zone)."""
    if len(candles) < 2:
        return False
    prev = candles[-2]
    curr = candles[-1]
    if direction == "long":
        # Prev must be bearish, curr must be bullish and engulf prev body
        prev_bear = prev["close"] < prev["open"]
        curr_bull = curr["close"] > curr["open"]
        if not (prev_bear and curr_bull):
            return False
        # Engulf: current body fully covers previous body
        return curr["close"] >= prev["open"] and curr["open"] <= prev["close"]
    else:  # short
        # Prev must be bullish, curr must be bearish and engulf prev body
        prev_bull = prev["close"] > prev["open"]
        curr_bear = curr["close"] < curr["open"]
        if not (prev_bull and curr_bear):
            return False
        return curr["close"] <= prev["open"] and curr["open"] >= prev["close"]


def analyze_candle_structure(candle: dict) -> dict:
    """
    Analyze a single candle's body and wick components.
    Returns dict with upper_wick, lower_wick, body, total_range, is_bullish.
    Used for v8.1 candle body/wick scoring.
    """
    high  = candle["high"]
    low   = candle["low"]
    open_ = candle["open"]
    close = candle["close"]
    total_range = high - low
    is_bullish  = close >= open_
    body_top    = max(open_, close)
    body_bottom = min(open_, close)
    body        = body_top - body_bottom
    upper_wick  = high - body_top
    lower_wick  = body_bottom - low
    return {
        "upper_wick":  upper_wick,
        "lower_wick":  lower_wick,
        "body":        body,
        "total_range": total_range,
        "is_bullish":  is_bullish,
    }


def detect_pin_bar(candles: list[dict], direction: str, wick_ratio: float = 0.6) -> bool:
    """Detect a pin bar (hammer / shooting star) rejection candle.
    For LONG: long lower wick (rejection of lower price)  wick_ratio of total range, small body.
    For SHORT: long upper wick (rejection of higher price)  wick_ratio of total range, small body.
    Pin bars at swept zones are extremely high-probability reversal signals."""
    if not candles:
        return False
    c = candles[-1]
    total_range = c["high"] - c["low"]
    if total_range == 0:
        return False
    body = abs(c["close"] - c["open"])
    body_pct = body / total_range

    if direction == "long":
        # Lower wick = distance from candle low to body bottom
        body_bottom = min(c["open"], c["close"])
        lower_wick = body_bottom - c["low"]
        wick_pct = lower_wick / total_range
        # Long lower wick + small body = hammer
        return wick_pct >= wick_ratio and body_pct <= 0.3
    else:
        # Upper wick = distance from body top to candle high
        body_top = max(c["open"], c["close"])
        upper_wick = c["high"] - body_top
        wick_pct = upper_wick / total_range
        # Long upper wick + small body = shooting star
        return wick_pct >= wick_ratio and body_pct <= 0.3


def detect_three_line_strike(candles: list[dict]) -> str | None:
    """Detect a three-line strike pattern from the last 4 candles.
    Bearish: three consecutive bullish candles + one large bearish candle that engulfs all three.
    Bullish: three consecutive bearish candles + one large bullish candle that engulfs all three.
    Returns 'bearish', 'bullish', or None."""
    if len(candles) < 4:
        return None
    c1, c2, c3, c4 = candles[-4], candles[-3], candles[-2], candles[-1]

    def is_bullish(c):
        return c["close"] > c["open"]

    def is_bearish(c):
        return c["close"] < c["open"]

    # Bearish three-line strike: 3 bullish candles, then large bearish engulfing all three
    if (is_bullish(c1) and is_bullish(c2) and is_bullish(c3) and is_bearish(c4)):
        if c4["open"] >= c3["close"] and c4["close"] <= c1["open"]:
            return "bearish"

    # Bullish three-line strike: 3 bearish candles, then large bullish engulfing all three
    if (is_bearish(c1) and is_bearish(c2) and is_bearish(c3) and is_bullish(c4)):
        if c4["open"] <= c3["close"] and c4["close"] >= c1["open"]:
            return "bullish"

    return None


def detect_pin_bar_single(candle: dict) -> str | None:
    """Detect a pin bar from a single candle dict (66% wick threshold).
    Bullish pin bar: long lower wick >= 66% of total range AND body in upper 33%.
    Bearish pin bar: long upper wick >= 66% of total range AND body in lower 33%.
    Returns 'bullish', 'bearish', or None."""
    total_range = candle["high"] - candle["low"]
    if total_range == 0:
        return None
    body_top = max(candle["open"], candle["close"])
    body_bottom = min(candle["open"], candle["close"])
    body = body_top - body_bottom
    lower_wick = body_bottom - candle["low"]
    upper_wick = candle["high"] - body_top
    wick_threshold = 0.66

    # Bullish: long lower wick, body in upper 33%
    if lower_wick / total_range >= wick_threshold and body / total_range <= 0.34:
        return "bullish"

    # Bearish: long upper wick, body in lower 33%
    if upper_wick / total_range >= wick_threshold and body / total_range <= 0.34:
        return "bearish"

    return None


def calc_stoch_rsi(closes: list[float], rsi_period: int = 14, stoch_period: int = 14) -> float | None:
    """Calculate Stochastic RSI value (0100).
    Computes RSI, then applies Stochastic formula over the last stoch_period RSI values.
    Returns None if insufficient data."""
    if len(closes) < rsi_period + stoch_period + 1:
        return None

    # Compute RSI series
    rsi_series = []
    for i in range(rsi_period, len(closes) + 1):
        window = closes[i - rsi_period - 1:i]
        if len(window) < rsi_period + 1:
            continue
        gains = [max(window[j] - window[j-1], 0) for j in range(1, len(window))]
        losses = [max(window[j-1] - window[j], 0) for j in range(1, len(window))]
        avg_gain = sum(gains) / rsi_period
        avg_loss = sum(losses) / rsi_period
        if avg_loss == 0:
            rsi_series.append(100.0)
        else:
            rs = avg_gain / avg_loss
            rsi_series.append(100 - (100 / (1 + rs)))

    if len(rsi_series) < stoch_period:
        return None

    rsi_window = rsi_series[-stoch_period:]
    rsi_min = min(rsi_window)
    rsi_max = max(rsi_window)
    if rsi_max == rsi_min:
        return None
    stoch_rsi_val = (rsi_series[-1] - rsi_min) / (rsi_max - rsi_min) * 100
    return stoch_rsi_val


def detect_inside_bar(candles: list[dict]) -> bool:
    """Return True if the most recent candle is an inside bar relative to the previous candle.
    Inside bar: current high < previous high AND current low > previous low. (v8.4)"""
    if not candles or len(candles) < 2:
        return False
    curr = candles[-1]
    prev = candles[-2]
    return curr["high"] < prev["high"] and curr["low"] > prev["low"]


def detect_sr_zones(candles: list[dict], lookback: int = 30) -> list[dict]:
    """Detect up to 3 support/resistance zones from recent price action. (v8.4)
    A zone forms where price reversed at least twice within 0.5% of each other.
    Returns list of {"level": float, "touches": int, "type": "support"|"resistance"}."""
    if not candles or len(candles) < lookback:
        return []
    window = candles[-lookback:]
    reversal_levels: list[float] = []
    for i in range(1, len(window) - 1):
        c_prev = window[i - 1]
        c_curr = window[i]
        c_next = window[i + 1]
        # Swing high
        if c_curr["high"] > c_prev["high"] and c_curr["high"] > c_next["high"]:
            reversal_levels.append(c_curr["high"])
        # Swing low
        if c_curr["low"] < c_prev["low"] and c_curr["low"] < c_next["low"]:
            reversal_levels.append(c_curr["low"])

    if not reversal_levels:
        return []

    # Cluster levels within 0.5% of each other
    current_price = candles[-1]["close"]
    clusters: list[dict] = []
    used = [False] * len(reversal_levels)
    for i, lvl in enumerate(reversal_levels):
        if used[i]:
            continue
        cluster = [lvl]
        used[i] = True
        for j in range(i + 1, len(reversal_levels)):
            if not used[j] and abs(reversal_levels[j] - lvl) / lvl < 0.005:
                cluster.append(reversal_levels[j])
                used[j] = True
        if len(cluster) >= 2:
            zone_level = sum(cluster) / len(cluster)
            zone_type = "support" if zone_level < current_price else "resistance"
            clusters.append({"level": zone_level, "touches": len(cluster), "type": zone_type})

    # Sort by touches desc, return top 3
    clusters.sort(key=lambda x: x["touches"], reverse=True)
    return clusters[:3]


def find_next_htf_level(candles_1h: list[dict], direction: str, current_price: float) -> float | None:
    """Find the next significant swing level on the 1H chart as a dynamic take-profit target.
    For LONG: next swing high above current price (resistance).
    For SHORT: next swing low below current price (support).
    Returns None if no clear level found."""
    if not candles_1h or len(candles_1h) < 20:
        return None
    swings = find_swing_highs_lows(candles_1h, lookback=3)
    if direction == "long":
        # Find the nearest swing high above current price
        highs_above = [h["price"] for h in swings["highs"] if h["price"] > current_price * 1.002]
        if highs_above:
            return min(highs_above)  # nearest resistance
    else:
        # Find the nearest swing low below current price
        lows_below = [l["price"] for l in swings["lows"] if l["price"] < current_price * 0.998]
        if lows_below:
            return max(lows_below)  # nearest support
    return None


# 
# SESSIONS & TIME HELPERS
# 

def is_edt() -> bool:
    """Check if current time is in EDT (UTC-4)."""
    now = datetime.now(timezone.utc)
    # EDT: second Sunday March  first Sunday November
    # Simplified check: months 3-10 = EDT, rest = EST
    month = now.month
    return 3 <= month <= 11


def is_trading_session() -> bool:
    """Return True if currently in a major trading session."""
    now = datetime.now(timezone.utc)
    offset = -4 if is_edt() else -5
    local_hour = (now.hour + offset) % 24
    # London: 3am12pm ET, NY: 8am5pm ET
    return (3 <= local_hour < 12) or (8 <= local_hour < 17)


def session_label() -> str:
    """Return name of current session."""
    now = datetime.now(timezone.utc)
    offset = -4 if is_edt() else -5
    local_hour = (now.hour + offset) % 24
    if 8 <= local_hour < 17:
        return "New York"
    if 3 <= local_hour < 12:
        return "London"
    if 19 <= local_hour or local_hour < 3:
        return "Asia"
    return "Off-Hours"


# Manual scan pause/resume (set by !pause / !resume commands)
_scan_manually_paused: bool = False
_scan_paused_until: float = 0.0  # epoch; 0 = indefinite pause until !resume

# Adaptive scan frequency (v8.5): updated each cycle based on BB width
# BB width > 2%  60s, BB squeeze < 0.5%  180s, normal  SCAN_INTERVAL
SCAN_INTERVAL: int = 300  # default 5 min
current_scan_interval: int = SCAN_INTERVAL

# Active timer tasks per user (v8.5): user_id -> asyncio.Task
_active_timers: dict[int, asyncio.Task] = {}

# Alert posting toggle  when False, signals are logged but no Discord embed is posted
ALERTS_ENABLED: bool = True


def is_news_dead_zone() -> bool:
    """Dead zone disabled — bot scans 24/7."""
    return False


def session_sl_multiplier() -> float:
    """
    Return SL width multiplier based on current session.
    Asian session = 1.3x (lower liquidity, wider fake-outs).
    London/NY = 1.0x (normal).
    """
    label = session_label()
    if label == "Asia":
        return 1.3
    return 1.0


# 
# PRICE FORMATTING
# 

def price_fmt(pair_label: str, price: float) -> str:
    """Format price based on pair type."""
    if pair_label in ("BTC/USD",):
        return f"${price:,.0f}"
    if pair_label in ("GOLD", "NASDAQ"):
        return f"${price:,.2f}"
    return f"${price:.4f}"


def calc_position_size(entry: float, sl: float, account_size: float = DEFAULT_ACCOUNT_SIZE, risk_pct: float = DEFAULT_RISK_PCT) -> dict:
    """
    Calculate suggested position size based on fixed % risk.
    Default: $10,000 account, 1% risk per trade.
    Returns dict with units, risk_usd, risk_pct, r2_reward_usd.
    """
    risk_usd = account_size * risk_pct
    sl_dist = abs(entry - sl)
    if sl_dist <= 0:
        return {"units": 0, "risk_usd": risk_usd, "risk_pct": risk_pct * 100}
    units = risk_usd / sl_dist
    return {
        "units": units,
        "risk_usd": risk_usd,
        "sl_dist": sl_dist,
        "risk_pct": risk_pct * 100,
    }


# 
# WHY THIS TRADE EXPLANATION
# 

def signal_strength_meter(score: int, max_display: int = 18) -> str:
    """Visual signal strength meter on a 010 block scale (v8.6 Feature 1).
    Represents score as fraction of max_display (18 = 'strong signal' ceiling).
    E.g. score=9, max=18  5 filled blocks = ' 9/10'
    """
    bar_len = 10
    clamped = min(score, max_display)
    filled = round(clamped / max_display * bar_len)
    empty = bar_len - filled
    bar = "" * filled + "" * empty
    strength_label = "Very Strong" if score >= 15 else "Strong" if score >= 12 else "Moderate" if score >= 9 else "Developing"
    return f"`{bar}` {filled}/10  {strength_label}"


def score_bar(score: int, max_score: int = 20) -> str:
    """Visual score bar using block chars. e.g. score=9/20  ' 9/20'"""
    filled = min(score, max_score)
    bar_len = 10
    filled_blocks = round(filled / max_score * bar_len)
    empty_blocks = bar_len - filled_blocks
    bar = "" * filled_blocks + "" * empty_blocks
    # Color hint using emoji prefix
    if score >= 12:
        star = ""
    elif score >= 9:
        star = ""
    elif score >= 7:
        star = ""
    else:
        star = ""
    return f"{star} `{bar}` {score}/{max_score}"


def make_why_explanation(signal: dict, htf_trend: str, counter_trend: bool) -> str:
    """Generate a plain-English explanation of why this trade is valid."""
    reasons = signal.get("reasons", [])
    direction = signal.get("direction", "long")
    lines = []

    # Liquidity sweep
    sweep = next((r for r in reasons if "sweep" in r.lower() or "liquidity" in r.lower()), None)
    if sweep:
        lines.append(f"Price swept {'sell-side' if direction == 'long' else 'buy-side'} liquidity  stop hunt complete.")

    # BOS
    if any("bos" in r.lower() or "break of structure" in r.lower() for r in reasons):
        lines.append(f"{'Bullish' if direction == 'long' else 'Bearish'} BOS confirms the structural reversal.")

    # FVG
    if any("fvg" in r.lower() or "fair value" in r.lower() for r in reasons):
        lines.append("Price is inside a Fair Value Gap  institutional imbalance zone providing entry precision.")

    # Order block
    if any("order block" in r.lower() or "ob" in r.lower() for r in reasons):
        lines.append("Entry aligns with an Order Block  prior institutional supply/demand zone.")

    # OTE / Fibonacci
    if any("ote" in r.lower() or "fib" in r.lower() or "79%" in r.lower() for r in reasons):
        lines.append("Price has retraced into the OTE (Optimal Trade Entry) 70.579% Fibonacci zone.")

    # Displacement
    if any("displacement" in r.lower() for r in reasons):
        lines.append("A displacement candle signals strong institutional momentum.")

    # RSI
    rsi_line = next((r for r in reasons if "rsi" in r.lower()), None)
    if rsi_line:
        lines.append(f"{rsi_line}  confirming exhaustion of the prior move.")

    # Volume spike
    vol_line = next((r for r in reasons if "volume spike" in r.lower()), None)
    if vol_line:
        lines.append(f"{vol_line}  institutional participation detected.")

    # Wick rejection
    if any("rejection wick" in r.lower() for r in reasons):
        lines.append("Strong rejection wick on the sweep candle confirms price refused to hold beyond liquidity.")

    # HTF trend
    htf_str = htf_trend.upper() if htf_trend else "UNKNOWN"
    if counter_trend:
        lines.append(f" HTF (1H) trend is {htf_str}  this is a COUNTER-TREND trade. Higher score required; trade with caution.")
    else:
        lines.append(f"HTF (1H) trend is {htf_str}  trade aligns with higher-timeframe bias.")

    return " ".join(lines) if lines else "Multi-confluence SMC setup detected."


# 
# ANALYSIS ENGINES
# 

def analyze(candles: list[dict], pair_label: str) -> dict | None:
    """
    Premium SMC/ICT analysis engine.
    Returns signal dict or None.
    """
    if len(candles) < 30:
        return None

    atr = calc_atr(candles)
    if atr is None:
        return None

    # --- Upgrade 5: Minimum ATR filter ---
    price = candles[-1]["close"]
    if atr / price < 0.0005:
        print(f"[SKIP] {pair_label} ATR too flat ({atr/price:.5f})")
        return None

    swings = find_swing_highs_lows(candles)
    fvgs = find_fvg(candles)
    sweep = check_liquidity_sweep(candles, swings)

    if not sweep:
        return None

    direction = sweep["direction"]
    score = 0
    reasons = []

    # Sweep is the base condition  v9.2: clean vs dirty scoring
    sweep_type_label = "Sell-Side" if sweep["type"] == "sell_side" else "Buy-Side"
    sweep_clean = sweep.get("clean", True)
    if sweep_clean:
        score += 2
        reasons.append(
            f" Clean Liquidity Sweep ({sweep_type_label} at {price_fmt(pair_label, sweep['level'])}) "
            f" wick dipped through EQH/EQL, no body close below  highest probability setup"
        )
    else:
        score += 1
        reasons.append(
            f" Dirty Liquidity Sweep ({sweep_type_label} at {price_fmt(pair_label, sweep['level'])}) "
            f" body closed through level  lower probability, await confirmation"
        )

    # BOS confirmation
    bos = check_bos(candles, direction, swings)
    if bos:
        score += 2
        reasons.append(f"BOS {'above' if direction == 'long' else 'below'} {price_fmt(pair_label, bos['level'])}")

    # FVG confluence
    current_price = candles[-1]["close"]
    fvg_hit = None
    for fvg in reversed(fvgs[-10:]):
        if direction == "long" and fvg["type"] == "bullish":
            if fvg["bottom"] <= current_price <= fvg["top"]:
                fvg_hit = fvg
                break
        elif direction == "short" and fvg["type"] == "bearish":
            if fvg["bottom"] <= current_price <= fvg["top"]:
                fvg_hit = fvg
                break
    if fvg_hit:
        score += 2
        reasons.append(f"FVG ({fvg_hit['type'].capitalize()}) at {price_fmt(pair_label, fvg_hit['bottom'])}{price_fmt(pair_label, fvg_hit['top'])}")

    # Order Block (with freshness check and mitigation detection)
    ob = find_order_block(candles, direction)
    ob_mitigated = False  # initialize before conditional block
    if ob:
        ob_price = candles[-1]["close"]
        # Mitigation check: OB is invalidated if price has fully traded through it
        ob_mitigated = False
        if direction == "long":
            # Bullish OB mitigated when price closed below OB bottom after OB formed
            for c in candles[ob.get("index", 0) + 2:]:
                if c["close"] < ob["bottom"]:
                    ob_mitigated = True
                    break
        else:
            # Bearish OB mitigated when price closed above OB top after OB formed
            for c in candles[ob.get("index", 0) + 2:]:
                if c["close"] > ob["top"]:
                    ob_mitigated = True
                    break
        if ob_mitigated:
            reasons.append(" OB mitigated  zone invalidated")
        elif ob["bottom"] <= ob_price <= ob["top"]:
            # Freshness: OB is at index ob["index"]; age = how many candles ago it formed
            ob_age = len(candles) - 1 - ob.get("index", 0)
            if ob_age > 50:
                # Stale OB  has been tested multiple times, weakened
                score = max(0, score - 1)
                reasons.append(f" Stale Order Block ({ob_age} candles old)  {'support' if direction == 'long' else 'resistance'} zone weakened")
            else:
                score += 1
                freshness_tag = "fresh" if ob_age <= 15 else "recent"
                reasons.append(f"Order Block ({freshness_tag}, {ob_age}c old) {'support' if direction == 'long' else 'resistance'} at {price_fmt(pair_label, ob['bottom'])}")

    #  v9.4 Feature 5: OB Stacking  check 20c and 50c lookback periods 
    if not ob_mitigated:
        try:
            ob_short_lb = find_order_block(candles[-20:] if len(candles) >= 20 else candles, direction)
            ob_long_lb  = find_order_block(candles[-50:] if len(candles) >= 50 else candles, direction)
            if ob_short_lb and ob_long_lb:
                # Convert ob_long_lb prices to absolute (it operates on a slice)
                _stack_check_top = max(ob_short_lb["top"], ob_long_lb["top"])
                _stack_check_bot = min(ob_short_lb["bottom"], ob_long_lb["bottom"])
                _mid1 = (ob_short_lb["top"] + ob_short_lb["bottom"]) / 2
                _mid2 = (ob_long_lb["top"]  + ob_long_lb["bottom"])  / 2
                _spread = abs(_mid1 - _mid2) / max(_mid1, 1e-9)
                if _spread <= 0.01:  # within 1% of each other
                    # Only add stacking bonus if we didn't already score the standard OB
                    # (replace the +1 with +2 net, so add +1 more)
                    score += 1
                    reasons.append(" Stacked Order Blocks  two OBs in same zone, institutional confluence zone")
        except Exception:
            pass

    # Displacement
    disp = detect_displacement(candles)
    if disp:
        if (direction == "long" and disp["direction"] == "up") or \
           (direction == "short" and disp["direction"] == "down"):
            score += 1
            reasons.append(f"Displacement candle ({disp['range']/disp['avg_range']:.1f} avg range)")

    # OTE Fibonacci
    if swings["highs"] and swings["lows"]:
        if direction == "long":
            recent_low = min(s["price"] for s in swings["lows"][-3:])
            recent_high = max(s["price"] for s in swings["highs"][-3:])
        else:
            recent_high = max(s["price"] for s in swings["highs"][-3:])
            recent_low = min(s["price"] for s in swings["lows"][-3:])
        fibs = calc_fib_79(recent_low, recent_high)
        if direction == "long" and fibs["ote_low"] <= current_price <= fibs["ote_high"]:
            score += 1
            reasons.append(f"OTE 79% zone ({price_fmt(pair_label, fibs['ote_low'])}{price_fmt(pair_label, fibs['ote_high'])})")
        elif direction == "short" and fibs["ote_low"] <= current_price <= fibs["ote_high"]:
            score += 1
            reasons.append(f"OTE 79% zone ({price_fmt(pair_label, fibs['ote_low'])}{price_fmt(pair_label, fibs['ote_high'])})")

    # Trading into liquidity
    if is_trading_into_liquidity(candles, direction, swings):
        score += 1
        reasons.append("Target: liquidity pool above" if direction == "long" else "Target: liquidity pool below")

    # --- Upgrade 6: Wick rejection confluence ---
    sweep_cidx = sweep.get("cidx", None)
    sweep_c_idx = sweep_cidx if sweep_cidx is not None else -2
    try:
        sweep_c = candles[sweep_c_idx]
        candle_range = sweep_c["high"] - sweep_c["low"]
        if candle_range > 0:
            if direction == "long":
                lower_wick = (sweep_c["open"] - sweep_c["low"]) if sweep_c["open"] > sweep_c["low"] \
                             else (sweep_c["close"] - sweep_c["low"])
                if lower_wick / candle_range > 0.5:
                    score += 1
                    reasons.append("Strong rejection wick on sweep")
            else:
                upper_wick = (sweep_c["high"] - sweep_c["open"]) if sweep_c["open"] < sweep_c["high"] \
                             else (sweep_c["high"] - sweep_c["close"])
                if upper_wick / candle_range > 0.5:
                    score += 1
                    reasons.append("Strong rejection wick on sweep")
    except (IndexError, KeyError):
        pass

    # --- Upgrade 3: RSI exhaustion filter ---
    closes = [c["close"] for c in candles]
    rsi_val = rsi(closes, 14)
    rsi_exhausted = False
    if rsi_val is not None:
        if direction == "long" and rsi_val < 35:
            score += 1
            reasons.append(f"RSI exhausted oversold ({rsi_val:.1f})")
            rsi_exhausted = True
        elif direction == "short" and rsi_val > 65:
            score += 1
            reasons.append(f"RSI exhausted overbought ({rsi_val:.1f})")
            rsi_exhausted = True

    # --- Upgrade 4: Volume spike confirmation ---
    volumes = [c["volume"] for c in candles]
    valid_vols = [v for v in volumes[-21:-1] if v and v > 0]
    vol_spike = False
    if valid_vols:
        avg_vol = statistics.mean(valid_vols)
        last_vol = volumes[-1]
        if last_vol and avg_vol > 0 and last_vol >= avg_vol * 1.5:
            score += 1
            reasons.append(f"Volume spike ({last_vol/avg_vol:.1f})")
            vol_spike = True

    # RSI divergence  graded: weak=+1, strong (5 RSI pts gap)=+2
    rsi_div_strength = detect_rsi_divergence(candles, direction)
    if rsi_div_strength > 0:
        score += rsi_div_strength
        strength_label = "strong" if rsi_div_strength == 2 else "weak"
        reasons.append(f"RSI divergence ({'bullish' if direction == 'long' else 'bearish'}, {strength_label})")

    # Divergence scoring using detect_rsi_divergence_type  checks supporting vs opposing divergence
    _rsi_series_div = []
    for _i in range(14, len(candles)):
        _r = rsi([c["close"] for c in candles[:_i+1]], 14)
        if _r is not None:
            _rsi_series_div.append(_r)
    if len(_rsi_series_div) >= 4:
        _div_type = detect_rsi_divergence_type(candles, _rsi_series_div, direction)
        if direction == "long":
            if _div_type == "bullish":
                score += 1
                reasons.append("RSI bullish divergence (price lower low, RSI higher low)  supporting long")
            elif _div_type == "bearish":
                reasons.append(" RSI bearish divergence opposing long  momentum caution")
        else:
            if _div_type == "bearish":
                score += 1
                reasons.append("RSI bearish divergence (price higher high, RSI lower high)  supporting short")
            elif _div_type == "bullish":
                reasons.append(" RSI bullish divergence opposing short  momentum caution")

    # VWAP bias  price above VWAP bullish, below bearish
    vwap_val = calc_vwap(candles)
    if vwap_val is not None:
        if direction == "long" and current_price > vwap_val:
            score += 1
            reasons.append(f"Price above VWAP ({price_fmt(pair_label, vwap_val)})  bullish bias")
        elif direction == "short" and current_price < vwap_val:
            score += 1
            reasons.append(f"Price below VWAP ({price_fmt(pair_label, vwap_val)})  bearish bias")

    # Equal highs/lows  untested liquidity pools act as targets/magnets
    eql = find_equal_highs_lows(candles)
    if direction == "long" and eql["equal_lows"]:
        score += 1
        reasons.append(f"Equal lows at {price_fmt(pair_label, eql['equal_lows'][-1])}  sweep target")
    elif direction == "short" and eql["equal_highs"]:
        score += 1
        reasons.append(f"Equal highs at {price_fmt(pair_label, eql['equal_highs'][-1])}  sweep target")

    # Bollinger Band squeeze  tight bands signal imminent breakout
    if detect_bb_squeeze(candles):
        score += 1
        reasons.append("BB squeeze detected  volatility contraction, breakout likely")

    # BB width trend  expanding bands = momentum building; contracting after squeeze = ideal entry
    bb_trend = calc_bb_width_trend(candles)
    if bb_trend is not None:
        if bb_trend["expanding"] and not bb_trend["squeeze"]:
            score += 1
            reasons.append(f"BB expanding ({bb_trend['width']*100:.2f}% width)  momentum building, move underway")
        elif bb_trend["contracting"]:
            score += 1
            reasons.append(f"BB contracting ({bb_trend['width']*100:.2f}% width)  pre-breakout compression")

    # Volume POC confluence  entry near Point of Control = high-volume price magnet
    poc = calc_volume_poc(candles)
    if poc is not None and atr > 0:
        poc_dist = abs(current_price - poc)
        if poc_dist < atr * 0.5:
            score += 1
            reasons.append(f"Entry near volume POC ({price_fmt(pair_label, poc)})  high-volume magnet")

    # Momentum candle  require strong-bodied candle at entry (filters dojis)
    if is_momentum_candle(candles, direction):
        score += 1
        reasons.append(f"Momentum candle confirmed ({'bullish' if direction == 'long' else 'bearish'} body 60% range)")

    # Engulfing candle  strong reversal body at the swept zone (v8.1: +2 double-weight)
    if detect_engulfing(candles, direction):
        _eng_pts = round(2 * SCORE_MULTIPLIERS.get("engulfing", 1.0))
        score += _eng_pts
        eng_dir = "Bullish" if direction == "long" else "Bearish"
        reasons.append(f" {eng_dir} Engulfing candle  strong reversal signal")

    # v8.3: Three-Line Strike  high-probability reversal (double weight +2)
    _tls = detect_three_line_strike(candles)
    if _tls is not None:
        if (direction == "long" and _tls == "bullish") or (direction == "short" and _tls == "bearish"):
            _tls_pts = round(2 * SCORE_MULTIPLIERS.get("three_line_strike", 1.0))
            score += _tls_pts
            reasons.append(" Three-Line Strike  high-probability reversal pattern")

    # Pin bar  rejection wick at swept level (existing list-based version)
    if detect_pin_bar(candles, direction):
        _pb_pts = round(1 * SCORE_MULTIPLIERS.get("pin_bar", 1.0))
        score += _pb_pts
        reasons.append(f"{'Hammer' if direction == 'long' else 'Shooting star'} pin bar at swept zone")

    # v8.3: Single-candle pin bar (66% wick threshold)
    if len(candles) >= 1:
        _pb_single = detect_pin_bar_single(candles[-1])
        if _pb_single == "bullish" and direction == "long":
            score += 1
            reasons.append(" Bullish Pin Bar  strong rejection from lows")
        elif _pb_single == "bearish" and direction == "short":
            score += 1
            reasons.append(" Bearish Pin Bar  strong rejection from highs")

    # Swing Failure Pattern (SFP)  wick beyond swing level, close back inside
    # Very high probability  trapped traders on the wrong side
    if detect_swing_failure_pattern(candles, direction, lookback=20):
        score += 2  # double weight: one of the strongest reversal signals
        sfp_dir = "Bullish" if direction == "long" else "Bearish"
        sfp_action = "swept swing low, closed above" if direction == "long" else "swept swing high, closed below"
        reasons.append(f" SFP  {sfp_dir} Swing Failure Pattern: candle {sfp_action}  trapped liquidity hunt")

    # --- v8.1: Candle body/wick analysis  rejection wick scoring ---
    # Examine the last closed candle's wick relative to body
    if len(candles) >= 2:
        _last_candle = candles[-2]  # last CLOSED candle (not current forming)
        _cs = analyze_candle_structure(_last_candle)
        _body = _cs["body"]
        if _body > 0:
            if direction == "long" and _cs["lower_wick"] >= 2 * _body:
                score += 1
                reasons.append(" Long lower wick rejection  buying pressure evident")
            elif direction == "short" and _cs["upper_wick"] >= 2 * _body:
                score += 1
                reasons.append(" Long upper wick rejection  selling pressure evident")

    # --- v8.1: EMA20 momentum slope scoring ---
    # Compute slope of last 5 EMA20 values from candle closes
    _ema20_series = []
    _closes_for_ema = [c["close"] for c in candles]
    for _i in range(max(20, len(candles) - 10), len(candles)):
        _ev = ema(_closes_for_ema[:_i + 1], 20)
        if _ev is not None:
            _ema20_series.append(_ev)
    if len(_ema20_series) >= 5:
        _ema20_last5 = _ema20_series[-5:]
        # Average per-candle slope as % of first value
        _slope_pct = (_ema20_last5[-1] - _ema20_last5[0]) / max(_ema20_last5[0], 1e-9) / 4 * 100
        if direction == "long" and _slope_pct > 0.05:
            score += 1
            reasons.append(" EMA20 momentum aligned  trending strongly in signal direction")
        elif direction == "short" and _slope_pct < -0.05:
            score += 1
            reasons.append(" EMA20 momentum aligned  trending strongly in signal direction")

    # Stochastic RSI confirmation
    stoch = stoch_rsi(closes)
    if stoch is not None:
        if direction == "long" and stoch < 25:
            score += 1
            reasons.append(f"Stoch RSI oversold ({stoch:.1f})  momentum reversal zone")
        elif direction == "short" and stoch > 75:
            score += 1
            reasons.append(f"Stoch RSI overbought ({stoch:.1f})  momentum reversal zone")

    # v8.3: calc_stoch_rsi  stricter thresholds (<20 / >80) for mean reversion confirmation
    _srsi = calc_stoch_rsi(closes)
    if _srsi is not None:
        if direction == "long" and _srsi < 20:
            score += 1
            reasons.append(f" StochRSI oversold (<20)  mean reversion setup confirmed")
        elif direction == "short" and _srsi > 80:
            score += 1
            reasons.append(f" StochRSI overbought (>80)  mean reversion setup confirmed")

    # Market Structure Shift  early reversal confirmation
    if detect_market_structure_shift(candles, direction, lookback=30):
        score += 1
        mss_label = "bullish" if direction == "long" else "bearish"
        reasons.append(f"Market Structure Shift ({mss_label} MSS)  early trend reversal confirmed on 5m")

    # Ichimoku Cloud  price position relative to cloud (1H-level context)
    ichi = ichimoku(candles)
    if ichi is not None:
        if direction == "long":
            if ichi["above_cloud"] and ichi["cloud_bullish"]:
                score += 1
                reasons.append(f"Ichimoku: price above green cloud  bullish structure confirmed")
            elif ichi["in_cloud"]:
                # In cloud = uncertain  slight penalty (-1) but don't block
                score = max(0, score - 1)
                reasons.append(f" Ichimoku: price inside cloud  choppy zone, caution")
            elif ichi["below_cloud"]:
                # Strongly counter-trend
                score = max(0, score - 1)
                reasons.append(f" Ichimoku: price below bearish cloud  counter-trend LONG, elevated risk")
        else:  # short
            if ichi["below_cloud"] and not ichi["cloud_bullish"]:
                score += 1
                reasons.append(f"Ichimoku: price below red cloud  bearish structure confirmed")
            elif ichi["in_cloud"]:
                score = max(0, score - 1)
                reasons.append(f" Ichimoku: price inside cloud  choppy zone, caution")
            elif ichi["above_cloud"]:
                score = max(0, score - 1)
                reasons.append(f" Ichimoku: price above bullish cloud  counter-trend SHORT, elevated risk")

    # --- v8.0: Volume profile scoring ---
    # Compute 20-candle volume profile and check if current price is near the POC
    # or at a low-volume node (thin area where price moves quickly).
    vol_profile = calc_volume_profile(candles, lookback=20)
    if vol_profile is not None and atr > 0:
        poc_p = vol_profile["poc_price"]
        poc_dist = abs(current_price - poc_p)
        if poc_dist < atr * 0.3:
            # Price is very close to the highest-volume node (institutional interest zone)
            score += 1
            reasons.append(f" Price at high-volume POC ({price_fmt(pair_label, poc_p)})  institutional interest zone")
        else:
            # Check for low-volume node: find lowest-volume bins in the profile
            bin_vols = [v for _, v in vol_profile["bins"]]
            if bin_vols:
                low_vol_threshold = sorted(bin_vols)[max(0, int(len(bin_vols) * 0.10) - 1)]
                near_low_vol = any(
                    abs(current_price - bp) < atr * 0.3 and bv <= low_vol_threshold
                    for bp, bv in vol_profile["bins"]
                )
                if near_low_vol:
                    if direction == "long":
                        score += 1
                        reasons.append(" Low volume node near support  price likely to move quickly through this zone")
                    else:
                        score += 1
                        reasons.append(" Low volume node near resistance  price likely to move quickly through this zone")

    # --- v8.0: Fibonacci retracement scoring ---
    # Check if current price is within 0.3% of the 0.618 or 0.5 key Fib level
    # and that the level aligns with the signal direction (long near support fib, short near resistance fib).
    fib_lvls = calc_fib_levels(candles, lookback=50)
    if fib_lvls is not None:
        fib_618 = fib_lvls["levels"][0.618]
        fib_500 = fib_lvls["levels"][0.5]
        fib_382 = fib_lvls["levels"][0.382]
        for fib_ratio, fib_price, fib_name in [
            (0.618, fib_618, "0.618"),
            (0.5,   fib_500, "0.5"),
            (0.382, fib_382, "0.382"),
        ]:
            dist_pct = abs(current_price - fib_price) / max(current_price, 1e-9)
            if dist_pct <= 0.003:  # within 0.3%
                if direction == "long" and current_price <= fib_618 * 1.003:
                    # Long near a key fib support (price retraced to this level)
                    if fib_ratio in (0.618, 0.5):
                        score += 1
                        reasons.append(f" Price at {fib_name} Fib retracement ({price_fmt(pair_label, fib_price)})  golden ratio confluence")
                        break
                    elif fib_ratio == 0.382:
                        score += 1
                        reasons.append(f" Price at {fib_name} Fib retracement ({price_fmt(pair_label, fib_price)})  key retracement support")
                        break
                elif direction == "short" and current_price >= fib_618 * 0.997:
                    # Short near a key fib resistance (price retraced up to this level)
                    if fib_ratio in (0.618, 0.5):
                        score += 1
                        reasons.append(f" Price at {fib_name} Fib retracement ({price_fmt(pair_label, fib_price)})  golden ratio resistance confluence")
                        break
                    elif fib_ratio == 0.382:
                        score += 1
                        reasons.append(f" Price at {fib_name} Fib retracement ({price_fmt(pair_label, fib_price)})  key retracement resistance")
                        break

    # --- v8.2: MACD cross scoring ---
    _macd_result = calc_macd(closes)
    if _macd_result is not None:
        _macd_series = _macd_result["macd_series"]
        _sig_series  = _macd_result["signal_series"]
        # Check last 3 candles for a cross
        _cross_window = min(3, len(_macd_series), len(_sig_series))
        _bullish_cross = False
        _bearish_cross = False
        for _ci in range(-_cross_window, -1):
            try:
                _prev_diff = _macd_series[_ci - 1] - _sig_series[_ci - 1]
                _curr_diff = _macd_series[_ci]     - _sig_series[_ci]
                if _prev_diff < 0 and _curr_diff >= 0:
                    _bullish_cross = True
                if _prev_diff > 0 and _curr_diff <= 0:
                    _bearish_cross = True
            except IndexError:
                pass
        if direction == "long" and _bullish_cross:
            score += 1
            reasons.append(" MACD bullish cross  momentum confirming direction")
        elif direction == "short" and _bearish_cross:
            score += 1
            reasons.append(" MACD bearish cross  momentum confirming direction")

    # --- v8.2: Doji at key level scoring ---
    _last_c = candles[-1]
    if detect_doji(_last_c):
        _price_now = _last_c["close"]
        _near_key  = False
        _tol       = _price_now * 0.005  # 0.5%
        # Check near OB
        if ob and not ob_mitigated:
            if abs(_price_now - (ob["top"] + ob["bottom"]) / 2) <= _tol:
                _near_key = True
        # Check near fib level
        _fib_check = calc_fib_levels(candles, lookback=50)
        if not _near_key and _fib_check:
            for _fp in _fib_check["levels"].values():
                if abs(_price_now - _fp) <= _tol:
                    _near_key = True
                    break
        # Check near BB bands
        if not _near_key and len(candles) >= 20:
            _bb_closes = [c["close"] for c in candles[-20:]]
            _bb_mean   = statistics.mean(_bb_closes)
            _bb_std    = statistics.stdev(_bb_closes)
            _bb_upper  = _bb_mean + 2 * _bb_std
            _bb_lower  = _bb_mean - 2 * _bb_std
            if abs(_price_now - _bb_upper) <= _tol or abs(_price_now - _bb_lower) <= _tol:
                _near_key = True
        if _near_key:
            score += 1
            reasons.append(" Doji at key level  indecision turning into directional move")

    # --- v8.2: Hammer / Shooting Star scoring ---
    _hs = detect_hammer_or_star(_last_c)
    if _hs == "hammer" and direction == "long":
        score += 1
        reasons.append(" Hammer candle  bullish reversal at support")
    elif _hs == "shooting_star" and direction == "short":
        score += 1
        reasons.append(" Shooting star  bearish reversal at resistance")

    # Inside bar confluence (v8.4): consolidation before breakout aligned with trend
    if detect_inside_bar(candles):
        prev_c = candles[-2]
        mother_range = prev_c["high"] - prev_c["low"]
        mother_body = abs(prev_c["close"] - prev_c["open"])
        if mother_range > 0 and (mother_body / mother_range) >= 0.6:
            score += 1
            reasons.append(" Inside Bar  consolidation before breakout")

    # Support/Resistance zone confluence (v8.4): price at key horizontal level
    _sr_zones = detect_sr_zones(candles, lookback=30)
    for _zone in _sr_zones:
        if abs(current_price - _zone["level"]) / current_price < 0.003:
            score += 1
            reasons.append(f" Price at S/R zone ({_zone['touches']} touches)  key horizontal level")
            break  # only one SR bonus per signal

    # --- v9.0: Heikin Ashi trend confirmation ---
    _ha_candles = to_heikin_ashi(candles)
    if len(_ha_candles) >= 3:
        _ha_last3 = _ha_candles[-3:]
        _ha_all_green = all(c["close"] >= c["open"] for c in _ha_last3)
        _ha_all_red   = all(c["close"] <  c["open"] for c in _ha_last3)
        if direction == "long" and _ha_all_green:
            score += 1
            reasons.append(" 3 consecutive Heikin Ashi candles  strong trend confirmation")
        elif direction == "short" and _ha_all_red:
            score += 1
            reasons.append(" 3 consecutive Heikin Ashi candles  strong trend confirmation")

    # --- v9.0: Keltner Channel + BB squeeze confirmation ---
    if detect_bb_squeeze(candles) and detect_keltner_squeeze(candles):
        score += 2
        reasons.append(" BB inside Keltner Channel  confirmed volatility squeeze, explosive move imminent")

    # --- v9.0: Fair Value Gap (FVG/ICT) scoring ---
    _fvg_zones = detect_fvg_zones(candles)
    for _fvg in _fvg_zones[:5]:  # check 5 most recent FVGs
        if direction == "long" and _fvg["type"] == "bullish":
            # Bullish FVG below current price  institutional demand zone beneath us
            if _fvg["top"] < current_price:
                score += 1
                reasons.append(f" Bullish Fair Value Gap below  institutional demand zone")
                break
        elif direction == "short" and _fvg["type"] == "bearish":
            # Bearish FVG above current price  institutional supply zone above
            if _fvg["bottom"] > current_price:
                score += 1
                reasons.append(f" Bearish Fair Value Gap above  institutional supply zone")
                break

    # v9.5 Feature 4: Choppiness Index scoring
    _ci_val = calc_choppiness_index(candles, period=14)
    if _ci_val is not None:
        if _ci_val > 61.8:
            score -= 1
            reasons.append(f" Choppiness Index high ({_ci_val:.1f})  choppy/ranging conditions, lower follow-through")
        elif _ci_val < 38.2:
            score += 1
            reasons.append(f" Low choppiness ({_ci_val:.1f})  trending conditions, higher follow-through")

    # v9.6 Feature 2: Donchian Channel breakout scoring
    _dc = calc_donchian_channel(candles, period=20)
    if _dc is not None:
        if direction == "long" and current_price > _dc["upper"]:
            score += 1
            reasons.append(f" Donchian Channel breakout  price breaking 20-period range (upper: {price_fmt(pair_label, _dc['upper'])})")
        elif direction == "short" and current_price < _dc["lower"]:
            score += 1
            reasons.append(f" Donchian Channel breakout  price breaking 20-period range (lower: {price_fmt(pair_label, _dc['lower'])})")

    # v9.6 Feature 4: Range expansion scoring
    _re = detect_range_expansion(candles, lookback=10)
    if _re["expansion"]:
        if (direction == "long" and _re["direction"] == "bullish") or \
           (direction == "short" and _re["direction"] == "bearish"):
            score += 1
            reasons.append(f" Range expansion candle ({_re['ratio']:.1f} avg)  above-average size = institutional participation")
        else:
            score -= 1
            reasons.append(f" Range expansion against direction ({_re['ratio']:.1f} avg)  strong counter-move, reconsider")

    # v9.6 Feature 5: EMA Ribbon scoring (EMA5/8/13/21)
    _ribbon = calc_ema_ribbon(candles)
    if _ribbon is not None:
        if direction == "long":
            if _ribbon["aligned_bull"]:
                score += 2
                reasons.append(f" EMA Ribbon aligned  4 EMAs in perfect trend order (EMA5>{price_fmt(pair_label,_ribbon['ema5'])} > EMA8 > EMA13 > EMA21)")
            elif _ribbon["partial_bull"] == 3:
                score += 1
                reasons.append(f" EMA Ribbon partial bull (3/4 aligned)  near-perfect trend order")
        elif direction == "short":
            if _ribbon["aligned_bear"]:
                score += 2
                reasons.append(f" EMA Ribbon aligned  4 EMAs in perfect bearish order (EMA5<{price_fmt(pair_label,_ribbon['ema5'])} < EMA8 < EMA13 < EMA21)")
            elif _ribbon["partial_bear"] == 3:
                score += 1
                reasons.append(f" EMA Ribbon partial bear (3/4 aligned)  near-perfect bearish order")

    # v9.7 Feature 1: ICT Optimal Trade Entry (OTE) zone scoring
    _ote = detect_ote_zone(candles, direction)
    if _ote is not None and _ote["in_ote"]:
        # Only award OTE bonus when MSS has been detected (direction confirmed)
        _mss_confirmed = detect_market_structure_shift(candles, direction, lookback=30)
        if _mss_confirmed:
            score += 2
            reasons.append(
                f" ICT Optimal Trade Entry zone  price in 62-79% retracement sweet spot "
                f"({price_fmt(pair_label, _ote['ote_low'])}{price_fmt(pair_label, _ote['ote_high'])})"
            )
        else:
            score += 1
            reasons.append(
                f" ICT OTE zone  price at 62-79% Fib retracement "
                f"({price_fmt(pair_label, _ote['ote_low'])}{price_fmt(pair_label, _ote['ote_high'])})"
            )

    # v9.7 Feature 3: Power of Three (PO3) scoring
    _po3 = detect_power_of_three(candles)
    if _po3["detected"] and _po3["phase"] == "distribution":
        if _po3["direction"] == direction:
            score += 2
            _po3_dir_label = "long" if direction == "long" else "short"
            reasons.append(
                f" ICT Power of Three  {'bearish' if direction == 'long' else 'bullish'} manipulation confirmed, "
                f"{_po3_dir_label} setup ({_po3['range_low']:.4f}{_po3['range_high']:.4f})"
            )

    # v9.7 Feature 5: NWOG/NDOG  price at daily/weekly open level
    _open_bonus_added = False
    for _open_store in (DAILY_OPENS, WEEKLY_OPENS):
        if pair_label in _open_store and not _open_bonus_added:
            for _open_entry in list(_open_store[pair_label]):
                _open_price = _open_entry.get("price", 0)
                if _open_price > 0:
                    _open_dist = abs(current_price - _open_price) / _open_price
                    if _open_dist <= 0.003:
                        _open_type = _open_entry.get("type", "daily")
                        score += 1
                        reasons.append(
                            f" Price at {'weekly' if _open_type == 'weekly' else 'daily'} open "
                            f"({price_fmt(pair_label, _open_price)})  high-probability reaction level"
                        )
                        _open_bonus_added = True
                        break

    # v9.8 Feature 3: Dealing Range zone scoring
    _dr = detect_dealing_range(candles, lookback=50)
    if _dr["current_zone"] == "deep_discount" and direction == "long":
        score += 2
        reasons.append(
            f" ICT Dealing Range: Deep Discount zone (<23.6%)  prime long setup "
            f"({price_fmt(pair_label, _dr['low'])}{price_fmt(pair_label, _dr['deep_discount_threshold'])})"
        )
    elif _dr["current_zone"] == "discount" and direction == "long":
        score += 1
        reasons.append(
            f" ICT Dealing Range: Discount zone (<38.2%)  favorable long territory"
        )
    elif _dr["current_zone"] == "premium" and direction == "short":
        score += 1
        reasons.append(
            f" ICT Dealing Range: Premium zone (>61.8%)  favorable short territory"
        )
    elif _dr["current_zone"] == "premium" and direction == "long":
        score -= 1
        reasons.append(
            f" ICT Dealing Range: Premium zone  buying into supply, reduced long probability"
        )

    # v9.8 Feature 3: Breaker Block scoring
    _bb_ict = detect_breaker_block(candles, direction)
    if _bb_ict["found"] and _bb_ict["level"] > 0:
        _bb_dist = abs(current_price - _bb_ict["level"]) / current_price
        if _bb_dist <= 0.005:  # within 0.5%
            score += 2
            _bb_type = "support" if direction == "long" else "resistance"
            reasons.append(
                f" ICT Breaker Block ({_bb_type}) near price "
                f"({price_fmt(pair_label, _bb_ict['zone_low'])}{price_fmt(pair_label, _bb_ict['zone_high'])}) "
                f" mitigated OB now acting as {_bb_type}"
            )

    # v9.8 Feature 4: ICT Consequent Encroachment (CE) scoring
    # CE = 50% midpoint of an FVG; price within 0.2% = high-probability reaction
    _fvg_ce_zones = detect_fvg_zones(candles)
    for _fvg_ce in _fvg_ce_zones[:8]:
        _ce_mid = (_fvg_ce["top"] + _fvg_ce["bottom"]) / 2
        _ce_dist = abs(current_price - _ce_mid) / current_price if current_price > 0 else 1
        if _ce_dist <= 0.002:  # within 0.2%
            if (direction == "long" and _fvg_ce["type"] == "bullish") or \
               (direction == "short" and _fvg_ce["type"] == "bearish"):
                score += 1
                reasons.append(
                    f" ICT Consequent Encroachment  price at FVG midpoint "
                    f"({price_fmt(pair_label, _ce_mid)})  50% retracement into {_fvg_ce['type']} FVG"
                )
                break  # one CE bonus per signal

    # Adaptive learning penalty: reduce score for reasons that have repeatedly led to SL hits
    adaptive_penalty = get_adaptive_penalty(reasons)
    if adaptive_penalty > 0:
        print(f"[LEARN] {pair_label}: adaptive penalty -{adaptive_penalty} (score {score}  {score - adaptive_penalty})")
        score -= adaptive_penalty

    # v8.5 Feature 6: consecutive directional candles bonus
    _dc_count, _dc_bonus = count_directional_candles(candles, direction)
    if _dc_bonus == 2:
        score += 2
        reasons.append(f" 5/5 candles aligned  very strong directional momentum")
    elif _dc_bonus == 1:
        score += 1
        reasons.append(f" 4/5 candles aligned  strong directional momentum")

    # v9.1 Feature 1: Near-miss capture  return near-miss signal instead of None
    if score < MIN_SCORE:
        if score >= MIN_SCORE - 2:
            # Close enough to qualify as a watchlist candidate
            sweep_level = sweep["level"]
            poi_distance = abs(current_price - sweep_level)
            if poi_distance <= atr * 1.2:
                sl_mult_nm = session_sl_multiplier()
                if direction == "long":
                    _entry_nm = sweep_level * 1.0005
                    _sl_nm    = sweep_level - atr * 1.0 * sl_mult_nm
                    _t1_nm    = _entry_nm + atr * 2.0
                    _t2_nm    = _entry_nm + atr * 4.0
                else:
                    _entry_nm = sweep_level * 0.9995
                    _sl_nm    = sweep_level + atr * 1.0 * sl_mult_nm
                    _t1_nm    = _entry_nm - atr * 2.0
                    _t2_nm    = _entry_nm - atr * 4.0
                return {
                    "type": "premium",
                    "near_miss": True,
                    "direction": direction,
                    "entry": _entry_nm,
                    "sl": _sl_nm,
                    "t1": _t1_nm,
                    "t2": _t2_nm,
                    "score": score,
                    "rating": "C",
                    "reasons": reasons,
                    "rsi_val": rsi_val,
                    "rsi_exhausted": rsi_exhausted,
                    "vol_spike": vol_spike,
                    "sweep_level": sweep["level"],
                    "bos_level": bos["level"] if bos else None,
                    "atr": atr,
                    "sl_atr_mult": 1.0,
                    "time": datetime.now(timezone.utc).isoformat(),
                }
        return None

    # Build targets
    # Entry is set at the POI (sweep level), not current price.
    # For LONG: enter at the swept low (demand zone top edge)  price should retrace here.
    # For SHORT: enter at the swept high (supply zone bottom edge)  price should retrace here.
    # SL goes 1 ATR beyond the sweep wick; T1/T2 use ATR multiples from the POI entry.
    sweep_level = sweep["level"]

    # Check how far current price is from POI  if already >1 ATR away, signal is late
    poi_distance = abs(current_price - sweep_level)
    if poi_distance > atr * 1.2:
        # Price has moved too far from the zone  risk/reward is degraded, skip signal
        print(f"[SKIP] {pair_label} price {current_price:.4f} too far from POI {sweep_level:.4f} ({poi_distance/atr:.2f}ATR)")
        return None

    sl_mult = session_sl_multiplier()  # Wider SL in Asian session (more fakeouts)
    if sl_mult > 1.0:
        print(f"[SESSION] Asian session  applying {sl_mult}x SL multiplier")

    # v9.1 Feature 5: Adaptive SL  BB squeeze gets 1.5 base multiplier
    # (regime-based adjustment applied in scan_pair after 4H regime detection)
    _bb_squeeze_active = detect_bb_squeeze(candles)
    sl_atr_mult = 1.5 if _bb_squeeze_active else 1.0

    if direction == "long":
        # Entry at or just above the swept low (POI), SL below the wick
        entry = sweep_level * 1.0005                              # 0.05% above the swept low (queue limit order zone)
        sl    = sweep_level - atr * sl_atr_mult * sl_mult        # adaptive ATR mult  session mult
        t1    = entry + atr * 2.0
        t2    = entry + atr * 4.0
    else:
        # Entry at or just below the swept high (POI), SL above the wick
        entry = sweep_level * 0.9995                              # 0.05% below the swept high
        sl    = sweep_level + atr * sl_atr_mult * sl_mult        # adaptive ATR mult  session mult
        t1    = entry - atr * 2.0
        t2    = entry - atr * 4.0

    # Rating
    if score >= RATING_A:
        rating = "A"
    elif score >= RATING_B:
        rating = "B"
    else:
        rating = "C"

    return {
        "type": "premium",
        "direction": direction,
        "entry": entry,
        "sl": sl,
        "t1": t1,
        "t2": t2,
        "score": score,
        "rating": rating,
        "reasons": reasons,
        "rsi_val": rsi_val,
        "rsi_exhausted": rsi_exhausted,
        "vol_spike": vol_spike,
        "sweep_level": sweep["level"],
        "bos_level": bos["level"] if bos else None,
        "atr": atr,
        "sl_atr_mult": sl_atr_mult,
        "choppiness_index": _ci_val,
    }


def analyze_standard(candles: list[dict], pair_label: str) -> dict | None:
    """
    Standard EMA crossover engine.
    Returns signal dict or None.
    """
    if len(candles) < 50:
        return None

    closes = [c["close"] for c in candles]

    ema9 = ema(closes, 9)
    ema21 = ema(closes, 21)
    ema50 = ema(closes, 50)

    if ema9 is None or ema21 is None or ema50 is None:
        return None

    # Need previous values for crossover detection
    prev_closes = closes[:-1]
    prev_ema9 = ema(prev_closes, 9)
    prev_ema21 = ema(prev_closes, 21)

    if prev_ema9 is None or prev_ema21 is None:
        return None

    atr = calc_atr(candles)
    if atr is None:
        return None

    current_price = closes[-1]

    # Min ATR filter for standard engine too
    if atr / current_price < 0.0005:
        return None

    score = 0
    reasons = []
    direction = None

    # Golden cross (9 EMA crossing above 21 EMA)
    if prev_ema9 <= prev_ema21 and ema9 > ema21:
        direction = "long"
        score += 3
        reasons.append(f"EMA 9 crossed above EMA 21 ({price_fmt(pair_label, ema9)})")
    # Death cross
    elif prev_ema9 >= prev_ema21 and ema9 < ema21:
        direction = "short"
        score += 3
        reasons.append(f"EMA 9 crossed below EMA 21 ({price_fmt(pair_label, ema9)})")
    else:
        return None  # No crossover

    # Trend confirmation from EMA 50
    if direction == "long" and current_price > ema50:
        score += 2
        reasons.append(f"Price above EMA 50 (trend aligned, {price_fmt(pair_label, ema50)})")
    elif direction == "short" and current_price < ema50:
        score += 2
        reasons.append(f"Price below EMA 50 (trend aligned, {price_fmt(pair_label, ema50)})")

    # RSI filter
    rsi_val = rsi(closes, 14)
    rsi_exhausted = False
    if rsi_val is not None:
        if direction == "long" and rsi_val < 35:
            score += 1
            reasons.append(f"RSI oversold ({rsi_val:.1f})")
            rsi_exhausted = True
        elif direction == "short" and rsi_val > 65:
            score += 1
            reasons.append(f"RSI overbought ({rsi_val:.1f})")
            rsi_exhausted = True
        elif direction == "long" and 40 <= rsi_val <= 60:
            score += 1
            reasons.append(f"RSI neutral ({rsi_val:.1f})  room to run")
        elif direction == "short" and 40 <= rsi_val <= 60:
            score += 1
            reasons.append(f"RSI neutral ({rsi_val:.1f})  room to run")

    # Volume spike
    volumes = [c["volume"] for c in candles]
    valid_vols = [v for v in volumes[-21:-1] if v and v > 0]
    vol_spike = False
    if valid_vols:
        avg_vol = statistics.mean(valid_vols)
        last_vol = volumes[-1]
        if last_vol and avg_vol > 0 and last_vol >= avg_vol * 1.5:
            score += 1
            reasons.append(f"Volume spike ({last_vol/avg_vol:.1f})")
            vol_spike = True

    # RSI divergence adds confluence to EMA crossover (graded)
    rsi_div_strength = detect_rsi_divergence(candles, direction)
    if rsi_div_strength > 0:
        score += rsi_div_strength
        strength_label = "strong" if rsi_div_strength == 2 else "weak"
        reasons.append(f"RSI divergence ({'bullish' if direction == 'long' else 'bearish'}, {strength_label})")

    # VWAP bias for EMA engine
    vwap_val = calc_vwap(candles)
    if vwap_val is not None:
        if direction == "long" and current_price > vwap_val:
            score += 1
            reasons.append(f"Price above VWAP ({price_fmt(pair_label, vwap_val)})  bullish bias")
        elif direction == "short" and current_price < vwap_val:
            score += 1
            reasons.append(f"Price below VWAP ({price_fmt(pair_label, vwap_val)})  bearish bias")

    # BB squeeze  high-conviction entry timing
    if detect_bb_squeeze(candles):
        score += 1
        reasons.append("BB squeeze  volatility compression, breakout timing")

    # BB width trend  expanding = momentum; contracting = pre-breakout
    bb_trend = calc_bb_width_trend(candles)
    if bb_trend is not None:
        if bb_trend["expanding"] and not bb_trend["squeeze"]:
            score += 1
            reasons.append(f"BB expanding ({bb_trend['width']*100:.2f}%)  momentum building on EMA crossover")
        elif bb_trend["contracting"]:
            score += 1
            reasons.append(f"BB contracting ({bb_trend['width']*100:.2f}%)  compression before breakout")

    # Volume POC  EMA crossover near POC = high-probability entry zone
    poc = calc_volume_poc(candles)
    if poc is not None and atr > 0:
        poc_dist = abs(current_price - poc)
        if poc_dist < atr * 0.5:
            score += 1
            reasons.append(f"EMA crossover near volume POC ({price_fmt(pair_label, poc)})")

    # Momentum candle at crossover (reject dojis)
    if is_momentum_candle(candles, direction):
        score += 1
        reasons.append(f"Momentum candle at crossover ({'bull' if direction == 'long' else 'bear'} body 60%)")

    # Engulfing candle at crossover (v8.1: +2 double-weight)
    if detect_engulfing(candles, direction):
        score += 2  # double weight like SFP  strong reversal signal
        eng_dir_std = "Bullish" if direction == "long" else "Bearish"
        reasons.append(f" {eng_dir_std} Engulfing candle  strong reversal signal")

    # Pin bar at crossover  strong rejection at EMA level
    if detect_pin_bar(candles, direction):
        score += 1
        reasons.append(f"{'Hammer' if direction == 'long' else 'Shooting star'} pin bar at EMA crossover")

    # Swing Failure Pattern at EMA  wick beyond swing, close back inside
    if detect_swing_failure_pattern(candles, direction, lookback=20):
        score += 2
        sfp_dir = "Bullish" if direction == "long" else "Bearish"
        sfp_action = "swept low, closed above" if direction == "long" else "swept high, closed below"
        reasons.append(f" SFP  {sfp_dir} Swing Failure Pattern at EMA: {sfp_action}  high probability reversal")

    # Stochastic RSI for EMA engine
    stoch = stoch_rsi(closes)
    if stoch is not None:
        if direction == "long" and stoch < 25:
            score += 1
            reasons.append(f"Stoch RSI oversold ({stoch:.1f})  added momentum")
        elif direction == "short" and stoch > 75:
            score += 1
            reasons.append(f"Stoch RSI overbought ({stoch:.1f})  added momentum")

    # Market Structure Shift  structural reversal signal for EMA engine
    if detect_market_structure_shift(candles, direction, lookback=30):
        score += 1
        mss_label = "bullish" if direction == "long" else "bearish"
        reasons.append(f"Market Structure Shift ({mss_label} MSS)  early reversal signal confirmed")

    # Ichimoku Cloud  structural bias filter for EMA engine
    ichi = ichimoku(candles)
    if ichi is not None:
        if direction == "long":
            if ichi["above_cloud"] and ichi["cloud_bullish"]:
                score += 1
                reasons.append(f"Ichimoku: price above green cloud  bullish confirmation")
            elif ichi["in_cloud"] or ichi["below_cloud"]:
                score = max(0, score - 1)
                reasons.append(f" Ichimoku: price in/below cloud  trend unclear")
        else:
            if ichi["below_cloud"] and not ichi["cloud_bullish"]:
                score += 1
                reasons.append(f"Ichimoku: price below red cloud  bearish confirmation")
            elif ichi["in_cloud"] or ichi["above_cloud"]:
                score = max(0, score - 1)
                reasons.append(f" Ichimoku: price in/above cloud  trend unclear")

    # v8.5 Feature 6: consecutive directional candles bonus
    _std_dc_count, _std_dc_bonus = count_directional_candles(candles, direction)
    if _std_dc_bonus == 2:
        score += 2
        reasons.append(f" 5/5 candles aligned  very strong directional momentum")
    elif _std_dc_bonus == 1:
        score += 1
        reasons.append(f" 4/5 candles aligned  strong directional momentum")

    if score < MIN_SCORE:
        return None

    # EMA engine: entry at the EMA21 level (the actual crossover point),
    # not the candle close which may have already moved away.
    # This gives a more accurate entry for anyone waiting to fill a limit order.
    if direction == "long":
        entry = min(current_price, ema21 * 1.001)  # at EMA21 or current if already below
        sl    = entry - atr * 1.5
        t1    = entry + atr * 2.0
        t2    = entry + atr * 4.0
    else:
        entry = max(current_price, ema21 * 0.999)  # at EMA21 or current if already above
        sl    = entry + atr * 1.5
        t1    = entry - atr * 2.0
        t2    = entry - atr * 4.0

    rating = "A" if score >= RATING_A else "B" if score >= RATING_B else "C"

    return {
        "type": "standard",
        "direction": direction,
        "entry": entry,
        "sl": sl,
        "t1": t1,
        "t2": t2,
        "score": score,
        "rating": rating,
        "reasons": reasons,
        "rsi_val": rsi_val,
        "rsi_exhausted": rsi_exhausted,
        "vol_spike": vol_spike,
        "ema9": ema9,
        "ema21": ema21,
        "ema50": ema50,
        "atr": atr,
    }


# 
# 5M ENTRY CONFIRMATION
# 

async def confirm_5m_entry(pair: dict, direction: str) -> bool:
    """Confirm entry on 5m chart by checking EMA alignment."""
    candles = await fetch_candles(pair, timeframe="5m")
    if not candles or len(candles) < 21:
        return True  # default allow if can't fetch

    closes = [c["close"] for c in candles]
    e9 = ema(closes, 9)
    e21 = ema(closes, 21)

    if e9 is None or e21 is None:
        return True

    if direction == "long":
        return e9 > e21
    return e9 < e21


# 
# HTF TREND
# 

async def get_htf_trend(pair: dict) -> str:
    """Get higher timeframe trend from 1H candles using EMA9/21/50."""
    candles = await fetch_candles(pair, timeframe="1h")
    if not candles or len(candles) < 50:
        return "unknown"

    closes = [c["close"] for c in candles]
    e9 = ema(closes, 9)
    e21 = ema(closes, 21)
    e50 = ema(closes, 50)

    if e9 is None or e21 is None or e50 is None:
        return "unknown"

    price = closes[-1]
    if e9 > e21 and price > e50:
        return "long"
    if e9 < e21 and price < e50:
        return "short"
    return "neutral"


async def get_4h_trend(pair: dict) -> str:
    """
    Get 4-hour timeframe trend via EMA20/50.
    Returns "long", "short", or "unknown".
    """
    try:
        candles_4h = await fetch_coinbase_candles(pair["product_id"], granularity=14400, limit=60)
        if not candles_4h or len(candles_4h) < 50:
            return "unknown"
        closes = [c["close"] for c in candles_4h]
        ema20 = ema(closes, 20)
        ema50 = ema(closes, 50)
        if ema20 is None or ema50 is None:
            return "unknown"
        return "long" if ema20 > ema50 else "short"
    except Exception as e:
        print(f"[WARN] get_4h_trend({pair['label']}): {e}")
        return "unknown"


def calc_htf_candle_bias(candles_4h: list[dict], lookback: int = 10) -> dict | None:
    """
    Count bullish vs bearish candles over the last `lookback` 4H candles.
    Returns dict: {bull_count, bear_count, lookback, bias_label, bias_emoji}
    Used to show HTF directional conviction in signal embeds.
    """
    if not candles_4h or len(candles_4h) < lookback:
        return None
    recent = candles_4h[-lookback:]
    bull = sum(1 for c in recent if c["close"] > c["open"])
    bear = lookback - bull
    if bull >= 7:
        label, emoji = "Strong Bull", ""
    elif bull >= 6:
        label, emoji = "Mild Bull", ""
    elif bear >= 7:
        label, emoji = "Strong Bear", ""
    elif bear >= 6:
        label, emoji = "Mild Bear", ""
    else:
        label, emoji = "Neutral", ""
    return {"bull_count": bull, "bear_count": bear, "lookback": lookback,
            "bias_label": label, "bias_emoji": emoji}


# 
# ACTIVE TRADE MONITORING
# 

async def update_active_trades(channel: discord.TextChannel):  # noqa: C901
    """Check open trades for exits (T1, T2, SL)."""
    global session_pnl, _daily_opened, _daily_closed, _daily_pnl_pct, _daily_wins, _daily_losses

    to_remove = []
    for pair_label, trade in active_trades.items():
        pair = next((p for p in PAIRS if p["label"] == pair_label), None)
        if not pair:
            continue

        candles = await fetch_candles(pair, timeframe="5m")
        if not candles:
            continue

        price = candles[-1]["close"]
        direction = trade["direction"]
        entry = trade["entry"]
        t1 = trade["t1"]
        t2 = trade["t2"]
        sl = trade["sl"]
        t1_hit = trade.get("t1_hit", False)

        # v8.7 Feature 1: Track entry_hit  mark True once price reaches entry zone
        entry_hit = trade.get("entry_hit")
        if entry_hit is None:
            # Backward compat: trades without the flag are treated as already entered
            active_trades[pair_label]["entry_hit"] = True
            entry_hit = True

        if not entry_hit:
            # Check if price has now reached the entry level
            if direction == "LONG" and price >= entry:
                active_trades[pair_label]["entry_hit"] = True
                entry_hit = True
            elif direction == "SHORT" and price <= entry:
                active_trades[pair_label]["entry_hit"] = True
                entry_hit = True

        if not entry_hit and not trade.get("invalidated", False):
            # Check if price has moved >1% beyond SL (setup invalidated)
            sl_dist = abs(entry - sl)
            if direction == "LONG":
                # For a LONG waiting for entry: invalidate if price drops 1% below SL
                invalidation_level = sl * 0.99
                if price < invalidation_level:
                    active_trades[pair_label]["invalidated"] = True
                    try:
                        inv_embed = discord.Embed(
                            title=f" {pair_label}  Trade Setup Invalidated",
                            description=(
                                f"**LONG** setup on {pair_label} has been invalidated.\n"
                                f"Price has moved more than 1% below the stop loss level before entry was reached.\n"
                                f"The signal is stale  consider cancelling any pending limit orders."
                            ),
                            color=0xFF1744,
                            timestamp=datetime.now(timezone.utc)
                        )
                        inv_embed.add_field(name="Entry (limit)", value=price_fmt(pair_label, entry), inline=True)
                        inv_embed.add_field(name="Stop Loss", value=price_fmt(pair_label, sl), inline=True)
                        inv_embed.add_field(name="Current Price", value=price_fmt(pair_label, price), inline=True)
                        inv_embed.add_field(
                            name="Invalidation Level",
                            value=f"{price_fmt(pair_label, invalidation_level)} (SL  1%)",
                            inline=True
                        )
                        inv_embed.set_footer(text="Chartwise v10.0  Cancel pending limit orders for this setup")
                        await channel.send(embed=inv_embed)
                    except Exception as e:
                        print(f"[WARN] Invalidation embed failed {pair_label}: {e}")
                    to_remove.append(pair_label)
                    continue
            elif direction == "SHORT":
                # For a SHORT waiting for entry: invalidate if price rises 1% above SL
                invalidation_level = sl * 1.01
                if price > invalidation_level:
                    active_trades[pair_label]["invalidated"] = True
                    try:
                        inv_embed = discord.Embed(
                            title=f" {pair_label}  Trade Setup Invalidated",
                            description=(
                                f"**SHORT** setup on {pair_label} has been invalidated.\n"
                                f"Price has moved more than 1% above the stop loss level before entry was reached.\n"
                                f"The signal is stale  consider cancelling any pending limit orders."
                            ),
                            color=0xFF1744,
                            timestamp=datetime.now(timezone.utc)
                        )
                        inv_embed.add_field(name="Entry (limit)", value=price_fmt(pair_label, entry), inline=True)
                        inv_embed.add_field(name="Stop Loss", value=price_fmt(pair_label, sl), inline=True)
                        inv_embed.add_field(name="Current Price", value=price_fmt(pair_label, price), inline=True)
                        inv_embed.add_field(
                            name="Invalidation Level",
                            value=f"{price_fmt(pair_label, invalidation_level)} (SL + 1%)",
                            inline=True
                        )
                        inv_embed.set_footer(text="Chartwise v10.0  Cancel pending limit orders for this setup")
                        await channel.send(embed=inv_embed)
                    except Exception as e:
                        print(f"[WARN] Invalidation embed failed {pair_label}: {e}")
                    to_remove.append(pair_label)
                    continue

        # v9.0 Feature 2: Signal confidence decay  auto-expire stale setups
        # If entry has NOT been hit and signal is older than 2 SIGNAL_COOLDOWN (3 hours),
        # the setup is considered stale and is auto-invalidated.
        if not entry_hit and not trade.get("invalidated", False) and not trade.get("expired", False):
            _opened_at_str = trade.get("opened_at", "")
            if _opened_at_str:
                try:
                    _opened_dt = datetime.fromisoformat(_opened_at_str)
                    if _opened_dt.tzinfo is None:
                        _opened_dt = _opened_dt.replace(tzinfo=timezone.utc)
                    _age_secs = (datetime.now(timezone.utc) - _opened_dt).total_seconds()
                    if _age_secs > 2 * SIGNAL_COOLDOWN:
                        active_trades[pair_label]["expired"] = True
                        _age_str = f"{int(_age_secs // 3600)}h {int((_age_secs % 3600) // 60)}m"
                        try:
                            _exp_embed = discord.Embed(
                                title=f" {pair_label}  Signal Expired  Setup Too Old",
                                description=(
                                    f"The **{direction}** signal on {pair_label} has expired after {_age_str} "
                                    f"without entry being reached.\n"
                                    f"Entry level was never touched  setup conditions are likely no longer valid.\n"
                                    f"Cancel any pending limit orders at **{price_fmt(pair_label, entry)}**."
                                ),
                                color=0x607D8B,
                                timestamp=datetime.now(timezone.utc)
                            )
                            _exp_embed.add_field(name="Entry (expired)", value=price_fmt(pair_label, entry), inline=True)
                            _exp_embed.add_field(name="Current Price", value=price_fmt(pair_label, price), inline=True)
                            _exp_embed.add_field(name="Age", value=_age_str, inline=True)
                            _exp_embed.add_field(
                                name="What happened?",
                                value="Price never pulled back to the limit entry zone. The signal's market context has decayed  do not force entry.",
                                inline=False
                            )
                            _exp_embed.set_footer(text=f"Chartwise v10.0  Expired after {_age_str}  signal confidence decayed")
                            await channel.send(embed=_exp_embed)
                        except Exception as _e:
                            print(f"[WARN] Signal expiry embed failed {pair_label}: {_e}")
                        to_remove.append(pair_label)
                        print(f"[EXPIRE] {pair_label} signal expired after {_age_str} without entry hit  removed from active trades")
                        continue
                except Exception:
                    pass

        # v8.7 Feature 5: Trade management nudge after T1 hit and 4h elapsed
        if t1_hit and not trade.get("mgmt_nudge_sent", False):
            opened_at_str = trade.get("opened_at", "")
            if opened_at_str:
                try:
                    opened_dt = datetime.fromisoformat(opened_at_str)
                    if opened_dt.tzinfo is None:
                        opened_dt = opened_dt.replace(tzinfo=timezone.utc)
                    elapsed_secs = (datetime.now(timezone.utc) - opened_dt).total_seconds()
                    if elapsed_secs >= 14400:  # 4 hours
                        dur_str = format_trade_duration(opened_at_str)
                        active_trades[pair_label]["mgmt_nudge_sent"] = True
                        try:
                            nudge_embed = discord.Embed(
                                title=f" {pair_label}  Trade Management Alert",
                                description=(
                                    f"Your **{direction}** {pair_label} trade has been running **{dur_str}**.\n"
                                    f"T1 was already hit  consider moving your stop loss to entry (breakeven) "
                                    f"and managing this position actively."
                                ),
                                color=0xFFAB00,
                                timestamp=datetime.now(timezone.utc)
                            )
                            nudge_embed.add_field(name="Entry", value=price_fmt(pair_label, entry), inline=True)
                            nudge_embed.add_field(name="Current Price", value=price_fmt(pair_label, price), inline=True)
                            nudge_embed.add_field(name="T2 Target", value=price_fmt(pair_label, t2), inline=True)
                            nudge_embed.add_field(name="Time Running", value=dur_str, inline=True)
                            nudge_embed.set_footer(text="Chartwise v10.0  Active management recommended  ride to T2 or secure gains")
                            await channel.send(embed=nudge_embed)
                        except Exception as e:
                            print(f"[WARN] Management nudge failed {pair_label}: {e}")
                except Exception:
                    pass

        exit_type = None
        exit_price = None

        # Trailing stop: once T1 hit, trail SL by 0.5 ATR below/above current price
        trade_atr = trade.get("atr_at_entry")
        if t1_hit and trade_atr and trade_atr > 0:
            trail_notified = trade.get("trail_notified", False)
            if direction == "LONG":
                trail_sl = price - trade_atr * 0.5
                if trail_sl > sl:  # only move SL up, never down
                    if not trail_notified:
                        # First time trailing activates  send notification
                        try:
                            trail_embed = discord.Embed(
                                title=f" {pair_label}  Trailing Stop Active",
                                description=(
                                    f"**LONG** trade is now protected by trailing stop.\n"
                                    f"T1 was hit  SL moved to entry. Now trailing 0.5 ATR below price."
                                ),
                                color=0x00BFA5,
                                timestamp=datetime.now(timezone.utc)
                            )
                            trail_embed.add_field(name="Current Price", value=price_fmt(pair_label, price), inline=True)
                            trail_embed.add_field(name="Trailing SL", value=price_fmt(pair_label, trail_sl), inline=True)
                            trail_embed.add_field(name="T2 Target", value=price_fmt(pair_label, trade.get("t2", 0)), inline=True)
                            trail_embed.set_footer(text="Chartwise v10.0  Ride to T2  SL trails 0.5 ATR below price")
                            await channel.send(embed=trail_embed)
                        except Exception as e:
                            print(f"[WARN] Trail notification failed {pair_label}: {e}")
                        active_trades[pair_label]["trail_notified"] = True
                    active_trades[pair_label]["sl"] = trail_sl
                    sl = trail_sl
            elif direction == "SHORT":
                trail_sl = price + trade_atr * 0.5
                if trail_sl < sl:  # only move SL down, never up
                    if not trail_notified:
                        # First time trailing activates  send notification
                        try:
                            trail_embed = discord.Embed(
                                title=f" {pair_label}  Trailing Stop Active",
                                description=(
                                    f"**SHORT** trade is now protected by trailing stop.\n"
                                    f"T1 was hit  SL moved to entry. Now trailing 0.5 ATR above price."
                                ),
                                color=0x00BFA5,
                                timestamp=datetime.now(timezone.utc)
                            )
                            trail_embed.add_field(name="Current Price", value=price_fmt(pair_label, price), inline=True)
                            trail_embed.add_field(name="Trailing SL", value=price_fmt(pair_label, trail_sl), inline=True)
                            trail_embed.add_field(name="T2 Target", value=price_fmt(pair_label, trade.get("t2", 0)), inline=True)
                            trail_embed.set_footer(text="Chartwise v10.0  Ride to T2  SL trails 0.5 ATR above price")
                            await channel.send(embed=trail_embed)
                        except Exception as e:
                            print(f"[WARN] Trail notification failed {pair_label}: {e}")
                        active_trades[pair_label]["trail_notified"] = True
                    active_trades[pair_label]["sl"] = trail_sl
                    sl = trail_sl

        if direction == "LONG":
            if price <= sl:
                exit_type = "stop"
                exit_price = sl
            elif price >= t2:
                exit_type = "t2"
                exit_price = t2
            elif not t1_hit and price >= t1:
                exit_type = "t1"
                exit_price = t1
                active_trades[pair_label]["t1_hit"] = True
                active_trades[pair_label]["sl"] = entry  # move SL to breakeven
        elif direction == "SHORT":
            if price >= sl:
                exit_type = "stop"
                exit_price = sl
            elif price <= t2:
                exit_type = "t2"
                exit_price = t2
            elif not t1_hit and price <= t1:
                exit_type = "t1"
                exit_price = t1
                active_trades[pair_label]["t1_hit"] = True
                active_trades[pair_label]["sl"] = entry

        if exit_type == "t1":
            embed = make_exit_embed(pair_label, trade, exit_type, exit_price)
            await channel.send(embed=embed)
            continue  # trade still open

        if exit_type in ("stop", "t2"):
            embed = make_exit_embed(pair_label, trade, exit_type, exit_price)
            await channel.send(embed=embed)

            # v9.1 Feature 3: Trade Journal Embed
            try:
                _tj_outcome = "WIN " if exit_type == "t2" else "LOSS "
                _tj_color = 0x00E676 if exit_type == "t2" else 0xFF5252
                _tj_dur = format_trade_duration(trade.get("opened_at", datetime.now(timezone.utc).isoformat()))
                _tj_regime = trade.get("market_regime", "Unknown")
                _tj_session = trade.get("session", session_label())
                _tj_mtf = trade.get("mtf_consensus")
                _tj_patterns = trade.get("candle_patterns", [])
                _tj_reasons = trade.get("reasons", [])
                _tj_score = trade.get("score", 0)
                _tj_sl_mult = trade.get("sl_atr_mult", 1.0)

                # Build MTF string
                if _tj_mtf:
                    _mtf_icons = {0: " None", 1: " 1/3", 2: " 2/3", 3: " 3/3"}
                    _tj_mtf_str = _mtf_icons.get(_tj_mtf.get("agreeing", 0), "")
                    if _tj_mtf.get("tfs_scored"):
                        _tj_mtf_str += f" ({', '.join(_tj_mtf['tfs_scored'])})"
                else:
                    _tj_mtf_str = " Not recorded"

                # Lesson
                if exit_type == "t2":
                    _top_patterns = _tj_patterns[:2] or [r for r in _tj_reasons if any(k in r.lower() for k in ["engulfing", "hammer", "pin bar", "inside bar"])][:2]
                    if _top_patterns:
                        _tj_lesson = f" Winning patterns: {', '.join(_top_patterns)}"
                    else:
                        _tj_lesson = f" High-confluence setup ({_tj_score} score) hit T2  model confirmed"
                else:
                    _tj_hours = _tj_dur
                    _tj_lesson = f" SL hit after {_tj_hours}  {_tj_regime} regime may have caused volatility. Review entry timing."

                journal_embed = discord.Embed(
                    title=f" Trade Journal  {pair_label} {_tj_outcome}",
                    description=f"Comprehensive post-trade analysis for closed {trade.get('direction', '?').upper()} trade.",
                    color=_tj_color,
                    timestamp=datetime.now(timezone.utc)
                )
                journal_embed.add_field(name="Outcome", value=_tj_outcome, inline=True)
                journal_embed.add_field(name="Duration", value=_tj_dur, inline=True)
                journal_embed.add_field(name="Session", value=_tj_session, inline=True)
                journal_embed.add_field(name="Market Regime at Entry", value=f" {_tj_regime}", inline=True)
                journal_embed.add_field(name="MTF Consensus at Entry", value=_tj_mtf_str, inline=True)
                journal_embed.add_field(name="Score at Entry", value=str(_tj_score), inline=True)
                journal_embed.add_field(name="SL ATR Multiplier", value=f"{_tj_sl_mult:.2f}", inline=True)
                journal_embed.add_field(
                    name="Entry Candle Patterns",
                    value=", ".join(_tj_patterns) if _tj_patterns else "None detected",
                    inline=False
                )
                _top_reasons = _tj_reasons[:5]
                journal_embed.add_field(
                    name="Entry Reasons (Top 5)",
                    value="\n".join(f" {r}" for r in _top_reasons) if _top_reasons else "",
                    inline=False
                )
                journal_embed.add_field(name=" Lesson", value=_tj_lesson, inline=False)
                journal_embed.set_footer(text=f"Chartwise v10.0  Trade Journal  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
                await channel.send(embed=journal_embed)
            except Exception as _tj_err:
                print(f"[WARN] Trade journal embed failed for {pair_label}: {_tj_err}")

            # --- Update session P&L ---
            sig_type = trade.get("signal_type", "standard")
            # v8.0: use the session the trade was opened in (not the current session)
            sess = trade.get("session", session_label())
            if exit_type == "stop":
                session_pnl["losses"] += 1
                sl_dist = abs(entry - sl)
                _stop_pnl_pct = sl_dist / entry * 100
                session_pnl["total_pnl_pct"] -= _stop_pnl_pct
                # Dynamic cooldown: record loss time
                last_loss_time[pair_label] = time.time()
                last_trade_result[pair_label] = "LOSS"
                # Per-engine
                if sig_type == "premium":
                    session_pnl["premium_losses"] += 1
                else:
                    session_pnl["standard_losses"] += 1
                # Per-pair
                session_pnl["pair_losses"][pair_label] = session_pnl["pair_losses"].get(pair_label, 0) + 1
                # Per-session
                session_pnl["session_losses"][sess] = session_pnl["session_losses"].get(sess, 0) + 1
                # Daily counters
                _daily_closed += 1
                _daily_losses += 1
                _daily_pnl_pct -= _stop_pnl_pct
                # Post-mortem analysis on SL hit
                postmortem = make_postmortem_embed(pair_label, trade, price)
                await channel.send(embed=postmortem)
            elif exit_type == "t2":
                session_pnl["wins"] += 1
                _t2_pnl_pct = abs((t2 - entry) / entry * 100)
                session_pnl["total_pnl_pct"] += _t2_pnl_pct
                last_win_time[pair_label] = time.time()
                last_trade_result[pair_label] = "WIN"
                # Per-engine
                if sig_type == "premium":
                    session_pnl["premium_wins"] += 1
                else:
                    session_pnl["standard_wins"] += 1
                # Per-pair
                session_pnl["pair_wins"][pair_label] = session_pnl["pair_wins"].get(pair_label, 0) + 1
                # Per-session
                session_pnl["session_wins"][sess] = session_pnl["session_wins"].get(sess, 0) + 1
                # Daily counters
                _daily_closed += 1
                _daily_wins += 1
                _daily_pnl_pct += _t2_pnl_pct

            # Log outcome + adaptive learning
            sig_id = trade.get("sig_id")
            if sig_id:
                log_outcome(sig_id, exit_type, exit_price, entry, sl)

            # v8.1: Append to TRADE_HISTORY for !streak and !export
            _pnl_pct_hist = ((exit_price - entry) / entry * 100) if trade.get("direction") == "LONG" \
                            else ((entry - exit_price) / entry * 100)
            _dur_str = format_trade_duration(trade.get("opened_at", datetime.now(timezone.utc).isoformat()))
            TRADE_HISTORY.append({
                "pair":      pair_label,
                "direction": trade.get("direction", "?"),
                "entry":     entry,
                "sl":        sl,
                "t1":        trade.get("t1"),
                "t2":        trade.get("t2"),
                "exit":      exit_price,
                "exit_type": exit_type,
                "pnl_pct":   round(_pnl_pct_hist, 3),
                "outcome":   "WIN" if exit_type in ("t1", "t2") else "LOSS",
                "session":   trade.get("session", session_label()),
                "duration":  _dur_str,
                "opened_at": trade.get("opened_at", ""),
                "closed_at": datetime.now(timezone.utc).isoformat(),
                "score":     trade.get("score", 0),
                "reasons":   trade.get("reasons", []),
            })

            to_remove.append(pair_label)

    for pair_label in to_remove:
        del active_trades[pair_label]


def _record_t1_pnl(pair_label: str, trade: dict, exit_price: float):
    """Record partial T1 P&L in session tracker."""
    global session_pnl
    entry = trade["entry"]
    direction = trade["direction"]
    pnl_pct = ((exit_price - entry) / entry * 100) if direction == "LONG" \
              else ((entry - exit_price) / entry * 100)
    session_pnl["t1_hits"] += 1
    session_pnl["total_pnl_pct"] += pnl_pct / 2  # partial close credit


# 
# EMBED BUILDERS
# 

def make_premium_embed(pair_label: str, signal: dict, htf_trend: str, counter_trend: bool) -> discord.Embed:
    """Build Discord embed for premium SMC signal."""
    direction = signal["direction"].upper()
    color = 0x00E676 if signal["direction"] == "long" else 0xFF5252
    rating = signal.get("rating", "B")

    title = f"{'' if direction == 'LONG' else ''} {pair_label}  {direction} Signal [{rating}-Grade]"
    embed = discord.Embed(title=title, color=color)
    conf_label, conf_dot = confidence_tier(signal["score"])
    embed.add_field(name="Engine", value=" Premium SMC/ICT", inline=True)
    embed.add_field(name="Session", value=session_label(), inline=True)
    embed.add_field(name="Confidence", value=f"{conf_dot} {conf_label}", inline=True)
    # v9.0 Feature 4: Score normalization  theoretical max ~28 in normal conditions
    _score_potential = signal.get("score_potential", 28)
    _score_note = f"Score: **{signal['score']}** / ~{_score_potential} potential"
    # v9.5 Feature 6: Signal score percentile vs last 50 signals in SIGNAL_LOG
    _pct_note = ""
    if len(SIGNAL_LOG) >= 3:
        _past_scores = [e.get("score", 0) for e in SIGNAL_LOG]
        _sig_score_val = signal.get("score", 0)
        _below = sum(1 for s in _past_scores if s < _sig_score_val)
        _percentile = int(_below / len(_past_scores) * 100)
        _top_pct = 100 - _percentile
        _pct_note = f"\n *Top {_top_pct}% of signals (better than {_percentile}% of last {len(_past_scores)} setups)*"
    embed.add_field(name="Signal Score", value=f"{score_bar(signal['score'])}\n{next_tier_display(signal['score'])}\n*{_score_note}*{_pct_note}", inline=False)
    # v9.0 Feature 1: MTF consensus display
    _mtf = signal.get("mtf_consensus")
    if _mtf:
        _mtf_icons = {0: " None", 1: " 1/3", 2: " 2/3", 3: " 3/3"}
        _mtf_str = _mtf_icons.get(_mtf["agreeing"], "")
        if _mtf["tfs_scored"]:
            _mtf_str += f" ({', '.join(_mtf['tfs_scored'])})"
        if _mtf["avg_score"] > 0:
            _mtf_str += f"  avg score {_mtf['avg_score']:.1f}"
        embed.add_field(name=" MTF Alignment", value=_mtf_str, inline=True)
    # v8.6 Feature 1: Signal Strength Meter
    embed.add_field(name=" Signal Meter", value=signal_strength_meter(signal['score']), inline=False)
    atr_val  = signal.get("atr", 0) or 0
    entry_p  = signal["entry"]
    atr_pct  = (atr_val / entry_p * 100) if entry_p > 0 and atr_val > 0 else None
    atr_str  = f"{price_fmt(pair_label, atr_val)}  ({atr_pct:.2f}% of price)" if atr_pct else ""

    embed.add_field(name=" Limit Entry", value=price_fmt(pair_label, signal["entry"]), inline=True)
    _sl_mult_val = signal.get("sl_atr_mult", 1.0)
    _sl_mult_str = f"{price_fmt(pair_label, signal['sl'])}  ({_sl_mult_val:.2f} ATR)"
    embed.add_field(name="Stop Loss", value=_sl_mult_str, inline=True)
    embed.add_field(name="ATR (volatility)", value=atr_str, inline=True)
    embed.add_field(name="Target 1", value=price_fmt(pair_label, signal["t1"]), inline=True)
    embed.add_field(name="Target 2", value=price_fmt(pair_label, signal["t2"]), inline=True)
    # R:R to T2
    _entry_p = signal["entry"]
    _sl_p    = signal["sl"]
    _t2_p    = signal["t2"]
    if abs(_entry_p - _sl_p) > 0:
        _rr = abs(_entry_p - _t2_p) / abs(_entry_p - _sl_p)
        embed.add_field(name="R:R to T2", value=f"1 : {_rr:.2f}", inline=True)
    embed.add_field(name="HTF Trend", value=htf_trend.upper(), inline=True)
    # HTF candle bias is stored in signal dict if available
    htf_bias = signal.get("htf_candle_bias")
    if htf_bias:
        bias_val = f"{htf_bias['bias_emoji']} {htf_bias['bias_label']}  ({htf_bias['bull_count']}/{htf_bias['lookback']} bull)"
        embed.add_field(name="4H Candle Bias", value=bias_val, inline=True)
    if counter_trend:
        embed.add_field(name=" Counter-Trend", value="Against HTF bias  elevated risk", inline=True)

    reasons_text = "\n".join(f" {r}" for r in signal["reasons"])
    embed.add_field(name="Confluence", value=reasons_text or "", inline=False)

    # Score Breakdown field (up to 8 reasons, then show remainder count)
    _reasons_list = signal.get("reasons", [])
    if _reasons_list:
        _shown = _reasons_list[:8]
        _breakdown_lines = [f" {r}" for r in _shown]
        if len(_reasons_list) > 8:
            _breakdown_lines.append(f"+ {len(_reasons_list) - 8} more")
        embed.add_field(name=" Score Breakdown", value="\n".join(_breakdown_lines), inline=False)

    # --- Upgrade 8: Why This Trade ---
    why = make_why_explanation(signal, htf_trend, counter_trend)
    embed.add_field(name=" Why This Trade", value=why, inline=False)
    embed.add_field(name=" Entry Note", value="Entry is the POI level (limit order zone). Place a limit order  do not chase if price has moved past the zone.", inline=False)

    # v8.7 Feature 3: ATR-based position sizing with concrete $ calculation
    _acct = ACCOUNT_SIZE
    _risk_amt = _acct * DEFAULT_RISK_PCT  # 1% of account
    _sl_dist_abs = abs(signal["entry"] - signal["sl"])
    _sl_dist_pct = (_sl_dist_abs / signal["entry"] * 100) if signal["entry"] > 0 else 0
    if _sl_dist_abs > 0:
        _suggested_usd = _risk_amt / (_sl_dist_pct / 100) if _sl_dist_pct > 0 else 0
        _units_calc = _risk_amt / _sl_dist_abs
        _units_str2 = f"{_units_calc:.4f}" if _units_calc < 1 else f"{_units_calc:.2f}"
        _pos_value = (
            f"Account: **${_acct:,.0f}**  Risk: **${_risk_amt:.0f}** (1%)\n"
            f"SL distance: {price_fmt(pair_label, _sl_dist_abs)} ({_sl_dist_pct:.2f}%)\n"
            f"Suggested size: **{_units_str2} units** (~${_suggested_usd:,.0f} notional)\n"
            f"*Use `!account [amount]` to set your account size.*"
        )
    else:
        _pos_value = (
            f"Account: **${_acct:,.0f}**  Risk: **${_risk_amt:.0f}** (1%)\n"
            f"Formula: Risk  SL% = Position size in USD\n"
            f"*Use `!account [amount]` to set your account size.*"
        )
    embed.add_field(name=" Position Sizing (ATR-Based)", value=_pos_value, inline=False)

    # Position sizing advisory based on score
    _sig_score = signal.get("score", 0)
    if _sig_score >= 12:
        _sizing_advice = "Full size (high conviction)"
    elif _sig_score >= 9:
        _sizing_advice = "75% size (medium conviction)"
    else:
        _sizing_advice = "50% size (standard)"
    embed.add_field(name=" Position Sizing", value=f"*{_sizing_advice}*  advisory only", inline=False)

    # v8.8 Feature 2: Confluence heatmap  group reasons by category
    _heat_reasons = signal.get("reasons", [])
    _heat_groups = {
        "Structure":  ["mss", "sfp", "order block", "ob", "s/r zone", "bos", "break of structure", "liquidity sweep", "equal"],
        "Momentum":   ["rsi", "macd", "stochrsi", "stoch rsi", "divergence", "candles aligned", "ema20 momentum"],
        "Candle":     ["engulfing", "hammer", "pin bar", "doji", "inside bar", "shooting star", "three-line", "rejection wick", "wick rejection"],
        "Volume":     ["poc", "volume node", "volume spike", "volume profile", "vwap", "volume trend"],
        "Multi-TF":   ["htf", "4h", "weekly trend", "15m trend", "ichimoku", "1h swing", "mtf"],
    }
    _heat_max = {"Structure": 5, "Momentum": 5, "Candle": 5, "Volume": 5, "Multi-TF": 5}
    _heat_lines = []
    for _grp, _keywords in _heat_groups.items():
        _count = 0
        for _r in _heat_reasons:
            _rl = _r.lower()
            if any(_kw in _rl for _kw in _keywords):
                _count += 1
        _count = min(_count, _heat_max[_grp])
        _mx = _heat_max[_grp]
        _bar = "" * _count + "" * (_mx - _count)
        _heat_lines.append(f"`{_grp:<9}` {_bar}  {_count}/{_mx}")
    embed.add_field(
        name=" Confluence Heat",
        value="\n".join(_heat_lines),
        inline=False
    )

    # v9.4 Feature 2: Volatility regime display
    _vol_regime_val = signal.get("vol_regime")
    if _vol_regime_val:
        _vol_icon_e = "" if _vol_regime_val == "High" else ("" if _vol_regime_val == "Low" else "")
        embed.add_field(name=" Vol Regime", value=f"{_vol_icon_e} {_vol_regime_val}", inline=True)

    embed.set_footer(text=f"Chartwise v10.0  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    return embed


def make_standard_embed(pair_label: str, signal: dict, htf_trend: str, counter_trend: bool) -> discord.Embed:
    """Build Discord embed for standard EMA signal."""
    direction = signal["direction"].upper()
    color = 0x00B0FF if signal["direction"] == "long" else 0xFF9100
    rating = signal.get("rating", "B")

    title = f"{'' if direction == 'LONG' else ''} {pair_label}  {direction} Signal [{rating}-Grade]"
    embed = discord.Embed(title=title, color=color)
    conf_label, conf_dot = confidence_tier(signal["score"])
    embed.add_field(name="Engine", value=" Standard EMA", inline=True)
    embed.add_field(name="Session", value=session_label(), inline=True)
    embed.add_field(name="Confidence", value=f"{conf_dot} {conf_label}", inline=True)
    embed.add_field(name="Signal Score", value=f"{score_bar(signal['score'])}\n{next_tier_display(signal['score'])}", inline=False)
    # v8.6 Feature 1: Signal Strength Meter
    embed.add_field(name=" Signal Meter", value=signal_strength_meter(signal['score']), inline=False)
    ema_atr  = signal.get("atr", 0) or 0
    ema_ep   = signal["entry"]
    ema_atr_pct = (ema_atr / ema_ep * 100) if ema_ep > 0 and ema_atr > 0 else None
    ema_atr_str = f"{price_fmt(pair_label, ema_atr)}  ({ema_atr_pct:.2f}%)" if ema_atr_pct else ""

    embed.add_field(name=" EMA Entry", value=price_fmt(pair_label, signal["entry"]), inline=True)
    embed.add_field(name="Stop Loss", value=price_fmt(pair_label, signal["sl"]), inline=True)
    embed.add_field(name="ATR (volatility)", value=ema_atr_str, inline=True)
    embed.add_field(name="Target 1", value=price_fmt(pair_label, signal["t1"]), inline=True)
    embed.add_field(name="Target 2", value=price_fmt(pair_label, signal["t2"]), inline=True)
    # R:R to T2
    _s_entry = signal["entry"]
    _s_sl    = signal["sl"]
    _s_t2    = signal["t2"]
    if abs(_s_entry - _s_sl) > 0:
        _s_rr = abs(_s_entry - _s_t2) / abs(_s_entry - _s_sl)
        embed.add_field(name="R:R to T2", value=f"1 : {_s_rr:.2f}", inline=True)
    embed.add_field(name="HTF Trend", value=htf_trend.upper(), inline=True)
    # HTF candle bias is stored in signal dict if available
    htf_bias_s = signal.get("htf_candle_bias")
    if htf_bias_s:
        bias_val_s = f"{htf_bias_s['bias_emoji']} {htf_bias_s['bias_label']}  ({htf_bias_s['bull_count']}/{htf_bias_s['lookback']} bull)"
        embed.add_field(name="4H Candle Bias", value=bias_val_s, inline=True)
    if counter_trend:
        embed.add_field(name=" Counter-Trend", value="Against HTF bias  elevated risk", inline=True)

    reasons_text = "\n".join(f" {r}" for r in signal["reasons"])
    embed.add_field(name="Confluence", value=reasons_text or "", inline=False)

    # --- Upgrade 8: Why This Trade ---
    why = make_why_explanation(signal, htf_trend, counter_trend)
    embed.add_field(name=" Why This Trade", value=why, inline=False)
    embed.add_field(name=" Entry Note", value="Entry is at the EMA21 crossover level. Place at or near this price  do not chase if price has moved significantly.", inline=False)

    # Position sizing suggestion (1% risk on $10k account  use !risk to personalize)
    pos = calc_position_size(signal["entry"], signal["sl"])
    if pos["units"] > 0:
        units_str = f"{pos['units']:.4f}" if pos['units'] < 1 else f"{pos['units']:.2f}"
        embed.add_field(
            name=" Position Size (1% risk / $10k)",
            value=f"`{units_str} units`  Risk: ${pos['risk_usd']:.0f}  SL dist: {price_fmt(pair_label, pos['sl_dist'])}\n*Use `!risk` to customize for your account.*",
            inline=False
        )

    # Position sizing advisory based on score
    _std_score = signal.get("score", 0)
    if _std_score >= 12:
        _std_sizing = "Full size (high conviction)"
    elif _std_score >= 9:
        _std_sizing = "75% size (medium conviction)"
    else:
        _std_sizing = "50% size (standard)"
    embed.add_field(name=" Position Sizing", value=f"*{_std_sizing}*  advisory only", inline=False)

    # v9.4 Feature 2: Volatility regime display
    _vol_regime_std = signal.get("vol_regime")
    if _vol_regime_std:
        _vol_icon_s = "" if _vol_regime_std == "High" else ("" if _vol_regime_std == "Low" else "")
        embed.add_field(name=" Vol Regime", value=f"{_vol_icon_s} {_vol_regime_std}", inline=True)

    embed.set_footer(text=f"Chartwise v10.0  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    return embed


def make_exit_embed(pair_label: str, trade: dict, exit_type: str, exit_price: float) -> discord.Embed:
    """Build Discord embed for trade exit."""
    direction = trade["direction"]
    entry = trade["entry"]

    # --- Upgrade 9: % P&L ---
    pnl_pct = ((exit_price - entry) / entry * 100) if direction == "LONG" \
              else ((entry - exit_price) / entry * 100)
    pnl_pct_str = f"{'+' if pnl_pct >= 0 else ''}{pnl_pct:.2f}%"
    pnl_usd = exit_price - entry if direction == "LONG" else entry - exit_price
    pnl_str = f"{'+' if pnl_usd >= 0 else ''}{price_fmt(pair_label, abs(pnl_usd))}"

    if exit_type == "stop":
        color = 0xFF5252
        title = f" {pair_label}  Stop Loss Hit"
        outcome = " Loss"
    elif exit_type == "t1":
        color = 0xFFD740
        title = f" {pair_label}  Target 1 Hit"
        outcome = " Partial Win"
    elif exit_type == "t2":
        color = 0x00E676
        title = f" {pair_label}  Target 2 Hit"
        outcome = " Full Win"
    else:
        color = 0x9E9E9E
        title = f" {pair_label}  Exit"
        outcome = "Closed"

    # R-multiple: how many R's (risk units) the trade made or lost
    sl_dist_trade = abs(entry - trade.get("sl", entry))
    r_multiple = (abs(exit_price - entry) / max(sl_dist_trade, 1e-9))
    if pnl_usd < 0:
        r_multiple = -r_multiple  # negative on loss
    r_str = f"{'+' if r_multiple >= 0 else ''}{r_multiple:.2f}R"

    embed = discord.Embed(title=title, color=color)
    embed.add_field(name="Direction", value=direction, inline=True)
    embed.add_field(name="Entry", value=price_fmt(pair_label, entry), inline=True)
    embed.add_field(name="Exit", value=price_fmt(pair_label, exit_price), inline=True)
    embed.add_field(name="P/L (price)", value=pnl_str, inline=True)
    embed.add_field(name="% P&L", value=pnl_pct_str, inline=True)
    embed.add_field(name="R Multiple", value=f"**{r_str}**", inline=True)
    embed.add_field(name="Outcome", value=outcome, inline=True)

    if exit_type == "t1":
        # Show R multiple for the partial close
        sl_dist = abs(entry - trade.get("sl", entry))
        r_val = abs(exit_price - entry) / max(sl_dist, 1e-9)
        embed.add_field(
            name=" Partial Close (50%)",
            value=f"**{r_val:.1f}R** banked. SL auto-moved to entry (breakeven). Trailing stop active  let rest run to T2.",
            inline=False
        )
        # Track partial P&L
        _record_t1_pnl(pair_label, trade, exit_price)

    if exit_type == "t2":
        # Show full R multiple
        sl_dist = abs(entry - trade.get("sl", entry))
        r_val = abs(exit_price - entry) / max(sl_dist, 1e-9)
        embed.add_field(name=" R Multiple", value=f"{r_val:.1f}R", inline=True)
        score = trade.get("score", "?")
        embed.add_field(name="Signal Score", value=str(score), inline=True)

    embed.set_footer(text=f"Chartwise v10.0  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    return embed


def make_postmortem_embed(pair_label: str, trade: dict, current_price: float) -> discord.Embed:
    """Build post-mortem analysis embed after a stop loss is hit."""
    direction = trade["direction"]
    entry = trade["entry"]
    sl = trade["sl"]
    t1 = trade["t1"]
    t2 = trade["t2"]
    score = trade.get("score", "?")
    signal_type = trade.get("signal_type", "?")
    reasons = trade.get("reasons", [])
    t1_hit = trade.get("t1_hit", False)

    # Determine failure category
    distance_to_t1 = abs(t1 - entry)
    distance_moved = abs(current_price - entry)
    pct_toward_t1 = min(distance_moved / max(distance_to_t1, 1e-9) * 100, 100)

    if t1_hit:
        failure_type = "Moved to breakeven after T1  late reversal"
        what_happened = (
            "Trade hit T1 and SL was moved to entry (breakeven). Price then reversed and hit the breakeven SL. "
            "The market gave a partial win opportunity  capital was protected by the breakeven move."
        )
    elif pct_toward_t1 < 30:
        failure_type = "Immediate rejection  structure did not hold"
        what_happened = (
            "Price reversed almost immediately after entry, suggesting the sweep/break-of-structure "
            "was a liquidity grab rather than a genuine structural shift. The setup had confluence "
            "but market makers pushed price through the level before continuation."
        )
    elif pct_toward_t1 < 70:
        failure_type = "Partial move  momentum failed mid-run"
        what_happened = (
            "Price moved partially toward T1 but stalled. This typically signals weakening momentum, "
            "either from opposing liquidity or a higher-timeframe resistance that wasn't visible on 5m."
        )
    else:
        failure_type = "Near-miss  reversed after approaching T1"
        what_happened = (
            "Price came close to T1 but reversed. Consider whether a tighter T1 or earlier partial "
            "close could have captured profit before the reversal."
        )

    # What to learn
    learn_points = []
    if not t1_hit:
        learn_points.append(" Watch for opposing HTF liquidity before entry")
        learn_points.append(" Confirm displacement candle closed above/below key level")
    if signal_type == "standard":
        learn_points.append(" EMA crossover entries are lower probability  prefer SMC setups")
    if score < 8:
        learn_points.append(f" Score was {score}/10  wait for 8+ in choppy conditions")
    learn_points.append(" Check for news/macro events that could override technicals")
    learn_points.append(" This pattern has been logged for adaptive learning")

    embed = discord.Embed(
        title=f" {pair_label}  Trade Post-Mortem",
        description=f"**Why the SL hit:** {failure_type}",
        color=0xFF6B35
    )
    # R-distance: how far price was from SL at point of failure
    sl_dist = abs(entry - sl)
    moved_from_entry = abs(current_price - entry)
    r_drawdown = moved_from_entry / max(sl_dist, 1e-9)

    embed.add_field(name="Direction", value=direction, inline=True)
    embed.add_field(name="Engine", value=signal_type.upper() if signal_type else "?", inline=True)
    embed.add_field(name="Score", value=str(score), inline=True)
    embed.add_field(name="Entry", value=price_fmt(pair_label, entry), inline=True)
    embed.add_field(name="SL", value=price_fmt(pair_label, sl), inline=True)
    embed.add_field(name="T1 Hit?", value=" Yes (BE)" if t1_hit else " No", inline=True)
    embed.add_field(name="R Drawdown", value=f"{r_drawdown:.1f}R from entry", inline=True)
    embed.add_field(name="Session", value=session_label(), inline=True)
    embed.add_field(name="Consecutive L", value=str(_consecutive_losses), inline=True)
    embed.add_field(name=" What Happened", value=what_happened, inline=False)

    if reasons:
        confluence_text = "\n".join(f" {r}" for r in reasons[:6])
        embed.add_field(name="Confluence That Was Present", value=confluence_text, inline=False)

    embed.add_field(name=" What to Learn", value="\n".join(learn_points), inline=False)
    embed.set_footer(text=f"Chartwise v10.0  Logged for adaptive learning  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    return embed


def make_status_embed() -> discord.Embed:
    """Build comprehensive bot health dashboard embed. (v9.4 enhanced)"""
    embed = discord.Embed(title=" Chartwise v10.0  Bot Health Dashboard", color=0x7C4DFF)

    #  Row 1: Scan interval 
    if current_scan_interval == 60:
        _scan_reason = "volatile (BB expanding > 2%)"
        _scan_emoji  = " Fast"
    elif current_scan_interval == 180:
        _scan_reason = "squeeze (BB width < 0.5%)"
        _scan_emoji  = " Slow"
    else:
        _scan_reason = "normal market conditions"
        _scan_emoji  = " Normal"
    embed.add_field(
        name=" Scan Interval",
        value=f"**{current_scan_interval}s** {_scan_emoji}\nReason: {_scan_reason}",
        inline=True
    )

    #  Row 1: Sensitivity 
    embed.add_field(
        name=" Sensitivity",
        value=f"Level **{_sensitivity_level}** / 5\nMIN_SCORE = {MIN_SCORE}",
        inline=True
    )

    #  Row 1: Session 
    embed.add_field(
        name=" Session",
        value=session_label(),
        inline=True
    )

    #  Signal count today vs yesterday 
    _now_utc = datetime.now(timezone.utc)
    _today_str = _now_utc.strftime("%Y-%m-%d")
    _yesterday_str = (_now_utc - timedelta(days=1)).strftime("%Y-%m-%d")
    _signals_today = 0
    _signals_yest  = 0
    _wins_this_week  = 0
    _losses_this_week  = 0
    _wins_last_week  = 0
    _losses_last_week  = 0
    _week_start = _now_utc - timedelta(days=_now_utc.weekday())  # Monday
    _last_week_start = _week_start - timedelta(days=7)
    try:
        _all_sigs = _read_signals()
        for _s in _all_sigs:
            _s_ts = _s.get("ts", 0)
            _s_dt = datetime.fromtimestamp(_s_ts, tz=timezone.utc) if _s_ts else None
            if _s_dt:
                if _s_dt.strftime("%Y-%m-%d") == _today_str:
                    _signals_today += 1
                elif _s_dt.strftime("%Y-%m-%d") == _yesterday_str:
                    _signals_yest += 1
                # Win rate this week vs last week
                _outcome = _s.get("outcome", "PENDING")
                if _s_dt >= _week_start.replace(hour=0, minute=0, second=0, microsecond=0):
                    if _outcome == "WIN":
                        _wins_this_week += 1
                    elif _outcome == "LOSS":
                        _losses_this_week += 1
                elif _s_dt >= _last_week_start.replace(hour=0, minute=0, second=0, microsecond=0):
                    if _outcome == "WIN":
                        _wins_last_week += 1
                    elif _outcome == "LOSS":
                        _losses_last_week += 1
    except Exception:
        pass
    embed.add_field(
        name=" Signals Today / Yesterday",
        value=f"Today: **{_signals_today}**  Yesterday: **{_signals_yest}**",
        inline=True
    )

    _tw_total = _wins_this_week + _losses_this_week
    _lw_total = _wins_last_week + _losses_last_week
    _tw_wr = f"{_wins_this_week / _tw_total * 100:.0f}%" if _tw_total > 0 else "N/A"
    _lw_wr = f"{_wins_last_week / _lw_total * 100:.0f}%" if _lw_total > 0 else "N/A"
    embed.add_field(
        name=" Win Rate (This Wk / Last Wk)",
        value=f"This week: **{_tw_wr}** ({_tw_total} closed)\nLast week: **{_lw_wr}** ({_lw_total} closed)",
        inline=True
    )

    #  Active pairs / watchlist / price alerts 
    embed.add_field(
        name=" Active Pairs",
        value=f"**{len(DYNAMIC_PAIRS)}** pairs scanning\n{', '.join(p['label'] for p in DYNAMIC_PAIRS)}",
        inline=True
    )
    _wl_count = sum(len(v) for v in WATCHLIST.values())
    embed.add_field(
        name=" Watchlist",
        value=f"**{_wl_count}** near-miss signal{'s' if _wl_count != 1 else ''}\n`!watchlist` to view",
        inline=True
    )
    embed.add_field(
        name=" Price Alerts",
        value=f"**{len(PRICE_ALERTS)}** active alert{'s' if len(PRICE_ALERTS) != 1 else ''}\n`!alert list` to view",
        inline=True
    )

    #  Open positions 
    if not ALERTS_ENABLED:
        embed.add_field(name=" Alerts muted", value="Signals logged but NOT posted. `!alerts on` to re-enable.", inline=False)
    if active_trades:
        trade_lines = []
        for label, trade in active_trades.items():
            t1_status = " T1 hit" if trade.get("t1_hit") else " Open"
            duration_str = format_trade_duration(trade["opened_at"]) if trade.get("opened_at") else "?"
            trade_lines.append(
                f"**{label}** {trade['direction']} @ {price_fmt(label, trade['entry'])} [{t1_status}]  {duration_str}"
            )
        embed.add_field(name=" Open Positions", value="\n".join(trade_lines), inline=False)
    else:
        embed.add_field(name=" Open Positions", value="None", inline=False)

    #  Circuit breaker 
    if _circuit_tripped_at > 0:
        _cb_elapsed = time.time() - _circuit_tripped_at
        _cb_remaining = max(0, int((CIRCUIT_BREAKER_COOLDOWN - _cb_elapsed) / 60))
        _cb_val = f" **TRIPPED**  {_cb_remaining}m remaining\nTripped after {CIRCUIT_BREAKER_LOSSES} consecutive losses"
    else:
        _cb_val = f" **OK**  {_consecutive_losses}/{CIRCUIT_BREAKER_LOSSES} consecutive losses\nWill trip at {CIRCUIT_BREAKER_LOSSES} losses in a row"
    embed.add_field(name=" Circuit Breaker", value=_cb_val, inline=False)

    #  Avg score per pair 
    if SCORE_HISTORY:
        score_lines = []
        for _pl, _dq in SCORE_HISTORY.items():
            if _dq:
                _avg = sum(_dq) / len(_dq)
                score_lines.append(f"**{_pl}:** avg {_avg:.1f} (last {len(_dq)})")
        if score_lines:
            embed.add_field(name=" Avg Signal Score", value="  ".join(score_lines), inline=False)

    embed.set_footer(text=f"Chartwise v10.0  {datetime.now(timezone.utc).strftime('%H:%M UTC')}  !help for all commands")
    return embed


# 
# SCAN PAIR
# 


@bot.command(name="vwap")
async def cmd_vwap(ctx):
    """Show current VWAP vs price for all pairs."""
    embed = discord.Embed(title=" VWAP Bias Dashboard", color=0x00CED1)
    for pair in PAIRS:
        try:
            candles = await fetch_coinbase_candles(pair["product_id"], granularity=900, limit=30)
            if candles and len(candles) >= 24:
                vwap_val = calc_vwap(candles)
                price = candles[-1]["close"]
                if vwap_val:
                    diff_pct = (price - vwap_val) / vwap_val * 100
                    bias = " Bullish" if price > vwap_val else " Bearish"
                    embed.add_field(
                        name=pair["label"],
                        value=f"{bias}\nPrice: {price_fmt(pair['label'], price)}\nVWAP: {price_fmt(pair['label'], vwap_val)}\nDiff: {diff_pct:+.2f}%",
                        inline=True,
                    )
        except Exception:
            embed.add_field(name=pair["label"], value=" Error fetching", inline=True)
    await ctx.send(embed=embed)


# 
# v9.0 Feature 1: Multi-Timeframe Signal Consensus
# 

async def calc_mtf_consensus(pair: dict, direction: str) -> dict:
    """
    Run analyze() on 5m, 15m, and 1H candles and return how many timeframes
    agree with the given signal direction.

    Returns dict:
      {
        "agreeing": int,   # 0-3 TFs that score >= MIN_SCORE in the signal direction
        "total": 3,
        "avg_score": float,
        "tfs_scored": list[str],  # TF labels that fired a qualifying signal
      }
    """
    tf_map = [
        ("5m",  "5m"),
        ("15m", "15m"),
        ("1H",  "1h"),
    ]
    agreeing = 0
    scores = []
    tfs_scored = []
    for tf_label, tf_key in tf_map:
        try:
            candles_tf = await fetch_candles(pair, timeframe=tf_key)
            if not candles_tf or len(candles_tf) < 30:
                continue
            result = analyze(candles_tf, direction)
            if result and result.get("score", 0) >= MIN_SCORE:
                agreeing += 1
                scores.append(result["score"])
                tfs_scored.append(tf_label)
        except Exception as e:
            print(f"[MTF] {pair['label']} {tf_label} consensus check error: {e}")
    avg_score = sum(scores) / len(scores) if scores else 0.0
    return {
        "agreeing": agreeing,
        "total": 3,
        "avg_score": avg_score,
        "tfs_scored": tfs_scored,
    }


async def scan_pair(pair: dict, channel: discord.TextChannel):
    """Scan a single pair for signals. Uses per-pair lock to prevent race conditions."""
    global _daily_opened
    pair_label = pair["label"]

    async with pair_locks[pair_label]:
        # --- Upgrade 2: Hard block while trade is open ---
        if pair_label in active_trades:
            # Only do exit monitoring (handled by update_active_trades), skip signal search
            return

        # All pairs are crypto (24/7)  no session gate needed

        #  Cooldown gates 
        now = time.time()
        last_time = last_signal_time.get(pair_label, 0)

        # Dynamic cooldown: scale based on last trade result for this pair
        last_result = last_trade_result.get(pair_label)
        if last_result == "LOSS":
            effective_cooldown = max(MIN_COOLDOWN, int(SIGNAL_COOLDOWN * 1.5))  # +50% after loss
        elif last_result == "WIN":
            effective_cooldown = max(MIN_COOLDOWN, int(SIGNAL_COOLDOWN * 0.8))  # -20% after win (momentum)
        else:
            effective_cooldown = SIGNAL_COOLDOWN  # default: no history

        # Base cooldown
        if now - last_time < effective_cooldown:
            return

        # Post-WIN cooldown: market ran, don't re-enter too soon
        last_win = last_win_time.get(pair_label, 0)
        if now - last_win < POST_WIN_COOLDOWN:
            print(f"[COOL] {pair_label}: post-win cooldown ({int((POST_WIN_COOLDOWN - (now - last_win)) / 60)}m remaining)")
            return

        # Fetch candles
        candles_5m = await fetch_candles(pair, timeframe="5m")
        if not candles_5m or len(candles_5m) < 30:
            print(f"[WARN] {pair_label}: insufficient candles")
            return

        # HTF trend (1H) + 4H trend
        htf_trend = await get_htf_trend(pair)
        trend_4h  = await get_4h_trend(pair)

        # 15m trend alignment check  adds a mid-timeframe confirmation layer
        candles_15m = await fetch_candles(pair, timeframe="15m")
        mtf_trend = "unknown"
        if candles_15m and len(candles_15m) >= 20:
            closes_15 = [c["close"] for c in candles_15m]
            ema9_15  = ema(closes_15, 9)
            ema21_15 = ema(closes_15, 21)
            if ema9_15 and ema21_15:
                mtf_trend = "long" if ema9_15 > ema21_15 else "short"

        # Run both engines
        smc_signal = analyze(candles_5m, pair_label)
        std_signal = analyze_standard(candles_5m, pair_label)

        # v9.1 Feature 1: Capture near-miss signals for watchlist
        if smc_signal and smc_signal.get("near_miss"):
            _nm = smc_signal
            smc_signal = None  # don't process as a real signal
            _existing_wl = WATCHLIST.setdefault(pair_label, [])
            # Avoid duplicate watchlist entries for same direction
            _dup = any(
                w.get("direction") == _nm["direction"] and
                abs(w.get("entry", 0) - _nm["entry"]) < _nm.get("atr", 1) * 0.5
                for w in _existing_wl
            )
            if not _dup:
                _existing_wl.append({
                    "score": _nm["score"],
                    "direction": _nm["direction"],
                    "entry": _nm["entry"],
                    "sl": _nm["sl"],
                    "t1": _nm["t1"],
                    "t2": _nm["t2"],
                    "atr": _nm.get("atr", 0),
                    "reasons": _nm.get("reasons", []),
                    "time": _nm.get("time", datetime.now(timezone.utc).isoformat()),
                })
                # Keep only last 5 watchlist items per pair
                WATCHLIST[pair_label] = _existing_wl[-5:]
                print(f"[WATCHLIST] {pair_label}: near-miss {_nm['direction'].upper()} score={_nm['score']} added to watchlist")

        # Determine counter-trend
        def is_counter_trend(signal: dict, htf: str) -> bool:
            if htf == "unknown" or htf == "neutral":
                return False
            sig_dir = signal.get("direction", "")
            return (sig_dir == "long" and htf == "short") or (sig_dir == "short" and htf == "long")

        def is_4h_counter_trend(signal: dict) -> bool:
            """True if signal direction opposes the 4H trend."""
            if trend_4h == "unknown":
                return False
            sig_dir = signal.get("direction", "")
            return (sig_dir == "long" and trend_4h == "short") or (sig_dir == "short" and trend_4h == "long")

        # --- Upgrade 7: Counter-trend penalty ---
        if smc_signal:
            counter_trend_smc = is_counter_trend(smc_signal, htf_trend)
            if counter_trend_smc and smc_signal.get("score", 0) < RATING_A:
                print(f"[SKIP] {pair_label} SMC counter-trend signal below A-grade threshold (score={smc_signal['score']})")
                smc_signal = None

        if std_signal:
            counter_trend_std = is_counter_trend(std_signal, htf_trend)
            if counter_trend_std:
                # Skip counter-trend standard signals entirely  too risky
                print(f"[SKIP] {pair_label} Standard counter-trend signal skipped entirely")
                std_signal = None

        # --- v5: 4H trend filter  skip any signal that goes against the 4H trend ---
        # (allows counter-trend 1H trades if the 4H agrees  only blocks true 4H opposition)
        if smc_signal and is_4h_counter_trend(smc_signal):
            sig_score = smc_signal.get("score", 0)
            if sig_score < RATING_A + 2:  # Need 9+ to trade against 4H
                print(f"[SKIP] {pair_label} SMC signal opposes 4H trend ({trend_4h}) and score {sig_score} < 9")
                smc_signal = None

        if std_signal and is_4h_counter_trend(std_signal):
            print(f"[SKIP] {pair_label} EMA signal opposes 4H trend ({trend_4h})  skip")
            std_signal = None

        # 5m entry confirmation
        best_signal = None
        signal_type = None

        if smc_signal:
            confirmed = await confirm_5m_entry(pair, smc_signal["direction"])
            if confirmed:
                best_signal = smc_signal
                signal_type = "premium"

        if best_signal is None and std_signal:
            confirmed = await confirm_5m_entry(pair, std_signal["direction"])
            if confirmed:
                best_signal = std_signal
                signal_type = "standard"

        if best_signal is None:
            # v8.1: log raw signals from engines that were filtered by score/circuit
            # Re-run engines without score gate to capture what was rejected
            _raw_smc = analyze(candles_5m, pair_label) if smc_signal is None else None
            _raw_std = analyze_standard(candles_5m, pair_label) if std_signal is None else None
            _any_raw = _raw_smc or _raw_std or smc_signal or std_signal
            if _any_raw:
                _filt_signal = _any_raw
                _reason_filtered = "score_below_min" if (_filt_signal and _filt_signal.get("score", 0) < MIN_SCORE) else "engine_returned_none"
                FILTERED_LOG.append({
                    "pair":            pair_label,
                    "direction":       _filt_signal.get("direction", "?").upper() if _filt_signal else "?",
                    "score":           _filt_signal.get("score", 0) if _filt_signal else 0,
                    "reason_filtered": _reason_filtered,
                    "time":            datetime.now(timezone.utc).isoformat(),
                })
            return

        #  Same-direction rapid re-entry block 
        sig_dir = best_signal["direction"].upper()
        prev_dir = last_signal_dir.get(pair_label)
        if prev_dir == sig_dir and (now - last_time) < SAME_DIR_BLOCK:
            mins_ago = int((now - last_time) / 60)
            print(f"[BLOCK] {pair_label}: same-direction {sig_dir} re-entry blocked ({mins_ago}m since last {prev_dir})")
            return

        counter_trend_flag = is_counter_trend(best_signal, htf_trend)

        #  Cross-pair correlation filter 
        # If 2+ other pairs have active trades in the OPPOSITE direction, this signal
        # diverges from the broader crypto market  penalize score -1 and flag it.
        # If 2+ other pairs have active trades in the SAME direction, boost +1 (market consensus).
        sig_dir_upper = best_signal["direction"].upper()
        other_active = [
            t for lbl, t in active_trades.items()
            if lbl != pair_label
        ]
        same_dir_count = sum(1 for t in other_active if t.get("direction") == sig_dir_upper)
        opp_dir_count  = sum(1 for t in other_active if t.get("direction") != sig_dir_upper and t.get("direction") in ("LONG", "SHORT"))

        if opp_dir_count >= 2:
            best_signal["score"] = max(0, best_signal.get("score", 0) - 1)
            best_signal.setdefault("reasons", []).append(
                f" Cross-pair divergence: {opp_dir_count} other pairs trading opposite direction"
            )
            print(f"[CORR] {pair_label}: {opp_dir_count} pairs opposite direction  -1 score")
        elif same_dir_count >= 2:
            best_signal["score"] = best_signal.get("score", 0) + 1
            best_signal.setdefault("reasons", []).append(
                f"Cross-pair alignment: {same_dir_count} other pairs in same direction  market consensus"
            )
            print(f"[CORR] {pair_label}: {same_dir_count} pairs same direction  +1 score")

        #  v8.0: Multi-pair correlation filter 
        # If >= 2 pairs already have active trades in the SAME direction as this new signal,
        # that's correlated risk  all positions moving together amplifies drawdown.
        # Penalise score -2 and suggest reduced position size.
        same_dir_active = sum(
            1 for lbl, t in active_trades.items()
            if lbl != pair_label and t.get("direction") == sig_dir_upper
        )
        if same_dir_active >= 2:
            best_signal["score"] = max(0, best_signal.get("score", 0) - 2)
            best_signal.setdefault("reasons", []).append(
                f" Correlated risk: {same_dir_active} pairs already in same direction ({sig_dir_upper})  position size suggested at 50%"
            )
            print(f"[CORR] {pair_label}: correlated risk  {same_dir_active} active {sig_dir_upper} trades  -2 score")

        # MTF alignment: boost score if 15m trend aligns, reduce if diverges
        sig_dir_check = best_signal.get("direction", "")
        if mtf_trend != "unknown":
            if sig_dir_check == mtf_trend:
                best_signal["score"] = best_signal.get("score", 0) + 1
                best_signal.setdefault("reasons", []).append(f"15m trend aligns ({mtf_trend})")
                print(f"[MTF] {pair_label}: 15m trend aligns +1 score")
            else:
                # Counter-15m: lower score by 1 (filters more marginal signals)
                best_signal["score"] = max(0, best_signal.get("score", 0) - 1)
                best_signal.setdefault("reasons", []).append(f" 15m trend diverges ({mtf_trend})")
                print(f"[MTF] {pair_label}: 15m trend diverges -1 score")

        # v8.6 Feature 3: Weekly trend filter via 42-candle 4H SMA (7 days  6 candles/day)
        # If LONG signal in weekly downtrend OR SHORT signal in weekly uptrend  reduce score -1
        try:
            candles_4h_weekly = await fetch_candles(pair, timeframe="4h")
            if candles_4h_weekly and len(candles_4h_weekly) >= 42:
                weekly_closes = [c["close"] for c in candles_4h_weekly[-42:]]
                weekly_sma42 = sum(weekly_closes) / len(weekly_closes)
                weekly_current_price = candles_4h_weekly[-1]["close"]
                weekly_trend_dir = "long" if weekly_current_price > weekly_sma42 else "short"
                sig_weekly_dir = best_signal.get("direction", "")
                if sig_weekly_dir and sig_weekly_dir != weekly_trend_dir:
                    best_signal["score"] = max(0, best_signal.get("score", 0) - 1)
                    best_signal.setdefault("reasons", []).append(
                        " Against weekly trend  reduced confidence"
                    )
                    print(f"[WEEKLY] {pair_label}: signal {sig_weekly_dir} vs weekly trend {weekly_trend_dir}  -1 score")
                else:
                    print(f"[WEEKLY] {pair_label}: signal aligns with weekly trend ({weekly_trend_dir})")
        except Exception as e:
            print(f"[WARN] Weekly trend filter failed for {pair_label}: {e}")

        #  v8.8 Feature 4: Market regime  reduce score if ranging 
        try:
            candles_4h_regime = await fetch_candles(pair, timeframe="4h")
            if candles_4h_regime and len(candles_4h_regime) >= 25:
                _regime = detect_market_regime(candles_4h_regime, lookback=20)
                best_signal["market_regime"] = _regime
                if _regime == "Ranging":
                    best_signal["score"] = max(0, best_signal.get("score", 0) - 1)
                    best_signal.setdefault("reasons", []).append(
                        " Ranging market regime  breakout-dependent signal, reduced confidence"
                    )
                    print(f"[REGIME] {pair_label}: Ranging market  -1 score")
                else:
                    print(f"[REGIME] {pair_label}: {_regime}")

                # v9.1 Feature 5: Adaptive SL  apply regime multiplier on top of BB squeeze mult
                if best_signal.get("type") == "premium":
                    _base_mult = best_signal.get("sl_atr_mult", 1.0)
                    if _regime in ("Trending Up", "Trending Down"):
                        _regime_mult = 1.2
                    elif _regime == "Ranging":
                        _regime_mult = 0.8
                    else:
                        _regime_mult = 1.0
                    _new_mult = _base_mult * _regime_mult
                    # Recompute SL with new multiplier
                    _entry_v = best_signal["entry"]
                    _atr_v = best_signal.get("atr", 0) or 0
                    _sess_mult = session_sl_multiplier()
                    _sweep_v = best_signal.get("sweep_level", _entry_v)
                    if best_signal["direction"] == "long":
                        best_signal["sl"] = _sweep_v - _atr_v * _new_mult * _sess_mult
                    else:
                        best_signal["sl"] = _sweep_v + _atr_v * _new_mult * _sess_mult
                    best_signal["sl_atr_mult"] = _new_mult
                    print(f"[ADAPTIVE_SL] {pair_label}: {_regime}  SL mult {_base_mult:.2f}{_regime_mult:.1f} = {_new_mult:.2f}")
        except Exception as _regime_err:
            print(f"[WARN] Market regime check failed for {pair_label}: {_regime_err}")

        #  Dynamic TP: use next 1H swing level as T1 if closer than ATR-based T1 
        # This sets a more precise T1 target at real market structure rather than a fixed 2ATR
        try:
            candles_1h = await fetch_candles(pair, timeframe="1h")
            if candles_1h and len(candles_1h) >= 20:
                entry_price = best_signal["entry"]
                direction_str = best_signal["direction"]
                htf_level = find_next_htf_level(candles_1h, direction_str, entry_price)
                if htf_level is not None:
                    atr_val = best_signal.get("atr", 0) or 0
                    # Only use HTF level as T1 if it's within 3 ATR and better than 1:1 R/R
                    sl_dist = abs(entry_price - best_signal["sl"])
                    level_dist = abs(htf_level - entry_price)
                    if level_dist >= sl_dist * 1.2 and atr_val > 0 and level_dist <= atr_val * 3.5:
                        old_t1 = best_signal["t1"]
                        best_signal["t1"] = htf_level
                        best_signal.setdefault("reasons", []).append(
                            f"T1 set at 1H swing level {price_fmt(pair_label, htf_level)} (dynamic)"
                        )
                        print(f"[DYNTP] {pair_label}: T1 adjusted {price_fmt(pair_label, old_t1)}  {price_fmt(pair_label, htf_level)} (1H level)")
        except Exception as e:
            print(f"[WARN] Dynamic TP failed for {pair_label}: {e}")

        #  Fibonacci retracement TP refinement 
        # After basic entry/SL/TP is set, check if a Fibonacci level (0.618 golden ratio)
        # aligns near T1 or T2 and annotate it. If Fib 0.618 is between entry and T1,
        # use it as T1 for a higher-probability partial exit zone.
        try:
            fib_data = calc_fibonacci_levels(candles_5m, lookback=50)
            if fib_data:
                sig_dir_fib = best_signal["direction"]
                entry_fib   = best_signal["entry"]
                t1_current  = best_signal["t1"]
                atr_fib     = best_signal.get("atr", 0) or 0

                if sig_dir_fib == "long":
                    # For longs: key fib levels going up (0.618, 0.786)
                    # measured from the recent swing low as 0% to swing high as 100%
                    fib_618 = fib_data["levels"][0.618]
                    fib_786 = fib_data["levels"][0.786]
                    # If 61.8% fib level is between entry and current T1, snap T1 to fib
                    if entry_fib < fib_618 < t1_current and atr_fib > 0:
                        if abs(fib_618 - t1_current) < atr_fib * 1.0:
                            best_signal["t1"] = fib_618
                            best_signal.setdefault("reasons", []).append(
                                f"T1 aligned to Fib 61.8% level at {price_fmt(pair_label, fib_618)} (golden ratio)"
                            )
                            print(f"[FIB] {pair_label}: T1 snapped to 61.8% fib {price_fmt(pair_label, fib_618)}")
                else:  # short
                    # For shorts: key fib levels going down (0.382, 0.236)
                    fib_382 = fib_data["levels"][0.382]
                    fib_236 = fib_data["levels"][0.236]
                    if entry_fib > fib_382 > t1_current and atr_fib > 0:
                        if abs(fib_382 - t1_current) < atr_fib * 1.0:
                            best_signal["t1"] = fib_382
                            best_signal.setdefault("reasons", []).append(
                                f"T1 aligned to Fib 38.2% level at {price_fmt(pair_label, fib_382)} (key retracement)"
                            )
                            print(f"[FIB] {pair_label}: T1 snapped to 38.2% fib {price_fmt(pair_label, fib_382)}")
        except Exception as e:
            print(f"[WARN] Fibonacci TP refinement failed for {pair_label}: {e}")

        #  4H volume trend  accumulation/distribution proxy 
        # If the last 3 4H candles show rising volume in the signal direction
        # (up-candles with rising volume for LONG, down-candles for SHORT), it indicates
        # smart money accumulation/distribution  a strong structural conviction signal
        try:
            candles_4h_vol = await fetch_candles(pair, timeframe="4h")
            if candles_4h_vol and len(candles_4h_vol) >= 5:
                recent_4h = candles_4h_vol[-4:]  # last 4 candles
                sig_dir_check = best_signal["direction"]
                # Count candles in signal direction with non-zero volume
                directional = []
                for c in recent_4h:
                    is_bullish_candle = c["close"] > c["open"]
                    vol = c.get("volume") or 0
                    if sig_dir_check == "long" and is_bullish_candle and vol > 0:
                        directional.append(vol)
                    elif sig_dir_check == "short" and not is_bullish_candle and vol > 0:
                        directional.append(vol)

                if len(directional) >= 3:
                    # Check if volume is trending up across those candles
                    vol_trending_up = all(directional[i] <= directional[i+1] for i in range(len(directional)-1))
                    if vol_trending_up:
                        best_signal["score"] = best_signal.get("score", 0) + 1
                        dir_label = "bullish" if sig_dir_check == "long" else "bearish"
                        best_signal.setdefault("reasons", []).append(
                            f"4H volume trend: rising {dir_label} volume (accumulation/distribution signal)"
                        )
                        print(f"[4H-VOL] {pair_label}: 4H volume accumulation +1")
        except Exception as e:
            print(f"[WARN] 4H volume trend check failed for {pair_label}: {e}")

        #  HTF candle bias  attach to signal for embed display 
        try:
            candles_4h_bias = await fetch_candles(pair, timeframe="4h")
            if candles_4h_bias and len(candles_4h_bias) >= 10:
                bias = calc_htf_candle_bias(candles_4h_bias, lookback=10)
                if bias:
                    best_signal["htf_candle_bias"] = bias
                    # Score bonus/penalty based on 4H candle bias vs signal direction
                    sig_dir_bias = best_signal.get("direction", "")
                    if sig_dir_bias == "long" and bias["bull_count"] >= 7:
                        best_signal["score"] = best_signal.get("score", 0) + 1
                        best_signal.setdefault("reasons", []).append(
                            f"4H candle bias: {bias['bull_count']}/10 bull candles  strong HTF conviction"
                        )
                        print(f"[BIAS] {pair_label}: 4H candle bias bullish {bias['bull_count']}/10 +1")
                    elif sig_dir_bias == "short" and bias["bear_count"] >= 7:
                        best_signal["score"] = best_signal.get("score", 0) + 1
                        best_signal.setdefault("reasons", []).append(
                            f"4H candle bias: {bias['bear_count']}/10 bear candles  strong HTF conviction"
                        )
                        print(f"[BIAS] {pair_label}: 4H candle bias bearish {bias['bear_count']}/10 +1")
        except Exception as e:
            print(f"[WARN] HTF candle bias failed for {pair_label}: {e}")

        #  4H RSI divergence bonus 
        # If 4H timeframe also shows RSI divergence in the signal direction, it's a
        # very strong confirmation  add up to +2 to the score
        try:
            candles_4h_div = await fetch_candles(pair, timeframe="4h")
            if candles_4h_div and len(candles_4h_div) >= 30:
                rsi_div_4h = detect_rsi_divergence(candles_4h_div, best_signal["direction"], lookback=8)
                if rsi_div_4h > 0:
                    best_signal["score"] = best_signal.get("score", 0) + rsi_div_4h
                    label_4h = "strong" if rsi_div_4h == 2 else "weak"
                    div_dir = "bullish" if best_signal["direction"] == "long" else "bearish"
                    best_signal.setdefault("reasons", []).append(
                        f"4H RSI divergence ({div_dir}, {label_4h})  multi-TF momentum shift"
                    )
                    print(f"[4H-DIV] {pair_label}: 4H RSI divergence +{rsi_div_4h} (score now {best_signal['score']})")
        except Exception as e:
            print(f"[WARN] 4H RSI divergence check failed for {pair_label}: {e}")

        #  v9.0 Feature 1: Multi-Timeframe Consensus 
        try:
            mtf = await calc_mtf_consensus(pair, best_signal["direction"])
            best_signal["mtf_consensus"] = mtf
            if mtf["agreeing"] == 3:
                best_signal["score"] = best_signal.get("score", 0) + 3
                best_signal.setdefault("reasons", []).append(
                    f" 3/3 MTF perfect confluence  all timeframes aligned (5m, 15m, 1H)"
                )
                print(f"[MTF] {pair_label}: 3/3 TF consensus +3 (score now {best_signal['score']})")
            elif mtf["agreeing"] == 2:
                best_signal["score"] = best_signal.get("score", 0) + 2
                best_signal.setdefault("reasons", []).append(
                    f" 2/3 MTF consensus  multi-timeframe alignment confirmed ({', '.join(mtf['tfs_scored'])})"
                )
                print(f"[MTF] {pair_label}: 2/3 TF consensus +2 (score now {best_signal['score']})")
        except Exception as e:
            print(f"[WARN] MTF consensus check failed for {pair_label}: {e}")

        #  v9.4 Feature 2: Volatility regime scoring adjustment 
        try:
            candles_1h_vol = await fetch_candles(pair, timeframe="1h")
            if candles_1h_vol and len(candles_1h_vol) >= 22:
                _vol_regime = detect_volatility_regime(candles_1h_vol, lookback=20)
                best_signal["vol_regime"] = _vol_regime
                _sig_dir_vol = best_signal.get("direction", "")
                _reasons_vol = best_signal.get("reasons", [])
                _has_squeeze = any("squeeze" in r.lower() or "bb/kc" in r.lower() for r in _reasons_vol)
                if _vol_regime == "Low" and not _has_squeeze:
                    best_signal["score"] = max(0, best_signal.get("score", 0) - 1)
                    best_signal.setdefault("reasons", []).append(
                        " Low vol regime  muted market, non-squeeze signals less reliable (-1)"
                    )
                    print(f"[VOL] {pair_label}: Low volatility regime  -1 score")
                elif _vol_regime == "High" and _sig_dir_vol == "long":
                    best_signal["score"] = max(0, best_signal.get("score", 0) - 1)
                    best_signal.setdefault("reasons", []).append(
                        " High vol regime  chaotic price action, long direction harder to predict (-1)"
                    )
                    print(f"[VOL] {pair_label}: High volatility regime + LONG  -1 score")
                else:
                    print(f"[VOL] {pair_label}: Volatility regime = {_vol_regime}")
        except Exception as _ve:
            print(f"[WARN] Volatility regime check failed for {pair_label}: {_ve}")

        # v8.0: determine session for this trade open (UTC-based windows)
        _open_hour = datetime.now(timezone.utc).hour
        if 0 <= _open_hour < 8:
            _trade_session = "Asia"
        elif 8 <= _open_hour < 16:
            _trade_session = "London"
        elif 13 <= _open_hour < 21:
            # New York overlaps with London 13-16  tag as New York when NY window is open
            _trade_session = "New York"
        else:
            _trade_session = "Off-Hours"
        # Refine: London/NY overlap (13:0016:00 UTC)  tag as "London/NY"
        if 13 <= _open_hour < 16:
            _trade_session = "London/NY"

        # v9.2 Feature 2: Pattern streak bonus  check if a pattern in the current signal
        # has fired in the last 3 consecutive signals for this pair. If so, +1 and  reason.
        try:
            _streak_reasons, _streak_score = apply_pattern_streak_bonus(
                pair_label, best_signal.get("reasons", []), best_signal["score"]
            )
            if _streak_score > best_signal["score"]:
                best_signal["reasons"] = _streak_reasons
                best_signal["score"] = _streak_score
                print(f"[STREAK] {pair_label}: pattern streak bonus +1 (score now {best_signal['score']})")
        except Exception as _se:
            print(f"[WARN] Pattern streak check failed for {pair_label}: {_se}")

        # Register trade
        # v9.1 Feature 3: Collect candle patterns that fired at entry for trade journal
        _entry_candle_patterns: list[str] = []
        try:
            if candles_5m and len(candles_5m) >= 5:
                _ec = candles_5m[-1]
                _ep = candles_5m[-2]
                _ec_body = abs(_ec["close"] - _ec["open"])
                _ec_range = _ec["high"] - _ec["low"]
                # Engulfing
                if _ec["close"] > _ep["open"] and _ec["open"] < _ep["close"] and best_signal["direction"] == "long":
                    _entry_candle_patterns.append("Bullish Engulfing")
                elif _ec["close"] < _ep["open"] and _ec["open"] > _ep["close"] and best_signal["direction"] == "short":
                    _entry_candle_patterns.append("Bearish Engulfing")
                # Hammer / Pin bar
                if _ec_range > 0 and _ec_body / _ec_range < 0.3:
                    _lower_wick = min(_ec["open"], _ec["close"]) - _ec["low"]
                    _upper_wick = _ec["high"] - max(_ec["open"], _ec["close"])
                    if _lower_wick > _ec_body * 2 and best_signal["direction"] == "long":
                        _entry_candle_patterns.append("Hammer/Pin Bar")
                    elif _upper_wick > _ec_body * 2 and best_signal["direction"] == "short":
                        _entry_candle_patterns.append("Shooting Star/Pin Bar")
                # Inside bar
                if _ec["high"] < _ep["high"] and _ec["low"] > _ep["low"]:
                    _entry_candle_patterns.append("Inside Bar")
        except Exception:
            pass

        active_trades[pair_label] = {
            "direction": best_signal["direction"].upper(),
            "entry": best_signal["entry"],
            "sl": best_signal["sl"],
            "t1": best_signal["t1"],
            "t2": best_signal["t2"],
            "t1_hit": False,
            "entry_hit": False,        # v8.7: True once price reaches entry
            "invalidated": False,      # v8.7: True once invalidation alert sent
            "mgmt_nudge_sent": False,  # v8.7: True once 4h management nudge sent
            "signal_type": signal_type,
            "score": best_signal["score"],
            "reasons": best_signal.get("reasons", []),
            "atr_at_entry": best_signal.get("atr"),  # for trailing stop
            "opened_at": datetime.now(timezone.utc).isoformat(),
            "session": _trade_session,  # v8.0: session when trade opened
            # v9.1 Feature 3: Trade journal fields
            "market_regime": best_signal.get("market_regime", "Unknown"),
            "mtf_consensus": best_signal.get("mtf_consensus"),
            "candle_patterns": _entry_candle_patterns,
            "sl_atr_mult": best_signal.get("sl_atr_mult", 1.0),
        }
        last_signal_time[pair_label] = time.time()
        last_signal_dir[pair_label] = best_signal["direction"].upper()
        _daily_opened += 1

        # Append to in-memory signal log
        _confidence_label, _ = confidence_tier(best_signal["score"])
        SIGNAL_LOG.append({
            "pair": pair_label,
            "direction": best_signal["direction"].upper(),
            "score": best_signal["score"],
            "time": datetime.now(timezone.utc).isoformat(),
            "entry": best_signal["entry"],
            "sl": best_signal["sl"],
            "t1": best_signal["t1"],
            "t2": best_signal["t2"],
            "confidence": _confidence_label,
            "reasons": best_signal.get("reasons", []),
        })

        # v8.8 Feature 6: score history per pair
        if pair_label not in SCORE_HISTORY:
            SCORE_HISTORY[pair_label] = deque(maxlen=10)
        SCORE_HISTORY[pair_label].append(best_signal["score"])

        # Post embed (only if alerts are enabled)
        if ALERTS_ENABLED:
            if signal_type == "premium":
                embed = make_premium_embed(pair_label, best_signal, htf_trend, counter_trend_flag)
            else:
                embed = make_standard_embed(pair_label, best_signal, htf_trend, counter_trend_flag)
            await channel.send(embed=embed)
        else:
            print(f"[MUTED] {pair_label} signal logged but alerts muted (ALERTS_ENABLED=False)")
        print(f"[SIGNAL] {pair_label} {best_signal['direction'].upper()} [{signal_type}] score={best_signal['score']}")

        # Log signal + store ID in active trade for outcome tracking
        sig_id = log_signal(pair_label, best_signal, signal_type, htf_trend)
        active_trades[pair_label]["sig_id"] = sig_id

        # v9.4 Feature 4: Multi-pair wave detection
        _now_ts = time.time()
        _recent_signal_ts[pair_label] = _now_ts
        _recent_signal_info[pair_label] = {
            "direction": best_signal["direction"].upper(),
            "score": best_signal["score"],
        }
        # Check for near-simultaneous signals (other pairs within WAVE_WINDOW seconds)
        _wave_pairs = [
            lbl for lbl, ts in _recent_signal_ts.items()
            if lbl != pair_label and (_now_ts - ts) <= WAVE_WINDOW
        ]
        if _wave_pairs and ALERTS_ENABLED:
            try:
                _wave_embed = discord.Embed(
                    title=" Multi-Pair Wave Alert",
                    description=(
                        "Two or more pairs just signalled within 30 seconds of each other.\n"
                        "Correlated move possible  consider reducing size per trade."
                    ),
                    color=0xFF6347,
                    timestamp=datetime.now(timezone.utc)
                )
                _wave_lines = []
                # Current pair
                _dir_now = best_signal["direction"].upper()
                _score_now = best_signal["score"]
                _wave_lines.append(f"**{pair_label}**  {_dir_now} (score {_score_now})")
                # Other wave pairs
                for _wlbl in _wave_pairs:
                    _wi = _recent_signal_info.get(_wlbl, {})
                    _wdir = _wi.get("direction", "?")
                    _wsc  = _wi.get("score", "?")
                    _wave_lines.append(f"**{_wlbl}**  {_wdir} (score {_wsc})")
                # Correlated direction check
                _all_dirs = [_dir_now] + [_recent_signal_info.get(l, {}).get("direction", "?") for l in _wave_pairs]
                if len(set(_all_dirs)) == 1:
                    _wave_embed.add_field(
                        name=" Same-Direction Wave",
                        value="All signals point the same way  high correlation, market-wide move likely.",
                        inline=False
                    )
                _wave_embed.add_field(
                    name=" Signals",
                    value="\n".join(_wave_lines),
                    inline=False
                )
                _wave_embed.add_field(
                    name=" Sizing Advice",
                    value="Reduce position size per trade by 3050% when correlated signals fire together.",
                    inline=False
                )
                _wave_embed.set_footer(text=f"Chartwise v10.0  Wave window: {int(WAVE_WINDOW)}s  !copy for size calculator")
                await channel.send(embed=_wave_embed)
                print(f"[WAVE] Multi-pair wave alert sent: {pair_label} + {_wave_pairs}")
            except Exception as _we:
                print(f"[WARN] Wave alert error: {_we}")


# 
# SCAN LOOP
# 

async def scan_loop():
    """Main scan loop  runs with adaptive interval (v8.5 Feature 4).
    BB width > 2% on 15m  60s; BB squeeze < 0.5%  180s; normal  SCAN_INTERVAL.
    """
    global _circuit_tripped_at, _consecutive_losses, current_scan_interval
    await bot.wait_until_ready()

    while not bot.is_closed():
        try:
            channel = bot.get_channel(CHANNEL_ID)
            if not channel:
                print("[ERROR] Channel not found")
                await asyncio.sleep(current_scan_interval)
                continue

            # Circuit breaker check
            if _circuit_tripped_at > 0:
                elapsed = time.time() - _circuit_tripped_at
                if elapsed < CIRCUIT_BREAKER_COOLDOWN:
                    remaining = int((CIRCUIT_BREAKER_COOLDOWN - elapsed) / 60)
                    # v9.0 Feature 6: Auto-recovery  if most recent closed trade is a WIN, lift circuit breaker early
                    _auto_recovered = False
                    if TRADE_HISTORY:
                        _last_trade = TRADE_HISTORY[-1]
                        if _last_trade.get("outcome") == "WIN":
                            _auto_recovered = True
                            _circuit_tripped_at = 0.0
                            _consecutive_losses = 0
                            print(f"[CIRCUIT] Auto-lifted  most recent trade was a WIN, resuming scans early")
                            try:
                                _recover_embed = discord.Embed(
                                    title=" Circuit Breaker Auto-Lifted",
                                    description=(
                                        f"The circuit breaker was automatically lifted because the most recent "
                                        f"closed trade was a **WIN**.\n"
                                        f"Market conditions appear to have improved  scanning is resuming early.\n"
                                        f"Remaining cooldown waived: **{remaining}m**."
                                    ),
                                    color=0x00E676,
                                    timestamp=datetime.now(timezone.utc)
                                )
                                _recover_embed.add_field(
                                    name="Last Trade",
                                    value=f" WIN  {_last_trade.get('pair', '?')} {_last_trade.get('direction', '?').upper()}",
                                    inline=True
                                )
                                _recover_embed.add_field(name="Cooldown Saved", value=f"{remaining}m", inline=True)
                                _recover_embed.set_footer(text="Chartwise v10.0  Circuit breaker auto-recovery on confirmed WIN")
                                _cb_channel = bot.get_channel(CHANNEL_ID)
                                if _cb_channel:
                                    await _cb_channel.send(embed=_recover_embed)
                            except Exception as _e:
                                print(f"[WARN] Circuit auto-lift embed failed: {_e}")
                    if not _auto_recovered:
                        print(f"[CIRCUIT] Scanning paused  {remaining}m remaining after {CIRCUIT_BREAKER_LOSSES} consecutive losses")
                        # v8.1: log any would-be signals as circuit-breaker filtered
                        for _cb_pair in PAIRS:
                            FILTERED_LOG.append({
                                "pair":            _cb_pair["label"],
                                "direction":       "?",
                                "score":           0,
                                "reason_filtered": f"circuit_breaker ({remaining}m remaining)",
                                "time":            datetime.now(timezone.utc).isoformat(),
                            })
                        write_state_file()
                        await asyncio.sleep(current_scan_interval)
                        continue
                else:
                    # Reset circuit
                    print("[CIRCUIT] Circuit breaker reset  resuming scans")
                    _circuit_tripped_at = 0.0
                    _consecutive_losses = 0

            # Update active trades first (exits)
            await update_active_trades(channel)

            # v9.1 Feature 1: Watchlist price-touch check
            try:
                for _wl_pair in list(WATCHLIST.keys()):
                    _wl_items = WATCHLIST.get(_wl_pair, [])
                    if not _wl_items:
                        continue
                    # Get current price for this pair
                    _wl_p_obj = next((p for p in PAIRS if p["label"] == _wl_pair), None)
                    if _wl_p_obj is None:
                        continue
                    _wl_candles = await fetch_candles(_wl_p_obj, timeframe="5m")
                    if not _wl_candles:
                        continue
                    _wl_price = _wl_candles[-1]["close"]
                    _to_remove_wl = []
                    for _wi, _witem in enumerate(_wl_items):
                        _wl_entry = _witem.get("entry", 0)
                        _wl_atr = _witem.get("atr", 0) or (_wl_entry * 0.005)
                        _touch_threshold = _wl_atr * 0.3  # within 30% of ATR = "touched"
                        if abs(_wl_price - _wl_entry) <= _touch_threshold:
                            # Price touched watchlist entry  send alert
                            _wl_dir = _witem.get("direction", "?").upper()
                            _wl_embed = discord.Embed(
                                title=f" Watchlist Alert  {_wl_pair}",
                                description=(
                                    f"A near-miss signal's entry zone has been reached!\n"
                                    f"This was a **{_wl_dir}** setup that scored **{_witem.get('score', '?')}** "
                                    f"(needed {MIN_SCORE})  now price is at the zone."
                                ),
                                color=0xFFD700,
                                timestamp=datetime.now(timezone.utc)
                            )
                            _wl_embed.add_field(name="Direction", value=_wl_dir, inline=True)
                            _wl_embed.add_field(name="Score at Detection", value=str(_witem.get("score", "?")), inline=True)
                            _wl_embed.add_field(name="Entry Zone", value=price_fmt(_wl_pair, _wl_entry), inline=True)
                            _wl_embed.add_field(name="Current Price", value=price_fmt(_wl_pair, _wl_price), inline=True)
                            _wl_embed.add_field(name="SL", value=price_fmt(_wl_pair, _witem.get("sl", 0)), inline=True)
                            _wl_embed.add_field(name="T1", value=price_fmt(_wl_pair, _witem.get("t1", 0)), inline=True)
                            _wl_reasons = _witem.get("reasons", [])
                            if _wl_reasons:
                                _wl_embed.add_field(
                                    name="Original Confluence",
                                    value="\n".join(f" {r}" for r in _wl_reasons[:5]) or "",
                                    inline=False
                                )
                            # Show when it was added
                            _wl_time_str = _witem.get("time", "")
                            if _wl_time_str:
                                try:
                                    _wl_dt = datetime.fromisoformat(_wl_time_str)
                                    if _wl_dt.tzinfo is None:
                                        _wl_dt = _wl_dt.replace(tzinfo=timezone.utc)
                                    _wl_age_m = int((datetime.now(timezone.utc) - _wl_dt).total_seconds() / 60)
                                    _wl_embed.add_field(name="Added to Watchlist", value=f"{_wl_age_m}m ago", inline=True)
                                except Exception:
                                    pass
                            _wl_embed.set_footer(text=f"Chartwise v10.0  Watchlist alert  not a confirmed signal  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
                            await channel.send(embed=_wl_embed)
                            _to_remove_wl.append(_wi)
                            print(f"[WATCHLIST] {_wl_pair}: entry touched at {_wl_price:.4f}  alert sent")
                    # Remove triggered items (reverse to preserve indices)
                    for _ri in reversed(_to_remove_wl):
                        _wl_items.pop(_ri)
                    if not _wl_items:
                        WATCHLIST.pop(_wl_pair, None)
                    # Also expire watchlist items older than 12 hours
                    _now_iso = datetime.now(timezone.utc)
                    WATCHLIST[_wl_pair] = [
                        _w for _w in WATCHLIST.get(_wl_pair, [])
                        if _w.get("time") and
                        (_now_iso - datetime.fromisoformat(_w["time"]).replace(tzinfo=timezone.utc)
                         if datetime.fromisoformat(_w["time"]).tzinfo is None
                         else _now_iso - datetime.fromisoformat(_w["time"])
                        ).total_seconds() < 43200  # 12 hours
                    ] if _wl_pair in WATCHLIST else []
                    if not WATCHLIST.get(_wl_pair):
                        WATCHLIST.pop(_wl_pair, None)
            except Exception as _wl_err:
                print(f"[WATCHLIST] Error in price-touch check: {_wl_err}")

            #  v9.4 Feature 2: Price alert checking 
            try:
                if PRICE_ALERTS:
                    _triggered_indices = []
                    for _ai, _alert in enumerate(PRICE_ALERTS):
                        _al_pair_obj = next((p for p in DYNAMIC_PAIRS if p["label"] == _alert["pair"]), None)
                        if _al_pair_obj is None:
                            continue
                        _al_candles = await fetch_candles(_al_pair_obj, timeframe="5m")
                        if not _al_candles:
                            continue
                        _al_price = _al_candles[-1]["close"]
                        _triggered = False
                        if _alert["direction"] == "above" and _al_price >= _alert["price"]:
                            _triggered = True
                        elif _alert["direction"] == "below" and _al_price <= _alert["price"]:
                            _triggered = True
                        if _triggered:
                            _al_dir_word = "above" if _alert["direction"] == "above" else "below"
                            _al_embed = discord.Embed(
                                title=f" Price Alert: {_alert['pair']}",
                                description=(
                                    f"**{_alert['pair']}** crossed **{_al_dir_word}** "
                                    f"**{price_fmt(_alert['pair'], _alert['price'])}**!\n"
                                    f"Current price: **{price_fmt(_alert['pair'], _al_price)}**"
                                ),
                                color=0xFFD700,
                                timestamp=datetime.now(timezone.utc),
                            )
                            _al_set_str = _alert.get("set_time", "")
                            if _al_set_str:
                                try:
                                    _al_set_dt = datetime.fromisoformat(_al_set_str)
                                    if _al_set_dt.tzinfo is None:
                                        _al_set_dt = _al_set_dt.replace(tzinfo=timezone.utc)
                                    _al_age_m = int((datetime.now(timezone.utc) - _al_set_dt).total_seconds() / 60)
                                    _al_embed.add_field(name="Alert Age", value=f"{_al_age_m}m", inline=True)
                                except Exception:
                                    pass
                            _al_embed.add_field(name="Alert Price", value=price_fmt(_alert["pair"], _alert["price"]), inline=True)
                            _al_embed.add_field(name="Direction", value=_al_dir_word.title(), inline=True)
                            _al_embed.set_footer(text=f"Chartwise v10.0  Price alert triggered  Use !alert to set new alerts")
                            try:
                                await channel.send(embed=_al_embed)
                            except Exception as _al_send_err:
                                print(f"[ALERT] Could not send price alert embed: {_al_send_err}")
                            _triggered_indices.append(_ai)
                            print(f"[ALERT] {_alert['pair']} {_al_dir_word} {_alert['price']} triggered at {_al_price:.4f}")
                    for _ri in reversed(_triggered_indices):
                        PRICE_ALERTS.pop(_ri)
            except Exception as _al_err:
                print(f"[ALERT] Price alert check error: {_al_err}")

            # Manual pause override
            if _scan_manually_paused:
                if _scan_paused_until > 0 and time.time() > _scan_paused_until:
                    # Timed pause expired  auto-resume
                    globals()["_scan_manually_paused"] = False
                    globals()["_scan_paused_until"] = 0.0
                    print("[PAUSE] Timed pause expired  scan auto-resumed")
                else:
                    reason = f"until {datetime.fromtimestamp(_scan_paused_until, tz=timezone.utc).strftime('%H:%M UTC')}" if _scan_paused_until > 0 else "until !resume"
                    print(f"[PAUSE] Scan manually paused ({reason})")
                    write_state_file()
                    await asyncio.sleep(current_scan_interval)
                    continue

            # News dead zone  skip new signal scanning around macro release windows
            if is_news_dead_zone():
                print(f"[DEADZONE] Skipping signal scan  news dead zone active ({datetime.now(timezone.utc).strftime('%H:%M')} UTC)")
                write_state_file()
                await asyncio.sleep(current_scan_interval)
                continue

            # v8.5 Feature 4: update current_scan_interval based on BB width (15m first pair)
            try:
                _bb_pair = DYNAMIC_PAIRS[0] if DYNAMIC_PAIRS else PAIRS[0]
                _bb_data = await fetch_candles(_bb_pair, timeframe="15m")
                if _bb_data and len(_bb_data) >= 20:
                    _bb_result = calc_bb_width_trend(_bb_data)
                    if _bb_result:
                        _bb_width = _bb_result.get("width", 1.0) * 100  # convert to %
                        if _bb_width > 2.0:
                            current_scan_interval = 60   # expanding  scan faster
                        elif _bb_width < 0.5 or _bb_result.get("squeeze"):
                            current_scan_interval = 180  # squeeze  scan slower
                        else:
                            current_scan_interval = SCAN_INTERVAL
                        print(f"[ADAPTIVE] BB width {_bb_width:.2f}%  scan interval {current_scan_interval}s")
            except Exception as _bb_err:
                print(f"[ADAPTIVE] BB width check failed: {_bb_err}")

            # Scan all pairs in parallel
            await asyncio.gather(*[scan_pair(pair, channel) for pair in DYNAMIC_PAIRS])

            # Write state snapshot for API server
            write_state_file()

        except Exception as _loop_err:
            print(f"[SCAN_LOOP] Unhandled error: {_loop_err}")

        await asyncio.sleep(current_scan_interval)


# 
# DAILY SUMMARY TASK
# 

import datetime as _dt_module
@tasks.loop(time=_dt_module.time(hour=0, minute=0, second=0))
async def daily_summary():
    """Post a daily P&L summary at 00:00 UTC and reset daily counters."""
    global _daily_opened, _daily_closed, _daily_pnl_pct, _daily_wins, _daily_losses

    if _daily_closed == 0 and _daily_opened == 0:
        # Nothing happened today  skip posting
        _daily_opened = 0
        _daily_closed = 0
        _daily_pnl_pct = 0.0
        _daily_wins = 0
        _daily_losses = 0
        return

    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        _daily_opened = 0
        _daily_closed = 0
        _daily_pnl_pct = 0.0
        _daily_wins = 0
        _daily_losses = 0
        return

    day_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    embed = discord.Embed(
        title=f" Daily Summary  {day_str}",
        description="Automated end-of-day performance report (UTC midnight).",
        color=0x7C4DFF,
        timestamp=datetime.now(timezone.utc),
    )
    embed.add_field(name="Trades Opened", value=str(_daily_opened), inline=True)
    embed.add_field(name="Trades Closed", value=str(_daily_closed), inline=True)
    embed.add_field(name="", value="", inline=True)

    if _daily_closed > 0:
        total = _daily_wins + _daily_losses
        wr = (_daily_wins / total * 100) if total > 0 else 0.0
        pnl_sign = "+" if _daily_pnl_pct >= 0 else ""
        embed.add_field(name="Day Wins", value=str(_daily_wins), inline=True)
        embed.add_field(name="Day Losses", value=str(_daily_losses), inline=True)
        embed.add_field(name="Win Rate", value=f"{wr:.0f}%", inline=True)
        embed.add_field(name="Net PnL (sum %)", value=f"{pnl_sign}{_daily_pnl_pct:.2f}%", inline=False)
    else:
        embed.add_field(name="Closed Trades", value="No trades closed today", inline=False)

    embed.set_footer(text=f"Chartwise v10.0  Counters reset for new day")
    try:
        await channel.send(embed=embed)
    except Exception as e:
        print(f"[WARN] daily_summary: could not send embed: {e}")

    # Reset daily counters
    _daily_opened = 0
    _daily_closed = 0
    _daily_pnl_pct = 0.0
    _daily_wins = 0
    _daily_losses = 0

    # v9.7 Feature 5: Record NWOG/NDOG opening prices for each pair
    now_utc = datetime.now(timezone.utc)
    is_monday = now_utc.weekday() == 0  # Monday = 0
    asyncio.ensure_future(_record_opening_prices(now_utc, is_monday))


async def _record_opening_prices(now_utc: datetime, is_monday: bool):
    """
    v9.7 Feature 5: Fetch current price for each pair and record as the
    daily open (every day) and weekly open (Mondays only).
    Stored in DAILY_OPENS and WEEKLY_OPENS dicts.
    """
    time_str = now_utc.strftime("%Y-%m-%d %H:%M UTC")
    for pair in DYNAMIC_PAIRS:
        label = pair["label"]
        try:
            candles = await fetch_candles(pair, "15")
            if not candles:
                continue
            open_price = candles[-1]["open"]
            # Initialize deques if needed
            if label not in DAILY_OPENS:
                DAILY_OPENS[label] = deque(maxlen=7)
            if label not in WEEKLY_OPENS:
                WEEKLY_OPENS[label] = deque(maxlen=4)
            entry = {"price": open_price, "time_utc": time_str, "type": "daily"}
            DAILY_OPENS[label].append(entry)
            if is_monday:
                weekly_entry = {"price": open_price, "time_utc": time_str, "type": "weekly"}
                WEEKLY_OPENS[label].append(weekly_entry)
            print(f"[OPENS] {label} daily open recorded: {open_price:.4f} {time_str}")
        except Exception as e:
            print(f"[WARN] _record_opening_prices {label}: {e}")


@daily_summary.before_loop
async def before_daily_summary():
    """Wait until bot is ready before starting the daily summary loop."""
    await bot.wait_until_ready()


# 
# BOT EVENTS & COMMANDS
# 

@bot.event
async def on_ready():
    global pair_locks
    # Initialize per-pair locks (safe to call here in case not initialized at module level)
    for pair in PAIRS:
        if pair["label"] not in pair_locks:
            pair_locks[pair["label"]] = asyncio.Lock()

    print(f"[READY] Chartwise v10.0 online as {bot.user}  outcome-tracker weight-rebalancer learning-sync")
    print(f"[READY] Monitoring {len(PAIRS)} pairs: {', '.join(p['label'] for p in PAIRS)}")
    asyncio.ensure_future(scan_loop())
    daily_summary.start()
    outcome_tracker.start()


@bot.command(name="status")
async def cmd_status(ctx):
    """Show comprehensive bot health dashboard (v9.4)."""
    embed = make_status_embed()
    await ctx.send(embed=embed)


@bot.command(name="correlation")
async def cmd_correlation(ctx):
    """v9.4  Compute rolling Pearson correlation BTC/SOL and BTC/XRP using last 20 4H candle % changes."""
    await ctx.send(" Computing correlations...")
    try:
        btc_pair = next((p for p in PAIRS if "BTC" in p["label"]), None)
        sol_pair = next((p for p in PAIRS if "SOL" in p["label"]), None)
        xrp_pair = next((p for p in PAIRS if "XRP" in p["label"]), None)

        if not (btc_pair and sol_pair and xrp_pair):
            await ctx.send(" Requires BTC, SOL, and XRP pairs to be active.")
            return

        btc_candles = await fetch_candles(btc_pair, timeframe="4h")
        sol_candles = await fetch_candles(sol_pair, timeframe="4h")
        xrp_candles = await fetch_candles(xrp_pair, timeframe="4h")

        if not (btc_candles and sol_candles and xrp_candles):
            await ctx.send(" Could not fetch 4H candles for all pairs.")
            return

        # Take last 20 candles and compute % change per candle
        _n = 20
        def pct_changes(candles):
            recent = candles[-(_n + 1):] if len(candles) >= _n + 1 else candles
            changes = []
            for i in range(1, len(recent)):
                prev = recent[i-1]["close"]
                curr = recent[i]["close"]
                if prev > 0:
                    changes.append((curr - prev) / prev * 100)
            return changes[-_n:]

        btc_chgs = pct_changes(btc_candles)
        sol_chgs = pct_changes(sol_candles)
        xrp_chgs = pct_changes(xrp_candles)

        min_len = min(len(btc_chgs), len(sol_chgs), len(xrp_chgs))
        if min_len < 5:
            await ctx.send(" Not enough data for correlation (need 5 candles).")
            return

        btc_t = btc_chgs[-min_len:]
        sol_t = sol_chgs[-min_len:]
        xrp_t = xrp_chgs[-min_len:]

        corr_sol = pearson_correlation(btc_t, sol_t)
        corr_xrp = pearson_correlation(btc_t, xrp_t)

        embed = discord.Embed(
            title=" BTC Correlation Dashboard",
            description=f"Rolling Pearson correlation using last **{min_len}** 4H candle % changes.",
            color=0x00CED1,
            timestamp=datetime.now(timezone.utc),
        )

        if corr_sol is not None:
            _lbl_sol = corr_label(corr_sol)
            _emoji_sol = "" if abs(corr_sol) >= 0.8 else ("" if abs(corr_sol) >= 0.6 else "")
            embed.add_field(
                name=f"BTC / SOL  {_emoji_sol} {_lbl_sol}",
                value=f"**r = {corr_sol:+.4f}**",
                inline=True
            )
        else:
            embed.add_field(name="BTC / SOL", value="Insufficient data", inline=True)

        if corr_xrp is not None:
            _lbl_xrp = corr_label(corr_xrp)
            _emoji_xrp = "" if abs(corr_xrp) >= 0.8 else ("" if abs(corr_xrp) >= 0.6 else "")
            embed.add_field(
                name=f"BTC / XRP  {_emoji_xrp} {_lbl_xrp}",
                value=f"**r = {corr_xrp:+.4f}**",
                inline=True
            )
        else:
            embed.add_field(name="BTC / XRP", value="Insufficient data", inline=True)

        embed.add_field(name="", value="", inline=True)

        embed.add_field(
            name=" Interpretation",
            value=(
                "**r > 0.8**  High correlation: pairs move together strongly\n"
                "**r 0.60.8**  Moderate correlation: general alignment\n"
                "**r < 0.6**  Low correlation: pairs move more independently\n\n"
                " **High correlation (>0.8) means positions in the same direction = concentrated risk.** "
                "If BTC/SOL and BTC/XRP are both high, opening all three longs is essentially 3 BTC exposure."
            ),
            inline=False
        )

        embed.set_footer(text="Chartwise v10.0  4H rolling correlation  Not financial advice")
        await ctx.send(embed=embed)
        print(f"[CMD] !correlation  BTC/SOL r={corr_sol}, BTC/XRP r={corr_xrp}  sent to #{ctx.channel.name}")
    except Exception as _e:
        await ctx.send(f" Correlation error: {_e}")
        print(f"[CMD] !correlation error: {_e}")


#  v9.4 Feature 2: !alert command 
@bot.command(name="alert")
async def cmd_alert(ctx, *args):
    """
    v9.4  Set, list, or clear price alerts.
    Usage:
      !alert [pair] [price] [above|below]    set a new alert
      !alert list                             show all active alerts
      !alert clear                            remove all alerts
    """
    if not args:
        embed = discord.Embed(
            title=" Price Alert  Usage",
            description=(
                "`!alert BTC 97500 above`  alert when BTC crosses above $97,500\n"
                "`!alert SOL 180 below`  alert when SOL drops below $180\n"
                "`!alert list`  show all active alerts\n"
                "`!alert clear`  remove all alerts"
            ),
            color=0xFFD700,
        )
        await ctx.send(embed=embed)
        return

    # Sub-commands
    if args[0].lower() == "list":
        if not PRICE_ALERTS:
            await ctx.send(" No active price alerts. Use `!alert [pair] [price] [above|below]` to set one.")
            return
        embed = discord.Embed(
            title=f" Active Price Alerts ({len(PRICE_ALERTS)})",
            color=0xFFD700,
            timestamp=datetime.now(timezone.utc),
        )
        for _ai, _alert in enumerate(PRICE_ALERTS, 1):
            _al_age = ""
            try:
                _al_set_dt = datetime.fromisoformat(_alert.get("set_time", ""))
                if _al_set_dt.tzinfo is None:
                    _al_set_dt = _al_set_dt.replace(tzinfo=timezone.utc)
                _al_age_m = int((datetime.now(timezone.utc) - _al_set_dt).total_seconds() / 60)
                _al_age = f" (set {_al_age_m}m ago)"
            except Exception:
                pass
            embed.add_field(
                name=f"Alert #{_ai}: {_alert['pair']}",
                value=f"**{_alert['direction'].upper()}** {price_fmt(_alert['pair'], _alert['price'])}{_al_age}",
                inline=False
            )
        embed.set_footer(text="Chartwise v10.0  !alert clear to remove all  !alert [pair] [price] [above|below] to add")
        await ctx.send(embed=embed)
        return

    if args[0].lower() == "clear":
        _count = len(PRICE_ALERTS)
        PRICE_ALERTS.clear()
        await ctx.send(f" Cleared **{_count}** price alert{'s' if _count != 1 else ''}.")
        return

    # Set a new alert: !alert [pair] [price] [above|below]
    if len(args) < 3:
        await ctx.send(" Usage: `!alert [pair] [price] [above|below]`  e.g. `!alert BTC 97500 above`")
        return

    _pair_input = args[0].upper()
    # Normalize pair label
    if "/" not in _pair_input:
        _pair_input = _pair_input + "/USD"

    _pair_obj = next((p for p in DYNAMIC_PAIRS if p["label"].upper() == _pair_input.upper()), None)
    if _pair_obj is None:
        # Try partial match
        _pair_obj = next((p for p in DYNAMIC_PAIRS if _pair_input.split("/")[0] in p["label"]), None)
    if _pair_obj is None:
        await ctx.send(f" Unknown pair: `{_pair_input}`. Active pairs: {', '.join(p['label'] for p in DYNAMIC_PAIRS)}")
        return

    try:
        _alert_price = float(args[1].replace(",", ""))
    except ValueError:
        await ctx.send(f" Invalid price: `{args[1]}`. Must be a number.")
        return

    _direction = args[2].lower()
    if _direction not in ("above", "below"):
        await ctx.send(" Direction must be `above` or `below`.")
        return

    # Check for duplicates
    for _ex in PRICE_ALERTS:
        if _ex["pair"] == _pair_obj["label"] and _ex["price"] == _alert_price and _ex["direction"] == _direction:
            await ctx.send(f" Alert already exists: **{_pair_obj['label']}** {_direction} {price_fmt(_pair_obj['label'], _alert_price)}")
            return

    PRICE_ALERTS.append({
        "pair": _pair_obj["label"],
        "price": _alert_price,
        "direction": _direction,
        "set_time": datetime.now(timezone.utc).isoformat(),
        "user_id": ctx.author.id,
    })
    _dir_emoji = "" if _direction == "above" else ""
    await ctx.send(
        f" Alert set! {_dir_emoji} **{_pair_obj['label']}** crosses **{_direction}** "
        f"**{price_fmt(_pair_obj['label'], _alert_price)}**  you'll be notified when triggered."
    )
    print(f"[CMD] !alert {_pair_obj['label']} {_alert_price} {_direction}  set by {ctx.author}")


#  v9.4 Feature 4: !close command 
# Stores pending confirmations: {pair_label: user_id}
_pending_close_confirmations: dict[str, int] = {}

@bot.command(name="close")
async def cmd_close(ctx, pair_arg: str = None, confirm_arg: str = None):
    """
    v9.4  Manually close an active trade.
    Usage:
      !close BTC              request confirmation
      !close BTC confirm      execute the close at current price
    """
    global _consecutive_losses, _circuit_tripped_at

    if not pair_arg:
        await ctx.send(" Usage: `!close [pair]`  e.g. `!close BTC` or `!close BTC/USD`")
        return

    _cl_input = pair_arg.upper()
    if "/" not in _cl_input:
        _cl_input = _cl_input + "/USD"

    # Find matching active trade
    _cl_label = next((lbl for lbl in active_trades if _cl_input in lbl.upper() or lbl.upper() in _cl_input), None)
    if _cl_label is None:
        await ctx.send(f" No active trade found for **{_cl_input}**. Use `!status` to see open positions.")
        return

    trade = active_trades[_cl_label]

    # Confirmation flow
    if confirm_arg and confirm_arg.lower() == "confirm":
        # Check that a confirmation was previously requested by this user
        if _pending_close_confirmations.get(_cl_label) != ctx.author.id:
            await ctx.send(f" Please first type `!close {pair_arg}` to initiate, then `!close {pair_arg} confirm` to execute.")
            return

        # Fetch current price
        _cl_pair_obj = next((p for p in DYNAMIC_PAIRS if p["label"] == _cl_label), None)
        _exit_price = trade["entry"]  # fallback
        if _cl_pair_obj:
            try:
                _cl_candles = await fetch_candles(_cl_pair_obj, timeframe="5m")
                if _cl_candles:
                    _exit_price = _cl_candles[-1]["close"]
            except Exception:
                pass

        # Calculate PnL
        _entry = trade["entry"]
        _sl    = trade.get("sl", _entry)
        _direction = trade.get("direction", "LONG").upper()
        _sl_dist = abs(_entry - _sl)
        if _direction == "LONG":
            _pnl_pts = _exit_price - _entry
        else:
            _pnl_pts = _entry - _exit_price
        _pnl_pct = _pnl_pts / _entry * 100
        _pnl_r   = _pnl_pts / max(_sl_dist, 1e-9)
        _outcome  = "WIN" if _pnl_pts > 0 else "LOSS"
        _outcome_emoji = "" if _outcome == "WIN" else ""

        # Log outcome
        _sig_id = trade.get("sig_id")
        if _sig_id:
            log_outcome(_sig_id, "t2" if _outcome == "WIN" else "stop", _exit_price, _entry, _sl)

        # Update session PnL
        if _outcome == "WIN":
            session_pnl["wins"] += 1
            session_pnl["pair_wins"][_cl_label] = session_pnl["pair_wins"].get(_cl_label, 0) + 1
            _consecutive_losses = 0
        else:
            session_pnl["losses"] += 1
            session_pnl["pair_losses"][_cl_label] = session_pnl["pair_losses"].get(_cl_label, 0) + 1
            _consecutive_losses += 1
            if _consecutive_losses >= CIRCUIT_BREAKER_LOSSES and _circuit_tripped_at == 0.0:
                _circuit_tripped_at = time.time()

        _pnl_sign = "+" if _pnl_pct >= 0 else ""
        session_pnl["total_pnl_pct"] += _pnl_pct

        # Append to TRADE_HISTORY
        TRADE_HISTORY.append({
            "pair": _cl_label,
            "direction": _direction,
            "entry": _entry,
            "exit_price": _exit_price,
            "sl": _sl,
            "pnl_pct": round(_pnl_pct, 3),
            "pnl_r": round(_pnl_r, 2),
            "outcome": _outcome,
            "exit_type": "manual",
            "closed_at": datetime.now(timezone.utc).isoformat(),
            "opened_at": trade.get("opened_at", ""),
        })

        # Remove from active trades
        del active_trades[_cl_label]
        _pending_close_confirmations.pop(_cl_label, None)

        # Build exit embed
        _cl_color = 0x00E676 if _outcome == "WIN" else 0xFF5252
        embed = discord.Embed(
            title=f"{_outcome_emoji} Manual Close  {_cl_label} {_direction}",
            description=f"Trade manually closed by {ctx.author.mention} at current market price.",
            color=_cl_color,
            timestamp=datetime.now(timezone.utc),
        )
        embed.add_field(name="Entry", value=price_fmt(_cl_label, _entry), inline=True)
        embed.add_field(name="Exit (manual)", value=price_fmt(_cl_label, _exit_price), inline=True)
        embed.add_field(name="Stop Loss", value=price_fmt(_cl_label, _sl), inline=True)
        embed.add_field(name="Outcome", value=f"{_outcome_emoji} **{_outcome}**", inline=True)
        embed.add_field(name="PnL %", value=f"{_pnl_sign}{_pnl_pct:.2f}%", inline=True)
        embed.add_field(name="PnL R", value=f"{_pnl_sign}{_pnl_r:.2f}R", inline=True)
        _dur = format_trade_duration(trade.get("opened_at", ""))
        embed.add_field(name="Trade Duration", value=_dur, inline=True)
        embed.set_footer(text="Chartwise v10.0  Manual close  Use !pnl for session summary")
        await ctx.send(embed=embed)
        write_state_file()
        print(f"[CMD] !close {_cl_label} confirm  {_outcome} {_pnl_pct:+.2f}% by {ctx.author}")
    else:
        # First step: ask for confirmation
        _pending_close_confirmations[_cl_label] = ctx.author.id
        _t1_status = " T1 already hit" if trade.get("t1_hit") else " T1 not yet hit"
        _dur = format_trade_duration(trade.get("opened_at", ""))
        embed = discord.Embed(
            title=f" Confirm Manual Close  {_cl_label}",
            description=(
                f"Are you sure you want to close the **{trade.get('direction','?').upper()}** trade on **{_cl_label}**?\n\n"
                f"Entry: **{price_fmt(_cl_label, trade['entry'])}**  Duration: **{_dur}**  {_t1_status}\n\n"
                f"Type `!close {pair_arg} confirm` to execute at current market price."
            ),
            color=0xFFA500,
            timestamp=datetime.now(timezone.utc),
        )
        embed.set_footer(text="Chartwise v10.0  Confirmation required to close trade")
        await ctx.send(embed=embed)
        print(f"[CMD] !close {_cl_label}  confirmation pending from {ctx.author}")


#  v9.4 Feature 6: !top [n] command 
@bot.command(name="top")
async def cmd_top(ctx, n_arg: str = "5"):
    """v9.4  Show the N highest-scoring signals in SIGNAL_LOG (default 5)."""
    try:
        n = max(1, min(int(n_arg), 20))
    except ValueError:
        await ctx.send(" Usage: `!top [n]`  e.g. `!top 5` or `!top 10`")
        return

    if not SIGNAL_LOG:
        await ctx.send(" No signals in the session log yet.")
        return

    # Sort by score descending
    _sorted = sorted(SIGNAL_LOG, key=lambda x: x.get("score", 0), reverse=True)
    _top_n = _sorted[:n]

    # Cross-reference with on-disk signal log to get outcomes
    try:
        _disk_sigs = {s["id"]: s for s in _read_signals() if "id" in s}
    except Exception:
        _disk_sigs = {}

    embed = discord.Embed(
        title=f" Top {n} Signals by Score",
        description=f"Highest-scoring signals from the session log (max {len(SIGNAL_LOG)} entries tracked).",
        color=0xFFD700,
        timestamp=datetime.now(timezone.utc),
    )

    for _rank, _sig in enumerate(_top_n, 1):
        _sig_id  = _sig.get("id", "")
        _pair    = _sig.get("pair", "?")
        _dir     = _sig.get("direction", "?").upper()
        _score   = _sig.get("score", 0)
        _ts      = _sig.get("ts", 0)
        _engine  = _sig.get("engine", "?")
        # Time display
        try:
            _dt = datetime.fromtimestamp(_ts, tz=timezone.utc)
            _time_str = _dt.strftime("%m/%d %H:%M UTC")
        except Exception:
            _time_str = "?"
        # Outcome lookup from disk
        _outcome = _sig.get("outcome", "PENDING")
        if _sig_id in _disk_sigs:
            _outcome = _disk_sigs[_sig_id].get("outcome", _outcome)
        _outcome_emoji = {"WIN": "", "LOSS": "", "PENDING": ""}.get(_outcome, "")

        _conf_label, _conf_emoji = confidence_tier(_score)
        embed.add_field(
            name=f"#{_rank}  {_pair} {_dir} ({_engine})",
            value=(
                f"Score: **{_score}** {_conf_emoji} {_conf_label}\n"
                f"Time: {_time_str}\n"
                f"Outcome: {_outcome_emoji} **{_outcome}**"
            ),
            inline=True
        )

    if len(_top_n) % 3 != 0:
        for _ in range(3 - len(_top_n) % 3):
            embed.add_field(name="", value="", inline=True)

    embed.add_field(
        name=" What makes a 10/10 signal?",
        value=(
            "Top signals typically have: liquidity sweep + BOS + OB + FVG + MTF consensus + "
            "OTE fib alignment + volume spike. Each factor adds +1 to +3. "
            "Use `!scoretable` for the complete reference."
        ),
        inline=False
    )
    embed.set_footer(text=f"Chartwise v10.0  Top signals by score  !scoretable for scoring reference")
    await ctx.send(embed=embed)
    print(f"[CMD] !top {n}  sent {len(_top_n)} signals to #{ctx.channel.name}")


#  v9.4 Feature 1: !correlation command (defined above) 

@bot.command(name="scan")
async def cmd_scan(ctx):
    """Manually trigger a scan of all 5 pairs."""
    await ctx.send(" Scanning all 3 pairs...")
    channel = ctx.channel
    found_any = False

    for pair in PAIRS:
        pair_label = pair["label"]
        candles_5m = await fetch_candles(pair, timeframe="5m")
        if not candles_5m or len(candles_5m) < 30:
            await ctx.send(f" {pair_label}: could not fetch candles")
            continue

        htf_trend = await get_htf_trend(pair)

        smc_signal = analyze(candles_5m, pair_label)
        std_signal = analyze_standard(candles_5m, pair_label)

        def is_counter_trend(signal: dict, htf: str) -> bool:
            if htf in ("unknown", "neutral"):
                return False
            sig_dir = signal.get("direction", "")
            return (sig_dir == "long" and htf == "short") or (sig_dir == "short" and htf == "long")

        if smc_signal:
            ct = is_counter_trend(smc_signal, htf_trend)
            if ct and smc_signal.get("score", 0) < RATING_A:
                smc_signal = None

        if std_signal and is_counter_trend(std_signal, htf_trend):
            std_signal = None

        if smc_signal:
            ct = is_counter_trend(smc_signal, htf_trend)
            embed = make_premium_embed(pair_label, smc_signal, htf_trend, ct)
            await channel.send(embed=embed)
            found_any = True
        elif std_signal:
            ct = is_counter_trend(std_signal, htf_trend)
            embed = make_standard_embed(pair_label, std_signal, htf_trend, ct)
            await channel.send(embed=embed)
            found_any = True
        else:
            await ctx.send(f" {pair_label}: no signal (HTF: {htf_trend})")

    if not found_any:
        await ctx.send("No signals found across all 3 pairs right now.")


@bot.command(name="pnl")
async def cmd_pnl(ctx):
    """Show enhanced session P&L with per-engine, per-pair, per-session breakdown."""
    total_trades = session_pnl["wins"] + session_pnl["losses"]
    wr = session_pnl["wins"] / max(total_trades, 1) * 100
    net = session_pnl["total_pnl_pct"]
    color = 0x00E676 if net >= 0 else 0xFF5252
    embed = discord.Embed(title=" Session P&L  Deep Stats", color=color)

    # Top-line summary
    embed.add_field(name="Total W/L", value=f"{session_pnl['wins']}W / {session_pnl['losses']}L", inline=True)
    embed.add_field(name="Win Rate", value=f"{wr:.1f}%", inline=True)
    embed.add_field(name="Net P&L", value=f"{'+' if net >= 0 else ''}{net:.2f}%", inline=True)
    embed.add_field(name="T1 Hits", value=str(session_pnl["t1_hits"]), inline=True)
    embed.add_field(name="Consecutive Losses", value=str(_consecutive_losses), inline=True)
    embed.add_field(name="Circuit", value=" TRIPPED" if _circuit_tripped_at > 0 else " OK", inline=True)

    # Per-engine breakdown
    p_total = session_pnl["premium_wins"] + session_pnl["premium_losses"]
    s_total = session_pnl["standard_wins"] + session_pnl["standard_losses"]
    p_wr = session_pnl["premium_wins"] / max(p_total, 1) * 100
    s_wr = session_pnl["standard_wins"] / max(s_total, 1) * 100
    embed.add_field(
        name=" SMC Engine",
        value=f"{session_pnl['premium_wins']}W/{session_pnl['premium_losses']}L ({p_wr:.0f}% WR)",
        inline=True
    )
    embed.add_field(
        name=" EMA Engine",
        value=f"{session_pnl['standard_wins']}W/{session_pnl['standard_losses']}L ({s_wr:.0f}% WR)",
        inline=True
    )
    embed.add_field(name="", value="", inline=True)

    # Per-pair breakdown
    pair_lines = []
    for pair in PAIRS:
        lbl = pair["label"]
        pw = session_pnl["pair_wins"].get(lbl, 0)
        pl = session_pnl["pair_losses"].get(lbl, 0)
        pt = pw + pl
        pwr = pw / max(pt, 1) * 100
        pair_lines.append(f"**{lbl}**: {pw}W/{pl}L ({pwr:.0f}%)")
    embed.add_field(name=" Per Pair", value="\n".join(pair_lines) or "No trades yet", inline=False)

    # Per-session breakdown
    sess_lines = []
    for sess_name in ["New York", "London", "Asia", "Off-Hours"]:
        sw = session_pnl["session_wins"].get(sess_name, 0)
        sl_c = session_pnl["session_losses"].get(sess_name, 0)
        st = sw + sl_c
        if st > 0:
            swr = sw / st * 100
            sess_lines.append(f"**{sess_name}**: {sw}W/{sl_c}L ({swr:.0f}%)")
    embed.add_field(name=" Per Session", value="\n".join(sess_lines) or "No trades yet", inline=False)

    # Equity curve (v8.4): ASCII bar chart of last 20 closed trades
    _closed_trades = [t for t in list(TRADE_HISTORY) if t.get("outcome") in ("WIN", "LOSS")]
    if len(_closed_trades) >= 2:
        _curve_trades = _closed_trades[-20:]
        _pnls = [t.get("pnl_pct", 0.0) or 0.0 for t in _curve_trades]
        _cum = []
        _running = 0.0
        for _p in _pnls:
            _running += _p if _curve_trades[len(_cum)].get("outcome") == "WIN" else -abs(_p)
            _cum.append(_running)
        _mn = min(_cum)
        _mx = max(_cum)
        _bar_chars = ""
        if _mx == _mn:
            _curve_str = "" * len(_cum)
        else:
            _curve_str = "".join(_bar_chars[int((_v - _mn) / (_mx - _mn) * 7)] for _v in _cum)
        embed.add_field(
            name=" Equity Curve (last 20 trades)",
            value=f"`{_curve_str}`\n{_mn:+.2f}%  {_mx:+.2f}% (running: {_running:+.2f}%)",
            inline=False
        )

    embed.set_footer(text=f"Chartwise v10.0  Stats reset on restart  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)



@bot.command(name="circuit")
async def cmd_circuit(ctx):
    """Show circuit breaker status."""
    if _circuit_tripped_at > 0:
        elapsed = time.time() - _circuit_tripped_at
        remaining = max(0, CIRCUIT_BREAKER_COOLDOWN - elapsed)
        mins = int(remaining / 60)
        hrs  = mins // 60
        mins_left = mins % 60
        embed = discord.Embed(
            title=" Circuit Breaker  ACTIVE",
            description=f"Scanning is paused after **{CIRCUIT_BREAKER_LOSSES} consecutive losses**.",
            color=0xFF5252
        )
        embed.add_field(name="Time Remaining", value=f"{hrs}h {mins_left}m", inline=True)
        embed.add_field(name="Consecutive Losses", value=str(_consecutive_losses), inline=True)
        embed.add_field(
            name="What This Means",
            value="The bot detected an unusual losing streak and paused to protect capital. It will auto-resume after the cooldown. Trading conditions may be choppy  review manually.",
            inline=False
        )
    else:
        embed = discord.Embed(
            title=" Circuit Breaker  INACTIVE",
            description="Scanning is running normally.",
            color=0x00E676
        )
        embed.add_field(name="Consecutive Losses", value=str(_consecutive_losses), inline=True)
        embed.add_field(name="Trips Needed", value=str(CIRCUIT_BREAKER_LOSSES), inline=True)
    embed.set_footer(text=f"Chartwise v10.0  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)


@bot.command(name="pairs")
async def cmd_pairs(ctx, action: str = None, pair_arg: str = None):
    """Show or manage monitored pairs. (v8.4)
    Usage: !pairs                   show current list
           !pairs add BTC           add BTC-USD to scan list
           !pairs remove SOL        remove SOL-USD from scan list
           !pairs reset             restore original PAIRS list"""
    global DYNAMIC_PAIRS

    if action == "add" and pair_arg:
        # v9.2 Feature 1: Normalize input  "eth"  "ETH-USD", "eth-usd"  "ETH-USD", "ETHUSD"  "ETH-USD"
        raw = pair_arg.upper().strip()
        # Strip common suffixes and normalize
        if raw.endswith("-USD"):
            ticker = raw[:-4]
        elif raw.endswith("USD") and len(raw) > 3:
            ticker = raw[:-3]
        elif raw.endswith("/USD"):
            ticker = raw[:-4]
        else:
            ticker = raw
        # Remove any remaining dashes/slashes from the ticker
        ticker = ticker.replace("-", "").replace("/", "")
        product_id = f"{ticker}-USD"
        label = f"{ticker}/USD"

        if any(p["label"] == label for p in DYNAMIC_PAIRS):
            await ctx.send(f" `{label}` is already in the scan list.")
            return

        # v9.2 Feature 1: Validate the pair exists on Coinbase by attempting a candle fetch
        await ctx.send(f" Validating `{product_id}` on Coinbase")
        validation_candles = await fetch_coinbase_candles(product_id, granularity=300, limit=5)
        if not validation_candles:
            await ctx.send(
                f" Pair `{product_id}` not found on Coinbase  verify the ticker.\n"
                f"Tip: use the base ticker only, e.g. `!pairs add ETH` for ETH-USD."
            )
            return

        new_pair = {"label": label, "source": "coinbase", "product_id": product_id, "yahoo": None}
        DYNAMIC_PAIRS.append(new_pair)
        # Initialize lock for new pair
        if label not in pair_locks:
            pair_locks[label] = asyncio.Lock()
        await ctx.send(f" Added `{label}` (`{product_id}`) to scan list. Now scanning {len(DYNAMIC_PAIRS)} pairs.")
        return

    if action == "remove" and pair_arg:
        ticker = pair_arg.upper()
        label = f"{ticker}/USD"
        if len(DYNAMIC_PAIRS) <= 1:
            await ctx.send(" Cannot remove  must keep at least 1 pair in the scan list.")
            return
        before = len(DYNAMIC_PAIRS)
        DYNAMIC_PAIRS = [p for p in DYNAMIC_PAIRS if p["label"] != label]
        if len(DYNAMIC_PAIRS) == before:
            await ctx.send(f" `{label}` not found in scan list.")
        else:
            await ctx.send(f" Removed `{label}` from scan list. Now scanning {len(DYNAMIC_PAIRS)} pairs.")
        return

    if action == "reset":
        DYNAMIC_PAIRS = list(PAIRS)
        await ctx.send(f" Scan list reset to original {len(DYNAMIC_PAIRS)} pairs: {', '.join(p['label'] for p in DYNAMIC_PAIRS)}")
        return

    now = time.time()
    embed = discord.Embed(title=" Monitored Pairs", color=0x7C4DFF)
    for pair in DYNAMIC_PAIRS:
        lbl = pair["label"]
        cooldown_left = max(0, SIGNAL_COOLDOWN - (now - last_signal_time.get(lbl, 0)))
        win_cool_left = max(0, POST_WIN_COOLDOWN - (now - last_win_time.get(lbl, 0)))
        in_trade = " IN TRADE" if lbl in active_trades else " Watching"
        cool_str = f" {int(cooldown_left/60)}m cooldown" if cooldown_left > 0 else ""
        win_str  = f" {int(win_cool_left/60)}m post-win" if win_cool_left > 0 else ""
        status_parts = [in_trade]
        if cool_str: status_parts.append(cool_str)
        if win_str: status_parts.append(win_str)
        embed.add_field(name=lbl, value="  ".join(status_parts), inline=False)
    embed.set_footer(text=f"Chartwise v10.0  !pairs add/remove/reset to manage  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)


@bot.command(name="heatmap")
async def cmd_heatmap(ctx):
    """Show win rate by score band, engine, and top-performing confluence reasons."""
    signals = _read_signals()
    closed = [s for s in signals if s["outcome"] in ("WIN", "LOSS")]
    if len(closed) < 5:
        await ctx.send(" Need at least 5 closed signals for heatmap. Keep running!")
        return

    # Score band breakdown (7, 8, 9, 10, 11+)
    bands: dict[str, list[int]] = {}
    for s in closed:
        score = s.get("score", 0)
        band = str(score) if score <= 11 else "12+"
        if band not in bands:
            bands[band] = [0, 0]  # [wins, losses]
        if s["outcome"] == "WIN":
            bands[band][0] += 1
        else:
            bands[band][1] += 1

    embed = discord.Embed(title=" Signal Quality Heatmap", color=0x7B2FBE)
    embed.add_field(name="Total Signals Analyzed", value=str(len(closed)), inline=True)
    embed.add_field(name="Overall WR", value=f"{sum(1 for s in closed if s['outcome']=='WIN')/len(closed)*100:.1f}%", inline=True)
    embed.add_field(name="", value="", inline=True)

    # Score band table
    score_lines = []
    for band in sorted(bands.keys(), key=lambda x: int(x.replace("+", "99"))):
        w, l = bands[band]
        total = w + l
        wr = w / total * 100
        bar = "" if wr >= 60 else ("" if wr >= 45 else "")
        score_lines.append(f"{bar} Score {band}: {w}W/{l}L ({wr:.0f}%) [{total} trades]")
    embed.add_field(name=" Win Rate by Score", value="\n".join(score_lines), inline=False)

    # Best performing confluence reasons
    reason_wins: dict[str, list[int]] = {}
    for s in closed:
        for reason in s.get("reasons", []):
            key = reason[:50]
            if key not in reason_wins:
                reason_wins[key] = [0, 0]
            if s["outcome"] == "WIN":
                reason_wins[key][0] += 1
            else:
                reason_wins[key][1] += 1

    # Filter reasons with 3 samples, sort by WR
    qualified = {k: v for k, v in reason_wins.items() if sum(v) >= 3}
    sorted_reasons = sorted(qualified.items(), key=lambda x: x[1][0]/sum(x[1]), reverse=True)
    top5 = sorted_reasons[:5]
    if top5:
        top_lines = []
        for reason, (w, l) in top5:
            wr = w / (w + l) * 100
            top_lines.append(f" {wr:.0f}%  {reason[:45]}")
        embed.add_field(name=" Best Confluence Reasons", value="\n".join(top_lines), inline=False)

    # Worst performing
    worst5 = sorted(qualified.items(), key=lambda x: x[1][0]/sum(x[1]))[:5]
    if worst5:
        worst_lines = []
        for reason, (w, l) in worst5:
            wr = w / (w + l) * 100
            worst_lines.append(f" {wr:.0f}%  {reason[:45]}")
        embed.add_field(name=" Weakest Confluence Reasons", value="\n".join(worst_lines), inline=False)

    #  4H HTF Bias column per pair 
    bias_lines = []
    for pair in PAIRS:
        try:
            candles_4h_hm = await fetch_candles(pair, timeframe="4h")
            if candles_4h_hm and len(candles_4h_hm) >= 10:
                bias_result = calc_htf_candle_bias(candles_4h_hm, lookback=10)
                if bias_result:
                    bias_lines.append(
                        f"{bias_result['bias_emoji']} **{pair['label']}**  {bias_result['bias_label']} "
                        f"({bias_result['bull_count']}/{bias_result['lookback']} bull)"
                    )
                else:
                    bias_lines.append(f" **{pair['label']}**  Insufficient data")
            else:
                bias_lines.append(f" **{pair['label']}**  No 4H data")
        except Exception:
            bias_lines.append(f" **{pair['label']}**  Error")
    if bias_lines:
        embed.add_field(name=" 4H HTF Bias (Live)", value="\n".join(bias_lines), inline=False)

    embed.set_footer(text=f"Chartwise v10.0  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)


@bot.command(name="backtest")
async def cmd_backtest(ctx, min_score_arg: int = None):
    """Simulate performance if a higher MIN_SCORE filter had been applied.
    Usage: !backtest [score]  defaults to testing score thresholds 7-12.
    Shows how WR and trade count change at each threshold using logged signals."""
    try:
        closed = [s for s in json.loads(SIGNALS_FILE.read_text())
                  if s.get("outcome") in ("WIN", "SL")]
    except Exception:
        await ctx.send(" No closed signal data yet  signals accumulate as trades close.")
        return

    if len(closed) < 5:
        await ctx.send(f" Only {len(closed)} closed trades  need at least 5 for backtest.")
        return

    embed = discord.Embed(
        title=" Score Threshold Backtest",
        description=(
            f"Simulating how different MIN_SCORE filters would have performed on "
            f"**{len(closed)} closed trades**. Current threshold: **{MIN_SCORE}**"
        ),
        color=0x2ECC71
    )

    # Test each threshold from 5 to max score seen
    max_seen = max((s.get("score", 0) for s in closed), default=12)
    thresholds = range(5, min(max_seen + 1, 16))

    rows = []
    for threshold in thresholds:
        subset = [s for s in closed if s.get("score", 0) >= threshold]
        if not subset:
            break
        wins = sum(1 for s in subset if s["outcome"] == "WIN")
        losses = len(subset) - wins
        wr = wins / len(subset) * 100
        current = "  current" if threshold == MIN_SCORE else ""
        rows.append(
            f"`Score {threshold:2d}`  {wins}W/{losses}L  **{wr:.0f}%** WR  [{len(subset)} trades]{current}"
        )

    embed.add_field(name=" Win Rate by Minimum Score", value="\n".join(rows), inline=False)

    # Find optimal threshold (max WR with  5 trades)
    best_wr = 0
    best_threshold = MIN_SCORE
    for threshold in thresholds:
        subset = [s for s in closed if s.get("score", 0) >= threshold]
        if len(subset) < 5:
            break
        wr = sum(1 for s in subset if s["outcome"] == "WIN") / len(subset) * 100
        if wr > best_wr:
            best_wr = wr
            best_threshold = threshold

    # Trade volume vs accuracy tradeoff note
    all_wins = sum(1 for s in closed if s["outcome"] == "WIN")
    baseline_wr = all_wins / len(closed) * 100

    embed.add_field(
        name=" Insight",
        value=(
            f"Optimal threshold (5 trades): **Score {best_threshold}**  **{best_wr:.0f}% WR**\n"
            f"Baseline (current {MIN_SCORE}): {baseline_wr:.0f}% WR across {len(closed)} trades\n\n"
            f"Raising the threshold filters more trades but may improve WR. "
            f"Lowering it increases signal frequency but risks lower quality."
        ),
        inline=False
    )
    embed.set_footer(text=f"Chartwise v10.0  Backtest on logged data  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)


@bot.command(name="setmin")
async def cmd_setmin(ctx, score_arg: str = None):
    """Change the minimum signal score threshold at runtime.
    Usage: !setmin [score]   must be an integer between 5 and 15.
    """
    global MIN_SCORE, CONFIDENCE_HIGH, CONFIDENCE_MEDIUM
    if score_arg is None:
        embed = discord.Embed(
            title=" Current Min Score",
            description=f"Current `MIN_SCORE` = **{MIN_SCORE}**\nUsage: `!setmin <515>` to change.",
            color=0x7C4DFF
        )
        embed.set_footer(text=f"Chartwise v10.0  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
        await ctx.send(embed=embed)
        return
    try:
        new_score = int(score_arg)
    except ValueError:
        await ctx.send(" Invalid value. Usage: `!setmin <515>` (integer only).")
        return
    if new_score < 5 or new_score > 15:
        await ctx.send(" Score must be between **5** and **15**. Current value unchanged.")
        return
    old_score = MIN_SCORE
    MIN_SCORE = new_score
    CONFIDENCE_HIGH   = MIN_SCORE + 5
    CONFIDENCE_MEDIUM = MIN_SCORE + 2
    embed = discord.Embed(
        title=" Min Score Updated",
        color=0x00E676
    )
    embed.add_field(name="Previous", value=str(old_score), inline=True)
    embed.add_field(name="New", value=str(MIN_SCORE), inline=True)
    embed.add_field(name="Effect", value="Signals scoring below this threshold will no longer fire.", inline=False)
    embed.add_field(name="Confidence Tiers", value=f"High: {CONFIDENCE_HIGH}    Medium: {CONFIDENCE_MEDIUM}", inline=False)
    embed.set_footer(text=f"Chartwise v10.0  Changed by {ctx.author}  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !setmin  MIN_SCORE changed from {old_score} to {MIN_SCORE} by {ctx.author}")


@bot.command(name="learn")
async def cmd_learn(ctx):
    """Show what the adaptive learning engine has learned so far."""
    embed = discord.Embed(title="Chartwise Learning Engine", color=0x9b59b6)

    if not pattern_performance:
        embed.description = "No learning data yet. Signal outcomes are tracked automatically as trades resolve."
        await ctx.send(embed=embed)
        return

    # Sort patterns by sample size then win rate
    patterns = []
    for pattern, data in pattern_performance.items():
        wins = data.get("wins", 0)
        losses = data.get("losses", 0)
        total = wins + losses
        if total < 2:
            continue
        wr = wins / total * 100
        patterns.append((pattern, wins, losses, total, wr))

    patterns.sort(key=lambda x: (-x[4], -x[3]))

    if not patterns:
        embed.description = "Not enough data yet (need at least 2 outcomes per pattern)."
        await ctx.send(embed=embed)
        return

    # Top performers
    top = patterns[:8]
    top_str = ""
    for p, w, l, t, wr in top:
        bar = "█" * int(wr / 10) + "░" * (10 - int(wr / 10))
        top_str += f"`{p[:20]:<20}` {bar} {wr:.0f}% ({w}W/{l}L)\n"
    embed.add_field(name="Top Patterns", value=top_str or "N/A", inline=False)

    # Bottom performers
    bottom = sorted(patterns, key=lambda x: x[4])[:5]
    bot_str = ""
    for p, w, l, t, wr in bottom:
        bot_str += f"`{p[:20]:<20}` {wr:.0f}% ({w}W/{l}L)\n"
    embed.add_field(name="Weakest Patterns", value=bot_str or "N/A", inline=False)

    # Overall stats
    total_w = sum(p[1] for p in patterns)
    total_l = sum(p[2] for p in patterns)
    total_t = total_w + total_l
    overall_wr = total_w / total_t * 100 if total_t else 0

    embed.add_field(name="Overall", value=f"{total_w}W / {total_l}L — {overall_wr:.1f}% win rate\n{len(patterns)} patterns tracked", inline=False)

    # v10.0: Score multipliers section
    if SCORE_MULTIPLIERS:
        mult_lines = []
        for pat, mult in sorted(SCORE_MULTIPLIERS.items()):
            if mult > 1.05:
                mult_lines.append(f" `{pat:<22}` ×{mult:.2f} (boosted)")
            elif mult < 0.95:
                mult_lines.append(f" `{pat:<22}` ×{mult:.2f} (penalized)")
            else:
                mult_lines.append(f"  `{pat:<22}` ×{mult:.2f}")
        embed.add_field(name=" Score Multipliers (v10.0)", value="\n".join(mult_lines) or "All at ×1.00", inline=False)
    else:
        embed.add_field(name=" Score Multipliers (v10.0)", value="Not yet calculated (need 10+ outcomes per pattern)", inline=False)

    # v10.0: Resolved outcomes counter
    next_rebalance = 50 - (RESOLVED_OUTCOMES_COUNT % 50) if RESOLVED_OUTCOMES_COUNT % 50 != 0 else 50
    embed.add_field(
        name=" Outcome Tracker (v10.0)",
        value=f"Resolved outcomes: **{RESOLVED_OUTCOMES_COUNT}**\nNext rebalance in: **{next_rebalance}** outcomes",
        inline=False
    )

    embed.set_footer(text="Learning data auto-saves to chartwise_learning.json  |  Weights: chartwise_weights.json")
    await ctx.send(embed=embed)


@bot.command(name="winners")
async def cmd_winners(ctx):
    """
    Show top-performing confluence factors  patterns that appear most often on winning trades.
    Complements !learn (which shows penalized losers).
    Usage: !winners
    """
    wins = _adaptive_win_counts
    losses = _adaptive_sl_counts

    if not wins and not losses:
        await ctx.send(" No trade data yet  confluence stats accumulate as trades close.")
        return

    embed = discord.Embed(
        title=" Winning Confluence Factors",
        description="Patterns that appear most often on T2 winners vs SL losers.",
        color=0x00E676
    )

    # Top 10 winners by win count, with win/loss ratio
    all_reasons = set(list(wins.keys()) + list(losses.keys()))
    stats = []
    for key in all_reasons:
        w = wins.get(key, 0)
        l = losses.get(key, 0)
        total = w + l
        win_rate = (w / total * 100) if total > 0 else 0
        stats.append((key, w, l, total, win_rate))

    # Sort by win count descending
    by_wins = sorted(stats, key=lambda x: x[1], reverse=True)[:10]
    if by_wins:
        lines = []
        for key, w, l, total, wr in by_wins:
            bar = "" * min(10, w) + "" * max(0, 10 - w)
            lines.append(f"`{bar}` **{w}W/{l}L** ({wr:.0f}% WR)  `{key[:35]}`")
        embed.add_field(name="Top by Win Count", value="\n".join(lines), inline=False)

    # Sort by win rate (min 3 occurrences)
    by_wr = sorted([s for s in stats if s[3] >= 3], key=lambda x: x[4], reverse=True)[:5]
    if by_wr:
        lines2 = []
        for key, w, l, total, wr in by_wr:
            lines2.append(f"**{wr:.0f}%** WR ({w}W/{l}L)  `{key[:40]}`")
        embed.add_field(name="Top by Win Rate (min 3 trades)", value="\n".join(lines2), inline=False)

    embed.add_field(
        name="How to Use This",
        value="Patterns with high win counts AND high win rate are your most reliable confluence signals. "
              "Patterns with low win rate appear in !learn as penalized factors.",
        inline=False
    )

    #  Worst Patterns section 
    # Sort by SL count descending (most SL hits = worst patterns), min 1 SL hit
    worst = sorted(
        [(key, w, l, w + l, (w / (w + l) * 100) if (w + l) > 0 else 0)
         for key, w, l, *_ in stats if losses.get(key, 0) >= 1],
        key=lambda x: x[2],   # sort by loss count descending
        reverse=True
    )[:5]
    if worst:
        worst_lines = []
        for key, w, l, total, wr in worst:
            worst_lines.append(f"**{l} SL** / {w}W  ({wr:.0f}% WR)  `{key[:40]}`")
        embed.add_field(name=" Worst Patterns", value="\n".join(worst_lines), inline=False)

    embed.set_footer(text=f"Chartwise v10.0  !learn for penalized patterns  !help for all commands")
    await ctx.send(embed=embed)
    print(f"[CMD] !winners  sent winner confluence stats to #{ctx.channel.name}")


@bot.command(name="log")
async def cmd_log(ctx, n_arg: str = "10"):
    """Show the last N signals fired (default 10, max 25).
    Usage: !log [n]
    """
    try:
        n = max(1, min(25, int(n_arg)))
    except ValueError:
        n = 10

    if not SIGNAL_LOG:
        await ctx.send(" No signals fired yet this session. Signals appear here once the scanner fires one.")
        return

    entries = list(SIGNAL_LOG)[-n:][::-1]  # most recent first
    embed = discord.Embed(
        title=f" Last {len(entries)} Signal(s) Fired",
        color=0x7B68EE,
        timestamp=datetime.now(timezone.utc)
    )
    now_dt = datetime.now(timezone.utc)
    for entry in entries:
        try:
            fired_dt = datetime.fromisoformat(entry["time"])
            if fired_dt.tzinfo is None:
                fired_dt = fired_dt.replace(tzinfo=timezone.utc)
            age_min = int((now_dt - fired_dt).total_seconds() // 60)
            age_str = f"{age_min}m ago" if age_min < 60 else f"{age_min // 60}h {age_min % 60}m ago"
        except Exception:
            age_str = "?"
        dir_emoji = "" if entry["direction"] == "LONG" else ""
        embed.add_field(
            name=f"{dir_emoji} {entry['pair']} {entry['direction']}",
            value=(
                f"Score: **{entry['score']}**  {entry['confidence']}\n"
                f"Entry: {price_fmt(entry['pair'], entry['entry'])}\n"
                f"Fired: {age_str}"
            ),
            inline=True
        )

    embed.set_footer(text=f"Chartwise v10.0  Showing {len(entries)} of {len(SIGNAL_LOG)} logged  !log [n] for more")
    await ctx.send(embed=embed)
    print(f"[CMD] !log {n}  sent signal log to #{ctx.channel.name}")


@bot.command(name="winrate")
async def cmd_winrate(ctx, n_arg: str = "20"):
    """Show rolling win rate for last N trades (default 20) with progress bar and per-pair breakdown.
    Usage: !winrate [n]
    """
    try:
        n = max(1, min(200, int(n_arg)))
    except ValueError:
        n = 20

    trades_list = list(TRADE_HISTORY)
    closed = [t for t in trades_list if t.get("outcome") in ("WIN", "LOSS")]

    if not closed:
        await ctx.send(" No closed trades yet  win rate unavailable.")
        return

    recent = closed[-n:]
    n_wins = sum(1 for t in recent if t.get("outcome") == "WIN")
    n_total = len(recent)
    win_rate = n_wins / n_total * 100 if n_total > 0 else 0.0

    # Progress bar: 10 segments
    filled = round(win_rate / 10)
    bar = "" * filled + "" * (10 - filled)

    # Per-pair breakdown
    pair_stats: dict = {}
    for t in recent:
        p = t.get("pair", "?")
        if p not in pair_stats:
            pair_stats[p] = {"wins": 0, "total": 0}
        pair_stats[p]["total"] += 1
        if t.get("outcome") == "WIN":
            pair_stats[p]["wins"] += 1

    embed = discord.Embed(
        title=f" Rolling Win Rate  Last {n_total} Trades",
        color=0x00BFFF,
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(
        name="Overall",
        value=f"`{bar}` **{win_rate:.0f}%**  ({n_wins}W / {n_total - n_wins}L of {n_total})",
        inline=False
    )
    pair_lines = []
    for pair, ps in sorted(pair_stats.items()):
        pr = ps["wins"] / ps["total"] * 100 if ps["total"] > 0 else 0.0
        pf = round(pr / 10)
        pb = "" * pf + "" * (10 - pf)
        pair_lines.append(f"**{pair}** `{pb}` {pr:.0f}%  ({ps['wins']}W/{ps['total']-ps['wins']}L)")
    if pair_lines:
        embed.add_field(name="Per Pair", value="\n".join(pair_lines), inline=False)

    embed.set_footer(text=f"Chartwise v10.0  Win rate across last {n_total} closed trades")
    await ctx.send(embed=embed)
    print(f"[CMD] !winrate {n}  sent to #{ctx.channel.name}")


@bot.command(name="recap")
async def cmd_recap(ctx):
    """End-of-week / last 7 days performance recap.
    Shows trades, win rate, best/worst pair, total PnL%, most common pattern in wins, most common session.
    Usage: !recap
    """
    from datetime import timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    trades_list = list(TRADE_HISTORY)
    week_trades = []
    for t in trades_list:
        closed_at_str = t.get("closed_at", "")
        if not closed_at_str:
            continue
        try:
            closed_dt = datetime.fromisoformat(closed_at_str)
            if closed_dt.tzinfo is None:
                closed_dt = closed_dt.replace(tzinfo=timezone.utc)
            if closed_dt >= cutoff:
                week_trades.append(t)
        except Exception:
            pass

    closed = [t for t in week_trades if t.get("outcome") in ("WIN", "LOSS")]

    if not closed:
        await ctx.send(" No closed trades in the last 7 days.")
        return

    n_wins = sum(1 for t in closed if t.get("outcome") == "WIN")
    n_total = len(closed)
    win_rate = n_wins / n_total * 100 if n_total > 0 else 0.0
    total_pnl = sum(t.get("pnl_pct", 0) or 0 for t in closed
                    if t.get("outcome") == "WIN") - sum(abs(t.get("pnl_pct", 0) or 0)
                    for t in closed if t.get("outcome") == "LOSS")

    # Best and worst pair by win rate
    pair_stats: dict = {}
    for t in closed:
        p = t.get("pair", "?")
        if p not in pair_stats:
            pair_stats[p] = {"wins": 0, "losses": 0, "pnl": 0.0}
        if t.get("outcome") == "WIN":
            pair_stats[p]["wins"] += 1
            pair_stats[p]["pnl"] += abs(t.get("pnl_pct", 0) or 0)
        else:
            pair_stats[p]["losses"] += 1
            pair_stats[p]["pnl"] -= abs(t.get("pnl_pct", 0) or 0)

    def pair_wr(ps):
        tot = ps["wins"] + ps["losses"]
        return ps["wins"] / tot if tot > 0 else 0.0

    best_pair = max(pair_stats.items(), key=lambda kv: pair_wr(kv[1]))[0] if pair_stats else ""
    worst_pair = min(pair_stats.items(), key=lambda kv: pair_wr(kv[1]))[0] if pair_stats else ""

    # Most common pattern in winning trades (from reasons field)
    pattern_counts: dict = {}
    for t in closed:
        if t.get("outcome") == "WIN":
            for reason in t.get("reasons", []):
                pattern_counts[reason] = pattern_counts.get(reason, 0) + 1
    top_pattern = max(pattern_counts.items(), key=lambda kv: kv[1])[0] if pattern_counts else "N/A"

    # Most common session
    session_counts: dict = {}
    for t in closed:
        s = t.get("session", "?")
        session_counts[s] = session_counts.get(s, 0) + 1
    top_session = max(session_counts.items(), key=lambda kv: kv[1])[0] if session_counts else "N/A"

    filled = round(win_rate / 10)
    bar = "" * filled + "" * (10 - filled)

    embed = discord.Embed(
        title=" 7-Day Performance Recap",
        description=f"Last 7 days  {n_total} closed trades",
        color=0x9B59B6,
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name="Win Rate", value=f"`{bar}` **{win_rate:.0f}%** ({n_wins}W / {n_total - n_wins}L)", inline=False)
    sign = "+" if total_pnl >= 0 else ""
    embed.add_field(name="Total PnL%", value=f"**{sign}{total_pnl:.2f}%**", inline=True)
    embed.add_field(name="Best Pair", value=f"**{best_pair}**", inline=True)
    embed.add_field(name="Worst Pair", value=f"**{worst_pair}**", inline=True)
    embed.add_field(name="Top Pattern (Wins)", value=top_pattern[:80], inline=False)
    embed.add_field(name="Most Active Session", value=f"**{top_session}**", inline=True)
    embed.set_footer(text="Chartwise v10.0  Last 7 days recap")
    await ctx.send(embed=embed)
    print(f"[CMD] !recap  sent to #{ctx.channel.name}")


@bot.command(name="best")
async def cmd_best(ctx, n_arg: str = "5"):
    """Show top N trades by PnL% (default 5).
    Usage: !best [n]
    """
    try:
        n = max(1, min(50, int(n_arg)))
    except ValueError:
        n = 5

    trades_list = list(TRADE_HISTORY)
    closed = [t for t in trades_list if t.get("outcome") in ("WIN", "LOSS")]

    if not closed:
        await ctx.send(" No closed trades yet.")
        return

    wins = [t for t in closed if t.get("outcome") == "WIN"]
    wins.sort(key=lambda t: t.get("pnl_pct", 0) or 0, reverse=True)
    top = wins[:n] if wins else []

    embed = discord.Embed(
        title=f" Best {n} Trades by PnL%",
        color=0x00FF7F,
        timestamp=datetime.now(timezone.utc)
    )

    if not top:
        embed.description = "No winning trades recorded yet."
    else:
        for i, t in enumerate(top, 1):
            pnl = t.get("pnl_pct", 0) or 0
            entry_fmt = price_fmt(t.get("pair", "?"), t.get("entry", 0))
            exit_fmt = price_fmt(t.get("pair", "?"), t.get("exit", 0))
            closed_at = t.get("closed_at", "")[:10]
            embed.add_field(
                name=f"#{i} {t.get('pair','?')} {t.get('direction','?')}",
                value=(
                    f"PnL: **+{pnl:.3f}%**\n"
                    f"Entry: {entry_fmt}  Exit: {exit_fmt}\n"
                    f"Session: {t.get('session','?')}  {closed_at}"
                ),
                inline=False
            )

    embed.set_footer(text=f"Chartwise v10.0  Top {len(top)} winning trades")
    await ctx.send(embed=embed)
    print(f"[CMD] !best {n}  sent to #{ctx.channel.name}")


@bot.command(name="worst")
async def cmd_worst(ctx, n_arg: str = "5"):
    """Show bottom N trades by PnL% (worst losses, default 5).
    Usage: !worst [n]
    """
    try:
        n = max(1, min(50, int(n_arg)))
    except ValueError:
        n = 5

    trades_list = list(TRADE_HISTORY)
    closed = [t for t in trades_list if t.get("outcome") in ("WIN", "LOSS")]

    if not closed:
        await ctx.send(" No closed trades yet.")
        return

    losses = [t for t in closed if t.get("outcome") == "LOSS"]
    losses.sort(key=lambda t: t.get("pnl_pct", 0) or 0)
    bottom = losses[:n] if losses else []

    embed = discord.Embed(
        title=f" Worst {n} Trades by PnL%",
        color=0xFF4500,
        timestamp=datetime.now(timezone.utc)
    )

    if not bottom:
        embed.description = "No losing trades recorded yet."
    else:
        for i, t in enumerate(bottom, 1):
            pnl = t.get("pnl_pct", 0) or 0
            entry_fmt = price_fmt(t.get("pair", "?"), t.get("entry", 0))
            exit_fmt = price_fmt(t.get("pair", "?"), t.get("exit", 0))
            closed_at = t.get("closed_at", "")[:10]
            embed.add_field(
                name=f"#{i} {t.get('pair','?')} {t.get('direction','?')}",
                value=(
                    f"PnL: **{pnl:.3f}%**\n"
                    f"Entry: {entry_fmt}  Exit: {exit_fmt}\n"
                    f"Session: {t.get('session','?')}  {closed_at}"
                ),
                inline=False
            )

    embed.set_footer(text=f"Chartwise v10.0  Bottom {len(bottom)} losing trades")
    await ctx.send(embed=embed)
    print(f"[CMD] !worst {n}  sent to #{ctx.channel.name}")


@bot.command(name="heat")
async def cmd_heat(ctx, n_arg: str = "7"):
    """Signal frequency heatmap by session over last N days. (v8.4)
    Usage: !heat [n]  (default 7 days)
    Shows BTC: Asia 2 | London 5 | NY 3 style counts from SIGNAL_LOG."""
    try:
        n_days = max(1, min(30, int(n_arg)))
    except ValueError:
        n_days = 7

    if not SIGNAL_LOG:
        await ctx.send(" No signals logged yet  run the bot for a while first.")
        return

    cutoff_dt = datetime.now(timezone.utc) - timedelta(days=n_days)
    # Session hour boundaries (UTC)
    def _hour_to_session(hour: int) -> str:
        if 0 <= hour < 8:
            return "Asia"
        elif 8 <= hour < 13:
            return "London"
        elif 13 <= hour < 21:
            return "NY"
        return "Off-Hours"

    # Count signals per pair per session
    counts: dict[str, dict[str, int]] = {}
    for entry in SIGNAL_LOG:
        try:
            fired_dt = datetime.fromisoformat(entry["time"])
            if fired_dt.tzinfo is None:
                fired_dt = fired_dt.replace(tzinfo=timezone.utc)
            if fired_dt < cutoff_dt:
                continue
        except Exception:
            continue
        pair = entry.get("pair", "?")
        session = _hour_to_session(fired_dt.hour)
        if pair not in counts:
            counts[pair] = {"Asia": 0, "London": 0, "NY": 0, "Off-Hours": 0}
        counts[pair][session] = counts[pair].get(session, 0) + 1

    embed = discord.Embed(
        title=f" Signal Frequency Heatmap  Last {n_days} Days",
        description="Signals fired per pair per trading session",
        color=0xFF8C00,
        timestamp=datetime.now(timezone.utc)
    )
    if not counts:
        embed.description = f"No signals found in the last {n_days} days."
    else:
        for pair_lbl, sess_counts in sorted(counts.items()):
            total = sum(sess_counts.values())
            line = f"Asia **{sess_counts.get('Asia',0)}** | London **{sess_counts.get('London',0)}** | NY **{sess_counts.get('NY',0)}** | Off **{sess_counts.get('Off-Hours',0)}**  Total: **{total}**"
            embed.add_field(name=pair_lbl, value=line, inline=False)
    embed.set_footer(text=f"Chartwise v10.0  SIGNAL_LOG (last {SIGNAL_LOG.maxlen})  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !heat {n_days}  sent to #{ctx.channel.name}")


@bot.command(name="notes")
async def cmd_notes(ctx, action: str = "list", *, text: str = ""):
    """In-memory notepad for quick trade notes. (v8.4)
    Usage: !notes add <text>   add a note (max 10, oldest dropped)
           !notes list         show all notes
           !notes clear        delete all notes"""
    global NOTES
    if action == "add":
        if not text:
            await ctx.send(" Usage: `!notes add <your note text>`")
            return
        if len(NOTES) >= 10:
            NOTES.pop(0)  # FIFO: remove oldest
        NOTES.append(text)
        await ctx.send(f" Note saved ({len(NOTES)}/10): `{text}`")
    elif action == "clear":
        NOTES.clear()
        await ctx.send(" All notes cleared.")
    else:  # list (default)
        if not NOTES:
            await ctx.send(" No notes yet. Use `!notes add <text>` to save one.")
            return
        embed = discord.Embed(
            title=" Trade Notes",
            color=0xFFD700,
            timestamp=datetime.now(timezone.utc)
        )
        for i, note in enumerate(NOTES, 1):
            embed.add_field(name=f"#{i}", value=note, inline=False)
        embed.set_footer(text=f"Chartwise v10.0  {len(NOTES)}/10 notes  !notes add/clear")
        await ctx.send(embed=embed)
    print(f"[CMD] !notes {action}  used in #{ctx.channel.name}")


@bot.command(name="timer")
async def cmd_timer(ctx, arg: str = None):
    """
    Start a personal countdown timer (v8.5 Feature 2).
    Usage:
      !timer [minutes]   start a countdown for N minutes (e.g. !timer 15)
      !timer cancel      cancel your running timer
    Only one timer per user at a time.
    """
    global _active_timers
    user_id = ctx.author.id

    if arg is None:
        await ctx.send(f" Usage: `!timer [minutes]` or `!timer cancel`")
        return

    if arg.lower() == "cancel":
        task = _active_timers.pop(user_id, None)
        if task:
            task.cancel()
            await ctx.send(f" {ctx.author.mention}  timer cancelled.")
        else:
            await ctx.send(f" {ctx.author.mention}  you have no active timer.")
        return

    try:
        minutes = float(arg)
        if minutes <= 0 or minutes > 1440:
            await ctx.send(" Minutes must be between 1 and 1440.")
            return
    except ValueError:
        await ctx.send(" Usage: `!timer 15` (number of minutes) or `!timer cancel`")
        return

    # Cancel any existing timer for this user
    existing = _active_timers.pop(user_id, None)
    if existing:
        existing.cancel()

    seconds = int(minutes * 60)

    async def _run_timer():
        try:
            await asyncio.sleep(seconds)
            channel = bot.get_channel(ctx.channel.id)
            if channel:
                await channel.send(f" {ctx.author.mention}  your **{minutes:.0f}-minute** timer is up! ")
        except asyncio.CancelledError:
            pass
        finally:
            _active_timers.pop(user_id, None)

    task = asyncio.ensure_future(_run_timer())
    _active_timers[user_id] = task
    await ctx.send(f" {ctx.author.mention}  timer set for **{minutes:.0f} minute(s)**. I'll ping you when it's done. Use `!timer cancel` to stop it.")
    print(f"[CMD] !timer {minutes}m  started for user {ctx.author}")


@bot.command(name="brief")
async def cmd_brief(ctx):
    """
    Morning market brief  current price, 24h change%, RSI (15m), BB position, 4H bias,
    and whether there's an active trade per pair (v8.5 Feature 3).
    Usage: !brief
    """
    await ctx.trigger_typing()

    embed = discord.Embed(
        title=" Morning Market Brief",
        description="Quick snapshot of each pair: price, momentum, and trade status.",
        color=0xFFD700,
        timestamp=datetime.now(timezone.utc)
    )

    for pair in PAIRS:
        try:
            candles_15m = await fetch_candles(pair, timeframe="15m")
            candles_4h  = await fetch_candles(pair, timeframe="4h")
            candles_5m  = await fetch_candles(pair, timeframe="5m")

            lines = []

            # Current price and 24h change
            if candles_5m and len(candles_5m) >= 2:
                price_now = candles_5m[-1]["close"]
                # Approximate 24h ago price using oldest 5m candle available (up to 288 candles = 24h)
                price_24h = candles_5m[0]["close"]
                change_pct = (price_now - price_24h) / price_24h * 100 if price_24h else 0.0
                sign = "+" if change_pct >= 0 else ""
                chg_emoji = "" if change_pct >= 0 else ""
                lines.append(f"**Price:** {price_fmt(pair['label'], price_now)}  {chg_emoji} `{sign}{change_pct:.2f}%` (24h est.)")
            else:
                lines.append("**Price:** ")

            # RSI on 15m
            if candles_15m and len(candles_15m) >= 15:
                closes_15m = [c["close"] for c in candles_15m]
                rsi_val = rsi(closes_15m, 14)
                if rsi_val is not None:
                    rsi_tag = "  OB" if rsi_val > 70 else ("  OS" if rsi_val < 30 else "")
                    lines.append(f"**RSI (15m):** {rsi_val:.1f}{rsi_tag}")
                else:
                    lines.append("**RSI (15m):** ")

                # BB position
                if len(closes_15m) >= 20:
                    bb_mean = statistics.mean(closes_15m[-20:])
                    bb_std  = statistics.stdev(closes_15m[-20:])
                    bb_upper = bb_mean + 2 * bb_std
                    bb_lower = bb_mean - 2 * bb_std
                    bb_range = bb_upper - bb_lower
                    cur_close = closes_15m[-1]
                    if bb_range > 0:
                        bb_pct = (cur_close - bb_lower) / bb_range * 100
                        if bb_pct > 80:
                            bb_pos = f"{bb_pct:.0f}% (near upper band)"
                        elif bb_pct < 20:
                            bb_pos = f"{bb_pct:.0f}% (near lower band)"
                        elif 45 <= bb_pct <= 55:
                            bb_pos = f"{bb_pct:.0f}% (at midband)"
                        else:
                            bb_pos = f"{bb_pct:.0f}%"
                    else:
                        bb_pos = ""
                    lines.append(f"**BB Position (15m):** {bb_pos}")
            else:
                lines.append("**RSI/BB (15m):** ")

            # 4H bias
            if candles_4h and len(candles_4h) >= 10:
                bias = calc_htf_candle_bias(candles_4h, lookback=10)
                if bias:
                    lines.append(f"**4H Bias:** {bias['bias_emoji']} {bias['bias_label']}")
                else:
                    lines.append("**4H Bias:** ")
            else:
                lines.append("**4H Bias:** ")

            # v8.8 Feature 4: Market regime from 4H candles
            if candles_4h and len(candles_4h) >= 25:
                _regime_val = detect_market_regime(candles_4h, lookback=20)
                regime_icon = "" if _regime_val == "Trending Up" else ("" if _regime_val == "Trending Down" else "")
                lines.append(f"**Market Regime:** {regime_icon} {_regime_val}")

            # v9.4 Feature 2: Volatility regime from 1H candles
            candles_1h_brief = await fetch_candles(pair, timeframe="1h")
            if candles_1h_brief and len(candles_1h_brief) >= 22:
                _vol_regime = detect_volatility_regime(candles_1h_brief, lookback=20)
                _vol_icon = "" if _vol_regime == "High" else ("" if _vol_regime == "Low" else "")
                lines.append(f"** Vol Regime:** {_vol_icon} {_vol_regime}")

            # v9.5 Feature 2: TWAP display in brief
            if candles_15m and len(candles_15m) >= 20:
                _brief_twap = calc_twap(candles_15m, lookback=20)
                if _brief_twap is not None:
                    _brief_price = candles_15m[-1]["close"]
                    _brief_twap_bias = " bullish" if _brief_price > _brief_twap else " bearish"
                    lines.append(f"**TWAP(20):** {price_fmt(pair['label'], _brief_twap)}  ({_brief_twap_bias})")

            # v9.5 Feature 4: Choppiness Index in brief
            if candles_15m and len(candles_15m) >= 15:
                _brief_ci = calc_choppiness_index(candles_15m, period=14)
                if _brief_ci is not None:
                    if _brief_ci > 61.8:
                        _ci_label = f"{_brief_ci:.1f}  choppy"
                    elif _brief_ci < 38.2:
                        _ci_label = f"{_brief_ci:.1f}  trending"
                    else:
                        _ci_label = f"{_brief_ci:.1f} neutral"
                    lines.append(f"**Choppiness:** {_ci_label}")

            # Active trade status
            in_trade = pair["label"] in active_trades
            if in_trade:
                t = active_trades[pair["label"]]
                dur = format_trade_duration(t.get("opened_at", ""))
                lines.append(f"**Trade:**  {t.get('direction','?').upper()} active ({dur})")
            else:
                lines.append(f"**Trade:**  No active trade")

            embed.add_field(
                name=f" {pair['label']}",
                value="\n".join(lines),
                inline=False
            )
        except Exception as e:
            embed.add_field(name=f" {pair['label']}", value=f" Error: {str(e)[:60]}", inline=False)

    embed.set_footer(text=f"Chartwise v10.0  {datetime.now(timezone.utc).strftime('%H:%M UTC')}  !snapshot [pair] for full view")
    await ctx.send(embed=embed)
    print(f"[CMD] !brief  sent morning brief to #{ctx.channel.name}")


@bot.command(name="since")
async def cmd_since(ctx, pair_arg: str = None):
    """
    Show how long ago the last signal fired for a pair (or all pairs) (v8.5 Feature 5).
    Reads from SIGNAL_LOG (last 50 in-memory) and the persistent signal file.
    Usage:
      !since        show last signal time for all pairs
      !since BTC    show last signal time for BTC/USD only
    """
    now_dt = datetime.now(timezone.utc)

    # Combine in-memory SIGNAL_LOG with persistent file
    persistent = _read_signals() or []
    mem_entries = list(SIGNAL_LOG)
    # Merge: persistent first (older), then in-memory
    all_entries = persistent + mem_entries

    if pair_arg:
        pa = pair_arg.upper().strip()
        check_pairs = [p["label"] for p in PAIRS if pa in p["label"] or pa == p["label"].split("/")[0]]
        if not check_pairs:
            await ctx.send(f" Unknown pair `{pair_arg}`. Valid: {', '.join(p['label'] for p in PAIRS)}")
            return
    else:
        check_pairs = [p["label"] for p in PAIRS]

    embed = discord.Embed(
        title=" Time Since Last Signal",
        description="How long ago the last signal fired per pair.",
        color=0x7B68EE,
        timestamp=now_dt
    )

    for pair_label in check_pairs:
        # Find most recent signal for this pair
        pair_entries = [e for e in all_entries if e.get("pair") == pair_label]
        if not pair_entries:
            embed.add_field(name=pair_label, value="No signals logged.", inline=True)
            continue

        # Sort by time descending
        def _parse_time(e):
            try:
                t = datetime.fromisoformat(e.get("time", ""))
                if t.tzinfo is None:
                    t = t.replace(tzinfo=timezone.utc)
                return t
            except Exception:
                return datetime.min.replace(tzinfo=timezone.utc)

        latest = max(pair_entries, key=_parse_time)
        fired_dt = _parse_time(latest)

        if fired_dt == datetime.min.replace(tzinfo=timezone.utc):
            embed.add_field(name=pair_label, value=" Could not parse signal time.", inline=True)
            continue

        delta = now_dt - fired_dt
        total_min = int(delta.total_seconds() // 60)
        if total_min < 60:
            age_str = f"{total_min}m ago"
        else:
            age_str = f"{total_min // 60}h {total_min % 60}m ago"

        direction = latest.get("direction", "?").upper()
        score = latest.get("score", "?")
        dir_icon = "" if direction == "LONG" else ("" if direction == "SHORT" else "")
        # v8.8 Feature 6: show avg score from SCORE_HISTORY alongside last signal time
        avg_score_str = ""
        if pair_label in SCORE_HISTORY and SCORE_HISTORY[pair_label]:
            _dq = SCORE_HISTORY[pair_label]
            _avg = sum(_dq) / len(_dq)
            avg_score_str = f"\n Avg Score: {_avg:.1f} (last {len(_dq)})"
        embed.add_field(
            name=pair_label,
            value=f"{dir_icon} {direction}  Score {score}\n {age_str}{avg_score_str}",
            inline=True
        )

    embed.set_footer(text=f"Chartwise v10.0  {now_dt.strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !since {pair_arg or 'all'}  sent to #{ctx.channel.name}")


@bot.command(name="avg")
async def cmd_avg(ctx, pair_arg: str = None):
    """DCA calculator  30-day equal-buy plan with breakeven estimates. (v8.6 Feature 2)
    Usage: !avg [pair]  e.g. !avg BTC  or  !avg SOL
    Shows current price, 30-buy average entry, and breakeven levels at -10/-20/-30%.
    """
    # Resolve pair
    target_pair = None
    if pair_arg:
        pair_upper = pair_arg.upper().replace("-", "/")
        if "/" not in pair_upper:
            pair_upper = pair_upper + "/USD"
        for p in DYNAMIC_PAIRS:
            if p["label"].upper() == pair_upper or p["label"].upper().startswith(pair_upper.split("/")[0]):
                target_pair = p
                break
        if not target_pair:
            await ctx.send(f" Unknown pair: `{pair_arg}`. Available: {', '.join(p['label'] for p in DYNAMIC_PAIRS)}")
            return
    else:
        target_pair = DYNAMIC_PAIRS[0]  # default to BTC

    candles = await fetch_candles(target_pair, timeframe="5m")
    if not candles:
        await ctx.send(f" Could not fetch price data for {target_pair['label']}.")
        return

    current_price = candles[-1]["close"]
    pair_label = target_pair["label"]

    # 30-day DCA at equal buys: if you buy equal dollar amounts over 30 days at current price
    # (educational baseline  all 30 buys at today's price for illustration)
    n_buys = 30
    # Average entry = current price (buying same asset repeatedly at market)
    # The key insight: DCA reduces TIMING risk, not price risk.
    avg_entry = current_price  # baseline: all 30 buys at current price

    # Breakeven price for various entry discounts (if you DCA and price drops)
    # If you start DCA now and price falls X%, your average buy will be BELOW current price
    # because later buys are cheaper. We simulate simple equal-weighted averaging.
    def dca_avg(start_price: float, end_price: float, steps: int) -> float:
        """Average price if you buy equal dollar amounts as price linearly moves from start to end."""
        if start_price <= 0 or steps <= 0:
            return start_price
        # Linear interpolation of prices across 30 steps
        prices = [start_price + (end_price - start_price) * i / (steps - 1) for i in range(steps)]
        # Equal dollar amount invested each step: avg price = harmonic mean
        # (equal dollar = more units when price is lower)
        inv_prices = [1 / p for p in prices if p > 0]
        if not inv_prices:
            return start_price
        hmean = len(inv_prices) / sum(inv_prices)
        return hmean

    # Scenario: price drops linearly to X% of current over 30 days
    price_down10 = current_price * 0.90
    price_down20 = current_price * 0.80
    price_down30 = current_price * 0.70

    avg_down10 = dca_avg(current_price, price_down10, n_buys)
    avg_down20 = dca_avg(current_price, price_down20, n_buys)
    avg_down30 = dca_avg(current_price, price_down30, n_buys)

    embed = discord.Embed(
        title=f" DCA Calculator  {pair_label}",
        description=f"30 equal buys over 30 days starting at current price **{price_fmt(pair_label, current_price)}**",
        color=0x00B0FF
    )
    embed.add_field(
        name="Current Price",
        value=price_fmt(pair_label, current_price),
        inline=True
    )
    embed.add_field(
        name="Number of Buys",
        value=f"{n_buys} (1 per day)",
        inline=True
    )
    embed.add_field(
        name="Baseline Avg Entry",
        value=f"{price_fmt(pair_label, avg_entry)} (if price stays flat)",
        inline=False
    )
    embed.add_field(
        name=" If Price Drops 10%",
        value=(
            f"Price falls to {price_fmt(pair_label, price_down10)}\n"
            f"DCA avg entry: **{price_fmt(pair_label, avg_down10)}**\n"
            f"Breakeven: {price_fmt(pair_label, avg_down10)}  that's your real cost basis"
        ),
        inline=False
    )
    embed.add_field(
        name=" If Price Drops 20%",
        value=(
            f"Price falls to {price_fmt(pair_label, price_down20)}\n"
            f"DCA avg entry: **{price_fmt(pair_label, avg_down20)}**\n"
            f"Breakeven: {price_fmt(pair_label, avg_down20)}"
        ),
        inline=False
    )
    embed.add_field(
        name=" If Price Drops 30%",
        value=(
            f"Price falls to {price_fmt(pair_label, price_down30)}\n"
            f"DCA avg entry: **{price_fmt(pair_label, avg_down30)}**\n"
            f"Breakeven: {price_fmt(pair_label, avg_down30)}"
        ),
        inline=False
    )
    embed.add_field(
        name=" How DCA Works",
        value=(
            "Buying equal dollar amounts means you get MORE units when price is lower. "
            "Your average cost basis improves as the market drops  this is the core benefit of DCA. "
            "These estimates assume linear price movement for illustration only."
        ),
        inline=False
    )
    embed.set_footer(text=f"Chartwise v10.0  Educational tool  not financial advice  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !avg {pair_label}  DCA calc sent to #{ctx.channel.name}")


@bot.command(name="rsi")
async def cmd_rsi(ctx, pair_arg: str = None):
    """Quick RSI lookup across all 4 timeframes for a pair or all pairs. (v8.6 Feature 4)
    Usage: !rsi [pair]  e.g. !rsi BTC  or  !rsi  (all pairs)
    Color codes: >70 =  overbought, 50-70 =  bullish, 30-50 =  neutral, <30 =  oversold
    """
    def rsi_icon(val: float) -> str:
        if val >= 70:
            return ""
        elif val >= 50:
            return ""
        elif val >= 30:
            return ""
        else:
            return ""

    # Resolve pairs to scan
    if pair_arg:
        pair_upper = pair_arg.upper().replace("-", "/")
        if "/" not in pair_upper:
            pair_upper = pair_upper + "/USD"
        target_pairs = [p for p in DYNAMIC_PAIRS if p["label"].upper() == pair_upper or
                        p["label"].upper().startswith(pair_upper.split("/")[0])]
        if not target_pairs:
            await ctx.send(f" Unknown pair: `{pair_arg}`. Available: {', '.join(p['label'] for p in DYNAMIC_PAIRS)}")
            return
    else:
        target_pairs = list(DYNAMIC_PAIRS)

    embed = discord.Embed(
        title=" RSI Dashboard  All Timeframes",
        description="RSI(14) across 5m / 15m / 1H / 4H for each pair",
        color=0x7B68EE
    )

    timeframe_map = [("5m", "5m"), ("15m", "15m"), ("1H", "1h"), ("4H", "4h")]

    for pair in target_pairs:
        pair_label = pair["label"]
        rsi_parts = []
        for tf_label, tf_key in timeframe_map:
            try:
                candles = await fetch_candles(pair, timeframe=tf_key)
                if candles and len(candles) >= 15:
                    closes = [c["close"] for c in candles]
                    rsi_val = rsi(closes, 14)
                    if rsi_val is not None:
                        icon = rsi_icon(rsi_val)
                        rsi_parts.append(f"{tf_label}={rsi_val:.1f}{icon}")
                    else:
                        rsi_parts.append(f"{tf_label}=")
                else:
                    rsi_parts.append(f"{tf_label}=")
            except Exception:
                rsi_parts.append(f"{tf_label}=err")

        embed.add_field(
            name=pair_label,
            value=" | ".join(rsi_parts),
            inline=False
        )

    embed.add_field(
        name="Legend",
        value=">70 =  Overbought  50-70 =  Bullish  30-50 =  Neutral  <30 =  Oversold",
        inline=False
    )
    embed.set_footer(text=f"Chartwise v10.0  RSI(14)  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !rsi {pair_arg or 'all'}  sent RSI dashboard to #{ctx.channel.name}")


@bot.command(name="scalp")
async def cmd_scalp(ctx, pair_arg: str = None):
    """Quick 5m-only scalp assessment for a pair. (v8.6 Feature 6)
    Shows 5m trend, RSI, BB position, nearest S/R, and a scalp direction recommendation.
    Usage: !scalp [pair]  e.g. !scalp BTC  or  !scalp SOL
    """
    # Resolve pair
    if pair_arg:
        pair_upper = pair_arg.upper().replace("-", "/")
        if "/" not in pair_upper:
            pair_upper = pair_upper + "/USD"
        target_pair = None
        for p in DYNAMIC_PAIRS:
            if p["label"].upper() == pair_upper or p["label"].upper().startswith(pair_upper.split("/")[0]):
                target_pair = p
                break
        if not target_pair:
            await ctx.send(f" Unknown pair: `{pair_arg}`. Available: {', '.join(p['label'] for p in DYNAMIC_PAIRS)}")
            return
    else:
        target_pair = DYNAMIC_PAIRS[0]

    pair_label = target_pair["label"]
    candles = await fetch_candles(target_pair, timeframe="5m")
    if not candles or len(candles) < 30:
        await ctx.send(f" Insufficient 5m data for {pair_label}.")
        return

    current_price = candles[-1]["close"]
    closes = [c["close"] for c in candles]

    # 1. 5m trend: last 3 candle direction
    last3 = candles[-3:]
    up_candles = sum(1 for c in last3 if c["close"] > c["open"])
    down_candles = sum(1 for c in last3 if c["close"] < c["open"])
    if up_candles == 3:
        trend_label = " Strong Up (3/3 bull)"
        trend_dir = "long"
    elif up_candles >= 2:
        trend_label = " Leaning Up (2/3 bull)"
        trend_dir = "long"
    elif down_candles == 3:
        trend_label = " Strong Down (3/3 bear)"
        trend_dir = "short"
    elif down_candles >= 2:
        trend_label = " Leaning Down (2/3 bear)"
        trend_dir = "short"
    else:
        trend_label = " Mixed (indecision)"
        trend_dir = "neutral"

    # 2. RSI on 5m
    rsi_val = rsi(closes, 14)
    if rsi_val is not None:
        if rsi_val >= 70:
            rsi_str = f"{rsi_val:.1f}  Overbought"
        elif rsi_val >= 50:
            rsi_str = f"{rsi_val:.1f}  Bullish zone"
        elif rsi_val >= 30:
            rsi_str = f"{rsi_val:.1f}  Neutral"
        else:
            rsi_str = f"{rsi_val:.1f}  Oversold"
    else:
        rsi_str = ""
        rsi_val = 50.0

    # 3. BB position on 5m
    bb_str = ""
    bb_pos = "mid"
    try:
        period = 20
        if len(closes) >= period:
            bb_closes = closes[-period:]
            bb_mean = sum(bb_closes) / len(bb_closes)
            variance = sum((x - bb_mean) ** 2 for x in bb_closes) / len(bb_closes)
            bb_stdev = variance ** 0.5
            bb_upper = bb_mean + 2 * bb_stdev
            bb_lower = bb_mean - 2 * bb_stdev
            pct_b = (current_price - bb_lower) / max(bb_upper - bb_lower, 1e-9) * 100
            if pct_b >= 80:
                bb_str = f"{pct_b:.0f}%  Near Upper Band  (overbought)"
                bb_pos = "upper"
            elif pct_b <= 20:
                bb_str = f"{pct_b:.0f}%  Near Lower Band  (oversold)"
                bb_pos = "lower"
            else:
                bb_str = f"{pct_b:.0f}%  Mid Band "
                bb_pos = "mid"
    except Exception:
        pass

    # 4. Nearest S/R zone
    sr_zones = detect_sr_zones(candles, lookback=30)
    if sr_zones:
        nearest = min(sr_zones, key=lambda z: abs(z["level"] - current_price))
        dist_pct = abs(nearest["level"] - current_price) / current_price * 100
        sr_str = f"{price_fmt(pair_label, nearest['level'])} ({nearest['type']}, {nearest['touches']} touches, {dist_pct:.2f}% away)"
    else:
        sr_str = "No clear S/R zones detected"

    # 5. Scalp recommendation
    long_signals = 0
    short_signals = 0
    if trend_dir == "long":
        long_signals += 2
    elif trend_dir == "short":
        short_signals += 2

    if rsi_val < 40:
        long_signals += 1
    elif rsi_val > 60:
        short_signals += 1

    if bb_pos == "lower":
        long_signals += 1
    elif bb_pos == "upper":
        short_signals += 1

    confidence = 0
    if long_signals >= 3:
        recommendation = " Scalp Long"
        confidence = long_signals
    elif short_signals >= 3:
        recommendation = " Scalp Short"
        confidence = short_signals
    elif long_signals >= 2:
        recommendation = " Possible Scalp Long (weak)"
        confidence = long_signals
    elif short_signals >= 2:
        recommendation = " Possible Scalp Short (weak)"
        confidence = short_signals
    else:
        recommendation = " No Clear Scalp Setup"
        confidence = 0

    conf_str = f"{confidence}/4 signals align" if confidence > 0 else "Mixed signals"

    embed = discord.Embed(
        title=f" Scalp Assessment  {pair_label}",
        description=f"Quick 5m-only analysis at {price_fmt(pair_label, current_price)}",
        color=0x00E676 if long_signals > short_signals else (0xFF5252 if short_signals > long_signals else 0x9E9E9E)
    )
    embed.add_field(name="Price", value=price_fmt(pair_label, current_price), inline=True)
    embed.add_field(name="5m Trend (last 3)", value=trend_label, inline=True)
    embed.add_field(name="RSI (5m)", value=rsi_str, inline=True)
    embed.add_field(name="BB Position (5m)", value=bb_str, inline=False)
    embed.add_field(name="Nearest S/R", value=sr_str, inline=False)
    embed.add_field(
        name=" Scalp Recommendation",
        value=f"**{recommendation}**\n{conf_str}",
        inline=False
    )
    embed.add_field(
        name=" Note",
        value="Scalp analysis uses 5m data only  no HTF filter. Use tight stops. Do not hold scalp positions through news events.",
        inline=False
    )
    embed.set_footer(text=f"Chartwise v10.0  5m Scalp  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !scalp {pair_label}  sent scalp assessment to #{ctx.channel.name}")


@bot.command(name="pivot")
async def cmd_pivot(ctx, pair_arg: str = None):
    """
    Calculate classic pivot points from the previous 4H candle for a given pair.
    Usage: !pivot [pair]   e.g. !pivot BTC or !pivot SOL
    Shows: Pivot, R1, R2, R3, S1, S2, S3 vs current price.
    """
    # Resolve pair
    pair = None
    if pair_arg:
        search = pair_arg.upper().replace("/", "").replace("-", "")
        for p in DYNAMIC_PAIRS:
            label_clean = p["label"].upper().replace("/", "").replace("-", "")
            if search in label_clean:
                pair = p
                break
    if pair is None:
        pair = DYNAMIC_PAIRS[0]  # default to BTC

    candles_4h = await fetch_candles(pair, timeframe="4h")
    if not candles_4h or len(candles_4h) < 2:
        await ctx.send(f" Could not fetch 4H candles for **{pair['label']}**.")
        return

    # Use previous completed 4H candle (index -2)
    prev = candles_4h[-2]
    H = prev["high"]
    L = prev["low"]
    C = prev["close"]

    P  = (H + L + C) / 3
    R1 = 2 * P - L
    R2 = P + (H - L)
    R3 = H + 2 * (P - L)
    S1 = 2 * P - H
    S2 = P - (H - L)
    S3 = L - 2 * (H - P)

    current_price = candles_4h[-1]["close"]

    def _label_vs_pivot(price: float, pivot: float) -> str:
        pct = (price - pivot) / pivot * 100
        if abs(pct) < 0.1:
            return " AT PIVOT"
        return f"{' +' if pct > 0 else ' '}{pct:.2f}%"

    embed = discord.Embed(
        title=f" {pair['label']}  Classic Pivot Points",
        description=(
            f"Calculated from previous 4H candle: H={price_fmt(pair['label'], H)}, "
            f"L={price_fmt(pair['label'], L)}, C={price_fmt(pair['label'], C)}"
        ),
        color=0x7B68EE,
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name="Current Price", value=f"**{price_fmt(pair['label'], current_price)}**", inline=False)
    embed.add_field(name=" Pivot (P)", value=f"{price_fmt(pair['label'], P)}  {_label_vs_pivot(current_price, P)}", inline=False)
    embed.add_field(name=" R3", value=price_fmt(pair["label"], R3), inline=True)
    embed.add_field(name=" R2", value=price_fmt(pair["label"], R2), inline=True)
    embed.add_field(name=" R1", value=price_fmt(pair["label"], R1), inline=True)
    embed.add_field(name=" S1", value=price_fmt(pair["label"], S1), inline=True)
    embed.add_field(name=" S2", value=price_fmt(pair["label"], S2), inline=True)
    embed.add_field(name=" S3", value=price_fmt(pair["label"], S3), inline=True)

    # Show nearest level
    all_levels = [("R3", R3), ("R2", R2), ("R1", R1), ("P", P), ("S1", S1), ("S2", S2), ("S3", S3)]
    nearest = min(all_levels, key=lambda x: abs(current_price - x[1]))
    embed.add_field(
        name=" Nearest Level",
        value=f"**{nearest[0]}** at {price_fmt(pair['label'], nearest[1])} ({abs(current_price - nearest[1]) / current_price * 100:.2f}% away)",
        inline=False
    )
    embed.set_footer(text=f"Chartwise v10.0  Classic pivot: (H+L+C)/3  Previous 4H candle  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !pivot {pair['label']}  sent to #{ctx.channel.name}")


@bot.command(name="account")
async def cmd_account(ctx, amount_arg: str = None):
    """
    Set or view the global account size used for position sizing.
    Usage:
      !account           show current account size
      !account 25000     set account to $25,000
    All position sizing calculations (in signal embeds and !rrhelper) will use this value.
    """
    global ACCOUNT_SIZE
    if amount_arg is None:
        embed = discord.Embed(
            title=" Account Size",
            description=(
                f"Current account size: **${ACCOUNT_SIZE:,.2f}**\n"
                f"Risk per trade (1%): **${ACCOUNT_SIZE * 0.01:,.2f}**\n\n"
                f"Use `!account 25000` to change it.\n"
                f"This setting persists until the bot restarts."
            ),
            color=0x00BCD4,
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_footer(text="Chartwise v10.0  !account [amount] to update")
        await ctx.send(embed=embed)
        return

    try:
        new_size = float(amount_arg.replace(",", "").replace("$", ""))
        if new_size < 100 or new_size > 10_000_000:
            await ctx.send(" Account size must be between $100 and $10,000,000.")
            return
        old_size = ACCOUNT_SIZE
        ACCOUNT_SIZE = new_size
        embed = discord.Embed(
            title=" Account Size Updated",
            description=(
                f"Account size changed from **${old_size:,.2f}**  **${ACCOUNT_SIZE:,.2f}**\n"
                f"Risk per trade (1%): **${ACCOUNT_SIZE * 0.01:,.2f}**\n\n"
                f"All future signal embeds and `!rrhelper` will use this value."
            ),
            color=0x00E676,
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_footer(text=f"Chartwise v10.0  Set by {ctx.author}")
        await ctx.send(embed=embed)
        print(f"[CMD] !account {new_size:,.0f}  set by {ctx.author}")
    except ValueError:
        await ctx.send(" Invalid amount. Example: `!account 25000`")


@bot.command(name="rrhelper")
async def cmd_rrhelper(ctx, entry_arg: str = None, sl_arg: str = None, t1_arg: str = None, t2_arg: str = None):
    """
    R:R calculator helper. Provide raw price levels.
    Usage: !rrhelper [entry] [sl] [t1] [t2]
    Example: !rrhelper 45000 44000 46500 48000
    Shows: SL distance, T1/T2 R:R, risk $, break-even, quality rating.
    """
    if not all([entry_arg, sl_arg, t1_arg, t2_arg]):
        await ctx.send(
            " Usage: `!rrhelper [entry] [sl] [t1] [t2]`\n"
            "Example: `!rrhelper 45000 44000 46500 48000`\n"
            "Assumes you're long when T1 > Entry, short when T1 < Entry."
        )
        return

    try:
        entry = float(entry_arg.replace(",", ""))
        sl    = float(sl_arg.replace(",", ""))
        t1    = float(t1_arg.replace(",", ""))
        t2    = float(t2_arg.replace(",", ""))
    except ValueError:
        await ctx.send(" All values must be numbers. Example: `!rrhelper 45000 44000 46500 48000`")
        return

    # Determine direction from T1 vs entry
    direction = "LONG" if t1 > entry else "SHORT"

    sl_dist = abs(entry - sl)
    t1_dist = abs(t1 - entry)
    t2_dist = abs(t2 - entry)

    if sl_dist == 0:
        await ctx.send(" SL cannot equal Entry price.")
        return

    rr_t1 = t1_dist / sl_dist
    rr_t2 = t2_dist / sl_dist

    sl_pct   = sl_dist / entry * 100
    risk_usd = ACCOUNT_SIZE * DEFAULT_RISK_PCT
    pos_usd  = risk_usd / (sl_pct / 100) if sl_pct > 0 else 0
    pos_units = risk_usd / sl_dist if sl_dist > 0 else 0

    # Break-even = entry (with half position closed at T1, BE is entry)
    # Actual break-even price at T1 on half = entry (net 0 if other half stopped at SL)
    breakeven_price = entry  # after closing half at T1, SL moves to entry

    # Quality rating based on T2 R:R
    if rr_t2 < 1.5:
        quality = " Poor"
        quality_note = "R:R below 1.5:1  not recommended"
    elif rr_t2 < 2.5:
        quality = " OK"
        quality_note = "Acceptable but look for better setups"
    elif rr_t2 < 3.5:
        quality = " Good"
        quality_note = "Solid setup  meets minimum criteria"
    else:
        quality = " Excellent"
        quality_note = "High R:R  take this setup"

    embed = discord.Embed(
        title=f" R:R Helper  {direction} Setup",
        description=f"Direction inferred from T1 vs Entry: **{direction}**",
        color=0x00E676 if direction == "LONG" else 0xFF5252,
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name="Entry", value=f"{entry:,.4f}", inline=True)
    embed.add_field(name="Stop Loss", value=f"{sl:,.4f}", inline=True)
    embed.add_field(name="SL Distance ($)", value=f"${sl_dist:,.4f} ({sl_pct:.2f}%)", inline=True)
    embed.add_field(name="T1", value=f"{t1:,.4f}", inline=True)
    embed.add_field(name="T2", value=f"{t2:,.4f}", inline=True)
    embed.add_field(name="", value="", inline=True)
    embed.add_field(name="R:R to T1", value=f"**1 : {rr_t1:.2f}**", inline=True)
    embed.add_field(name="R:R to T2", value=f"**1 : {rr_t2:.2f}**", inline=True)
    embed.add_field(name="", value="", inline=True)
    embed.add_field(name="Account Size", value=f"${ACCOUNT_SIZE:,.2f}", inline=True)
    embed.add_field(name="Risk (1%)", value=f"${risk_usd:,.2f}", inline=True)
    embed.add_field(name="Suggested Position", value=f"${pos_usd:,.0f} notional  ({pos_units:.4f} units)", inline=False)
    embed.add_field(name="Break-Even Price", value=f"{breakeven_price:,.4f} (move SL to entry after T1)", inline=False)
    embed.add_field(name="Quality Rating", value=f"{quality}\n*{quality_note}*", inline=False)
    embed.set_footer(text=f"Chartwise v10.0  !account [amount] to change account size  Not financial advice")
    await ctx.send(embed=embed)
    print(f"[CMD] !rrhelper entry={entry} sl={sl} t1={t1} t2={t2}  sent to #{ctx.channel.name}")


# 
# v9.0 Feature 3: !stats  Comprehensive performance dashboard
# 

@bot.command(name="stats")
async def cmd_stats(ctx):
    """
    Comprehensive statistics dashboard. Shows total signals, trades, win rate,
    PnL%, avg score, avg R:R, best/worst pair, session, streak, max drawdown,
    avg trade duration, and top pattern. (v9.0 Feature 3)
    """
    now_utc = datetime.now(timezone.utc)
    trades = list(TRADE_HISTORY)
    signals = list(SIGNAL_LOG)

    total_signals = len(signals)
    total_trades = len(trades)
    entry_rate = f"{total_trades / total_signals * 100:.1f}%" if total_signals > 0 else ""

    wins   = [t for t in trades if t.get("outcome") == "WIN"]
    losses = [t for t in trades if t.get("outcome") == "LOSS"]
    win_rate = f"{len(wins) / total_trades * 100:.1f}%" if total_trades > 0 else ""

    total_pnl = session_pnl.get("total_pnl_pct", 0.0)

    # Average score from signals
    scored = [s.get("score", 0) for s in signals if s.get("score") is not None]
    avg_score = f"{sum(scored)/len(scored):.1f}" if scored else ""

    # Average R:R achieved (from closed WIN trades that have exit_price, entry, sl)
    rr_vals = []
    for t in wins:
        try:
            _e = float(t.get("entry", 0) or 0)
            _sl = float(t.get("sl", 0) or 0)
            _ex = float(t.get("exit_price", 0) or 0)
            if _e > 0 and _sl > 0 and _ex > 0 and abs(_e - _sl) > 0:
                rr_vals.append(abs(_ex - _e) / abs(_e - _sl))
        except Exception:
            pass
    avg_rr = f"1 : {sum(rr_vals)/len(rr_vals):.2f}" if rr_vals else ""

    # Best session (by win rate)
    sess_wins: dict[str, int] = session_pnl.get("session_wins", {})
    sess_losses: dict[str, int] = session_pnl.get("session_losses", {})
    best_session = ""
    best_sess_wr = 0.0
    for _sess in set(list(sess_wins.keys()) + list(sess_losses.keys())):
        _sw = sess_wins.get(_sess, 0)
        _sl_s = sess_losses.get(_sess, 0)
        _tot = _sw + _sl_s
        if _tot >= 2:
            _wr = _sw / _tot
            if _wr > best_sess_wr:
                best_sess_wr = _wr
                best_session = f"{_sess} ({_wr*100:.0f}% WR)"

    # Best / worst pair by win rate
    pair_wins   = session_pnl.get("pair_wins", {})
    pair_losses = session_pnl.get("pair_losses", {})
    all_pair_keys = set(list(pair_wins.keys()) + list(pair_losses.keys()))
    best_pair = ""
    worst_pair = ""
    best_wr = -1.0
    worst_wr = 2.0
    for _p in all_pair_keys:
        _pw = pair_wins.get(_p, 0)
        _pl = pair_losses.get(_p, 0)
        _pt = _pw + _pl
        if _pt >= 2:
            _wr = _pw / _pt
            if _wr > best_wr:
                best_wr = _wr
                best_pair = f"{_p} ({_wr*100:.0f}% WR)"
            if _wr < worst_wr:
                worst_wr = _wr
                worst_pair = f"{_p} ({_wr*100:.0f}% WR)"

    # Current streak
    streak = 0
    streak_type = ""
    if trades:
        last_outcome = trades[-1].get("outcome")
        for _t in reversed(trades):
            if _t.get("outcome") == last_outcome:
                streak += 1
            else:
                break
        streak_icon = "" if last_outcome == "WIN" else ""
        streak_type = f"{streak_icon} {streak} {last_outcome}"

    # Max drawdown (worst consecutive loss PnL run)
    max_dd = 0.0
    running_dd = 0.0
    for _t in trades:
        if _t.get("outcome") == "LOSS":
            _pnl = _t.get("pnl_pct", -1.0) or -1.0
            running_dd += abs(_pnl)
            max_dd = max(max_dd, running_dd)
        else:
            running_dd = 0.0
    max_dd_str = f"-{max_dd:.2f}%" if max_dd > 0 else ""

    # Average trade duration (from opened_at to resolved  estimated from trade dicts)
    durations = []
    for _t in trades:
        _opened = _t.get("opened_at", "")
        _closed = _t.get("closed_at", "")
        if _opened and _closed:
            try:
                _o = datetime.fromisoformat(_opened)
                _c = datetime.fromisoformat(_closed)
                if _o.tzinfo is None: _o = _o.replace(tzinfo=timezone.utc)
                if _c.tzinfo is None: _c = _c.replace(tzinfo=timezone.utc)
                durations.append((_c - _o).total_seconds())
            except Exception:
                pass
    if durations:
        avg_dur_sec = sum(durations) / len(durations)
        avg_dur_str = f"{int(avg_dur_sec // 3600)}h {int((avg_dur_sec % 3600) // 60)}m"
    else:
        avg_dur_str = ""

    # Top pattern from pattern_performance
    top_pattern = ""
    best_pat_wr = -1.0
    for _pat, _pd in pattern_performance.items():
        _ptot = _pd["wins"] + _pd["losses"]
        if _ptot >= 2:
            _pwr = _pd["wins"] / _ptot
            if _pwr > best_pat_wr:
                best_pat_wr = _pwr
                top_pattern = f"{_pat} ({_pwr*100:.0f}% WR, {_ptot} trades)"

    embed = discord.Embed(
        title=" Chartwise Statistics Dashboard",
        description="Comprehensive performance overview  all-time session stats",
        color=0x7B68EE,
        timestamp=now_utc
    )
    embed.add_field(name=" Signals Fired", value=str(total_signals), inline=True)
    embed.add_field(name=" Trades Entered", value=str(total_trades), inline=True)
    embed.add_field(name=" Entry Rate", value=entry_rate, inline=True)
    embed.add_field(name=" Win Rate", value=win_rate, inline=True)
    embed.add_field(name=" Total PnL%", value=f"{total_pnl:+.2f}%", inline=True)
    embed.add_field(name=" Avg Score", value=avg_score, inline=True)
    embed.add_field(name=" Avg R:R Achieved", value=avg_rr, inline=True)
    embed.add_field(name=" Best Session", value=best_session, inline=True)
    embed.add_field(name=" Best Pair", value=best_pair, inline=True)
    embed.add_field(name=" Worst Pair", value=worst_pair, inline=True)
    embed.add_field(name=" Current Streak", value=streak_type, inline=True)
    embed.add_field(name=" Max Drawdown", value=max_dd_str, inline=True)
    embed.add_field(name=" Avg Trade Duration", value=avg_dur_str, inline=True)
    embed.add_field(name=" Top Pattern", value=top_pattern, inline=False)
    embed.add_field(
        name="Breakdown",
        value=f"Wins: {len(wins)}  Losses: {len(losses)}  T1 Hits: {session_pnl.get('t1_hits', 0)}",
        inline=False
    )
    embed.set_footer(text=f"Chartwise v10.0  Session stats reset on restart  {now_utc.strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !stats  sent dashboard to #{ctx.channel.name}")


# 
# v9.0 Feature 5: !sensitivity  Dynamic signal strictness control
# 

@bot.command(name="sensitivity")
async def cmd_sensitivity(ctx, level_arg: str = None):
    """
    Adjust signal sensitivity level (1=very strict to 5=very loose).
    Level 1: MIN_SCORE+3, very few signals  only the highest conviction setups.
    Level 2: MIN_SCORE+2, strict.
    Level 3: Default  standard MIN_SCORE and confidence thresholds.
    Level 4: MIN_SCORE-1, more signals allowed.
    Level 5: MIN_SCORE-2, maximum signals  catches more moves, more noise.
    No arg  show current level and description.
    Usage: !sensitivity [1-5]
    """
    global _sensitivity_level, MIN_SCORE, CONFIDENCE_HIGH, CONFIDENCE_MEDIUM
    DEFAULT_MIN_SCORE = 7  # v9.0 baseline

    level_descriptions = {
        1: " Very Strict  only elite setups (MIN_SCORE+3). Expect 1-2 signals per day max.",
        2: " Strict  high-conviction only (MIN_SCORE+2). Fewer but cleaner signals.",
        3: " Default  balanced quality/frequency. Standard MIN_SCORE thresholds.",
        4: " Loose  more signals, some lower-quality setups (MIN_SCORE-1).",
        5: " Very Loose  maximum signal frequency (MIN_SCORE-2). Expect more noise.",
    }

    if level_arg is None:
        embed = discord.Embed(
            title=" Signal Sensitivity Level",
            description=f"Current level: **{_sensitivity_level}**  {level_descriptions.get(_sensitivity_level, '?')}",
            color=0x9C27B0,
            timestamp=datetime.now(timezone.utc)
        )
        for _lv, _desc in level_descriptions.items():
            _marker = "  **current**" if _lv == _sensitivity_level else ""
            embed.add_field(name=f"Level {_lv}", value=f"{_desc}{_marker}", inline=False)
        embed.add_field(
            name="How to Change",
            value="`!sensitivity 1` through `!sensitivity 5`",
            inline=False
        )
        embed.set_footer(text=f"Chartwise v10.0  MIN_SCORE={MIN_SCORE}  CONF_HIGH={CONFIDENCE_HIGH}  CONF_MED={CONFIDENCE_MEDIUM}")
        await ctx.send(embed=embed)
        return

    try:
        level = int(level_arg.strip())
        if level < 1 or level > 5:
            await ctx.send(" Sensitivity must be between 1 and 5. Example: `!sensitivity 3`")
            return
    except ValueError:
        await ctx.send(" Invalid level. Use a number 15. Example: `!sensitivity 3`")
        return

    _sensitivity_level = level

    # Adjust thresholds relative to DEFAULT_MIN_SCORE
    offset = {1: 3, 2: 2, 3: 0, 4: -1, 5: -2}[level]
    MIN_SCORE         = DEFAULT_MIN_SCORE + offset
    CONFIDENCE_HIGH   = MIN_SCORE + 5
    CONFIDENCE_MEDIUM = MIN_SCORE + 2

    embed = discord.Embed(
        title=f" Sensitivity Set to Level {level}",
        description=level_descriptions[level],
        color=0x9C27B0,
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name="MIN_SCORE",         value=str(MIN_SCORE),         inline=True)
    embed.add_field(name="CONFIDENCE_HIGH",   value=str(CONFIDENCE_HIGH),   inline=True)
    embed.add_field(name="CONFIDENCE_MEDIUM", value=str(CONFIDENCE_MEDIUM), inline=True)
    embed.add_field(
        name="Effect",
        value=(
            "Signals below the new MIN_SCORE will be filtered out. "
            "CONFIDENCE_HIGH and CONFIDENCE_MEDIUM confidence tiers shift proportionally. "
            "Use `!setmin` to make fine-grained score adjustments, or `!sensitivity 3` to reset to default."
        ),
        inline=False
    )
    embed.set_footer(text=f"Chartwise v10.0  Set by {ctx.author}  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !sensitivity {level}  MIN_SCORE={MIN_SCORE}, CONF_HIGH={CONFIDENCE_HIGH}, CONF_MED={CONFIDENCE_MEDIUM}  by {ctx.author}")


@bot.command(name="charthelp", aliases=["commands", "cmds"])
async def cmd_help(ctx):
    """Show all Chartwise commands grouped by category. (v9.8)"""
    embed = discord.Embed(
        title=" Chartwise v10.0  Command Reference",
        description=(
            "High-probability SMC/ICT + EMA crypto signal bot for BTC/USD, SOL/USD, XRP/USD\n"
            "Commands grouped by category. Use `!scoretable` for the full scoring reference."
        ),
        color=0x7B68EE
    )

    #   Analysis 
    embed.add_field(
        name="** Analysis**",
        value=(
            "`!brief`  Morning brief: price, 24h%, RSI, BB, 4H bias, vol regime, trade status\n"
            "`!snapshot [pair]`  Full snapshot: price, trend, regime, recent signals\n"
            "`!tf [pair]`  Multi-TF: EMA stack, RSI, Ichimoku, MSS across 4 timeframes\n"
            "`!rsi [pair]`  RSI across 5m/15m/1H/4H (color-coded OS/OB)\n"
            "`!divergence`  RSI divergence dashboard: 5m/15m/1H/4H for all pairs\n"
            "`!momentum [pair]`  EMA slope, RSI zone, MACD across all TFs\n"
            "`!squeeze [pair]`  BB/KC squeeze status 5m4H; breakout timing alert\n"
            "`!bias [pair]`  4H candle bias: 10-candle bull/bear conviction\n"
            "`!levels [pair]`  SMC key levels: swing H/L, OBs, FVGs, VWAP, TWAP, Donchian, KC, today H/L\n"
            "`!vwap [pair]`  VWAP and price bias\n"
            "`!bb [pair]`  BB %B, width%, midband, upper/lower across 4 TFs\n"
            "`!kc [pair]`  Keltner Channel bands and squeeze indicator\n"
            "`!fvg [pair]`  ICT Fair Value Gaps: bullish/bearish zones, freshness\n"
            "`!ha [pair]`  Heikin Ashi trend: consecutive color streak per TF\n"
            "`!pivot [pair]`  Classic pivot points from prev 4H: P, R1/R2/R3, S1/S2/S3\n"
            "`!scalp [pair]`  5m scalp quick-read: trend/RSI/BB/S&R/recommendation\n"
            "`!pa [pair]`  Pure price action: candle colors, swing H/L, HH/HL or LH/LL\n"
            "`!targets [pair]`  Key targets above/below: S/R, Fib, Pivot R1/S1, OB\n"
            "`!heatmap`  Score heatmap: signal strength across pairs & timeframes\n"
            "`!news [pair]`  Auto narrative from price action + last signal\n"
            "`!compare [p1] [p2]`  Side-by-side RSI, BB, bias, last score comparison\n"
            "`!topgainer`  Rank pairs by 24h % change //\n"
            "`!volatility [pair]`   v9.6  ATR on all TFs, CI, BB width, squeeze, regime, hist vol\n"
            "`!ema [pair]`   v9.6  EMA ribbon (5/8/13/21) alignment across all 4 timeframes\n"
            "`!ote [pair]`   v9.7  ICT Optimal Trade Entry: OTE zone (61.879% Fib) on 15m/1H\n"
            "`!po3 [pair]`   v9.7  ICT Power of Three: accumulation/manipulation/distribution phase"
        ),
        inline=False
    )

    #   Signals & Trading 
    embed.add_field(
        name="** Signals & Trading**",
        value=(
            "`!scan`  Force immediate scan of all pairs\n"
            "`!status`   v9.4  Comprehensive bot health dashboard\n"
            "`!log [n]`  Last N signals fired this session (default 10)\n"
            "`!filtered [n]`  Last N signals blocked by score/circuit (debug)\n"
            "`!watchlist`  Near-miss signals (score MIN-1/2) waiting for price touch\n"
            "`!debug [pair]`  Full scoring breakdown: raw score, all reasons, indicators\n"
            "`!replay [n]`  Last N completed signals with full breakdown + outcome\n"
            "`!since [pair]`  Time since last signal per pair\n"
            "`!alerts [on|off]`  Toggle signal embeds (scanning continues regardless)\n"
            "`!calendar [week|month]`   v9.4  Trading activity calendar: signals + W/L per day\n"
            "`!copy [pair] [ratio]`   v9.4  Copy size calculator (e.g. !copy BTC 0.5 = 50% size)\n"
            "`!alert [pair] [price] [above|below]`   v9.4  Set price alert; `!alert list` / `!alert clear`\n"
            "`!close [pair]`   v9.4  Manually close an active trade (confirmation required)\n"
            "`!top [n]`   v9.4  Top N highest-scoring signals from session log\n"
            "`!correlation`   v9.4  BTC/SOL and BTC/XRP Pearson correlation (20 4H candles)\n"
            "`!add [pair] [entry] [sl] [t1] [t2] [long|short]`   v9.5  Manually add a trade to monitoring\n"
            "`!backtest2 [pair] [days=7]`   v9.5  Enhanced backtest: Sharpe, profit factor, consec W/L\n"
            "`!montecarlo [n_sims=1000]`   v9.5  Monte Carlo: median/P10/P90 after 50 trades + ruin prob\n"
            "`!optimize`   v9.6  Automated MIN_SCORE optimizer: tests 6-14, shows WR/EV table, recommends best\n"
            "`!opens`   v9.7  Last 7 daily opens + last 4 weekly opens per pair (NWOG/NDOG levels)"
        ),
        inline=False
    )

    #   Performance 
    embed.add_field(
        name="** Performance**",
        value=(
            "`!stats`  Full stats dashboard: signals, win rate, PnL%, avg score, drawdown\n"
            "`!pnl`  Session P&L: wins/losses by pair and engine\n"
            "`!winrate [n]`  Rolling win rate for last N trades with progress bar\n"
            "`!edge`  Statistical edge: Edge% and R-expectancy with significance check\n"
            "`!report [pair]`  Per-pair report: entry rate, win rate, PnL%, RR, streaks\n"
            "`!recap`  Last 7 days: trades, win rate, best/worst pair, top pattern\n"
            "`!streak`  Current W/L streak + all-time best/worst streaks\n"
            "`!drawdown`  Max drawdown: worst %, consecutive losses, recovery estimate\n"
            "`!patterns`  Pattern win rates: ICT/SMC, candle, momentum, MTF grouped\n"
            "`!hours`  Performance by UTC hour: signal count and win rate per hour\n"
            "`!heat [n]`  Signal frequency: count per pair per session over N days\n"
            "`!best [n]`  Top N winning trades by PnL%\n"
            "`!worst [n]`  Bottom N losing trades by PnL%\n"
            "`!backtest [n]`  Backtest score thresholds to find optimal MIN_SCORE\n"
            "`!backtest2 [pair] [days=7]`   v9.5  Enhanced backtest on real 15m candles\n"
            "`!montecarlo [n_sims=1000]`   v9.5  Monte Carlo simulation of next 50 trades\n"
            "`!winners`  Top confluence factors by win count & win rate\n"
            "`!export`  Export last 50 trades as CSV\n"
            "`!heatmap`  Score heatmap across pairs/timeframes"
        ),
        inline=False
    )

    #   Configuration 
    embed.add_field(
        name="** Configuration**",
        value=(
            "`!config`  Full bot config: MIN_SCORE, cooldowns, circuit breaker, pairs\n"
            "`!setmin [n]`  Set MIN_SCORE at runtime (515); affects which signals fire\n"
            "`!sensitivity [1-5]`  Signal strictness (1=strict, 3=default, 5=loose)\n"
            "`!setcooldown [min]`  Base signal cooldown between scans (default 90 min)\n"
            "`!pairs [add|remove|reset]`  Manage active trading pairs\n"
            "`!account [amount]`  Set global account size for position sizing\n"
            "`!risk [$ %]`  Personal account size and risk % per trade\n"
            "`!alerts [on|off]`  Toggle embed posting (scanning continues)\n"
            "`!pause [min]`  Pause scanning (indefinitely or N minutes)\n"
            "`!resume`  Resume after !pause\n"
            "`!circuit`  Circuit breaker status: consecutive loss tracking"
        ),
        inline=False
    )

    #   Utilities 
    embed.add_field(
        name="** Utilities**",
        value=(
            "`!scoretable`   v9.4  Full scoring reference: all factors and their point values\n"
            "`!rrhelper [entry] [sl] [t1] [t2]`  R:R calculator with quality rating\n"
            "`!avg [pair]`  DCA calculator: 30-day equal-buy plan with breakeven levels\n"
            "`!notes [add|list|clear] [text]`  In-memory notepad (up to 10 trade notes)\n"
            "`!timer [min]`  Personal countdown timer; `!timer cancel` to stop\n"
            "`!learn`  Adaptive learning: patterns penalized after repeated SL hits\n"
            "`!vwap [pair]`  VWAP price bias lookup"
        ),
        inline=False
    )

    embed.add_field(
        name=" Signal Engines",
        value=(
            "** Premium SMC/ICT**  liquidity sweep + BOS + OB + multi-TF confluence (max score ~28)\n"
            "** Standard EMA**  EMA9/21/50 crossover + volume + RSI + MSS (max score ~22)\n"
            f"Min score to fire: **{MIN_SCORE}** (A-grade only)  `!setmin` to change"
        ),
        inline=False
    )
    embed.add_field(
        name=" Pairs",
        value="BTC/USD  SOL/USD  XRP/USD  24/7 crypto scanning via Coinbase API",
        inline=False
    )
    embed.set_footer(text="Chartwise v10.0  !scoretable for scoring reference  Not financial advice")
    await ctx.send(embed=embed)


@bot.command(name="pause")
async def cmd_pause(ctx, minutes_arg: str = None):
    """
    Manually pause signal scanning.
    Usage: !pause [minutes]
    !pause        pause indefinitely (until !resume)
    !pause 60     pause for 60 minutes, then auto-resume
    """
    global _scan_manually_paused, _scan_paused_until
    _scan_manually_paused = True
    if minutes_arg is not None:
        try:
            mins = float(minutes_arg)
            if mins <= 0 or mins > 1440:
                await ctx.send(" Minutes must be between 1 and 1440 (24 hours).")
                return
            _scan_paused_until = time.time() + mins * 60
            resume_str = datetime.fromtimestamp(_scan_paused_until, tz=timezone.utc).strftime('%H:%M UTC')
            await ctx.send(f" Scanning paused for **{mins:.0f} minutes** (auto-resumes at {resume_str}). Use `!resume` to unpause early.")
        except ValueError:
            await ctx.send(" Invalid minutes. Usage: `!pause 60`")
            _scan_manually_paused = False
    else:
        _scan_paused_until = 0.0
        await ctx.send(" Scanning paused indefinitely. Use `!resume` to restart.")
    print(f"[CMD] !pause  scan paused by {ctx.author}")


@bot.command(name="resume")
async def cmd_resume(ctx):
    """Resume scanning after !pause."""
    global _scan_manually_paused, _scan_paused_until
    _scan_manually_paused = False
    _scan_paused_until = 0.0
    await ctx.send(" Scanning resumed.")
    print(f"[CMD] !resume  scan resumed by {ctx.author}")


@bot.command(name="setcooldown")
async def cmd_setcooldown(ctx, cooldown_minutes: str = None):
    """
    Adjust the base signal cooldown (how often bot can signal per pair).
    Default is 90 minutes. Lower = more signals, higher = fewer.
    Usage: !setcooldown [minutes]
    !setcooldown         show current cooldown
    !setcooldown 60      set to 60 minutes
    !setcooldown reset   reset to default (90 min)
    """
    global SIGNAL_COOLDOWN
    DEFAULT_COOLDOWN = 5400  # 90 min default

    if cooldown_minutes is None:
        current_mins = SIGNAL_COOLDOWN / 60
        await ctx.send(
            f" Current base cooldown: **{current_mins:.0f} minutes** per pair.\n"
            f"Use `!setcooldown 60` to change or `!setcooldown reset` to restore default (90 min)."
        )
        return

    if cooldown_minutes == "reset":
        SIGNAL_COOLDOWN = DEFAULT_COOLDOWN
        await ctx.send(f" Cooldown reset to default: **90 minutes**.")
        return

    try:
        mins = float(cooldown_minutes)
        if mins < 15 or mins > 720:
            await ctx.send(" Cooldown must be between 15 and 720 minutes.")
            return
        SIGNAL_COOLDOWN = int(mins * 60)
        await ctx.send(f" Base signal cooldown set to **{mins:.0f} minutes** per pair.")
        print(f"[CMD] !setcooldown {mins:.0f}m  by {ctx.author}")
    except ValueError:
        await ctx.send(" Invalid minutes. Example: `!setcooldown 60`")


@bot.command(name="risk")
async def cmd_risk(ctx, account_arg: str = None, risk_arg: str = None):
    """
    Set or view your personal risk settings for position sizing.
    Usage: !risk [account_size] [risk_%]
    Examples:
      !risk               show current settings
      !risk 5000          set account to $5,000 (risk% stays same)
      !risk 5000 2        set $5,000 account, 2% risk per trade
      !risk reset         reset to defaults ($10k, 1%)
    """
    user_id = ctx.author.id

    if account_arg == "reset":
        _user_risk_settings.pop(user_id, None)
        await ctx.send(" Risk settings reset to defaults: **$10,000 account, 1% risk per trade**.")
        return

    if account_arg is None:
        # Show current settings
        settings = _user_risk_settings.get(user_id, {})
        acct = settings.get("account", DEFAULT_ACCOUNT_SIZE)
        risk = settings.get("risk_pct", DEFAULT_RISK_PCT) * 100
        is_custom = user_id in _user_risk_settings
        embed = discord.Embed(
            title=" Your Risk Settings",
            description="Used for position sizing in signal embeds.",
            color=0x7B68EE
        )
        embed.add_field(name="Account Size", value=f"${acct:,.0f}", inline=True)
        embed.add_field(name="Risk Per Trade", value=f"{risk:.1f}%", inline=True)
        embed.add_field(name="Max Risk $", value=f"${acct * risk / 100:,.0f}", inline=True)
        embed.add_field(name="Status", value="Custom" if is_custom else "Default", inline=True)
        embed.add_field(
            name="How to Change",
            value="`!risk 5000`  $5k account\n`!risk 5000 2`  $5k + 2%\n`!risk reset`  defaults",
            inline=False
        )
        embed.set_footer(text="Chartwise v10.0  Settings are per-session (reset on bot restart)")
        await ctx.send(embed=embed)
        return

    # Parse account size
    try:
        account_val = float(account_arg.replace(",", "").replace("$", ""))
        if account_val < 100 or account_val > 10_000_000:
            await ctx.send(" Account size must be between $100 and $10,000,000.")
            return
    except ValueError:
        await ctx.send(" Invalid account size. Example: `!risk 5000` or `!risk 5000 2`")
        return

    # Parse risk %
    risk_pct_val = DEFAULT_RISK_PCT
    if risk_arg is not None:
        try:
            risk_pct_val = float(risk_arg.replace("%", "")) / 100
            if risk_pct_val < 0.001 or risk_pct_val > 0.10:
                await ctx.send(" Risk % must be between 0.1% and 10%.")
                return
        except ValueError:
            await ctx.send(" Invalid risk %. Example: `!risk 5000 2` for 2%.")
            return

    _user_risk_settings[user_id] = {"account": account_val, "risk_pct": risk_pct_val}
    max_risk = account_val * risk_pct_val
    await ctx.send(
        f" Risk settings updated: **${account_val:,.0f} account**, **{risk_pct_val * 100:.1f}% risk** per trade "
        f"(max ${max_risk:,.0f} at risk). Future signals will use these settings for position sizing."
    )


@bot.command(name="levels")
async def cmd_levels(ctx, pair_arg: str = None):
    """
    Show live SMC key levels for all pairs (or one pair).
    Displays: swing highs/lows, nearest OB, active FVG zones, equal H/L.
    Usage: !levels [BTC|SOL|XRP]
    """
    await ctx.trigger_typing()

    # Determine which pairs to show
    if pair_arg:
        pair_arg_upper = pair_arg.upper()
        # Match by ticker prefix
        target_pairs = [p for p in PAIRS if pair_arg_upper in p["label"].upper()]
        if not target_pairs:
            await ctx.send(f" Unknown pair `{pair_arg}`. Use BTC, SOL, or XRP.")
            return
    else:
        target_pairs = PAIRS

    for pair in target_pairs:
        pair_label = pair["label"]
        try:
            # Fetch 1H candles for structural levels (more meaningful than 5m for key levels)
            candles = await fetch_candles(pair, timeframe="1h")
            if not candles or len(candles) < 30:
                await ctx.send(f" {pair_label}: Insufficient data for level analysis.")
                continue

            current_price = candles[-1]["close"]
            atr = calc_atr(candles) or 0

            # Swing highs/lows (recent structure)
            swings = find_swing_highs_lows(candles, lookback=4)
            swing_highs = sorted([h["price"] for h in swings["highs"]], reverse=True)[:3]
            swing_lows  = sorted([l["price"] for l in swings["lows"]])[:3]

            # Order blocks
            ob_long  = find_order_block(candles, "long")
            ob_short = find_order_block(candles, "short")

            # FVG zones  find unmitigated FVGs near price (within 3 ATR)
            fvgs = find_fvg(candles)
            near_fvgs = []
            for fvg in fvgs[-20:]:  # Only recent FVGs
                fvg_mid = (fvg["top"] + fvg["bottom"]) / 2
                if atr > 0 and abs(fvg_mid - current_price) < atr * 3:
                    near_fvgs.append(fvg)

            # Equal highs/lows
            eql = find_equal_highs_lows(candles)

            # VWAP
            vwap_val = calc_vwap(candles)

            # Volume POC
            poc = calc_volume_poc(candles)

            # Build embed
            color = 0x7B68EE  # Purple for levels dashboard
            embed = discord.Embed(
                title=f" {pair_label}  Key Levels (1H Structure)",
                color=color
            )
            embed.add_field(
                name=" Current Price",
                value=f"**{price_fmt(pair_label, current_price)}**",
                inline=True
            )
            if atr > 0:
                embed.add_field(
                    name=" ATR (14)",
                    value=price_fmt(pair_label, atr),
                    inline=True
                )
            if vwap_val:
                bias = " Above" if current_price > vwap_val else " Below"
                embed.add_field(
                    name=" VWAP",
                    value=f"{price_fmt(pair_label, vwap_val)} ({bias})",
                    inline=True
                )

            # Swing levels
            if swing_highs:
                highs_str = "\n".join(
                    f"{' ' if abs(h - current_price) == min(abs(x - current_price) for x in swing_highs) else '  '}{price_fmt(pair_label, h)}"
                    for h in swing_highs
                )
                embed.add_field(name=" Swing Highs (Resistance)", value=highs_str, inline=True)
            if swing_lows:
                lows_str = "\n".join(
                    f"{' ' if abs(l - current_price) == min(abs(x - current_price) for x in swing_lows) else '  '}{price_fmt(pair_label, l)}"
                    for l in swing_lows
                )
                embed.add_field(name=" Swing Lows (Support)", value=lows_str, inline=True)

            # Order blocks
            ob_lines = []
            if ob_long:
                dist_pct = (current_price - ob_long["top"]) / current_price * 100
                ob_lines.append(f" Demand OB: {price_fmt(pair_label, ob_long['bottom'])}{price_fmt(pair_label, ob_long['top'])} ({dist_pct:+.2f}% from price)")
            if ob_short:
                dist_pct = (ob_short["bottom"] - current_price) / current_price * 100
                ob_lines.append(f" Supply OB: {price_fmt(pair_label, ob_short['bottom'])}{price_fmt(pair_label, ob_short['top'])} ({dist_pct:+.2f}% from price)")
            if ob_lines:
                embed.add_field(name=" Order Blocks", value="\n".join(ob_lines), inline=False)

            # FVG zones
            if near_fvgs:
                fvg_lines = []
                for fvg in near_fvgs[-4:]:
                    icon = "" if fvg["type"] == "bullish" else ""
                    fvg_mid = (fvg["top"] + fvg["bottom"]) / 2
                    dist_pct = (current_price - fvg_mid) / current_price * 100
                    fvg_lines.append(
                        f"{icon} {fvg['type'].title()} FVG: {price_fmt(pair_label, fvg['bottom'])}{price_fmt(pair_label, fvg['top'])} ({dist_pct:+.2f}%)"
                    )
                embed.add_field(name=" Fair Value Gaps (near price)", value="\n".join(fvg_lines), inline=False)
            else:
                embed.add_field(name=" Fair Value Gaps", value="No unmitigated FVGs within 3ATR", inline=False)

            # Equal H/L
            eq_lines = []
            if eql.get("equal_highs"):
                eq_lines.append(f" Equal Highs (liquidity pool): {price_fmt(pair_label, eql['equal_highs'][-1])}")
            if eql.get("equal_lows"):
                eq_lines.append(f" Equal Lows (liquidity pool): {price_fmt(pair_label, eql['equal_lows'][-1])}")
            if eq_lines:
                embed.add_field(name=" Liquidity Pools", value="\n".join(eq_lines), inline=False)

            # Volume POC
            if poc:
                dist_pct = (current_price - poc) / current_price * 100
                embed.add_field(
                    name=" Volume POC",
                    value=f"{price_fmt(pair_label, poc)} ({dist_pct:+.2f}% from price)  high-volume magnet",
                    inline=False
                )

            # v9.6: Donchian Channel levels
            dc = calc_donchian_channel(candles, period=20)
            if dc:
                dc_bias = " Above upper" if current_price > dc["upper"] else (" Below lower" if current_price < dc["lower"] else " Inside channel")
                embed.add_field(
                    name=" Donchian Channel (20-period)",
                    value=(
                        f"Upper: **{price_fmt(pair_label, dc['upper'])}**\n"
                        f"Middle: {price_fmt(pair_label, dc['middle'])}\n"
                        f"Lower: **{price_fmt(pair_label, dc['lower'])}**\n"
                        f"Status: {dc_bias}"
                    ),
                    inline=True
                )

            # v9.6: Keltner Channel levels
            kc = calc_keltner_channel(candles)
            if kc:
                kc_bias = " Above upper" if current_price > kc["upper"] else (" Below lower" if current_price < kc["lower"] else " Inside KC")
                embed.add_field(
                    name=" Keltner Channel",
                    value=(
                        f"Upper: **{price_fmt(pair_label, kc['upper'])}**\n"
                        f"Middle: {price_fmt(pair_label, kc['middle'])}\n"
                        f"Lower: **{price_fmt(pair_label, kc['lower'])}**\n"
                        f"Status: {kc_bias}"
                    ),
                    inline=True
                )

            # v9.6: TWAP
            twap_val = calc_twap(candles, lookback=20)
            if vwap_val and twap_val:
                vwap_bias = " Above" if current_price > vwap_val else " Below"
                twap_bias = " Above" if current_price > twap_val else " Below"
                embed.add_field(
                    name=" VWAP / TWAP",
                    value=(
                        f"VWAP: {price_fmt(pair_label, vwap_val)} ({vwap_bias})\n"
                        f"TWAP: {price_fmt(pair_label, twap_val)} ({twap_bias})"
                    ),
                    inline=True
                )

            # v9.6: Today's high and low from 5m candles (last 24h)
            try:
                candles_5m = await fetch_candles(pair, timeframe="5m")
                if candles_5m and len(candles_5m) >= 10:
                    now_ts = candles_5m[-1]["time"]
                    day_ago_ts = now_ts - 86400
                    day_candles = [c for c in candles_5m if c["time"] >= day_ago_ts]
                    if day_candles:
                        day_high = max(c["high"] for c in day_candles)
                        day_low  = min(c["low"]  for c in day_candles)
                        dh_pct = (day_high - current_price) / current_price * 100
                        dl_pct = (current_price - day_low) / current_price * 100
                        embed.add_field(
                            name=" Today's High / Low (24h, 5m)",
                            value=(
                                f"High: **{price_fmt(pair_label, day_high)}** ({dh_pct:+.2f}% from now)\n"
                                f"Low:  **{price_fmt(pair_label, day_low)}** ({dl_pct:+.2f}% below now)\n"
                                f"Range: {price_fmt(pair_label, day_high - day_low)} ({(day_high - day_low)/current_price*100:.2f}%)"
                            ),
                            inline=False
                        )
            except Exception:
                pass

            # v9.7 Feature 5: Show daily/weekly opens in !levels
            try:
                _opens_lines = []
                if pair_label in DAILY_OPENS and DAILY_OPENS[pair_label]:
                    last_d = list(DAILY_OPENS[pair_label])[-1]
                    dp = last_d["price"]
                    dp_pct = (current_price - dp) / dp * 100 if dp > 0 else 0
                    _opens_lines.append(f"Daily Open: **{price_fmt(pair_label, dp)}** ({dp_pct:+.2f}% from now, {last_d['time_utc']})")
                if pair_label in WEEKLY_OPENS and WEEKLY_OPENS[pair_label]:
                    last_w = list(WEEKLY_OPENS[pair_label])[-1]
                    wp = last_w["price"]
                    wp_pct = (current_price - wp) / wp * 100 if wp > 0 else 0
                    _opens_lines.append(f"Weekly Open: **{price_fmt(pair_label, wp)}** ({wp_pct:+.2f}% from now, {last_w['time_utc']})")
                if _opens_lines:
                    embed.add_field(
                        name=" Opening Prices (NWOG/NDOG)",
                        value="\n".join(_opens_lines),
                        inline=False
                    )
            except Exception:
                pass

            embed.set_footer(text=f"Chartwise v10.0  1H data + 5m intraday  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f" {pair_label}: Error fetching levels  {e}")
            print(f"[ERROR] cmd_levels {pair_label}: {e}")


@bot.command(name="volatility")
async def cmd_volatility(ctx, pair_arg: str = None):
    """
    v9.6 Feature 5: Comprehensive volatility breakdown for a pair.
    Shows: ATR on all 4 TFs ($ and %), Choppiness Index, BB width, Keltner/BB squeeze,
    volatility regime (High/Normal/Low), and historical volatility vs 30-day average.
    Usage: !volatility [BTC|SOL|XRP]
    """
    await ctx.trigger_typing()
    import math

    # Default to BTC if no pair given
    if pair_arg:
        pa = pair_arg.upper()
        target_pairs = [p for p in DYNAMIC_PAIRS if pa in p["label"].upper()]
        if not target_pairs:
            await ctx.send(f" Unknown pair `{pair_arg}`. Use BTC, SOL, or XRP.")
            return
        pair = target_pairs[0]
    else:
        pair = DYNAMIC_PAIRS[0]

    pair_label = pair["label"]

    try:
        tf_map = [("5m", "5m"), ("15m", "15m"), ("1H", "1h"), ("4H", "4h")]
        atr_lines = []
        bb_lines = []
        squeeze_status = []
        ci_lines = []

        for tf_label, tf_key in tf_map:
            try:
                c = await fetch_candles(pair, timeframe=tf_key)
                if not c or len(c) < 20:
                    atr_lines.append(f"`{tf_label}`: N/A")
                    continue
                price = c[-1]["close"]
                atr_val = calc_atr(c)
                if atr_val:
                    atr_pct = atr_val / price * 100
                    atr_lines.append(f"`{tf_label}`: {price_fmt(pair_label, atr_val)} ({atr_pct:.2f}%)")
                else:
                    atr_lines.append(f"`{tf_label}`: N/A")

                # BB width
                if len(c) >= 20:
                    bb_closes = [x["close"] for x in c[-20:]]
                    bb_mean = statistics.mean(bb_closes)
                    bb_std  = statistics.stdev(bb_closes)
                    bb_width = (4 * bb_std) / bb_mean * 100  # (upper-lower)/mean * 100
                    bb_lines.append(f"`{tf_label}`: {bb_width:.2f}% width")

                # Squeeze
                bb_sq = detect_bb_squeeze(c)
                kc_sq = detect_keltner_squeeze(c)
                if bb_sq and kc_sq:
                    sq_icon = " FULL SQUEEZE"
                elif bb_sq:
                    sq_icon = " BB squeeze"
                elif kc_sq:
                    sq_icon = " KC squeeze"
                else:
                    sq_icon = " No squeeze"
                squeeze_status.append(f"`{tf_label}`: {sq_icon}")

                # Choppiness Index
                ci = calc_choppiness_index(c, period=14)
                if ci is not None:
                    if ci > 61.8:
                        ci_icon = " Choppy"
                    elif ci < 38.2:
                        ci_icon = " Trending"
                    else:
                        ci_icon = " Neutral"
                    ci_lines.append(f"`{tf_label}`: {ci:.1f}  {ci_icon}")

            except Exception:
                atr_lines.append(f"`{tf_label}`: err")

        # Historical volatility (30-day) from 1H candles
        hist_vol_str = "N/A"
        regime_str = "N/A"
        try:
            c1h = await fetch_candles(pair, timeframe="1h", limit=200)
            if c1h and len(c1h) >= 30:
                # Calculate 30-day (720 1H candles) vs available
                sample = c1h[-min(720, len(c1h)):]
                closes_hv = [c["close"] for c in sample]
                if len(closes_hv) >= 2:
                    log_returns = [math.log(closes_hv[i] / closes_hv[i-1]) for i in range(1, len(closes_hv))]
                    if len(log_returns) >= 2:
                        hv_daily = statistics.stdev(log_returns) * math.sqrt(24) * 100  # annualized 24h
                        # Compare to recent 7-day (168 candles)
                        recent_sample = c1h[-min(168, len(c1h)):]
                        recent_closes = [c["close"] for c in recent_sample]
                        if len(recent_closes) >= 2:
                            recent_lr = [math.log(recent_closes[i] / recent_closes[i-1]) for i in range(1, len(recent_closes))]
                            if len(recent_lr) >= 2:
                                hv_recent = statistics.stdev(recent_lr) * math.sqrt(24) * 100
                                ratio = hv_recent / hv_daily if hv_daily > 0 else 1
                                if ratio > 1.3:
                                    regime_str = " HIGH Volatility  wider SL recommended, reduce size"
                                elif ratio < 0.7:
                                    regime_str = " LOW Volatility  tighter SL viable, watch for squeeze breakout"
                                else:
                                    regime_str = " NORMAL Volatility  standard sizing applies"
                                hist_vol_str = (
                                    f"30-day HV: {hv_daily:.2f}%/day\n"
                                    f"7-day HV: {hv_recent:.2f}%/day\n"
                                    f"Ratio: {ratio:.2f}"
                                )
        except Exception:
            pass

        # Verdict
        squeeze_count = sum(1 for s in squeeze_status if "FULL SQUEEZE" in s or "BB squeeze" in s)
        if squeeze_count >= 2:
            verdict = " **Multiple squeezes active  explosive move likely soon. Monitor closely.**"
        elif "NORMAL" in regime_str or "LOW" in regime_str:
            verdict = " **Good conditions to trade  volatility within normal range.**"
        elif "HIGH" in regime_str:
            verdict = " **High volatility  consider reducing position size or waiting for calmer conditions.**"
        else:
            verdict = " **Mixed signals  use caution and confirm with other tools.**"

        embed = discord.Embed(
            title=f" {pair_label}  Volatility Breakdown",
            description=verdict,
            color=0xFF8C00,
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name=" ATR (14)  All Timeframes", value="\n".join(atr_lines) or "N/A", inline=False)
        embed.add_field(name=" BB Width  All Timeframes", value="\n".join(bb_lines) or "N/A", inline=True)
        embed.add_field(name=" Squeeze Status", value="\n".join(squeeze_status) or "N/A", inline=True)
        embed.add_field(name=" Choppiness Index", value="\n".join(ci_lines) or "N/A", inline=False)
        embed.add_field(name=" Historical Volatility", value=hist_vol_str, inline=True)
        embed.add_field(name=" Volatility Regime", value=regime_str, inline=True)
        embed.set_footer(text=f"Chartwise v10.0  Volatility Report  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
        await ctx.send(embed=embed)
        print(f"[CMD] !volatility {pair_label}")
    except Exception as e:
        await ctx.send(f" Error fetching volatility data: {e}")
        print(f"[ERROR] cmd_volatility: {e}")


@bot.command(name="ema")
async def cmd_ema(ctx, pair_arg: str = None):
    """
    v9.6 Feature 6/7: EMA Ribbon status (EMA5/8/13/21) across all 4 timeframes.
    Shows alignment status, individual EMA values, and price vs each EMA.
    Usage: !ema [BTC|SOL|XRP]
    """
    await ctx.trigger_typing()

    if pair_arg:
        pa = pair_arg.upper()
        target_pairs = [p for p in DYNAMIC_PAIRS if pa in p["label"].upper()]
        if not target_pairs:
            await ctx.send(f" Unknown pair `{pair_arg}`. Use BTC, SOL, or XRP.")
            return
        pair = target_pairs[0]
    else:
        pair = DYNAMIC_PAIRS[0]

    pair_label = pair["label"]

    try:
        tf_map = [("5m", "5m"), ("15m", "15m"), ("1H", "1h"), ("4H", "4h")]
        embed = discord.Embed(
            title=f" {pair_label}  EMA Ribbon (5 / 8 / 13 / 21)",
            description="EMA ribbon alignment across all timeframes. Fully aligned = strongest trend signal.",
            color=0x00BCD4,
            timestamp=datetime.now(timezone.utc)
        )

        for tf_label, tf_key in tf_map:
            try:
                c = await fetch_candles(pair, timeframe=tf_key)
                if not c or len(c) < 21:
                    embed.add_field(name=f"**{tf_label}**", value="Insufficient data", inline=True)
                    continue

                price = c[-1]["close"]
                ribbon = calc_ema_ribbon(c)
                if ribbon is None:
                    embed.add_field(name=f"**{tf_label}**", value="N/A", inline=True)
                    continue

                e5, e8, e13, e21 = ribbon["ema5"], ribbon["ema8"], ribbon["ema13"], ribbon["ema21"]

                if ribbon["aligned_bull"]:
                    align_line = " **Fully aligned BULL**"
                elif ribbon["aligned_bear"]:
                    align_line = " **Fully aligned BEAR**"
                elif ribbon["partial_bull"] == 3:
                    align_line = " Partial bull (3/4)"
                elif ribbon["partial_bear"] == 3:
                    align_line = " Partial bear (3/4)"
                elif ribbon["partial_bull"] >= 2:
                    align_line = " Weak bull lean (2/4)"
                elif ribbon["partial_bear"] >= 2:
                    align_line = " Weak bear lean (2/4)"
                else:
                    align_line = " Chaotic / No trend"

                p_vs_e5  = "" if price > e5  else ""
                p_vs_e8  = "" if price > e8  else ""
                p_vs_e13 = "" if price > e13 else ""
                p_vs_e21 = "" if price > e21 else ""

                field_val = (
                    f"{align_line}\n"
                    f"{p_vs_e5} EMA5:  {price_fmt(pair_label, e5)}\n"
                    f"{p_vs_e8} EMA8:  {price_fmt(pair_label, e8)}\n"
                    f"{p_vs_e13} EMA13: {price_fmt(pair_label, e13)}\n"
                    f"{p_vs_e21} EMA21: {price_fmt(pair_label, e21)}\n"
                    f"Price: **{price_fmt(pair_label, price)}**"
                )
                embed.add_field(name=f"**{tf_label}**", value=field_val, inline=True)
            except Exception as _e:
                embed.add_field(name=f"**{tf_label}**", value=f"Error: {_e}", inline=True)

        embed.set_footer(text=f"Chartwise v10.0  EMA Ribbon  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
        await ctx.send(embed=embed)
        print(f"[CMD] !ema {pair_label}")
    except Exception as e:
        await ctx.send(f" Error computing EMA ribbon: {e}")
        print(f"[ERROR] cmd_ema: {e}")


@bot.command(name="optimize")
async def cmd_optimize(ctx):
    """
    v9.6 Feature 1: Automated MIN_SCORE threshold optimizer.
    Tests MIN_SCORE values 6-14 against SIGNAL_LOG + TRADE_HISTORY.
    For each: signal count, win rate, expected value (EV in R).
    Recommends the optimal threshold (highest EV).
    Usage: !optimize
    """
    await ctx.trigger_typing()

    all_signals = list(SIGNAL_LOG)
    if len(all_signals) < 5:
        await ctx.send(" Not enough signal history to optimize. Need at least 5 signals in SIGNAL_LOG.")
        return

    # Cross-reference SIGNAL_LOG with TRADE_HISTORY for outcomes
    # Build lookup: signal_id -> outcome from TRADE_HISTORY
    th_lookup: dict[str, str] = {}
    for t in TRADE_HISTORY:
        sig_id = t.get("sig_id") or t.get("id") or ""
        outcome = t.get("outcome", "PENDING")
        if sig_id:
            th_lookup[sig_id] = outcome

    # Also try disk signals for outcomes
    disk_signals = _read_signals()
    disk_lookup = {s["id"]: s for s in disk_signals if s.get("outcome") in ("WIN", "LOSS")}

    rows = []
    best_ev = -999.0
    best_threshold = MIN_SCORE

    for threshold in range(6, 15):
        # Signals that would pass this threshold
        passing = [s for s in all_signals if s.get("score", 0) >= threshold]
        n_passing = len(passing)
        if n_passing == 0:
            rows.append((threshold, 0, None, None))
            continue

        # Count wins/losses for passing signals
        wins = 0
        losses = 0
        for s in passing:
            sig_id = s.get("id") or s.get("sig_id") or ""
            # Check TRADE_HISTORY cross-ref
            outcome = th_lookup.get(sig_id)
            if outcome is None:
                # Try disk
                disk_s = disk_lookup.get(sig_id)
                if disk_s:
                    outcome = disk_s.get("outcome")
            if outcome == "WIN":
                wins += 1
            elif outcome == "LOSS":
                losses += 1

        resolved = wins + losses
        if resolved == 0:
            rows.append((threshold, n_passing, None, None))
            continue

        wr = wins / resolved
        # EV in R: win  +2R (avg), loss  -1R
        ev = wr * 2.0 - (1 - wr) * 1.0
        rows.append((threshold, n_passing, wr * 100, ev))
        if ev > best_ev:
            best_ev = ev
            best_threshold = threshold

    # Build embed
    embed = discord.Embed(
        title=" !optimize  MIN_SCORE Threshold Analysis",
        description=(
            f"Analyzed **{len(all_signals)}** signals from SIGNAL_LOG.\n"
            f"EV = expected R per trade (Win2R  Loss1R).\n"
            f"Recommendation: **MIN_SCORE = {best_threshold}** (highest EV)\n"
            f"Use `!setmin {best_threshold}` to apply."
        ),
        color=0x7C4DFF,
        timestamp=datetime.now(timezone.utc)
    )

    table_lines = []
    for threshold, n_pass, wr_pct, ev in rows:
        star = " " if threshold == best_threshold else ""
        if wr_pct is None:
            line = f"`MIN={threshold:2d}`: {n_pass:3d} signals  no resolved trades"
        else:
            wr_bar = "" * int(wr_pct / 10) + "" * (10 - int(wr_pct / 10))
            ev_sign = "+" if ev >= 0 else ""
            line = f"`MIN={threshold:2d}`: {n_pass:3d} signals  {wr_pct:.0f}% WR `{wr_bar}`  EV {ev_sign}{ev:.2f}R{star}"
        table_lines.append(line)

    embed.add_field(name=" Threshold Table", value="\n".join(table_lines), inline=False)
    embed.add_field(
        name=" Current Setting",
        value=f"MIN_SCORE = **{MIN_SCORE}**  To change: `!setmin [n]`",
        inline=False
    )
    embed.add_field(
        name=" Notes",
        value=(
            "Win rate based on SIGNAL_LOG  TRADE_HISTORY cross-reference.\n"
            "Higher threshold = fewer but higher-quality signals.\n"
            "EV > 0R is profitable in theory; target EV > +0.5R for robustness."
        ),
        inline=False
    )
    embed.set_footer(text=f"Chartwise v10.0  Optimizer  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !optimize  best threshold: MIN_SCORE={best_threshold} EV={best_ev:.2f}R")


@bot.command(name="divergence")
async def cmd_divergence(ctx):
    """
    Show RSI divergence status across all timeframes (5m, 15m, 1H, 4H) for all pairs.
    Helps spot multi-TF confluence before a signal fires.
    Usage: !divergence
    """
    tf_map = {"5m": "5m", "15m": "15m", "1H": "1h", "4H": "4h"}
    embed = discord.Embed(
        title=" RSI Divergence Dashboard",
        description="Live divergence scan across all pairs & timeframes.\n"
                    "`` = Bullish divergence  `` = Bearish divergence  `` = None",
        color=discord.Color.blurple(),
        timestamp=datetime.now(timezone.utc)
    )

    async def scan_tf_div(pair: dict, tf_label: str, tf_key: str) -> str:
        try:
            candles = await fetch_candles(pair, timeframe=tf_key)
            if not candles or len(candles) < 14:
                return ""
            bull = detect_rsi_divergence(candles, "long", lookback=8)
            bear = detect_rsi_divergence(candles, "short", lookback=8)
            parts = []
            if bull == 2:
                parts.append(" strong")
            elif bull == 1:
                parts.append(" weak")
            if bear == 2:
                parts.append(" strong")
            elif bear == 1:
                parts.append(" weak")
            return ", ".join(parts) if parts else ""
        except Exception:
            return "err"

    for pair in PAIRS:
        label = pair["label"]
        results = []
        for tf_label, tf_key in tf_map.items():
            result = await scan_tf_div(pair, tf_label, tf_key)
            results.append(f"`{tf_label}` {result}")
        embed.add_field(
            name=f"**{label}**",
            value="\n".join(results),
            inline=True
        )

    embed.set_footer(text="Chartwise v10.0  !scan to trigger manual scan  !help for all commands")
    await ctx.send(embed=embed)
    print(f"[CMD] !divergence  sent divergence dashboard to #{ctx.channel.name}")


@bot.command(name="tf")
async def cmd_tf(ctx, pair_arg: str = None):
    """
    Show multi-timeframe snapshot for a pair: EMA9/21/50, RSI, VWAP bias, and Ichimoku.
    Usage: !tf [BTC|SOL|XRP]   (defaults to BTC/USD)
    """
    # Resolve pair
    target_pair = None
    if pair_arg:
        pa = pair_arg.upper().strip()
        for p in PAIRS:
            if pa in p["label"] or pa == p["label"].split("/")[0]:
                target_pair = p
                break
    if target_pair is None:
        target_pair = PAIRS[0]  # default BTC

    label = target_pair["label"]
    tf_configs = [
        ("5m",  "5m"),
        ("15m", "15m"),
        ("1H",  "1h"),
        ("4H",  "4h"),
    ]

    embed = discord.Embed(
        title=f" Multi-TF Snapshot  {label}",
        description="EMA9/21/50  RSI  VWAP bias  Ichimoku  MSS",
        color=0x7289DA,
        timestamp=datetime.now(timezone.utc)
    )

    for tf_label, tf_key in tf_configs:
        try:
            candles = await fetch_candles(target_pair, timeframe=tf_key)
            if not candles or len(candles) < 52:
                embed.add_field(name=tf_label, value=" Insufficient data", inline=True)
                continue

            closes = [c["close"] for c in candles]
            highs  = [c["high"]  for c in candles]
            lows   = [c["low"]   for c in candles]

            # EMAs
            def ema(data: list[float], n: int) -> float:
                k = 2 / (n + 1)
                val = data[0]
                for x in data[1:]:
                    val = x * k + val * (1 - k)
                return val

            e9  = ema(closes, 9)
            e21 = ema(closes, 21)
            e50 = ema(closes, 50)
            price = closes[-1]

            # EMA stack
            if e9 > e21 > e50:
                ema_bias = " Bullish stack"
            elif e9 < e21 < e50:
                ema_bias = " Bearish stack"
            else:
                ema_bias = " Mixed"

            # RSI
            rsi_val = calc_rsi(closes, 14)
            if rsi_val is None:
                rsi_str = ""
            elif rsi_val > 70:
                rsi_str = f"{rsi_val:.0f}  OB"
            elif rsi_val < 30:
                rsi_str = f"{rsi_val:.0f}  OS"
            else:
                rsi_str = f"{rsi_val:.0f}"

            # Ichimoku
            ichi = ichimoku(candles)
            if ichi:
                if ichi["above_cloud"]:
                    ichi_str = " Above cloud "
                elif ichi["below_cloud"]:
                    ichi_str = " Below cloud "
                else:
                    ichi_str = " In cloud "
            else:
                ichi_str = ""

            # MSS
            mss_bull = detect_market_structure_shift(candles, "long")
            mss_bear = detect_market_structure_shift(candles, "short")
            if mss_bull:
                mss_str = " Bullish MSS"
            elif mss_bear:
                mss_str = " Bearish MSS"
            else:
                mss_str = ""

            # HTF candle bias (last 10 candles)
            recent10 = candles[-10:]
            bull_candles = sum(1 for c in recent10 if c["close"] > c["open"])
            bias_str = f"{bull_candles}/10 bull"

            value = (
                f"**EMA:** {ema_bias}\n"
                f"**RSI:** {rsi_str}\n"
                f"**Ichimoku:** {ichi_str}\n"
                f"**MSS:** {mss_str}\n"
                f"**Bias:** {bias_str}"
            )
            embed.add_field(name=f"**{tf_label}**", value=value, inline=True)

        except Exception as e:
            embed.add_field(name=tf_label, value=f"Error: {e}", inline=True)

    embed.set_footer(text=f"Chartwise v10.0  Use !divergence for RSI divergence map  !help for commands")
    await ctx.send(embed=embed)
    print(f"[CMD] !tf {label}  sent multi-TF snapshot to #{ctx.channel.name}")


@bot.command(name="bias")
async def cmd_bias(ctx, pair_arg: str = None):
    """
    4H candle bias across all pairs  shows directional conviction from 10 recent 4H candles.
    Useful for quick HTF bias check before entering trades.
    Usage: !bias           all pairs
           !bias BTC       BTC only
    """
    await ctx.trigger_typing()

    if pair_arg:
        pa = pair_arg.upper().strip()
        target_pairs = [p for p in PAIRS if pa in p["label"] or pa == p["label"].split("/")[0]]
        if not target_pairs:
            await ctx.send(f" Unknown pair `{pair_arg}`. Use BTC, SOL, or XRP.")
            return
    else:
        target_pairs = PAIRS

    embed = discord.Embed(
        title=" 4H Candle Bias Dashboard",
        description="10-candle directional conviction check across the 4H timeframe",
        color=0x7B68EE,
        timestamp=datetime.now(timezone.utc)
    )

    for pair in target_pairs:
        label = pair["label"]
        try:
            candles_4h = await fetch_candles(pair, timeframe="4h")
            if not candles_4h or len(candles_4h) < 10:
                embed.add_field(name=label, value=" Insufficient data", inline=True)
                continue

            bias = calc_htf_candle_bias(candles_4h, lookback=10)
            if bias is None:
                embed.add_field(name=label, value=" Calc error", inline=True)
                continue

            # Build bar: B = bull candle, b = bear candle
            recent_10 = candles_4h[-10:]
            bar = "".join("" if c["close"] > c["open"] else "" for c in recent_10)

            # Current price and 4H RSI
            closes_4h = [c["close"] for c in candles_4h]
            rsi_4h = rsi(closes_4h, 14)
            rsi_str = f"RSI: {rsi_4h:.1f}" if rsi_4h else ""

            field_val = (
                f"{bar}\n"
                f"{bias['bias_emoji']} **{bias['bias_label']}**  {bias['bull_count']}/10 bull, {bias['bear_count']}/10 bear\n"
                f"{rsi_str}"
            )
            embed.add_field(name=label, value=field_val, inline=False)
        except Exception as e:
            embed.add_field(name=label, value=f" Error: {str(e)[:40]}", inline=True)

    embed.add_field(
        name="Legend",
        value=" = bullish 4H candle   = bearish 4H candle\n7+/10 bull  Strong Bull bias  |  7+/10 bear  Strong Bear bias",
        inline=False
    )
    embed.set_footer(text="Chartwise v10.0  !squeeze for BB squeeze  !tf for multi-TF snapshot")
    await ctx.send(embed=embed)
    print(f"[CMD] !bias  sent 4H candle bias dashboard to #{ctx.channel.name}")


@bot.command(name="squeeze")
async def cmd_squeeze(ctx, pair_arg: str = None):
    """
    BB squeeze status across all 4 timeframes (5m, 15m, 1H, 4H).
    Squeeze = Bollinger Bands compressed below 1.5% width  breakout imminent.
    Usage: !squeeze [BTC|SOL|XRP]   (defaults to all pairs if no arg)
    """
    await ctx.trigger_typing()

    # Determine target pairs
    if pair_arg:
        pa = pair_arg.upper().strip()
        target_pairs = [p for p in PAIRS if pa in p["label"] or pa == p["label"].split("/")[0]]
        if not target_pairs:
            await ctx.send(f" Unknown pair `{pair_arg}`. Use BTC, SOL, or XRP.")
            return
    else:
        target_pairs = PAIRS

    timeframes = [("5m", 300), ("15m", 900), ("1h", 3600), ("4h", 14400)]

    embed = discord.Embed(
        title=" BB Squeeze Monitor",
        description="Bollinger Band squeeze across timeframes  compression signals breakout pending",
        color=0xFF6F00,
        timestamp=datetime.now(timezone.utc)
    )

    for pair in target_pairs:
        label = pair["label"]
        squeeze_rows = []
        for tf_label, gran in timeframes:
            try:
                candles = await fetch_candles(pair, timeframe=tf_label)
                if not candles or len(candles) < 25:
                    squeeze_rows.append(f"`{tf_label:3s}`   No data")
                    continue
                bb_info = calc_bb_width_trend(candles, period=20, lookback=5)
                squeezed = detect_bb_squeeze(candles, period=20, squeeze_pct=0.015)
                if bb_info is None:
                    squeeze_rows.append(f"`{tf_label:3s}`   Calc error")
                    continue
                width_pct = bb_info["width"] * 100
                if squeezed:
                    trend_tag = " SQUEEZE" if bb_info["contracting"] else " SQUEEZE"
                    row = f"`{tf_label:3s}` {trend_tag}  ({width_pct:.2f}% width)"
                elif bb_info["contracting"]:
                    row = f"`{tf_label:3s}`  Contracting  ({width_pct:.2f}%)"
                elif bb_info["expanding"]:
                    row = f"`{tf_label:3s}`  Expanding  ({width_pct:.2f}%)"
                else:
                    row = f"`{tf_label:3s}`  Normal  ({width_pct:.2f}%)"
                squeeze_rows.append(row)
            except Exception as e:
                squeeze_rows.append(f"`{tf_label:3s}`   Error: {str(e)[:30]}")

        embed.add_field(
            name=f"{'' if 'BTC' in label else '' if 'SOL' in label else ''} {label}",
            value="\n".join(squeeze_rows) or "",
            inline=True
        )

    embed.add_field(
        name="Legend",
        value=" **SQUEEZE** = bands compressed < 1.5% of price  breakout imminent\n Contracting = narrowing (pre-squeeze)\n Expanding = breakout underway\n Normal = no notable condition",
        inline=False
    )
    embed.set_footer(text="Chartwise v10.0  !snapshot for full pair analysis  !help for all commands")
    await ctx.send(embed=embed)
    print(f"[CMD] !squeeze  sent BB squeeze monitor to #{ctx.channel.name}")


@bot.command(name="snapshot")
async def cmd_snapshot(ctx, pair_arg: str = None):
    """
    Full market snapshot for a single pair: price, HTF trend, VWAP, RSI,
    active trade info, last signal, and cooldown status.
    Usage: !snapshot [BTC|SOL|XRP]   (defaults to BTC/USD)
    """
    target_pair = None
    if pair_arg:
        pa = pair_arg.upper().strip()
        for p in PAIRS:
            if pa in p["label"] or pa == p["label"].split("/")[0]:
                target_pair = p
                break
    if target_pair is None:
        target_pair = PAIRS[0]

    label = target_pair["label"]

    try:
        candles_5m  = await fetch_candles(target_pair, timeframe="5m")
        candles_4h  = await fetch_candles(target_pair, timeframe="4h")
    except Exception as e:
        await ctx.send(f" Failed to fetch data for {label}: {e}")
        return

    if not candles_5m or len(candles_5m) < 30:
        await ctx.send(f" Insufficient 5m candle data for {label}.")
        return

    price = candles_5m[-1]["close"]
    color = 0x00E676 if price > candles_5m[-2]["close"] else 0xFF5252

    embed = discord.Embed(
        title=f" Market Snapshot  {label}",
        color=color,
        timestamp=datetime.now(timezone.utc)
    )

    # --- Current price ---
    pchange = ((price - candles_5m[-2]["close"]) / candles_5m[-2]["close"]) * 100
    sign = "+" if pchange >= 0 else ""
    embed.add_field(
        name=" Price",
        value=f"**{price_fmt(label, price)}**  `{sign}{pchange:.2f}%` (5m)",
        inline=True
    )

    # --- Session ---
    embed.add_field(name=" Session", value=session_label(), inline=True)

    # --- 4H trend ---
    if candles_4h and len(candles_4h) >= 20:
        closes_4h = [c["close"] for c in candles_4h]
        bull_4h = sum(1 for c in candles_4h[-10:] if c["close"] > c["open"])
        htf_bias = " Bullish" if bull_4h >= 6 else (" Bearish" if bull_4h <= 4 else " Neutral")
        embed.add_field(name=" 4H Trend", value=f"{htf_bias}  ({bull_4h}/10 bull candles)", inline=False)
    else:
        embed.add_field(name=" 4H Trend", value="", inline=False)

    # --- VWAP + TWAP ---
    vwap = calc_vwap(candles_5m)
    if vwap:
        vwap_bias = "Above VWAP " if price > vwap else "Below VWAP "
        embed.add_field(name=" VWAP", value=f"{price_fmt(label, vwap)}  ({vwap_bias})", inline=True)
    # v9.5 Feature 2: TWAP display
    _snap_twap = calc_twap(candles_5m, lookback=20)
    if _snap_twap is not None:
        _snap_twap_bias = "Above TWAP  (bullish context)" if price > _snap_twap else "Below TWAP  (bearish context)"
        embed.add_field(name=" TWAP(20)", value=f"{price_fmt(label, _snap_twap)}  ({_snap_twap_bias})", inline=True)

    # --- RSI ---
    closes_5m = [c["close"] for c in candles_5m]
    rsi = calc_rsi(closes_5m, 14)
    if rsi is not None:
        rsi_tag = "  OB" if rsi > 70 else ("  OS" if rsi < 30 else "")
        embed.add_field(name=" RSI (5m)", value=f"{rsi:.1f}{rsi_tag}", inline=True)

    # --- Ichimoku ---
    ichi = ichimoku(candles_5m)
    if ichi:
        if ichi["above_cloud"]:
            ichi_str = " Above cloud "
        elif ichi["below_cloud"]:
            ichi_str = " Below cloud "
        else:
            ichi_str = " In cloud "
        embed.add_field(name="Ichimoku", value=ichi_str, inline=True)

    # --- Active trade ---
    trade = active_trades.get(label)
    if trade:
        entry = trade.get("entry", 0)
        sl    = trade.get("sl", 0)
        t1    = trade.get("t1", 0)
        t2    = trade.get("t2", 0)
        direction = trade.get("direction", "?")
        pnl_pct = ((price - entry) / entry * 100) if direction == "LONG" else ((entry - price) / entry * 100)
        pnl_sign = "+" if pnl_pct >= 0 else ""
        duration_str = format_trade_duration(trade["opened_at"]) if trade.get("opened_at") else "?"
        embed.add_field(
            name=f" Active {direction} Trade",
            value=(
                f"Entry: {price_fmt(label, entry)}   Open: {duration_str}\n"
                f"SL: {price_fmt(label, sl)}  |  T1: {price_fmt(label, t1)}  |  T2: {price_fmt(label, t2)}\n"
                f"Unrealised PnL: **{pnl_sign}{pnl_pct:.2f}%**"
            ),
            inline=False
        )
    else:
        embed.add_field(name="Trade Status", value="No active trade", inline=True)

    # --- Last trade result & cooldown ---
    last_result = last_trade_result.get(label, "")
    now = time.time()
    last_result_str = last_result
    if last_result == "WIN":
        last_result_str = " WIN"
    elif last_result == "LOSS":
        last_result_str = " LOSS"
    embed.add_field(name="Last Trade", value=last_result_str, inline=True)

    last_result_val = last_trade_result.get(label)
    if last_result_val == "LOSS":
        eff_cd = max(MIN_COOLDOWN, int(SIGNAL_COOLDOWN * 1.5))
    elif last_result_val == "WIN":
        eff_cd = max(MIN_COOLDOWN, int(SIGNAL_COOLDOWN * 0.8))
    else:
        eff_cd = SIGNAL_COOLDOWN
    cool_left = max(0, eff_cd - (now - last_signal_time.get(label, 0)))
    if cool_left > 0:
        cool_str = f" {int(cool_left / 60)}m remaining"
        if last_result_val == "LOSS":
            cool_str += " (+50% loss penalty)"
        elif last_result_val == "WIN":
            cool_str += " (-20% win bonus)"
    else:
        cool_str = " Ready to scan"
    embed.add_field(name="Cooldown", value=cool_str, inline=True)

    # --- Circuit breaker ---
    cb_str = f" OK ({_consecutive_losses} consecutive losses)"
    if _circuit_tripped_at > 0:
        resume_t = _circuit_tripped_at + CIRCUIT_BREAKER_COOLDOWN
        mins_left = max(0, int((resume_t - now) / 60))
        cb_str = f" TRIPPED  {mins_left}m until reset"
    embed.add_field(name="Circuit Breaker", value=cb_str, inline=False)

    # v8.8 Feature 4: market regime
    if candles_4h and len(candles_4h) >= 25:
        _snap_regime = detect_market_regime(candles_4h, lookback=20)
        _snap_regime_icon = "" if _snap_regime == "Trending Up" else ("" if _snap_regime == "Trending Down" else "")
        embed.add_field(name=" Market Regime", value=f"{_snap_regime_icon} {_snap_regime}", inline=True)

    embed.set_footer(text="Chartwise v10.0  !tf for multi-TF view  !divergence for RSI map  !squeeze for BB squeeze")
    await ctx.send(embed=embed)
    print(f"[CMD] !snapshot {label}  sent full snapshot to #{ctx.channel.name}")


@bot.command(name="alerts")
async def cmd_alerts(ctx, toggle: str = None):
    """
    Toggle whether the bot posts signal embeds to the channel.
    Scanning and signal logging continue regardless  only posting is affected.
    Usage:
      !alerts on    re-enable alert posting
      !alerts off   mute alert posting (signals still logged)
      !alerts       show current state
    """
    global ALERTS_ENABLED
    if toggle is None:
        state = " ON" if ALERTS_ENABLED else " OFF (muted)"
        await ctx.send(f" Alert posting is currently **{state}**. Use `!alerts on` or `!alerts off` to change.")
        return
    if toggle.lower() == "on":
        ALERTS_ENABLED = True
        await ctx.send(" Alert posting **enabled**  signals will be posted to this channel.")
        print(f"[CMD] !alerts on  by {ctx.author}")
    elif toggle.lower() == "off":
        ALERTS_ENABLED = False
        await ctx.send(" Alert posting **muted**  signals will be logged but NOT posted. Use `!alerts on` to re-enable.")
        print(f"[CMD] !alerts off  by {ctx.author}")
    else:
        await ctx.send(" Usage: `!alerts on` or `!alerts off`")


@bot.command(name="config")
async def cmd_config(ctx):
    """
    Show all current bot configuration in one embed.
    Displays MIN_SCORE, COOLDOWN_MINUTES, ALERTS_ENABLED, circuit breaker state,
    active pairs, scan interval, and confluence thresholds.
    Usage: !config
    """
    embed = discord.Embed(
        title=" Chartwise v10.0  Bot Configuration",
        description="Full runtime configuration at a glance.",
        color=0x7C4DFF,
        timestamp=datetime.now(timezone.utc)
    )

    # Signal thresholds
    embed.add_field(
        name=" Signal Thresholds",
        value=(
            f"**MIN_SCORE:** {MIN_SCORE}  (A-grade: {RATING_A}, B-grade: {RATING_B})\n"
            f"**High Confidence:** {CONFIDENCE_HIGH}\n"
            f"**Medium Confidence:** {CONFIDENCE_MEDIUM}"
        ),
        inline=False
    )

    # Cooldowns
    embed.add_field(
        name=" Cooldowns",
        value=(
            f"**Base cooldown:** {SIGNAL_COOLDOWN // 60} min\n"
            f"**Post-WIN cooldown:** {POST_WIN_COOLDOWN // 60} min\n"
            f"**Same-direction block:** {SAME_DIR_BLOCK // 60} min\n"
            f"**Min cooldown floor:** {MIN_COOLDOWN // 60} min"
        ),
        inline=True
    )

    # Scan & alerts
    _scan_mode = " Fast (BB expanding)" if current_scan_interval == 60 else (" Slow (BB squeeze)" if current_scan_interval == 180 else " Normal")
    embed.add_field(
        name=" Scan & Alerts",
        value=(
            f"**Scan interval:** {current_scan_interval}s {_scan_mode}\n"
            f"**Alerts posting:** {' ON' if ALERTS_ENABLED else ' OFF (muted)'}\n"
            f"**Scan paused:** {' YES' if _scan_manually_paused else ' NO'}"
        ),
        inline=True
    )

    # Circuit breaker
    cb_status = " TRIPPED" if _circuit_tripped_at > 0 else " OK"
    if _circuit_tripped_at > 0:
        remaining_cb = max(0, int((CIRCUIT_BREAKER_COOLDOWN - (time.time() - _circuit_tripped_at)) / 60))
        cb_detail = f"Trips at {CIRCUIT_BREAKER_LOSSES} consecutive losses  {remaining_cb}m remaining"
    else:
        cb_detail = f"Trips after {CIRCUIT_BREAKER_LOSSES} consecutive losses  {_consecutive_losses} current"
    embed.add_field(
        name=" Circuit Breaker",
        value=f"**Status:** {cb_status}\n{cb_detail}\n**Cooldown:** {CIRCUIT_BREAKER_COOLDOWN // 3600}h",
        inline=False
    )

    # Active pairs
    pairs_lines = []
    for p in PAIRS:
        in_trade = " IN TRADE" if p["label"] in active_trades else " Watching"
        pairs_lines.append(f"**{p['label']}**  {in_trade} (source: {p['source']})")
    embed.add_field(
        name=f" Active Pairs ({len(PAIRS)})",
        value="\n".join(pairs_lines),
        inline=False
    )

    # Adaptive learning
    sl_learned = len(_adaptive_sl_counts)
    win_learned = len(_adaptive_win_counts)
    embed.add_field(
        name=" Adaptive Learning",
        value=(
            f"**SL-penalised patterns:** {sl_learned}\n"
            f"**Win-reinforced patterns:** {win_learned}\n"
            f"**Penalty threshold:** {_ADAPTIVE_PENALTY_THRESHOLD} SL hits  -{_ADAPTIVE_PENALTY_SCORE} score"
        ),
        inline=True
    )

    # Session-based info
    embed.add_field(
        name=" Session Info",
        value=(
            f"**Current session:** {session_label()}\n"
            f"**Asia:** 00:0008:00 UTC\n"
            f"**London:** 08:0016:00 UTC\n"
            f"**New York:** 13:0021:00 UTC"
        ),
        inline=True
    )

    embed.set_footer(text=f"Chartwise v10.0  {datetime.now(timezone.utc).strftime('%H:%M UTC')}  Use !help for commands")
    await ctx.send(embed=embed)
    print(f"[CMD] !config  sent bot configuration to #{ctx.channel.name}")


@bot.command(name="compare")
async def cmd_compare(ctx, pair1_arg: str = None, pair2_arg: str = None):
    """
    Side-by-side comparison of two pairs: RSI, BB position, 4H bias, price change %, and last signal score.
    Usage: !compare BTC SOL   (compare BTC/USD vs SOL/USD)
    """
    if pair1_arg is None or pair2_arg is None:
        await ctx.send(" Usage: `!compare BTC SOL`  provide two pair tickers to compare.")
        return

    def resolve_pair(arg: str) -> dict | None:
        a = arg.upper().strip()
        for p in PAIRS:
            if a in p["label"] or a == p["label"].split("/")[0]:
                return p
        return None

    p1 = resolve_pair(pair1_arg)
    p2 = resolve_pair(pair2_arg)

    if p1 is None:
        await ctx.send(f" Unknown pair `{pair1_arg}`. Use BTC, SOL, or XRP.")
        return
    if p2 is None:
        await ctx.send(f" Unknown pair `{pair2_arg}`. Use BTC, SOL, or XRP.")
        return
    if p1["label"] == p2["label"]:
        await ctx.send(" Please choose two *different* pairs to compare.")
        return

    await ctx.trigger_typing()

    async def gather_pair_stats(pair: dict) -> dict:
        """Fetch key stats for one pair: RSI, BB position, 4H bias, price change, last signal score."""
        result = {"label": pair["label"], "error": None}
        try:
            candles_5m = await fetch_candles(pair, timeframe="5m")
            candles_4h = await fetch_candles(pair, timeframe="4h")

            if not candles_5m or len(candles_5m) < 30:
                result["error"] = "Insufficient 5m data"
                return result

            closes_5m = [c["close"] for c in candles_5m]
            price = closes_5m[-1]
            prev_price = closes_5m[-2] if len(closes_5m) >= 2 else price
            pchange = (price - prev_price) / prev_price * 100 if prev_price else 0.0

            # RSI (5m)
            rsi_val = rsi(closes_5m, 14)

            # Bollinger Band position (5m)
            bb_pos = None
            if len(closes_5m) >= 20:
                bb_mean = statistics.mean(closes_5m[-20:])
                bb_std = statistics.stdev(closes_5m[-20:])
                bb_upper = bb_mean + 2 * bb_std
                bb_lower = bb_mean - 2 * bb_std
                bb_range = bb_upper - bb_lower
                if bb_range > 0:
                    bb_pos = (price - bb_lower) / bb_range * 100  # 0% = lower band, 100% = upper band

            # 4H bias
            bias_label = ""
            bias_emoji = ""
            if candles_4h and len(candles_4h) >= 10:
                bias = calc_htf_candle_bias(candles_4h, lookback=10)
                if bias:
                    bias_label = bias["bias_label"]
                    bias_emoji = bias["bias_emoji"]

            # Last signal score from log
            signals = _read_signals()
            pair_sigs = [s for s in signals if s.get("pair") == pair["label"]]
            last_sig_score = pair_sigs[-1]["score"] if pair_sigs else None
            last_sig_dir = pair_sigs[-1]["direction"] if pair_sigs else None

            result.update({
                "price": price,
                "pchange": pchange,
                "rsi_val": rsi_val,
                "bb_pos": bb_pos,
                "bias_label": bias_label,
                "bias_emoji": bias_emoji,
                "last_sig_score": last_sig_score,
                "last_sig_dir": last_sig_dir,
                "in_trade": pair["label"] in active_trades,
            })
        except Exception as e:
            result["error"] = str(e)[:60]
        return result

    stats1, stats2 = await asyncio.gather(
        gather_pair_stats(p1),
        gather_pair_stats(p2),
    )

    embed = discord.Embed(
        title=f" Pair Comparison: {p1['label']} vs {p2['label']}",
        description="Side-by-side snapshot of key indicators for two pairs.",
        color=0x00CED1,
        timestamp=datetime.now(timezone.utc)
    )

    def fmt_col(stats: dict) -> str:
        if stats.get("error"):
            return f" Error: {stats['error']}"
        lines = []
        price = stats.get("price")
        pchange = stats.get("pchange", 0)
        sign = "+" if pchange >= 0 else ""
        lines.append(f"**Price:** {price_fmt(stats['label'], price)}  `{sign}{pchange:.2f}%`")
        rsi_val = stats.get("rsi_val")
        if rsi_val is not None:
            rsi_tag = "  OB" if rsi_val > 70 else ("  OS" if rsi_val < 30 else "")
            lines.append(f"**RSI (5m):** {rsi_val:.1f}{rsi_tag}")
        else:
            lines.append("**RSI:** ")
        bb_pos = stats.get("bb_pos")
        if bb_pos is not None:
            bb_tag = " (near upper)" if bb_pos > 80 else (" (near lower)" if bb_pos < 20 else "")
            lines.append(f"**BB Position:** {bb_pos:.0f}%{bb_tag}")
        else:
            lines.append("**BB Position:** ")
        lines.append(f"**4H Bias:** {stats.get('bias_emoji', '')} {stats.get('bias_label', '')}")
        last_score = stats.get("last_sig_score")
        last_dir = stats.get("last_sig_dir", "")
        if last_score is not None:
            lines.append(f"**Last Signal:** {last_dir}  Score {last_score}")
        else:
            lines.append("**Last Signal:** None logged")
        lines.append(f"**In Trade:** {' YES' if stats.get('in_trade') else ' No'}")
        return "\n".join(lines)

    embed.add_field(name=f" {p1['label']}", value=fmt_col(stats1), inline=True)
    embed.add_field(name=f" {p2['label']}", value=fmt_col(stats2), inline=True)

    embed.set_footer(text=f"Chartwise v10.0  {datetime.now(timezone.utc).strftime('%H:%M UTC')}  !snapshot [pair] for full view")
    await ctx.send(embed=embed)
    print(f"[CMD] !compare {p1['label']} {p2['label']}  sent comparison to #{ctx.channel.name}")


@bot.command(name="report")
async def cmd_report(ctx, pair_arg: str = None):
    """
    Per-pair performance report from signal log and trade history.
    Usage: !report [BTC|SOL|XRP]   (default: all pairs)
    Shows: total signals, entry rate, win rate, PnL%, RR, best/worst trade,
           most common direction, longest win streak.
    """
    signals = _read_signals()
    if not signals:
        await ctx.send(" No signal data yet  signals accumulate as trades close.")
        return

    # Determine which pairs to report on
    if pair_arg:
        pa = pair_arg.upper().strip()
        report_pairs = [p["label"] for p in PAIRS if pa in p["label"] or pa == p["label"].split("/")[0]]
        if not report_pairs:
            await ctx.send(f" Unknown pair `{pair_arg}`. Use BTC, SOL, or XRP.")
            return
    else:
        report_pairs = [p["label"] for p in PAIRS]

    embed = discord.Embed(
        title=" Per-Pair Performance Report",
        description="Signal statistics from the persistent signal log.",
        color=0x7B2FBE,
        timestamp=datetime.now(timezone.utc)
    )

    for pair_label in report_pairs:
        pair_sigs = [s for s in signals if s.get("pair") == pair_label]
        if not pair_sigs:
            embed.add_field(name=pair_label, value="No signals logged yet.", inline=False)
            continue

        total_signals = len(pair_sigs)
        closed = [s for s in pair_sigs if s.get("outcome") in ("WIN", "LOSS")]
        entered = len(closed)  # signals that resulted in a closed trade
        entry_rate = entered / total_signals * 100 if total_signals > 0 else 0.0

        wins = [s for s in closed if s.get("outcome") == "WIN"]
        losses = [s for s in closed if s.get("outcome") == "LOSS"]
        win_rate = len(wins) / max(entered, 1) * 100

        # PnL% using pnl_r (R multiples as proxy)  convert to % using entry/sl dist
        pnl_pcts = []
        for s in closed:
            entry_p = s.get("entry", 0)
            sl_p = s.get("sl", 0)
            pnl_r = s.get("pnl_r", 0) or 0
            if entry_p and sl_p and entry_p != sl_p:
                sl_dist_pct = abs(entry_p - sl_p) / entry_p * 100
                pnl_pcts.append(pnl_r * sl_dist_pct)

        total_pnl = sum(pnl_pcts) if pnl_pcts else 0.0
        avg_rr = statistics.mean([s.get("pnl_r", 0) or 0 for s in wins]) if wins else 0.0

        # Best and worst trade
        best_pnl = max(pnl_pcts) if pnl_pcts else 0.0
        worst_pnl = min(pnl_pcts) if pnl_pcts else 0.0

        # Most common direction
        long_count = sum(1 for s in pair_sigs if s.get("direction") == "LONG")
        short_count = total_signals - long_count
        dominant_dir = "LONG" if long_count >= short_count else "SHORT"

        # Longest win streak from closed trades (ordered by ts)
        sorted_closed = sorted(closed, key=lambda x: x.get("ts", 0))
        max_streak = 0
        cur_streak = 0
        for s in sorted_closed:
            if s.get("outcome") == "WIN":
                cur_streak += 1
                max_streak = max(max_streak, cur_streak)
            else:
                cur_streak = 0

        pnl_sign = "+" if total_pnl >= 0 else ""
        best_sign = "+" if best_pnl >= 0 else ""
        lines = [
            f"**Signals fired:** {total_signals}  |  **Entered:** {entered} ({entry_rate:.0f}%)",
            f"**Win Rate:** {win_rate:.1f}% ({len(wins)}W / {len(losses)}L)",
            f"**Net PnL:** {pnl_sign}{total_pnl:.2f}%  |  **Avg RR:** {avg_rr:.2f}R",
            f"**Best trade:** {best_sign}{best_pnl:.2f}%  |  **Worst:** {worst_pnl:.2f}%",
            f"**Direction:** {long_count}L / {short_count}S (dominant: {dominant_dir})",
            f"**Longest win streak:** {max_streak}",
        ]
        embed.add_field(name=f" {pair_label}", value="\n".join(lines), inline=False)

    embed.set_footer(text=f"Chartwise v10.0  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !report {pair_arg or 'all'}  sent to #{ctx.channel.name}")


# 
# v8.1 NEW COMMANDS
# 

@bot.command(name="streak")
async def cmd_streak(ctx):
    """
    Show the current win/loss streak from trade history, plus all-time best/worst streaks.
    Usage: !streak
    """
    if not TRADE_HISTORY:
        await ctx.send(" No closed trades yet this session  streaks will appear here as trades close.")
        return

    trades_list = list(TRADE_HISTORY)  # oldest  newest

    # Current streak (most recent trades)
    current_outcome = trades_list[-1]["outcome"]
    current_streak = 0
    for t in reversed(trades_list):
        if t["outcome"] == current_outcome:
            current_streak += 1
        else:
            break

    # All-time best win streak
    best_win_streak = 0
    cur_win = 0
    worst_loss_streak = 0
    cur_loss = 0
    for t in trades_list:
        if t["outcome"] == "WIN":
            cur_win += 1
            cur_loss = 0
            best_win_streak = max(best_win_streak, cur_win)
        else:
            cur_loss += 1
            cur_win = 0
            worst_loss_streak = max(worst_loss_streak, cur_loss)

    # Format current streak
    if current_outcome == "WIN":
        streak_str = f" {current_streak}W Streak"
        streak_color = 0x00E676
    else:
        streak_str = f" {current_streak}L Streak"
        streak_color = 0xFF5252

    embed = discord.Embed(
        title=" Trade Streak Tracker",
        description=f"**Current streak: {streak_str}**",
        color=streak_color,
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name="Current Streak", value=streak_str, inline=True)
    embed.add_field(name="Total Closed", value=str(len(trades_list)), inline=True)
    total_wins = sum(1 for t in trades_list if t["outcome"] == "WIN")
    total_losses = len(trades_list) - total_wins
    embed.add_field(name="Session W/L", value=f"{total_wins}W / {total_losses}L", inline=True)
    embed.add_field(name=" Best Win Streak (all-time)", value=f" {best_win_streak}W", inline=True)
    embed.add_field(name=" Worst Loss Streak (all-time)", value=f" {worst_loss_streak}L", inline=True)
    embed.add_field(name="", value="", inline=True)

    # Last 5 results as visual bar
    recent = trades_list[-5:]
    result_bar = " ".join("" if t["outcome"] == "WIN" else "" for t in recent)
    embed.add_field(name="Last 5 Results", value=result_bar or "", inline=False)

    embed.set_footer(text=f"Chartwise v10.0  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !streak  sent streak data to #{ctx.channel.name}")


@bot.command(name="export")
async def cmd_export(ctx):
    """
    Export last 50 trades as a CSV-formatted code block.
    Columns: Date, Pair, Direction, Entry, SL, T1, T2, Exit, PnL%, Session, Duration
    Usage: !export
    """
    if not TRADE_HISTORY:
        await ctx.send(" No closed trades yet this session  trade history appears here as trades close.")
        return

    trades_list = list(TRADE_HISTORY)[-50:]  # last 50

    # Build CSV
    header = "Date,Pair,Dir,Entry,SL,T1,T2,Exit,PnL%,Session,Duration,Outcome"
    rows = [header]
    for t in trades_list:
        date_str = t.get("closed_at", "")[:10]  # YYYY-MM-DD
        pair     = t.get("pair", "?")
        dir_str  = t.get("direction", "?")
        entry    = f"{t.get('entry', 0):.4f}"
        sl       = f"{t.get('sl', 0):.4f}"
        t1       = f"{t.get('t1', 0):.4f}" if t.get("t1") else ""
        t2       = f"{t.get('t2', 0):.4f}" if t.get("t2") else ""
        exit_p   = f"{t.get('exit', 0):.4f}"
        pnl      = f"{t.get('pnl_pct', 0):+.2f}%"
        sess     = t.get("session", "?")
        dur      = t.get("duration", "?")
        outcome  = t.get("outcome", "?")
        rows.append(f"{date_str},{pair},{dir_str},{entry},{sl},{t1},{t2},{exit_p},{pnl},{sess},{dur},{outcome}")

    csv_text = "\n".join(rows)
    # Discord has 2000 char limit per message; split if needed
    header_msg = f" **Chartwise v10.0  Trade Export** ({len(trades_list)} trades)\n"

    # Split into chunks of ~1800 chars to fit in code blocks
    chunk_size = 1700
    chunks = []
    lines = rows[:]
    chunk_lines = [lines[0]]  # always start with header
    for line in lines[1:]:
        tentative = "\n".join(chunk_lines + [line])
        if len(tentative) > chunk_size:
            chunks.append("\n".join(chunk_lines))
            chunk_lines = [lines[0], line]  # restart with header
        else:
            chunk_lines.append(line)
    if chunk_lines:
        chunks.append("\n".join(chunk_lines))

    await ctx.send(header_msg)
    for i, chunk in enumerate(chunks):
        part_str = f" (part {i+1}/{len(chunks)})" if len(chunks) > 1 else ""
        await ctx.send(f"```csv\n{chunk}\n```{part_str}")
    print(f"[CMD] !export  sent {len(trades_list)} trades to #{ctx.channel.name}")


@bot.command(name="filtered")
async def cmd_filtered(ctx, n_arg: str = "5"):
    """
    Show recent signals that were generated but filtered out (score below MIN_SCORE or circuit breaker).
    Useful for debugging why signals were rejected.
    Usage: !filtered [n]  (default 5, max 20)
    """
    try:
        n = max(1, min(20, int(n_arg)))
    except ValueError:
        n = 5

    if not FILTERED_LOG:
        await ctx.send(" No filtered signals logged yet  all generated signals have passed the score threshold.")
        return

    entries = list(FILTERED_LOG)[-n:][::-1]  # most recent first
    embed = discord.Embed(
        title=f" Last {len(entries)} Filtered Signal(s)",
        description=f"Signals generated but rejected before posting. MIN_SCORE={MIN_SCORE}",
        color=0xFF6B35,
        timestamp=datetime.now(timezone.utc)
    )
    now_dt = datetime.now(timezone.utc)
    for entry in entries:
        try:
            fired_dt = datetime.fromisoformat(entry["time"])
            if fired_dt.tzinfo is None:
                fired_dt = fired_dt.replace(tzinfo=timezone.utc)
            age_min = int((now_dt - fired_dt).total_seconds() // 60)
            age_str = f"{age_min}m ago" if age_min < 60 else f"{age_min // 60}h {age_min % 60}m ago"
        except Exception:
            age_str = "?"

        dir_icon = "" if entry.get("direction") == "LONG" else ("" if entry.get("direction") == "SHORT" else "")
        score = entry.get("score", 0)
        reason = entry.get("reason_filtered", "unknown")
        embed.add_field(
            name=f"{dir_icon} {entry.get('pair', '?')} {entry.get('direction', '?')}",
            value=(
                f"Score: **{score}** (need {MIN_SCORE})\n"
                f"Reason: `{reason}`\n"
                f"Time: {age_str}"
            ),
            inline=True
        )

    embed.set_footer(text=f"Chartwise v10.0  {FILTERED_LOG.maxlen} max entries  !setmin to lower threshold")
    await ctx.send(embed=embed)
    print(f"[CMD] !filtered {n}  sent filtered log to #{ctx.channel.name}")


@bot.command(name="momentum")
async def cmd_momentum(ctx, pair_arg: str = None):
    """
    Show momentum indicators across timeframes (5m/15m/1H/4H) for a pair.
    Usage: !momentum [pair]  (default: all pairs)
    Shows EMA20 slope direction, RSI level/zone, and MACD signal.
    """
    pairs_to_show = []
    if pair_arg:
        pair_arg_upper = pair_arg.upper().replace("-", "/")
        found = next((p for p in PAIRS if p["label"].upper() == pair_arg_upper or p["label"].split("/")[0] == pair_arg_upper), None)
        if not found:
            await ctx.send(f" Unknown pair `{pair_arg}`. Valid: {', '.join(p['label'] for p in PAIRS)}")
            return
        pairs_to_show = [found]
    else:
        pairs_to_show = PAIRS

    gran_map = {"5m": 300, "15m": 900, "1H": 3600, "4H": 14400}

    def rsi_zone(val: float) -> str:
        if val >= 70:
            return "Overbought"
        elif val >= 55:
            return "Bullish"
        elif val >= 45:
            return "Neutral"
        elif val >= 30:
            return "Bearish"
        return "Oversold"

    embed = discord.Embed(
        title=" Momentum Dashboard",
        description="EMA20 slope  RSI zone  MACD signal across timeframes",
        color=0x00CED1,
        timestamp=datetime.now(timezone.utc)
    )

    for pair in pairs_to_show:
        tf_rows = []
        for tf_label, gran in gran_map.items():
            try:
                candles = await fetch_coinbase_candles(pair["product_id"], granularity=gran, limit=80)
                if not candles or len(candles) < 30:
                    tf_rows.append(f"`{tf_label}`  no data")
                    continue
                closes = [c["close"] for c in candles]

                # EMA20 slope
                ema20_now  = ema(closes, 20)
                ema20_prev = ema(closes[:-3], 20) if len(closes) > 23 else None
                if ema20_now and ema20_prev:
                    if ema20_now > ema20_prev * 1.0002:
                        slope_sym = ""
                    elif ema20_now < ema20_prev * 0.9998:
                        slope_sym = ""
                    else:
                        slope_sym = ""
                else:
                    slope_sym = "?"

                # RSI
                rsi_val = rsi(closes, 14)
                if rsi_val is not None:
                    rsi_str = f"RSI {rsi_val:.0f} ({rsi_zone(rsi_val)})"
                else:
                    rsi_str = "RSI "

                # MACD
                macd_result = calc_macd(closes)
                if macd_result:
                    m = macd_result["macd"]
                    s = macd_result["signal_line"]
                    if m > s:
                        macd_str = "MACD "
                    elif m < s:
                        macd_str = "MACD "
                    else:
                        macd_str = "MACD ~"
                else:
                    macd_str = "MACD "

                tf_rows.append(f"`{tf_label}` EMA20 {slope_sym}  {rsi_str}  {macd_str}")
            except Exception as e:
                tf_rows.append(f"`{tf_label}`  error: {e}")

        embed.add_field(
            name=f" {pair['label']}",
            value="\n".join(tf_rows) if tf_rows else "No data",
            inline=False
        )

    embed.set_footer(text="Chartwise v10.0  EMA20 slope   RSI zone  MACD above/below signal")
    await ctx.send(embed=embed)
    print(f"[CMD] !momentum {pair_arg or 'all'}  sent to #{ctx.channel.name}")


@bot.command(name="topgainer")
async def cmd_topgainer(ctx):
    """
    Rank the 3 tracked pairs by 24h price change %.
    Fetches current price and oldest 4H candle available to compute 24h change.
    Usage: !topgainer
    """
    results = []
    for pair in PAIRS:
        try:
            # Use 4H candles  6 candles = 24h
            candles_4h = await fetch_coinbase_candles(pair["product_id"], granularity=14400, limit=7)
            if not candles_4h or len(candles_4h) < 2:
                results.append({"pair": pair["label"], "change_pct": None, "price": None})
                continue
            price_now  = candles_4h[-1]["close"]
            price_24h  = candles_4h[0]["open"]  # oldest candle open  24h ago
            if price_24h and price_24h > 0:
                change_pct = (price_now - price_24h) / price_24h * 100
            else:
                change_pct = 0.0
            results.append({"pair": pair["label"], "change_pct": change_pct, "price": price_now})
        except Exception as e:
            results.append({"pair": pair["label"], "change_pct": None, "price": None, "error": str(e)})

    # Sort by change_pct descending (None goes last)
    results.sort(key=lambda x: x.get("change_pct") or -999, reverse=True)

    embed = discord.Embed(
        title=" Top Gainers  24h % Change",
        description="Ranked by 24-hour price change (Coinbase 4H candles)",
        color=0x00FF7F,
        timestamp=datetime.now(timezone.utc)
    )

    rank_emojis = ["", "", ""]
    for i, r in enumerate(results):
        emoji = rank_emojis[i] if i < 3 else f"#{i+1}"
        if r.get("change_pct") is None:
            embed.add_field(
                name=f"{emoji} {r['pair']}",
                value=" No data",
                inline=False
            )
            continue
        chg = r["change_pct"]
        sign = "+" if chg >= 0 else ""
        color_emoji = "" if chg >= 0 else ""
        price_str = price_fmt(r["pair"], r["price"]) if r.get("price") else ""
        embed.add_field(
            name=f"{emoji} {r['pair']}",
            value=f"{color_emoji} **{sign}{chg:.2f}%**  Price: {price_str}",
            inline=False
        )

    embed.set_footer(text="Chartwise v10.0  24h change via Coinbase 4H OHLCV")
    await ctx.send(embed=embed)
    print(f"[CMD] !topgainer  sent to #{ctx.channel.name}")


@bot.command(name="drawdown")
async def cmd_drawdown(ctx):
    """
    Show max drawdown stats from trade history.
    Max drawdown = worst peak-to-trough sequence of consecutive losses.
    Usage: !drawdown
    """
    trades_list = list(TRADE_HISTORY)
    closed = [t for t in trades_list if t.get("outcome") in ("WIN", "LOSS")]

    if not closed:
        await ctx.send(" No closed trades yet  drawdown stats unavailable.")
        return

    # Build cumulative PnL series (each trade: +pnl_pct on WIN, -pnl_pct on LOSS)
    cum_pnl = 0.0
    peak    = 0.0
    max_dd  = 0.0  # worst drawdown % (negative means loss from peak)
    max_dd_start = 0
    max_dd_end   = 0
    equity_series = []

    for t in closed:
        outcome = t.get("outcome", "")
        pnl = t.get("pnl_pct", 0.0) or 0.0
        if outcome == "WIN":
            cum_pnl += abs(pnl)
        else:
            cum_pnl -= abs(pnl) if abs(pnl) > 0 else 1.0
        equity_series.append(cum_pnl)
        if cum_pnl > peak:
            peak = cum_pnl
        dd = cum_pnl - peak
        if dd < max_dd:
            max_dd = dd

    # Max consecutive losses
    max_consec_loss = 0
    cur_loss = 0
    for t in closed:
        if t.get("outcome") == "LOSS":
            cur_loss += 1
            max_consec_loss = max(max_consec_loss, cur_loss)
        else:
            cur_loss = 0

    # Recovery: find the longest sequence from the drawdown bottom back to a new peak
    # Simplified: count how many sequential wins would be needed to recover max_dd
    # using the average win pnl_pct
    wins_list = [abs(t.get("pnl_pct", 0) or 0) for t in closed if t.get("outcome") == "WIN"]
    avg_win_pct = statistics.mean(wins_list) if wins_list else 1.0
    recovery_trades = int(abs(max_dd) / avg_win_pct) + 1 if avg_win_pct > 0 else ""

    total_trades = len(closed)
    n_wins  = sum(1 for t in closed if t.get("outcome") == "WIN")
    n_losses = total_trades - n_wins
    win_rate = n_wins / total_trades * 100 if total_trades > 0 else 0.0

    embed = discord.Embed(
        title=" Drawdown Analysis",
        description=f"Based on last **{total_trades}** closed trades (WIN/LOSS)",
        color=0xFF4500,
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(
        name="Max Drawdown",
        value=f"**{max_dd:.2f}%** from peak",
        inline=True
    )
    embed.add_field(
        name="Max Consecutive Losses",
        value=f"**{max_consec_loss}** in a row",
        inline=True
    )
    embed.add_field(
        name="Recovery Trades (est.)",
        value=f"**{recovery_trades}** wins at avg {avg_win_pct:.2f}% each",
        inline=True
    )
    embed.add_field(
        name="Overall Stats",
        value=(
            f"Trades: {total_trades} | Wins: {n_wins} | Losses: {n_losses}\n"
            f"Win Rate: {win_rate:.1f}%"
        ),
        inline=False
    )

    embed.set_footer(text="Chartwise v10.0  Drawdown from cumulative PnL equity curve")
    await ctx.send(embed=embed)
    print(f"[CMD] !drawdown  sent to #{ctx.channel.name}")


@bot.command(name="replay")
async def cmd_replay(ctx, n_arg: str = "5"):
    """
    Show last N completed signals with full breakdown and outcome (v8.8 Feature 1).
    Reads from SIGNAL_LOG (in-memory) and persistent signal file.
    Usage: !replay [n]   default 5, max 15
    """
    try:
        n = max(1, min(15, int(n_arg)))
    except ValueError:
        n = 5

    # Combine persistent + in-memory signals (newest last)
    persistent = _read_signals() or []
    mem_entries = list(SIGNAL_LOG)
    all_entries = persistent + mem_entries

    if not all_entries:
        await ctx.send(" No signals logged yet  run `!scan` to generate signals.")
        return

    # Deduplicate by time+pair, keep latest N
    seen = set()
    unique = []
    for e in reversed(all_entries):
        key = (e.get("pair"), e.get("time"))
        if key not in seen:
            seen.add(key)
            unique.append(e)
        if len(unique) >= n:
            break

    # Build trade history lookup: pair+time  outcome
    trade_lookup: dict[str, str] = {}
    for t in TRADE_HISTORY:
        _tpair = t.get("pair", "")
        _ttime = t.get("opened_at", "")
        _out   = t.get("outcome", "PENDING")
        trade_lookup[f"{_tpair}|{_ttime}"] = _out

    embed = discord.Embed(
        title=f" Signal Replay  Last {len(unique)} Signals",
        description="Pair  Direction  Score  Entry  SL  T1  T2  Outcome  Top reasons",
        color=0x9B59B6,
        timestamp=datetime.now(timezone.utc)
    )

    for sig in unique:
        pair_l  = sig.get("pair", "?")
        direc   = sig.get("direction", "?").upper()
        score   = sig.get("score", "?")
        entry   = sig.get("entry")
        sl      = sig.get("sl")
        t1      = sig.get("t1")
        t2      = sig.get("t2")
        reasons = sig.get("reasons", [])
        sig_time = sig.get("time", "")

        # Determine outcome
        outcome = " Pending"
        for t in TRADE_HISTORY:
            if t.get("pair") == pair_l:
                t_open = t.get("opened_at", "")
                if t_open and sig_time and abs(
                    (datetime.fromisoformat(t_open.replace("Z", "+00:00") if t_open.endswith("Z") else t_open) -
                     datetime.fromisoformat(sig_time.replace("Z", "+00:00") if sig_time.endswith("Z") else sig_time)
                    ).total_seconds()
                ) < 300:  # within 5 minutes
                    t_out = t.get("outcome", "")
                    if t_out == "WIN":
                        outcome = " Won"
                    elif t_out == "LOSS":
                        outcome = " Lost"
                    break

        # Format prices
        def _fmt(v):
            if v is None:
                return ""
            try:
                fv = float(v)
                if fv >= 1000:
                    return f"${fv:,.2f}"
                elif fv >= 1:
                    return f"${fv:.4f}"
                else:
                    return f"${fv:.6f}"
            except Exception:
                return str(v)

        dir_icon = "" if direc == "LONG" else ("" if direc == "SHORT" else "")
        top_reasons = reasons[:3]
        reasons_str = "\n".join(f" {r}" for r in top_reasons) if top_reasons else ""

        field_val = (
            f"{dir_icon} **{direc}**  Score: **{score}**\n"
            f"Entry: {_fmt(entry)}  SL: {_fmt(sl)}\n"
            f"T1: {_fmt(t1)}  T2: {_fmt(t2)}\n"
            f"Outcome: {outcome}\n"
            f"{reasons_str}"
        )
        embed.add_field(name=f" {pair_l}", value=field_val, inline=False)

    embed.set_footer(text=f"Chartwise v10.0  !replay [n] to see more (max 15)  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !replay {n}  sent to #{ctx.channel.name}")


@bot.command(name="bb")
async def cmd_bb(ctx, pair_arg: str = None):
    """
    Bollinger Band deep analysis across 4 timeframes (v8.8 Feature 3).
    Shows BB %B, band width %, midband, upper/lower prices, and position vs midband.
    Usage: !bb [pair]  e.g. !bb BTC  or  !bb SOL
    """
    # Resolve pair
    target_pair = None
    if pair_arg:
        pa = pair_arg.upper().strip()
        for p in PAIRS:
            if pa in p["label"] or pa == p["label"].split("/")[0]:
                target_pair = p
                break
    if target_pair is None:
        target_pair = PAIRS[0]

    label = target_pair["label"]
    await ctx.trigger_typing()

    timeframes = [
        ("5m",  300,   "5m"),
        ("15m", 900,   "15m"),
        ("1H",  3600,  "1H"),
        ("4H",  14400, "4H"),
    ]

    embed = discord.Embed(
        title=f" Bollinger Band Analysis  {label}",
        description="BB %B  Width%  Midband  Upper  Lower  Position across 4 timeframes",
        color=0x00BCD4,
        timestamp=datetime.now(timezone.utc)
    )

    for tf_label, gran, _ in timeframes:
        try:
            candles = await fetch_coinbase_candles(target_pair["product_id"], granularity=gran, limit=50)
            if not candles or len(candles) < 22:
                embed.add_field(name=f" {tf_label}", value=" Insufficient data", inline=True)
                continue

            closes = [c["close"] for c in candles]
            price  = closes[-1]

            # 20-period BB
            window = closes[-20:]
            bb_mean  = statistics.mean(window)
            bb_std   = statistics.stdev(window)
            bb_upper = bb_mean + 2 * bb_std
            bb_lower = bb_mean - 2 * bb_std
            bb_range = bb_upper - bb_lower

            # BB %B: where price is within the band (0 = lower, 1 = upper)
            bb_pct_b = (price - bb_lower) / bb_range if bb_range > 0 else 0.5

            # Band width %: (upper - lower) / midband * 100
            bb_width_pct = (bb_range / bb_mean * 100) if bb_mean > 0 else 0.0

            # Position relative to midband
            if price > bb_upper:
                pos_str = " Above upper band"
            elif price < bb_lower:
                pos_str = " Below lower band"
            elif price > bb_mean * 1.002:
                pos_str = " Above midband"
            elif price < bb_mean * 0.998:
                pos_str = " Below midband"
            else:
                pos_str = " At midband"

            def _fmt_p(v):
                if v >= 1000:
                    return f"${v:,.2f}"
                elif v >= 1:
                    return f"${v:.4f}"
                else:
                    return f"${v:.6f}"

            field_val = (
                f"**%B:** {bb_pct_b:.2f}  **Width:** {bb_width_pct:.2f}%\n"
                f"**Upper:** {_fmt_p(bb_upper)}  **Lower:** {_fmt_p(bb_lower)}\n"
                f"**Midband:** {_fmt_p(bb_mean)}\n"
                f"{pos_str}"
            )
            embed.add_field(name=f" {tf_label}", value=field_val, inline=True)

        except Exception as e:
            embed.add_field(name=f" {tf_label}", value=f" Error: {str(e)[:50]}", inline=True)

    embed.set_footer(text=f"Chartwise v10.0  BB(20,2)  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !bb {label}  sent to #{ctx.channel.name}")


@bot.command(name="dr")
async def cmd_dr(ctx, pair_arg: str = None):
    """
    ICT Dealing Range across 4 timeframes (v9.8).
    Shows current zone (Premium/Equilibrium/Discount/Deep Discount) and key Fibonacci levels.
    Usage: !dr [pair]  e.g. !dr BTC  or  !dr SOL
    """
    target_pair = None
    if pair_arg:
        pa = pair_arg.upper().strip()
        for p in PAIRS:
            if pa in p["label"] or pa == p["label"].split("/")[0]:
                target_pair = p
                break
    if target_pair is None:
        target_pair = PAIRS[0]

    label = target_pair["label"]
    await ctx.trigger_typing()

    timeframes = [
        ("5m",  300,   50),
        ("15m", 900,   50),
        ("1H",  3600,  50),
        ("4H",  14400, 50),
    ]

    zone_emojis = {
        "premium":      " Premium",
        "equilibrium":  " Equilibrium",
        "discount":     " Discount",
        "deep_discount":" Deep Discount",
        "unknown":      " Unknown",
    }

    def _fmt_p(v):
        if v >= 1000:
            return f"${v:,.2f}"
        elif v >= 1:
            return f"${v:.4f}"
        else:
            return f"${v:.6f}"

    embed = discord.Embed(
        title=f" ICT Dealing Range  {label}",
        description="Premium / Equilibrium / Discount / Deep Discount zones across 4 timeframes",
        color=0x9C27B0,
        timestamp=datetime.now(timezone.utc)
    )

    for tf_label, gran, lookback in timeframes:
        try:
            candles = await fetch_coinbase_candles(target_pair["product_id"], granularity=gran, limit=lookback + 5)
            if not candles or len(candles) < 10:
                embed.add_field(name=f" {tf_label}", value=" Insufficient data", inline=True)
                continue
            dr = detect_dealing_range(candles, lookback=lookback)
            zone_label = zone_emojis.get(dr["current_zone"], "")
            field_val = (
                f"**Zone:** {zone_label}\n"
                f"**Range:** {_fmt_p(dr['low'])}  {_fmt_p(dr['high'])}\n"
                f"**Premium (61.8%):** {_fmt_p(dr['premium_threshold'])}\n"
                f"**Equilibrium (50%):** {_fmt_p(dr['equilibrium'])}\n"
                f"**Discount (38.2%):** {_fmt_p(dr['discount_threshold'])}\n"
                f"**Deep Disc (23.6%):** {_fmt_p(dr['deep_discount_threshold'])}"
            )
            embed.add_field(name=f" {tf_label}", value=field_val, inline=True)
        except Exception as e:
            embed.add_field(name=f" {tf_label}", value=f" Error: {str(e)[:50]}", inline=True)

    embed.set_footer(text=f"Chartwise v10.0  ICT Dealing Range  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !dr {label}  sent to #{ctx.channel.name}")


@bot.command(name="bb2")
async def cmd_bb2(ctx, pair_arg: str = None):
    """
    ICT Breaker Blocks on 15m and 1H timeframes (v9.8). NOT Bollinger Bands.
    Shows mitigated order blocks now acting as support/resistance.
    Usage: !bb2 [pair]  e.g. !bb2 BTC  or  !bb2 SOL
    """
    target_pair = None
    if pair_arg:
        pa = pair_arg.upper().strip()
        for p in PAIRS:
            if pa in p["label"] or pa == p["label"].split("/")[0]:
                target_pair = p
                break
    if target_pair is None:
        target_pair = PAIRS[0]

    label = target_pair["label"]
    await ctx.trigger_typing()

    timeframes = [
        ("15m", 900),
        ("1H",  3600),
    ]

    def _fmt_p(v):
        if v >= 1000:
            return f"${v:,.2f}"
        elif v >= 1:
            return f"${v:.4f}"
        else:
            return f"${v:.6f}"

    embed = discord.Embed(
        title=f" ICT Breaker Blocks  {label}",
        description="Mitigated order blocks now acting as support/resistance  15m & 1H",
        color=0xFF5722,
        timestamp=datetime.now(timezone.utc)
    )

    for tf_label, gran in timeframes:
        try:
            candles = await fetch_coinbase_candles(target_pair["product_id"], granularity=gran, limit=80)
            if not candles or len(candles) < 15:
                embed.add_field(name=f" {tf_label} LONG", value=" Insufficient data", inline=True)
                embed.add_field(name=f" {tf_label} SHORT", value=" Insufficient data", inline=True)
                continue
            current_price = candles[-1]["close"]
            for direction in ("long", "short"):
                bb_ict = detect_breaker_block(candles, direction)
                dir_label = "LONG " if direction == "long" else "SHORT "
                if bb_ict["found"]:
                    bb_dist_pct = abs(current_price - bb_ict["level"]) / current_price * 100
                    near_str = " Near price!" if bb_dist_pct <= 0.5 else f"{bb_dist_pct:.2f}% away"
                    bb_type_str = "Support " if bb_ict["type"] == "support" else "Resistance "
                    field_val = (
                        f"**Type:** {bb_type_str}\n"
                        f"**Zone:** {_fmt_p(bb_ict['zone_low'])}  {_fmt_p(bb_ict['zone_high'])}\n"
                        f"**Mid:** {_fmt_p(bb_ict['level'])}\n"
                        f"**Distance:** {near_str}"
                    )
                else:
                    field_val = "No breaker block found"
                embed.add_field(name=f" {tf_label} {dir_label}", value=field_val, inline=True)
        except Exception as e:
            embed.add_field(name=f" {tf_label}", value=f" Error: {str(e)[:50]}", inline=True)

    embed.set_footer(text=f"Chartwise v10.0  ICT Breaker Blocks  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !bb2 {label}  sent to #{ctx.channel.name}")


@bot.command(name="ce")
async def cmd_ce(ctx, pair_arg: str = None):
    """
    ICT Consequent Encroachment (CE) levels across all timeframes (v9.8).
    CE = 50% midpoint of each FVG  high-probability reaction level.
    Usage: !ce [pair]  e.g. !ce BTC  or  !ce SOL
    """
    target_pair = None
    if pair_arg:
        pa = pair_arg.upper().strip()
        for p in PAIRS:
            if pa in p["label"] or pa == p["label"].split("/")[0]:
                target_pair = p
                break
    if target_pair is None:
        target_pair = PAIRS[0]

    label = target_pair["label"]
    await ctx.trigger_typing()

    timeframes = [
        ("5m",  300),
        ("15m", 900),
        ("1H",  3600),
        ("4H",  14400),
    ]

    def _fmt_p(v):
        if v >= 1000:
            return f"${v:,.2f}"
        elif v >= 1:
            return f"${v:.4f}"
        else:
            return f"${v:.6f}"

    embed = discord.Embed(
        title=f" ICT Consequent Encroachment  {label}",
        description="50% midpoints of Fair Value Gaps  key reaction levels across all timeframes",
        color=0x00E5FF,
        timestamp=datetime.now(timezone.utc)
    )

    for tf_label, gran in timeframes:
        try:
            candles = await fetch_coinbase_candles(target_pair["product_id"], granularity=gran, limit=60)
            if not candles or len(candles) < 5:
                embed.add_field(name=f" {tf_label}", value=" Insufficient data", inline=True)
                continue
            current_price = candles[-1]["close"]
            fvgs = detect_fvg_zones(candles)
            if not fvgs:
                embed.add_field(name=f" {tf_label}", value="No FVGs detected", inline=True)
                continue
            lines = []
            for fvg in fvgs[:5]:  # show up to 5 most recent
                ce_mid = (fvg["top"] + fvg["bottom"]) / 2
                dist_pct = abs(current_price - ce_mid) / current_price * 100
                near_str = "" if dist_pct <= 0.2 else ""
                fvg_type_str = " Bull" if fvg["type"] == "bullish" else " Bear"
                lines.append(
                    f"{fvg_type_str} CE: {_fmt_p(ce_mid)} ({dist_pct:.2f}% away){near_str}"
                )
            embed.add_field(name=f" {tf_label}", value="\n".join(lines), inline=True)
        except Exception as e:
            embed.add_field(name=f" {tf_label}", value=f" Error: {str(e)[:50]}", inline=True)

    embed.set_footer(text=f"Chartwise v10.0  ICT CE = 50% of FVG  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !ce {label}  sent to #{ctx.channel.name}")


@bot.command(name="ha")
async def cmd_ha(ctx, pair_arg: str = None):
    """
    Heikin Ashi trend summary across 4 timeframes (v9.0).
    Shows consecutive same-color HA candles at the end of each TF for trend momentum.
    Usage: !ha [pair]  e.g. !ha BTC  or  !ha SOL
    """
    target_pair = None
    if pair_arg:
        pa = pair_arg.upper().strip()
        for p in PAIRS:
            if pa in p["label"] or pa == p["label"].split("/")[0]:
                target_pair = p
                break
    if target_pair is None:
        target_pair = PAIRS[0]

    label = target_pair["label"]
    await ctx.trigger_typing()

    timeframes = [
        ("5m",  300,   "5m"),
        ("15m", 900,   "15m"),
        ("1H",  3600,  "1H"),
        ("4H",  14400, "4H"),
    ]

    embed = discord.Embed(
        title=f" Heikin Ashi Trend  {label}",
        description="Consecutive same-color HA candles at end of each timeframe  strong color runs = strong trends",
        color=0xE91E63,
        timestamp=datetime.now(timezone.utc)
    )

    for tf_label, gran, _ in timeframes:
        try:
            candles = await fetch_coinbase_candles(target_pair["product_id"], granularity=gran, limit=60)
            if not candles or len(candles) < 10:
                embed.add_field(name=f" {tf_label}", value=" Insufficient data", inline=True)
                continue

            ha_candles = to_heikin_ashi(candles)
            count, color = count_consecutive_ha_candles(ha_candles)

            if color == "green":
                color_emoji = ""
                trend_label = "bullish"
            elif color == "red":
                color_emoji = ""
                trend_label = "bearish"
            else:
                color_emoji = ""
                trend_label = "neutral"

            # Momentum label
            if count >= 7:
                momentum = " Very strong"
            elif count >= 5:
                momentum = " Strong"
            elif count >= 3:
                momentum = " Moderate"
            else:
                momentum = " Weak"

            price = candles[-1]["close"]
            last_ha = ha_candles[-1]

            def _fmt(v):
                if v >= 1000:
                    return f"${v:,.2f}"
                elif v >= 1:
                    return f"${v:.4f}"
                else:
                    return f"${v:.6f}"

            field_val = (
                f"{color_emoji} **{count} {color} HA candle{'s' if count != 1 else ''} in a row**\n"
                f"Trend: **{trend_label.capitalize()}**  {momentum}\n"
                f"HA Close: {_fmt(last_ha['close'])} | Price: {_fmt(price)}"
            )
            embed.add_field(name=f" {tf_label}", value=field_val, inline=True)

        except Exception as e:
            embed.add_field(name=f" {tf_label}", value=f" Error: {str(e)[:50]}", inline=True)

    embed.set_footer(text=f"Chartwise v10.0  Heikin Ashi(OHLC/4)  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !ha {label}  sent to #{ctx.channel.name}")


@bot.command(name="kc")
async def cmd_kc(ctx, pair_arg: str = None):
    """
    Keltner Channel values + BB-inside-KC squeeze across 4 timeframes (v9.0).
    Shows upper/lower KC bands, price position, and BB squeeze confirmation.
    Usage: !kc [pair]  e.g. !kc BTC  or  !kc SOL
    """
    target_pair = None
    if pair_arg:
        pa = pair_arg.upper().strip()
        for p in PAIRS:
            if pa in p["label"] or pa == p["label"].split("/")[0]:
                target_pair = p
                break
    if target_pair is None:
        target_pair = PAIRS[0]

    label = target_pair["label"]
    await ctx.trigger_typing()

    timeframes = [
        ("5m",  300,   "5m"),
        ("15m", 900,   "15m"),
        ("1H",  3600,  "1H"),
        ("4H",  14400, "4H"),
    ]

    embed = discord.Embed(
        title=f" Keltner Channel  {label}",
        description="KC(EMA20, ATR14  1.5)  Upper  Middle  Lower  Price position  BB-inside-KC squeeze",
        color=0xFF9800,
        timestamp=datetime.now(timezone.utc)
    )

    for tf_label, gran, _ in timeframes:
        try:
            candles = await fetch_coinbase_candles(target_pair["product_id"], granularity=gran, limit=60)
            if not candles or len(candles) < 22:
                embed.add_field(name=f" {tf_label}", value=" Insufficient data", inline=True)
                continue

            price = candles[-1]["close"]
            kc = calc_keltner_channel(candles)
            if kc is None:
                embed.add_field(name=f" {tf_label}", value=" KC calc failed", inline=True)
                continue

            squeeze = detect_keltner_squeeze(candles)
            bb_squeeze = detect_bb_squeeze(candles)

            # Price position
            if price > kc["upper"]:
                pos_str = " Above KC upper"
            elif price < kc["lower"]:
                pos_str = " Below KC lower"
            elif price > kc["middle"] * 1.002:
                pos_str = " Above KC midline"
            elif price < kc["middle"] * 0.998:
                pos_str = " Below KC midline"
            else:
                pos_str = " At KC midline"

            squeeze_str = " **BB INSIDE KC  SQUEEZE!**" if squeeze else (" BB squeeze" if bb_squeeze else "No squeeze")

            def _fmt(v):
                if v >= 1000:
                    return f"${v:,.2f}"
                elif v >= 1:
                    return f"${v:.4f}"
                else:
                    return f"${v:.6f}"

            field_val = (
                f"**Upper:** {_fmt(kc['upper'])}  **Lower:** {_fmt(kc['lower'])}\n"
                f"**Middle:** {_fmt(kc['middle'])}  **Price:** {_fmt(price)}\n"
                f"{pos_str}\n"
                f"{squeeze_str}"
            )
            embed.add_field(name=f" {tf_label}", value=field_val, inline=True)

        except Exception as e:
            embed.add_field(name=f" {tf_label}", value=f" Error: {str(e)[:50]}", inline=True)

    embed.set_footer(text=f"Chartwise v10.0  KC(EMA20,ATR14,1.5)  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !kc {label}  sent to #{ctx.channel.name}")


@bot.command(name="fvg")
async def cmd_fvg(ctx, pair_arg: str = None):
    """
    Fair Value Gap (ICT FVG) detection across 4 timeframes (v9.0).
    Shows detected FVGs, price position relative to each gap, and freshness.
    Usage: !fvg [pair]  e.g. !fvg BTC  or  !fvg SOL
    """
    target_pair = None
    if pair_arg:
        pa = pair_arg.upper().strip()
        for p in PAIRS:
            if pa in p["label"] or pa == p["label"].split("/")[0]:
                target_pair = p
                break
    if target_pair is None:
        target_pair = PAIRS[0]

    label = target_pair["label"]
    await ctx.trigger_typing()

    timeframes = [
        ("5m",  300,   "5m"),
        ("15m", 900,   "15m"),
        ("1H",  3600,  "1H"),
        ("4H",  14400, "4H"),
    ]

    embed = discord.Embed(
        title=f" Fair Value Gaps (ICT FVG)  {label}",
        description="3-candle imbalance zones  institutional demand/supply gaps across 4 timeframes",
        color=0x9C27B0,
        timestamp=datetime.now(timezone.utc)
    )

    def _fmt(v):
        if v >= 1000:
            return f"${v:,.2f}"
        elif v >= 1:
            return f"${v:.4f}"
        else:
            return f"${v:.6f}"

    for tf_label, gran, _ in timeframes:
        try:
            candles = await fetch_coinbase_candles(target_pair["product_id"], granularity=gran, limit=60)
            if not candles or len(candles) < 5:
                embed.add_field(name=f" {tf_label}", value=" Insufficient data", inline=True)
                continue

            price = candles[-1]["close"]
            fvg_zones = detect_fvg_zones(candles)

            if not fvg_zones:
                embed.add_field(name=f" {tf_label}", value="No FVGs detected", inline=True)
                continue

            # Show up to 3 most recent FVGs
            lines = []
            for fvg in fvg_zones[:3]:
                fvg_emoji = "" if fvg["type"] == "bullish" else ""
                fvg_type  = fvg["type"].capitalize()
                # Freshness
                age = fvg["candles_ago"]
                fresh_tag = "fresh" if age <= 3 else f"{age}c ago"
                # Price position relative to FVG
                if price > fvg["top"]:
                    pos = " above"
                elif price < fvg["bottom"]:
                    pos = " below"
                else:
                    pos = " inside"
                lines.append(
                    f"{fvg_emoji} **{fvg_type}** [{fresh_tag}] {pos}\n"
                    f"  Zone: {_fmt(fvg['bottom'])}  {_fmt(fvg['top'])}"
                )

            field_val = "\n".join(lines)
            embed.add_field(name=f" {tf_label}", value=field_val, inline=True)

        except Exception as e:
            embed.add_field(name=f" {tf_label}", value=f" Error: {str(e)[:50]}", inline=True)

    embed.set_footer(text=f"Chartwise v10.0  ICT FVG (3-candle imbalance)  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !fvg {label}  sent to #{ctx.channel.name}")


@bot.command(name="news")
async def cmd_news(ctx, pair_arg: str = None):
    """
    Auto-generated market narrative from price action for a pair (v8.8 Feature 5).
    No real news scraping  narrative is generated from OHLCV indicators.
    Usage: !news [pair]  e.g. !news BTC  or  !news SOL
    """
    # Resolve pair
    target_pair = None
    if pair_arg:
        pa = pair_arg.upper().strip()
        for p in PAIRS:
            if pa in p["label"] or pa == p["label"].split("/")[0]:
                target_pair = p
                break
    if target_pair is None:
        target_pair = PAIRS[0]

    label = target_pair["label"]
    await ctx.trigger_typing()

    try:
        candles_5m  = await fetch_candles(target_pair, timeframe="5m")
        candles_4h  = await fetch_candles(target_pair, timeframe="4h")
    except Exception as e:
        await ctx.send(f" Failed to fetch data for {label}: {e}")
        return

    if not candles_5m or len(candles_5m) < 30:
        await ctx.send(f" Insufficient data for {label} narrative.")
        return

    price = candles_5m[-1]["close"]
    closes_5m = [c["close"] for c in candles_5m]

    # RSI narrative
    rsi_val = rsi(closes_5m, 14)
    if rsi_val is not None:
        if rsi_val > 70:
            rsi_narrative = f"RSI is deeply overbought at {rsi_val:.1f}, signaling potential exhaustion and reversal risk."
        elif rsi_val > 60:
            rsi_narrative = f"RSI at {rsi_val:.1f} shows strong bullish momentum without yet reaching extremes."
        elif rsi_val < 30:
            rsi_narrative = f"RSI is oversold at {rsi_val:.1f}, suggesting the asset may be due for a bounce."
        elif rsi_val < 40:
            rsi_narrative = f"RSI at {rsi_val:.1f} reflects bearish pressure, with sellers controlling momentum."
        else:
            rsi_narrative = f"RSI at {rsi_val:.1f} sits in neutral territory  market participants appear balanced."
    else:
        rsi_narrative = "RSI data unavailable for narrative."

    # BB narrative
    if len(closes_5m) >= 20:
        bb_mean_5m = statistics.mean(closes_5m[-20:])
        bb_std_5m  = statistics.stdev(closes_5m[-20:])
        bb_upper_5m = bb_mean_5m + 2 * bb_std_5m
        bb_lower_5m = bb_mean_5m - 2 * bb_std_5m
        bb_width_5m = (bb_upper_5m - bb_lower_5m) / bb_mean_5m * 100 if bb_mean_5m > 0 else 0.0
        if price > bb_upper_5m:
            bb_narrative = f"Price is trading above the upper Bollinger Band ({bb_width_5m:.1f}% width), indicating overextension  watch for mean reversion toward ${bb_mean_5m:,.2f}."
        elif price < bb_lower_5m:
            bb_narrative = f"Price has broken below the lower Bollinger Band ({bb_width_5m:.1f}% width), signaling a potential snap-back rally toward ${bb_mean_5m:,.2f}."
        elif bb_width_5m < 2.0:
            bb_narrative = f"Bollinger Bands are tightly squeezed ({bb_width_5m:.1f}% width), pointing to an imminent volatility expansion."
        else:
            pos_pct = (price - bb_lower_5m) / (bb_upper_5m - bb_lower_5m) * 100 if (bb_upper_5m - bb_lower_5m) > 0 else 50
            bb_narrative = f"Price sits at {pos_pct:.0f}% of the BB range (width: {bb_width_5m:.1f}%), with no immediate band extremes detected."
    else:
        bb_narrative = "Bollinger Band data insufficient for narrative."

    # 4H regime narrative
    if candles_4h and len(candles_4h) >= 25:
        regime = detect_market_regime(candles_4h, lookback=20)
        if regime == "Trending Up":
            regime_narrative = f"The 4H market regime is **Trending Up**  price action suggests buyers are in control on the higher timeframe, supporting long bias."
        elif regime == "Trending Down":
            regime_narrative = f"The 4H market regime is **Trending Down**  sellers dominate the higher timeframe, biasing toward short setups."
        else:
            regime_narrative = f"The 4H market regime is **Ranging**  price oscillates without directional conviction, increasing breakout-failure risk."
    else:
        regime_narrative = "4H regime data unavailable."

    # Price change narrative
    if len(closes_5m) >= 2:
        chg_pct = (closes_5m[-1] - closes_5m[-30]) / closes_5m[-30] * 100 if len(closes_5m) >= 30 else 0.0
        sign = "+" if chg_pct >= 0 else ""
        chg_dir = "gained" if chg_pct >= 0 else "shed"
        price_narrative = f"{label} has {chg_dir} **{sign}{chg_pct:.2f}%** over the past 2.5 hours, currently trading at **{price_fmt(label, price)}**."
    else:
        price_narrative = f"{label} is currently trading at **{price_fmt(label, price)}**."

    embed = discord.Embed(
        title=f" Market Narrative  {label}",
        description=f"*Auto-generated from price action  Not real news  Not financial advice*",
        color=0x1ABC9C,
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name=" Price Action", value=price_narrative, inline=False)
    embed.add_field(name=" Momentum (RSI)", value=rsi_narrative, inline=False)
    embed.add_field(name=" Volatility (BB)", value=bb_narrative, inline=False)
    embed.add_field(name=" Market Regime (4H)", value=regime_narrative, inline=False)

    # Last signal from log
    sig_entries = [e for e in list(SIGNAL_LOG) if e.get("pair") == label]
    if sig_entries:
        last_sig = sig_entries[-1]
        ls_dir  = last_sig.get("direction", "?").upper()
        ls_sc   = last_sig.get("score", "?")
        ls_time = last_sig.get("time", "")
        try:
            ls_dt = datetime.fromisoformat(ls_time.replace("Z", "+00:00") if ls_time.endswith("Z") else ls_time)
            if ls_dt.tzinfo is None:
                ls_dt = ls_dt.replace(tzinfo=timezone.utc)
            delta_m = int((datetime.now(timezone.utc) - ls_dt).total_seconds() // 60)
            ls_age = f"{delta_m}m ago" if delta_m < 60 else f"{delta_m // 60}h {delta_m % 60}m ago"
        except Exception:
            ls_age = "unknown"
        dir_icon = "" if ls_dir == "LONG" else ""
        embed.add_field(
            name=" Last Signal",
            value=f"{dir_icon} {ls_dir}  Score {ls_sc}  {ls_age}",
            inline=False
        )

    embed.set_footer(text=f"Chartwise v10.0  Narrative from OHLCV only  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !news {label}  sent narrative to #{ctx.channel.name}")


# 
# v9.1 NEW COMMANDS
# 

@bot.command(name="watchlist")
async def cmd_watchlist(ctx):
    """
    Show current near-miss signals waiting for price to touch their entry zone. (v9.1 Feature 1)
    Near-miss = signals that scored MIN_SCORE-1 or MIN_SCORE-2.
    Usage: !watchlist
    """
    if not WATCHLIST or all(not v for v in WATCHLIST.values()):
        await ctx.send(" Watchlist is empty  no near-miss signals currently tracked.")
        return

    embed = discord.Embed(
        title=" Signal Watchlist  Near-Miss Setups",
        description=f"Signals that almost qualified (score {MIN_SCORE - 2}{MIN_SCORE - 1})  waiting for price to touch entry zone.",
        color=0xFFD700,
        timestamp=datetime.now(timezone.utc)
    )

    now_dt = datetime.now(timezone.utc)
    total = 0
    for pair_label, items in WATCHLIST.items():
        for item in items:
            total += 1
            _wdir = item.get("direction", "?").upper()
            _wscore = item.get("score", "?")
            _wentry = item.get("entry", 0)
            _wsl = item.get("sl", 0)
            _wt1 = item.get("t1", 0)
            _wtime = item.get("time", "")
            dir_icon = "" if _wdir == "LONG" else ""

            # Age
            age_str = "?"
            if _wtime:
                try:
                    _wdt = datetime.fromisoformat(_wtime)
                    if _wdt.tzinfo is None:
                        _wdt = _wdt.replace(tzinfo=timezone.utc)
                    _age_m = int((now_dt - _wdt).total_seconds() / 60)
                    age_str = f"{_age_m}m ago" if _age_m < 60 else f"{_age_m // 60}h {_age_m % 60}m ago"
                except Exception:
                    pass

            _wreasons = item.get("reasons", [])[:3]
            embed.add_field(
                name=f"{dir_icon} {pair_label} {_wdir}",
                value=(
                    f"Score: **{_wscore}** / need {MIN_SCORE}\n"
                    f"Entry zone: {price_fmt(pair_label, _wentry)}\n"
                    f"SL: {price_fmt(pair_label, _wsl)}  T1: {price_fmt(pair_label, _wt1)}\n"
                    f"Added: {age_str}\n"
                    + ("\n".join(f" {r}" for r in _wreasons) if _wreasons else "")
                ),
                inline=False
            )

    if total == 0:
        await ctx.send(" Watchlist is empty  no near-miss signals currently tracked.")
        return

    embed.set_footer(text=f"Chartwise v10.0  {total} watchlist item(s)  Alert fires when price touches entry zone  {now_dt.strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !watchlist  sent {total} item(s) to #{ctx.channel.name}")


@bot.command(name="targets")
async def cmd_targets(ctx, pair_arg: str = None):
    """
    Show next key price targets above and below current price. (v9.1 Feature 2)
    Shows: next S/R zone, Fib level, pivot level, and order block above/below.
    Usage: !targets [pair]  e.g. !targets BTC  or  !targets SOL
    """
    # Resolve pair
    target_pair = None
    if pair_arg:
        pa = pair_arg.upper().strip()
        for p in PAIRS:
            if pa in p["label"] or pa == p["label"].split("/")[0]:
                target_pair = p
                break
    if target_pair is None:
        target_pair = PAIRS[0]

    label = target_pair["label"]
    await ctx.trigger_typing()

    try:
        candles_5m = await fetch_candles(target_pair, timeframe="5m")
        candles_4h = await fetch_candles(target_pair, timeframe="4h")
    except Exception as e:
        await ctx.send(f" Failed to fetch data for {label}: {e}")
        return

    if not candles_5m or len(candles_5m) < 30:
        await ctx.send(f" Insufficient data for {label}.")
        return

    price = candles_5m[-1]["close"]
    closes = [c["close"] for c in candles_5m]

    def _pct(target_price):
        return (target_price - price) / price * 100

    def _fmt_target(target_price, label_str):
        pct = _pct(target_price)
        sign = "+" if pct >= 0 else ""
        return f"{label_str} {price_fmt(label, target_price)} ({sign}{pct:.1f}%)"

    # S/R zones
    sr_above = None
    sr_below = None
    try:
        sr_zones = detect_sr_zones(candles_5m)
        for z in sorted(sr_zones, key=lambda x: x["level"]):
            lv = z["level"]
            if lv > price * 1.001 and sr_above is None:
                sr_above = lv
            elif lv < price * 0.999 and sr_below is None:
                sr_below = lv
        # Find highest below
        below_zones = [z["level"] for z in sr_zones if z["level"] < price * 0.999]
        sr_below = max(below_zones) if below_zones else None
    except Exception:
        pass

    # Fibonacci levels (use 4H for better swing data)
    fib_above = None
    fib_below = None
    try:
        _fib_candles = candles_4h if (candles_4h and len(candles_4h) >= 20) else candles_5m
        highs = [c["high"] for c in _fib_candles[-50:]]
        lows  = [c["low"]  for c in _fib_candles[-50:]]
        swing_high = max(highs)
        swing_low  = min(lows)
        fib_levels = calc_fib_levels(swing_high, swing_low)
        for level_name, level_val in sorted(fib_levels.items(), key=lambda x: x[1]):
            if level_val > price * 1.001 and fib_above is None:
                fib_above = (level_name, level_val)
            if level_val < price * 0.999:
                fib_below = (level_name, level_val)
    except Exception:
        pass

    # Classic pivot points (from previous 4H candle)
    pivot_r1 = None
    pivot_s1 = None
    try:
        if candles_4h and len(candles_4h) >= 2:
            prev = candles_4h[-2]
            ph, pl, pc = prev["high"], prev["low"], prev["close"]
            p_pivot = (ph + pl + pc) / 3
            pivot_r1 = 2 * p_pivot - pl
            pivot_s1 = 2 * p_pivot - ph
    except Exception:
        pass

    # Order blocks
    ob_above = None
    ob_below = None
    try:
        ob = find_order_block(candles_5m, "long")
        if ob:
            lv = ob.get("level", ob.get("high", 0))
            if lv > price * 1.001:
                ob_above = lv
        ob_short = find_order_block(candles_5m, "short")
        if ob_short:
            lv_s = ob_short.get("level", ob_short.get("low", 0))
            if lv_s < price * 0.999:
                ob_below = lv_s
    except Exception:
        pass

    embed = discord.Embed(
        title=f" {label} Key Targets",
        description=f"Current price: **{price_fmt(label, price)}**  Next key levels above and below",
        color=0x00BCD4,
        timestamp=datetime.now(timezone.utc)
    )

    # Above targets
    above_lines = []
    if sr_above:
        above_lines.append(_fmt_target(sr_above, " S/R"))
    if fib_above:
        above_lines.append(_fmt_target(fib_above[1], f" Fib {fib_above[0]}"))
    if pivot_r1:
        above_lines.append(_fmt_target(pivot_r1, " Pivot R1"))
    if ob_above:
        above_lines.append(_fmt_target(ob_above, " OB Supply"))
    embed.add_field(
        name=" Resistance / Targets Above",
        value="\n".join(above_lines) if above_lines else "No levels detected above",
        inline=False
    )

    # Below targets
    below_lines = []
    if sr_below:
        below_lines.append(_fmt_target(sr_below, " S/R"))
    if fib_below:
        below_lines.append(_fmt_target(fib_below[1], f" Fib {fib_below[0]}"))
    if pivot_s1:
        below_lines.append(_fmt_target(pivot_s1, " Pivot S1"))
    if ob_below:
        below_lines.append(_fmt_target(ob_below, " OB Demand"))
    embed.add_field(
        name=" Support / Targets Below",
        value="\n".join(below_lines) if below_lines else "No levels detected below",
        inline=False
    )

    embed.set_footer(text=f"Chartwise v10.0  Key targets from S/R  Fib  Pivot  OB  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !targets {label}  sent key targets to #{ctx.channel.name}")


@bot.command(name="pa")
async def cmd_pa(ctx, pair_arg: str = None):
    """
    Pure price action summary for a pair  no indicators. (v9.1 Feature 4)
    Shows: last 5 candle colors, last swing high/low, trend structure (HH/HL vs LH/LL),
    and whether current candle is breaking above/below structure.
    Usage: !pa [pair]  e.g. !pa BTC  or  !pa SOL
    """
    target_pair = None
    if pair_arg:
        pa_arg = pair_arg.upper().strip()
        for p in PAIRS:
            if pa_arg in p["label"] or pa_arg == p["label"].split("/")[0]:
                target_pair = p
                break
    if target_pair is None:
        target_pair = PAIRS[0]

    label = target_pair["label"]
    await ctx.trigger_typing()

    try:
        candles_5m = await fetch_candles(target_pair, timeframe="5m")
    except Exception as e:
        await ctx.send(f" Failed to fetch data for {label}: {e}")
        return

    if not candles_5m or len(candles_5m) < 15:
        await ctx.send(f" Insufficient data for {label}.")
        return

    price = candles_5m[-1]["close"]

    # Last 5 candle colors and sizes
    last5 = candles_5m[-5:]
    candle_icons = []
    bull_count = 0
    for c in last5:
        body = abs(c["close"] - c["open"])
        rng  = c["high"] - c["low"]
        is_bull = c["close"] >= c["open"]
        if is_bull:
            bull_count += 1
            candle_icons.append("")
        else:
            candle_icons.append("")

    candle_str = "".join(candle_icons)
    bull_label = f"{bull_count}/5 bullish" if bull_count >= 3 else f"{5 - bull_count}/5 bearish"

    # Swing highs and lows
    swing_high_price = None
    swing_low_price  = None
    try:
        sh, sl_swings = find_swing_highs_lows(candles_5m[-30:])
        if sh:
            swing_high_price = max(s["price"] for s in sh)
        if sl_swings:
            swing_low_price = min(s["price"] for s in sl_swings)
    except Exception:
        # fallback
        highs = [c["high"] for c in candles_5m[-20:]]
        lows  = [c["low"]  for c in candles_5m[-20:]]
        swing_high_price = max(highs) if highs else None
        swing_low_price  = min(lows) if lows else None

    # Trend direction: HH/HL = uptrend, LH/LL = downtrend
    trend_label = "Neutral / Unclear"
    trend_icon  = ""
    try:
        candle_highs = [c["high"] for c in candles_5m[-15:]]
        candle_lows  = [c["low"]  for c in candles_5m[-15:]]
        # Compare first half vs second half of the window
        mid = 7
        h_first_half = max(candle_highs[:mid])
        h_second_half = max(candle_highs[mid:])
        l_first_half  = min(candle_lows[:mid])
        l_second_half = min(candle_lows[mid:])
        if h_second_half > h_first_half and l_second_half > l_first_half:
            trend_label = "HH + HL (Uptrend)"
            trend_icon  = ""
        elif h_second_half < h_first_half and l_second_half < l_first_half:
            trend_label = "LH + LL (Downtrend)"
            trend_icon  = ""
        elif h_second_half > h_first_half:
            trend_label = "HH only  possible breakout"
            trend_icon  = ""
        elif l_second_half < l_first_half:
            trend_label = "LL only  possible breakdown"
            trend_icon  = ""
    except Exception:
        pass

    # Structure break check: is current candle breaking above swing high or below swing low?
    structure_str = "No structure break"
    if swing_high_price and price > swing_high_price:
        pct_abv = (price - swing_high_price) / swing_high_price * 100
        structure_str = f" Breaking ABOVE swing high {price_fmt(label, swing_high_price)} (+{pct_abv:.2f}%)"
    elif swing_low_price and price < swing_low_price:
        pct_blw = (swing_low_price - price) / swing_low_price * 100
        structure_str = f" Breaking BELOW swing low {price_fmt(label, swing_low_price)} (-{pct_blw:.2f}%)"
    elif swing_high_price and (swing_high_price - price) / swing_high_price < 0.005:
        structure_str = f" Approaching swing high {price_fmt(label, swing_high_price)}"
    elif swing_low_price and (price - swing_low_price) / swing_low_price < 0.005:
        structure_str = f" Approaching swing low {price_fmt(label, swing_low_price)}"

    embed = discord.Embed(
        title=f" Price Action  {label}",
        description=f"Pure price action analysis  No indicators  Current price: **{price_fmt(label, price)}**",
        color=0xE91E63,
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(
        name="Last 5 Candles",
        value=f"{candle_str}    **{bull_label}**",
        inline=False
    )
    embed.add_field(
        name="Swing High",
        value=price_fmt(label, swing_high_price) if swing_high_price else "",
        inline=True
    )
    embed.add_field(
        name="Swing Low",
        value=price_fmt(label, swing_low_price) if swing_low_price else "",
        inline=True
    )
    embed.add_field(
        name=f"{trend_icon} Trend Structure",
        value=trend_label,
        inline=False
    )
    embed.add_field(
        name="Structure Break",
        value=structure_str,
        inline=False
    )
    embed.set_footer(text=f"Chartwise v10.0  Pure price action (5m)  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !pa {label}  sent PA summary to #{ctx.channel.name}")


@bot.command(name="debug")
async def cmd_debug(ctx, pair_arg: str = None):
    """
    Developer/power user: show full scoring breakdown for a pair's latest scan. (v9.1 Feature 6)
    Fetches fresh 5m data and runs analyze() live, showing raw score, all reasons,
    which patterns fired and which were checked but didn't fire.
    Usage: !debug [pair]  e.g. !debug BTC  or  !debug SOL
    Power user: shows scoring breakdown
    """
    target_pair = None
    if pair_arg:
        pa_arg = pair_arg.upper().strip()
        for p in PAIRS:
            if pa_arg in p["label"] or pa_arg == p["label"].split("/")[0]:
                target_pair = p
                break
    if target_pair is None:
        target_pair = PAIRS[0]

    label = target_pair["label"]
    await ctx.trigger_typing()

    try:
        candles_5m = await fetch_candles(target_pair, timeframe="5m")
    except Exception as e:
        await ctx.send(f" Failed to fetch data for {label}: {e}")
        return

    if not candles_5m or len(candles_5m) < 50:
        await ctx.send(f" Insufficient data for {label}.")
        return

    # Run both engines live
    smc_result = analyze(candles_5m, label)
    std_result = analyze_standard(candles_5m, label)

    embed = discord.Embed(
        title=f" Debug  {label} Scoring Breakdown",
        description="Live fresh scan with full decision trace. For power users.",
        color=0x9C27B0,
        timestamp=datetime.now(timezone.utc)
    )

    price = candles_5m[-1]["close"]
    embed.add_field(name="Current Price", value=price_fmt(label, price), inline=True)
    embed.add_field(name="Candles Used", value=str(len(candles_5m)), inline=True)
    embed.add_field(name="MIN_SCORE", value=str(MIN_SCORE), inline=True)

    # SMC/ICT engine results
    if smc_result:
        _smc_score = smc_result.get("score", 0)
        _smc_near = smc_result.get("near_miss", False)
        _smc_dir = smc_result.get("direction", "?").upper()
        _smc_reasons = smc_result.get("reasons", [])
        _smc_sl_mult = smc_result.get("sl_atr_mult", 1.0)
        _smc_status = f"{' Near-Miss' if _smc_near else ' SIGNAL'}  score {_smc_score}"
        embed.add_field(
            name=f" SMC/ICT Engine  {_smc_dir}",
            value=(
                f"**Status:** {_smc_status}\n"
                f"**Score:** {_smc_score} / need {MIN_SCORE}\n"
                f"**SL ATR Mult:** {_smc_sl_mult:.2f}\n"
                f"**Reasons fired ({len(_smc_reasons)}):**\n"
                + "\n".join(f" {r}" for r in _smc_reasons[:10])
                + (f"\n+ {len(_smc_reasons) - 10} more" if len(_smc_reasons) > 10 else "")
            ),
            inline=False
        )
    else:
        embed.add_field(
            name=" SMC/ICT Engine",
            value=" No signal or near-miss  score too low or conditions not met",
            inline=False
        )

    # Standard EMA engine results
    if std_result:
        _std_score = std_result.get("score", 0)
        _std_dir = std_result.get("direction", "?").upper()
        _std_reasons = std_result.get("reasons", [])
        _std_status = f"{' SIGNAL' if _std_score >= MIN_SCORE else ' Below threshold'}  score {_std_score}"
        embed.add_field(
            name=f" EMA Engine  {_std_dir}",
            value=(
                f"**Status:** {_std_status}\n"
                f"**Score:** {_std_score} / need {MIN_SCORE}\n"
                f"**Reasons fired ({len(_std_reasons)}):**\n"
                + "\n".join(f" {r}" for r in _std_reasons[:8])
                + (f"\n+ {len(_std_reasons) - 8} more" if len(_std_reasons) > 8 else "")
            ),
            inline=False
        )
    else:
        embed.add_field(
            name=" EMA Engine",
            value=" No signal  conditions not met (insufficient trend, EMA alignment, or score too low)",
            inline=False
        )

    # Quick indicator snapshot for context
    try:
        closes = [c["close"] for c in candles_5m]
        _rsi_v = rsi(closes, 14)
        _atr_v = atr(candles_5m, 14)
        _bb_sq = detect_bb_squeeze(candles_5m)
        _ema9  = ema(closes, 9)
        _ema21 = ema(closes, 21)
        _ema50 = ema(closes, 50)
        _ema_stack = "9>21>50 " if (_ema9 and _ema21 and _ema50 and _ema9 > _ema21 > _ema50) else \
                     "9<21<50 " if (_ema9 and _ema21 and _ema50 and _ema9 < _ema21 < _ema50) else "Mixed"
        _vol_spike_now = False
        if len(candles_5m) >= 20:
            _vols = [c.get("volume", 0) for c in candles_5m[-20:]]
            _avg_vol = sum(_vols[:-1]) / (len(_vols) - 1) if len(_vols) > 1 else 1
            _vol_spike_now = _vols[-1] > _avg_vol * 1.5
        embed.add_field(
            name=" Indicator Snapshot",
            value=(
                f"RSI(14): {_rsi_v:.1f}" if _rsi_v else "RSI: "
            ) + f"\n"
            f"ATR(14): {price_fmt(label, _atr_v) if _atr_v else ''}\n"
            f"BB Squeeze: {' YES' if _bb_sq else 'No'}\n"
            f"EMA Stack: {_ema_stack}\n"
            f"Volume Spike: {' YES' if _vol_spike_now else 'No'}",
            inline=False
        )
    except Exception as _di_err:
        embed.add_field(name="Indicator Snapshot", value=f" {_di_err}", inline=False)

    # Watchlist status
    _wl_items = WATCHLIST.get(label, [])
    if _wl_items:
        embed.add_field(
            name=f" Watchlist ({len(_wl_items)} item(s))",
            value="\n".join(
                f" {w.get('direction','?').upper()} score={w.get('score','?')} entry={price_fmt(label, w.get('entry', 0))}"
                for w in _wl_items
            ),
            inline=False
        )

    embed.set_footer(text=f"Chartwise v10.0  !debug  power user scoring breakdown  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !debug {label}  sent scoring breakdown to #{ctx.channel.name}")


# 
# v9.2 Feature 3: !patterns  pattern win rate overview
# 

@bot.command(name="patterns")
async def cmd_patterns(ctx):
    """Show win rates for all tracked pattern groups. (v9.2)"""
    signals = _read_signals()
    closed = [s for s in signals if s.get("outcome") in ("WIN", "LOSS")]

    # Build per-pattern win/loss counts from closed signal reasons
    all_pp: dict[str, dict] = {k: {"wins": 0, "losses": 0} for k in _ALL_PATTERNS}
    # Seed from in-memory pattern_performance for candle patterns
    for k, v in pattern_performance.items():
        if k in all_pp:
            all_pp[k]["wins"] = v.get("wins", 0)
            all_pp[k]["losses"] = v.get("losses", 0)

    # Also tally from closed signals in disk log for broader patterns
    for sig in closed:
        for reason in sig.get("reasons", []):
            pk = _extract_pattern_from_reason(reason)
            if pk and pk in all_pp:
                if sig["outcome"] == "WIN":
                    all_pp[pk]["wins"] += 1
                else:
                    all_pp[pk]["losses"] += 1

    def _wr_line(label: str, pk: str) -> str:
        d = all_pp.get(pk, {"wins": 0, "losses": 0})
        total = d["wins"] + d["losses"]
        if total == 0:
            return f"{label}:  (no data)"
        wr = d["wins"] / total * 100
        bar = "" * int(wr // 20) + "" * (5 - int(wr // 20))
        return f"{label}: **{wr:.0f}%** {bar} ({total} trades)"

    embed = discord.Embed(
        title=" Pattern Performance Overview",
        description="Win rates by pattern group from all closed trades.",
        color=0x7B2FBE,
        timestamp=datetime.now(timezone.utc)
    )

    smc_lines = "\n".join([
        _wr_line("Market Structure Shift", "mss"),
        _wr_line("Swing Failure Pattern", "sfp"),
        _wr_line("Order Block", "order_block"),
        _wr_line("Fair Value Gap", "fvg"),
        _wr_line("Liquidity Sweep", "liquidity_sweep"),
    ])
    embed.add_field(name=" ICT/SMC Patterns", value=smc_lines or "No data", inline=False)

    candle_lines = "\n".join([
        _wr_line("Engulfing", "engulfing"),
        _wr_line("Hammer", "hammer"),
        _wr_line("Pin Bar", "pin_bar"),
        _wr_line("Three-Line Strike", "three_line_strike"),
        _wr_line("Inside Bar", "inside_bar"),
        _wr_line("Doji", "doji"),
    ])
    embed.add_field(name=" Candle Patterns", value=candle_lines or "No data", inline=False)

    momentum_lines = "\n".join([
        _wr_line("RSI Divergence", "rsi_divergence"),
        _wr_line("MACD Cross", "macd_cross"),
        _wr_line("Consecutive Candles", "consecutive_candles"),
        _wr_line("Heikin Ashi Streak", "ha_streak"),
    ])
    embed.add_field(name=" Momentum Patterns", value=momentum_lines or "No data", inline=False)

    mtf_lines = "\n".join([
        _wr_line("MTF Consensus 2/3", "mtf_consensus_2"),
        _wr_line("MTF Consensus 3/3", "mtf_consensus_3"),
        _wr_line("BB/KC Squeeze", "bb_kc_squeeze"),
    ])
    embed.add_field(name=" Multi-Timeframe", value=mtf_lines or "No data", inline=False)

    total_closed = len(closed)
    embed.set_footer(text=f"Chartwise v10.0  Based on {total_closed} closed trades  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !patterns  sent pattern overview to #{ctx.channel.name}")


# 
# v9.2 Feature 4: !hours  performance by UTC hour
# 

@bot.command(name="hours")
async def cmd_hours(ctx):
    """Show signal performance broken down by UTC hour of day. (v9.2)"""
    signals = _read_signals()
    closed = [s for s in signals if s.get("outcome") in ("WIN", "LOSS")]

    # Also include in-memory SIGNAL_LOG for recent signals (may not all be on disk)
    mem_entries = list(SIGNAL_LOG)

    if len(closed) < 5:
        await ctx.send(" Need at least 5 closed signals to show hourly performance. Keep running!")
        return

    # Bucket closed signals by UTC hour
    hour_data: dict[int, dict] = {h: {"wins": 0, "losses": 0, "signals": 0} for h in range(24)}

    for sig in closed:
        try:
            ts = sig.get("time_utc") or sig.get("ts")
            if isinstance(ts, (int, float)):
                dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            else:
                dt = datetime.fromisoformat(str(ts))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
            h = dt.hour
            hour_data[h]["signals"] += 1
            if sig["outcome"] == "WIN":
                hour_data[h]["wins"] += 1
            else:
                hour_data[h]["losses"] += 1
        except Exception:
            continue

    # Find best and worst hours (at least 2 trades in bucket)
    active_hours = {h: d for h, d in hour_data.items() if d["signals"] >= 2}
    if not active_hours:
        await ctx.send(" Not enough trades per hour yet. Need 2+ trades per hour bucket.")
        return

    best_h = max(active_hours, key=lambda h: active_hours[h]["wins"] / max(active_hours[h]["signals"], 1))
    worst_h = min(active_hours, key=lambda h: active_hours[h]["wins"] / max(active_hours[h]["signals"], 1))

    # Build display lines  only show hours with at least 1 signal
    lines = []
    for h in range(24):
        d = hour_data[h]
        if d["signals"] == 0:
            continue
        wr = d["wins"] / d["signals"] * 100
        bar_filled = int(wr // 25)  # 04
        bar = "" * bar_filled + "" * (4 - bar_filled)
        tag = ""
        if h == best_h:
            tag = "  BEST"
        elif h == worst_h:
            tag = "  WORST"
        lines.append(f"`{h:02d}:00{(h+1)%24:02d}:00` {bar} **{wr:.0f}%** WR ({d['signals']} signals){tag}")

    best_wr = active_hours[best_h]["wins"] / active_hours[best_h]["signals"] * 100
    worst_wr = active_hours[worst_h]["wins"] / active_hours[worst_h]["signals"] * 100

    embed = discord.Embed(
        title=" Performance by UTC Hour",
        description=f"Showing hours with at least 1 closed signal. Based on {len(closed)} closed trades.",
        color=0x1565C0,
        timestamp=datetime.now(timezone.utc)
    )

    # Split into two fields to avoid Discord 1024-char field limit
    half = len(lines) // 2
    embed.add_field(name="Early Hours (UTC)", value="\n".join(lines[:half]) or "No data", inline=False)
    embed.add_field(name="Late Hours (UTC)", value="\n".join(lines[half:]) or "No data", inline=False)

    embed.add_field(
        name=" Key Findings",
        value=(
            f" **Best hour**: `{best_h:02d}:00 UTC`  {best_wr:.0f}% WR ({active_hours[best_h]['signals']} signals)\n"
            f" **Worst hour**: `{worst_h:02d}:00 UTC`  {worst_wr:.0f}% WR ({active_hours[worst_h]['signals']} signals)\n"
            f" Tip: Focus manual review on signals in the best-performing UTC hour window."
        ),
        inline=False
    )
    embed.set_footer(text=f"Chartwise v10.0  All times UTC  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !hours  sent hourly breakdown to #{ctx.channel.name}")


# 
# v9.2 Feature 6: !edge  statistical edge calculator
# 

@bot.command(name="edge")
async def cmd_edge(ctx):
    """Show the bot's statistical trading edge and expectancy. (v9.2)"""
    signals = _read_signals()
    closed = [s for s in signals if s.get("outcome") in ("WIN", "LOSS")]
    total = len(closed)

    SIGNIFICANCE_THRESHOLD = 30

    embed = discord.Embed(
        title=" Statistical Edge Calculator",
        description="Edge = (Win Rate  Avg Win%)  (Loss Rate  Avg Loss%)",
        color=0x00897B,
        timestamp=datetime.now(timezone.utc)
    )

    if total == 0:
        embed.add_field(name="No Data", value="No closed trades to analyze yet. Run the bot and let trades close!", inline=False)
        embed.set_footer(text=f"Chartwise v10.0  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
        await ctx.send(embed=embed)
        return

    wins = [s for s in closed if s["outcome"] == "WIN"]
    losses = [s for s in closed if s["outcome"] == "LOSS"]

    win_rate = len(wins) / total
    loss_rate = len(losses) / total

    # PnL% is stored in TRADE_HISTORY; fall back to R-multiple if available
    def _get_pnl(sig: dict) -> float | None:
        """Get PnL% from signal. Prefer pnl_r (R-multiple); approximate from price levels."""
        pnl_r = sig.get("pnl_r")
        if pnl_r is not None:
            entry = sig.get("entry", 0)
            sl = sig.get("sl", 0)
            if entry and sl and entry != sl:
                sl_dist_pct = abs(entry - sl) / entry * 100
                return pnl_r * sl_dist_pct
        return None

    win_pnls = [p for s in wins if (p := _get_pnl(s)) is not None and p > 0]
    loss_pnls = [abs(p) for s in losses if (p := _get_pnl(s)) is not None]

    # Fall back to R-multiples if no pnl_pct
    if not win_pnls:
        win_r = [s.get("pnl_r", 1.5) for s in wins if s.get("pnl_r")]
        avg_win_pct = statistics.mean(win_r) * 1.5 if win_r else 1.5  # default 1.5%
    else:
        avg_win_pct = statistics.mean(win_pnls)

    if not loss_pnls:
        avg_loss_pct = 1.0  # default 1%
    else:
        avg_loss_pct = statistics.mean(loss_pnls)

    edge_pct = (win_rate * avg_win_pct) - (loss_rate * avg_loss_pct)

    # R-expectancy (per $1 risked)
    avg_win_r = statistics.mean([s.get("pnl_r", 1.5) for s in wins if s.get("pnl_r")]) if wins else 1.5
    avg_loss_r = abs(statistics.mean([s.get("pnl_r", -1.0) for s in losses if s.get("pnl_r")])) if losses else 1.0
    expectancy_r = (win_rate * avg_win_r) - (loss_rate * avg_loss_r)

    # Edge interpretation
    if edge_pct > 0.5:
        edge_label = " Positive Edge  bot is profitable in expectancy"
    elif edge_pct > 0:
        edge_label = " Marginal Edge  small positive expectancy, needs more data"
    else:
        edge_label = " Negative Edge  system losing in expectancy, review settings"

    embed.add_field(
        name=" Core Metrics",
        value=(
            f"Total Closed Trades: **{total}**\n"
            f"Win Rate: **{win_rate*100:.1f}%** ({len(wins)}W / {len(losses)}L)\n"
            f"Avg Win: **{avg_win_pct:.2f}%** | Avg Loss: **{avg_loss_pct:.2f}%**"
        ),
        inline=False
    )
    embed.add_field(
        name=" Edge Calculation",
        value=(
            f"Edge = ({win_rate*100:.1f}%  {avg_win_pct:.2f}%)  ({loss_rate*100:.1f}%  {avg_loss_pct:.2f}%)\n"
            f"**Edge = {edge_pct:+.3f}%** per trade\n"
            f"R-Expectancy: **{expectancy_r:+.3f}R** per trade risked\n"
            f"{edge_label}"
        ),
        inline=False
    )
    embed.add_field(
        name=" What This Means",
        value=(
            f"A positive edge means for every trade taken, the bot expects to gain **{edge_pct:.3f}%** on average.\n"
            f"Compounded over many trades, even a small positive edge builds account equity.\n"
            f"R-Expectancy of {expectancy_r:+.3f}R means you expect to make {expectancy_r:.2f} your risk per trade."
        ),
        inline=False
    )

    # Statistical significance note
    if total < SIGNIFICANCE_THRESHOLD:
        remaining = SIGNIFICANCE_THRESHOLD - total
        embed.add_field(
            name=" Statistical Significance",
            value=(
                f"Only **{total}/{SIGNIFICANCE_THRESHOLD}** trades needed to trust statistics.\n"
                f"Need **{remaining} more closed trades** before these numbers are statistically meaningful.\n"
                f"Rule of thumb: **30+ closed trades** for reliable win rate and edge estimates."
            ),
            inline=False
        )
    else:
        embed.add_field(
            name=" Statistical Significance",
            value=(
                f"**{total} closed trades**  sufficient sample size ({SIGNIFICANCE_THRESHOLD}).\n"
                f"These stats carry reasonable statistical weight. Edge reading is trustworthy."
            ),
            inline=False
        )

    embed.set_footer(text=f"Chartwise v10.0  !stats for full dashboard  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !edge  sent edge analysis to #{ctx.channel.name}")


# 
# v9.4 NEW COMMANDS
# 

@bot.command(name="calendar")
async def cmd_calendar(ctx, mode_arg: str = "week"):
    """
    v9.4 Feature 1: Trading activity calendar view.
    !calendar week   MonSun of current week, signals & trades per day + W/L indicator
    !calendar month  Full current month with same info
    """
    now_utc = datetime.now(timezone.utc)
    mode = mode_arg.lower().strip()
    if mode not in ("week", "month"):
        await ctx.send(" Usage: `!calendar week` or `!calendar month`")
        return

    # Build date range
    if mode == "week":
        # Monday of current week
        monday = now_utc - timedelta(days=now_utc.weekday())
        days = [monday + timedelta(days=i) for i in range(7)]
        title_str = f"Week of {monday.strftime('%d %b %Y')}"
    else:
        # Full current month
        first_of_month = now_utc.replace(day=1)
        # Days in month: go to next month day 1, subtract 1 day
        if first_of_month.month == 12:
            next_month = first_of_month.replace(year=first_of_month.year + 1, month=1)
        else:
            next_month = first_of_month.replace(month=first_of_month.month + 1)
        days_in_month = (next_month - first_of_month).days
        days = [first_of_month + timedelta(days=i) for i in range(days_in_month)]
        title_str = now_utc.strftime("%B %Y")

    # Build date -> {signals, wins, losses} from SIGNAL_LOG and TRADE_HISTORY
    cal_data: dict[str, dict] = {}
    for d in days:
        cal_data[d.strftime("%Y-%m-%d")] = {"signals": 0, "wins": 0, "losses": 0}

    # Count signals from SIGNAL_LOG
    for entry in list(SIGNAL_LOG):
        try:
            t = datetime.fromisoformat(entry.get("time", ""))
            if t.tzinfo is None:
                t = t.replace(tzinfo=timezone.utc)
            key = t.strftime("%Y-%m-%d")
            if key in cal_data:
                cal_data[key]["signals"] += 1
        except Exception:
            pass

    # Count wins/losses from TRADE_HISTORY
    for trade in list(TRADE_HISTORY):
        try:
            outcome = trade.get("outcome", "")
            ts = trade.get("closed_at") or trade.get("opened_at", "")
            if not ts:
                continue
            t = datetime.fromisoformat(ts)
            if t.tzinfo is None:
                t = t.replace(tzinfo=timezone.utc)
            key = t.strftime("%Y-%m-%d")
            if key in cal_data:
                if outcome == "WIN":
                    cal_data[key]["wins"] += 1
                elif outcome == "LOSS":
                    cal_data[key]["losses"] += 1
        except Exception:
            pass

    # Build display lines
    lines = []
    for d in days:
        key = d.strftime("%Y-%m-%d")
        info = cal_data.get(key, {"signals": 0, "wins": 0, "losses": 0})
        day_label = d.strftime("%a %-d%b")  # e.g. "Mon 6Oct"
        sigs = info["signals"]
        wins = info["wins"]
        losses = info["losses"]
        is_today = d.date() == now_utc.date()
        is_future = d.date() > now_utc.date()

        if is_future:
            lines.append(f"`{day_label}`  upcoming")
        elif sigs == 0 and wins == 0 and losses == 0:
            lines.append(f"`{day_label}`  No activity")
        else:
            wl_emoji = ""
            if wins > 0 and losses == 0:
                wl_emoji = ""
            elif losses > 0 and wins == 0:
                wl_emoji = ""
            elif wins > 0 and losses > 0:
                wl_emoji = ""
            today_tag = "  today" if is_today else ""
            parts = []
            if sigs > 0:
                parts.append(f" {sigs} signal{'s' if sigs != 1 else ''}")
            if wins > 0:
                parts.append(f" {wins}W")
            if losses > 0:
                parts.append(f" {losses}L")
            lines.append(f"`{day_label}` {wl_emoji} {' | '.join(parts)}{today_tag}")

    # Split into chunks if needed (Discord field limit: 1024 chars)
    embed = discord.Embed(
        title=f" Trading Calendar  {title_str}",
        description=f"Signals fired and trade outcomes per day (UTC).",
        color=0x7B68EE,
        timestamp=now_utc
    )
    chunk = []
    chunk_num = 1
    for line in lines:
        chunk.append(line)
        if len("\n".join(chunk)) > 900:
            embed.add_field(name=f"Days (part {chunk_num})", value="\n".join(chunk[:-1]), inline=False)
            chunk = [chunk[-1]]
            chunk_num += 1
    if chunk:
        field_name = "Days" if chunk_num == 1 else f"Days (part {chunk_num})"
        embed.add_field(name=field_name, value="\n".join(chunk), inline=False)

    # Summary totals
    total_sigs = sum(v["signals"] for v in cal_data.values())
    total_wins = sum(v["wins"] for v in cal_data.values())
    total_losses = sum(v["losses"] for v in cal_data.values())
    embed.add_field(
        name=" Period Totals",
        value=f"Signals: **{total_sigs}**  Wins: **{total_wins}**  Losses: **{total_losses}**",
        inline=False
    )
    embed.set_footer(text=f"Chartwise v10.0  !calendar week or month  {now_utc.strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !calendar {mode}  sent to #{ctx.channel.name}")


@bot.command(name="scoretable")
async def cmd_scoretable(ctx):
    """
    v9.4 Feature 3: Reference table of all scoring factors and their point values.
    Grouped by category so traders can understand what drives scores.
    """
    embed = discord.Embed(
        title=" Score Reference Table",
        description=(
            f"All scoring factors used by the Premium SMC/ICT and Standard EMA engines.\n"
            f"Current MIN_SCORE to fire: **{MIN_SCORE}**  Max theoretical: **~28**"
        ),
        color=0x7B68EE,
        timestamp=datetime.now(timezone.utc)
    )

    embed.add_field(
        name=" Structure (SMC/ICT Engine)",
        value=(
            " **Clean Liquidity Sweep**: +2 (wick only, body above level)\n"
            " **Dirty Liquidity Sweep**: +1 (body closed through level)\n"
            " **Break of Structure (BOS)**: +2 (structural confirmation)\n"
            " **Fair Value Gap (FVG)** hit: +2 (price in imbalance zone)\n"
            " **Order Block** (fresh 15c old): +1 (institutional zone)\n"
            " **Stale OB** (>50 candles): 1 (zone weakened)\n"
            " **SFP (Swing Failure Pattern)**: +2 (high-probability reversal)\n"
            " **Market Structure Shift (MSS)**: +2 (trend change confirmed)\n"
        ),
        inline=False
    )
    embed.add_field(
        name=" Momentum & Oscillators",
        value=(
            " **RSI Divergence** (strong, gap 5): +2\n"
            " **RSI Divergence** (weak): +1\n"
            " **MACD Cross** (crossover in signal direction): +1\n"
            " **RSI Oversold/Overbought** (< 30 / > 70): +1\n"
            " **Engulfing Candle**: +2 (body fully covers prior candle)\n"
            " **Hammer / Pin Bar**: +12 (wick rejection)\n"
            " **Three-Line Strike**: +2 (strong reversal pattern)\n"
            " **Inside Bar Breakout**: +1\n"
            " **5/5 Directional Candles aligned**: +2\n"
            " **4/5 Directional Candles aligned**: +1\n"
        ),
        inline=False
    )
    embed.add_field(
        name=" Volatility & Volume",
        value=(
            " **BB/KC Squeeze** (BB inside Keltner): +2 (explosive breakout imminent)\n"
            " **Volume Spike** (3 average): +2 (institutional participation)\n"
            " **Volume above average** (1.53): +1\n"
            " **4H Volume Accumulation** (rising directional vol): +1\n"
            " **POC** (price at Point of Control): +1 (HVN support/resistance)\n"
        ),
        inline=False
    )
    embed.add_field(
        name=" Multi-Timeframe (MTF)",
        value=(
            " **3/3 MTF Consensus** (5m+15m+1H aligned): +3 (perfect confluence)\n"
            " **2/3 MTF Consensus**: +2\n"
            " **15m Trend Aligns**: +1\n"
            " **15m Trend Diverges**: 1\n"
            " **Against 4H Trend**: 1 (fighting higher timeframe)\n"
            " **Against Weekly Trend**: 1 (42-bar SMA filter)\n"
            " **4H RSI Divergence** (strong): +2\n"
            " **4H RSI Divergence** (weak): +1\n"
            " **Ichimoku above/below cloud**: +12\n"
        ),
        inline=False
    )
    embed.add_field(
        name=" Regime & Context",
        value=(
            " **Ranging Market Regime**: 1 (breakout signals less reliable)\n"
            " **4H Candle Bias** (7/10 directional): +1\n"
            " **Cross-pair Alignment** (2+ pairs same direction): +1\n"
            " **Cross-pair Divergence** (2+ pairs opposite): 1\n"
            " **Correlated Risk** (2+ active same-dir trades): 2\n"
            " **Low Vol Regime** (ATR <0.5%): 1 (non-squeeze signals only)\n"
            " **High Vol Regime** (ATR >2%) + LONG: 1 (chaotic action)\n"
            " **Pattern Streak** (3 same pattern in a row): +1\n"
            " **Adaptive Penalty** (pattern has 3 SL hits): 1 per degraded reason\n"
        ),
        inline=False
    )
    embed.add_field(
        name=" Notes",
        value=(
            f" **MIN_SCORE** = **{MIN_SCORE}**  signals below this are filtered\n"
            f" Scores are additive; order of factors doesn't matter\n"
            f" Use `!sensitivity [1-5]` to shift the MIN_SCORE threshold\n"
            f" Use `!learn` to see which patterns have adaptive penalties"
        ),
        inline=False
    )
    embed.set_footer(text=f"Chartwise v10.0  !debug [pair] for live score breakdown  !learn for adaptive penalties")
    await ctx.send(embed=embed)
    print(f"[CMD] !scoretable  sent to #{ctx.channel.name}")


@bot.command(name="copy")
async def cmd_copy(ctx, pair_arg: str = None, ratio_arg: str = None):
    """
    v9.4 Feature 5: Copy trading size calculator.
    !copy BTC 0.5   shows 50% of the bot's recommended position size for BTC/USD
    !copy SOL 1.0   full size
    Usage: !copy [pair] [ratio]   ratio = 0.1 to 2.0
    """
    if pair_arg is None or ratio_arg is None:
        await ctx.send(
            " Usage: `!copy [pair] [ratio]`\n"
            "Example: `!copy BTC 0.5`  50% of recommended size for BTC/USD\n"
            "Ratio range: 0.1 (10%) to 2.0 (200%)"
        )
        return

    # Resolve pair
    pa = pair_arg.upper().strip()
    pair_obj = next((p for p in DYNAMIC_PAIRS if pa in p["label"] or pa == p["label"].split("/")[0]), None)
    if pair_obj is None:
        await ctx.send(f" Unknown pair `{pair_arg}`. Valid: {', '.join(p['label'] for p in DYNAMIC_PAIRS)}")
        return

    # Parse ratio
    try:
        ratio = float(ratio_arg)
        if not (0.05 <= ratio <= 5.0):
            await ctx.send(" Ratio must be between 0.05 (5%) and 5.0 (500%).")
            return
    except ValueError:
        await ctx.send(" Invalid ratio. Example: `!copy BTC 0.5`")
        return

    await ctx.trigger_typing()

    # Fetch current candles to get ATR
    candles = await fetch_candles(pair_obj, timeframe="5m")
    if not candles or len(candles) < 15:
        await ctx.send(f" Could not fetch candles for {pair_obj['label']}.")
        return

    atr_val = calc_atr(candles)
    current_price = candles[-1]["close"]
    pair_label = pair_obj["label"]

    if atr_val is None or current_price <= 0:
        await ctx.send(f" Could not compute ATR for {pair_label}.")
        return

    # Bot's standard sizing: 1% risk on ACCOUNT_SIZE with ATR-based SL (1 ATR)
    sl_distance = atr_val * 1.0   # default 1 ATR stop distance
    risk_amount = ACCOUNT_SIZE * DEFAULT_RISK_PCT  # 1% of account
    sl_pct = sl_distance / current_price if current_price > 0 else 0.01

    # Full recommended position size
    if sl_pct > 0:
        full_notional = risk_amount / sl_pct  # USD notional for full size
        full_units = full_notional / current_price
    else:
        full_notional = 0
        full_units = 0

    # Scaled by ratio
    copy_notional = full_notional * ratio
    copy_units = full_units * ratio
    copy_risk = risk_amount * ratio

    # Format units
    def fmt_units(u: float) -> str:
        return f"{u:.6f}" if u < 0.01 else (f"{u:.4f}" if u < 1 else f"{u:.2f}")

    ratio_pct = ratio * 100

    embed = discord.Embed(
        title=f" Copy Size Calculator  {pair_label}",
        description=(
            f"Copying at **{ratio_pct:.0f}%** of the bot's recommended position size.\n"
            f"Based on **${ACCOUNT_SIZE:,.0f}** account  **1% risk**  **1 ATR stop**"
        ),
        color=0x00897B,
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name=" Current Price", value=price_fmt(pair_label, current_price), inline=True)
    embed.add_field(name=" ATR (5m)", value=price_fmt(pair_label, atr_val), inline=True)
    embed.add_field(name=" Est. SL Distance", value=f"{sl_pct*100:.3f}%  ({price_fmt(pair_label, sl_distance)})", inline=True)

    embed.add_field(
        name=" Bot's Full Recommended Size",
        value=(
            f"Notional: **${full_notional:,.2f}**\n"
            f"Units: **{fmt_units(full_units)}**\n"
            f"Risk at 1%: **${risk_amount:.2f}**"
        ),
        inline=False
    )
    embed.add_field(
        name=f" Your Copy Size ({ratio_pct:.0f}%)",
        value=(
            f"Notional: **${copy_notional:,.2f}**\n"
            f"Units: **{fmt_units(copy_units)}**\n"
            f"Risk at ratio: **${copy_risk:.2f}**"
        ),
        inline=False
    )
    embed.add_field(
        name=" Tip",
        value=(
            f"Set your stop loss **{price_fmt(pair_label, sl_distance)}** away from entry.\n"
            f"Use `!account [amount]` to update the account size this is based on.\n"
            f"Use `!rrhelper` to verify R:R before entering."
        ),
        inline=False
    )
    embed.set_footer(text=f"Chartwise v10.0  !copy [pair] [ratio]  Not financial advice")
    await ctx.send(embed=embed)
    print(f"[CMD] !copy {pair_label} {ratio}  sent to #{ctx.channel.name}")


# 
# v9.5 NEW COMMANDS
# 

@bot.command(name="backtest2")
async def cmd_backtest2(ctx, pair_arg: str = None, days_arg: str = None):
    """
    v9.5 Feature 1: Enhanced backtest  fetches real 15m historical candles,
    runs analyze() on each candle in a rolling window, simulates entries at
    signal entry price, tracks SL/T1/T2 hits.
    Shows: win rate, Sharpe ratio, max consecutive wins/losses, profit factor.
    Usage: !backtest2 [pair=BTC] [days=7]  (max 30 days)
    """
    import math

    # Parse pair
    pair_obj = None
    if pair_arg:
        pa = pair_arg.upper().strip()
        for p in DYNAMIC_PAIRS:
            if pa in p["label"] or pa == p["label"].split("/")[0]:
                pair_obj = p
                break
    if pair_obj is None:
        pair_obj = next((p for p in DYNAMIC_PAIRS if "BTC" in p["label"]), DYNAMIC_PAIRS[0])

    # Parse days
    try:
        days = int(days_arg) if days_arg else 7
        days = max(1, min(days, 30))
    except ValueError:
        days = 7

    pair_label = pair_obj["label"]
    await ctx.trigger_typing()

    # Fetch 15m candles  each candle = 15 min, so days * 96 candles per day
    # Coinbase returns at most 300 candles per call; for extended history we use what's available.
    candles_15m = await fetch_candles(pair_obj, timeframe="15m")
    if not candles_15m or len(candles_15m) < 50:
        await ctx.send(f" Could not fetch 15m candles for {pair_label}.")
        return

    # Limit to requested days worth of 15m candles (96 per day)
    max_candles = days * 96
    if len(candles_15m) > max_candles:
        candles_15m = candles_15m[-max_candles:]

    # Rolling window analysis  need at least 30 candles of context
    WINDOW = 50
    signals_bt: list[dict] = []

    for i in range(WINDOW, len(candles_15m)):
        window_candles = candles_15m[:i]
        sig = analyze(window_candles, pair_label)
        if sig is None or sig.get("near_miss"):
            continue
        # Simulate outcome using subsequent candles
        entry = sig["entry"]
        sl    = sig["sl"]
        t1    = sig["t1"]
        t2    = sig["t2"]
        direction = sig["direction"]  # "long" or "short"

        outcome = "OPEN"
        ret_pct = 0.0
        for future_c in candles_15m[i:i + 20]:  # look forward up to 20 candles (5h)
            h, l = future_c["high"], future_c["low"]
            if direction == "long":
                if l <= sl:
                    outcome = "LOSS"
                    ret_pct = (sl - entry) / entry * 100 if entry > 0 else -1.0
                    break
                elif h >= t2:
                    outcome = "WIN"
                    ret_pct = (t2 - entry) / entry * 100 if entry > 0 else 2.0
                    break
                elif h >= t1:
                    outcome = "WIN_T1"
                    ret_pct = (t1 - entry) / entry * 100 if entry > 0 else 1.0
                    break
            else:  # short
                if h >= sl:
                    outcome = "LOSS"
                    ret_pct = (entry - sl) / entry * 100 if entry > 0 else -1.0
                    break
                elif l <= t2:
                    outcome = "WIN"
                    ret_pct = (entry - t2) / entry * 100 if entry > 0 else 2.0
                    break
                elif l <= t1:
                    outcome = "WIN_T1"
                    ret_pct = (entry - t1) / entry * 100 if entry > 0 else 1.0
                    break

        if outcome == "OPEN":
            continue  # exclude still-open trades

        signals_bt.append({
            "outcome": outcome,
            "ret_pct": ret_pct,
            "score": sig.get("score", 0),
        })

    if len(signals_bt) < 3:
        await ctx.send(
            f" Not enough completed trades in the backtest window for {pair_label} "
            f"over {days}d. Try a longer period or wait for more data."
        )
        return

    # Compute stats
    wins = [t for t in signals_bt if t["outcome"].startswith("WIN")]
    losses = [t for t in signals_bt if t["outcome"] == "LOSS"]
    total = len(signals_bt)
    wr = len(wins) / total * 100

    returns = [t["ret_pct"] for t in signals_bt]
    avg_ret = statistics.mean(returns)
    try:
        std_ret = statistics.stdev(returns)
        sharpe = avg_ret / std_ret if std_ret > 0 else 0.0
    except Exception:
        sharpe = 0.0

    gross_wins  = sum(t["ret_pct"] for t in wins) if wins else 0.0
    gross_losses = abs(sum(t["ret_pct"] for t in losses)) if losses else 0.0
    profit_factor = (gross_wins / gross_losses) if gross_losses > 0 else float("inf")

    # Max consecutive wins/losses
    max_consec_wins = 0
    max_consec_losses = 0
    cur_w = 0
    cur_l = 0
    for t in signals_bt:
        if t["outcome"].startswith("WIN"):
            cur_w += 1
            cur_l = 0
            max_consec_wins = max(max_consec_wins, cur_w)
        else:
            cur_l += 1
            cur_w = 0
            max_consec_losses = max(max_consec_losses, cur_l)

    # Actual date range used
    actual_days = len(candles_15m) / 96.0

    embed = discord.Embed(
        title=f" Enhanced Backtest  {pair_label}",
        description=(
            f"Rolling-window analyze() on **{len(candles_15m)} real 15m candles** (~{actual_days:.1f}d).\n"
            f"**{total} completed signals** simulated (entrySL/T1/T2)."
        ),
        color=0x2ECC71,
        timestamp=datetime.now(timezone.utc)
    )
    wr_emoji = "" if wr >= 55 else ("" if wr >= 45 else "")
    embed.add_field(name=" Win Rate", value=f"{wr_emoji} **{wr:.1f}%**  ({len(wins)}W / {len(losses)}L)", inline=True)
    embed.add_field(name=" Avg Return / Trade", value=f"{avg_ret:+.2f}%", inline=True)
    embed.add_field(name=" Std Dev of Returns", value=f"{std_ret:.2f}%", inline=True)

    sharpe_emoji = "" if sharpe > 0.5 else ("" if sharpe > 0 else "")
    embed.add_field(name=" Sharpe Ratio (simplified)", value=f"{sharpe_emoji} **{sharpe:.2f}**  (avg ret / std dev)", inline=True)

    pf_str = f"{profit_factor:.2f}" if profit_factor != float("inf") else ""
    pf_emoji = "" if profit_factor > 1.5 else ("" if profit_factor > 1.0 else "")
    embed.add_field(name=" Profit Factor", value=f"{pf_emoji} **{pf_str}**  (gross wins / gross losses)", inline=True)

    embed.add_field(
        name=" Streaks",
        value=f"Max consecutive wins: **{max_consec_wins}**\nMax consecutive losses: **{max_consec_losses}**",
        inline=True
    )
    embed.add_field(
        name=" Interpretation",
        value=(
            f"Sharpe > 0.5 = good risk-adjusted returns.\n"
            f"Profit factor > 1.5 = more gross profit than loss.\n"
            f"This backtest uses real candles but simplified execution (no slippage/fees)."
        ),
        inline=False
    )
    embed.set_footer(text=f"Chartwise v10.0  Enhanced backtest  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !backtest2 {pair_label} {days}d  {total} signals, WR={wr:.1f}% Sharpe={sharpe:.2f}")


@bot.command(name="montecarlo")
async def cmd_montecarlo(ctx, n_sims_arg: str = None):
    """
    v9.5 Feature 3: Monte Carlo simulation of the next 50 trades.
    Samples from TRADE_HISTORY win rate and avg win/loss % to simulate N paths.
    Shows: median, 10th/90th percentile outcome, probability of ruin.
    Usage: !montecarlo [n_sims=1000]  (max 5000)
    """
    import random
    import math

    try:
        n_sims = int(n_sims_arg) if n_sims_arg else 1000
        n_sims = max(100, min(n_sims, 5000))
    except ValueError:
        n_sims = 1000

    closed = [t for t in TRADE_HISTORY if t.get("outcome") in ("WIN", "LOSS")]
    if len(closed) < 5:
        await ctx.send(
            f" Need at least 5 closed trades for Monte Carlo  only {len(closed)} available. "
            f"Trades accumulate as the bot monitors positions."
        )
        return

    wins_hist   = [t for t in closed if t.get("outcome") == "WIN"]
    losses_hist = [t for t in closed if t.get("outcome") == "LOSS"]
    win_rate    = len(wins_hist) / len(closed)

    # Average win/loss % from history
    def safe_pnl(t):
        p = t.get("pnl_pct") or t.get("pnl_r")
        return float(p) if p is not None else 0.0

    avg_win_pct  = statistics.mean(safe_pnl(t) for t in wins_hist) if wins_hist else 2.0
    avg_loss_pct = abs(statistics.mean(safe_pnl(t) for t in losses_hist)) if losses_hist else 1.0
    # Ensure sign conventions
    if avg_win_pct < 0:
        avg_win_pct = abs(avg_win_pct)
    if avg_loss_pct < 0:
        avg_loss_pct = abs(avg_loss_pct)

    N_TRADES = 50
    START_BALANCE = 1000.0  # normalized starting equity

    final_balances = []
    ruin_count = 0

    for _ in range(n_sims):
        balance = START_BALANCE
        ruined = False
        for _trade in range(N_TRADES):
            if random.random() < win_rate:
                balance *= (1 + avg_win_pct / 100)
            else:
                balance *= (1 - avg_loss_pct / 100)
            if balance <= 0:
                ruined = True
                break
        if ruined:
            ruin_count += 1
            final_balances.append(0.0)
        else:
            final_balances.append(balance)

    final_balances.sort()
    median_bal  = statistics.median(final_balances)
    p10_bal     = final_balances[int(len(final_balances) * 0.10)]
    p90_bal     = final_balances[int(len(final_balances) * 0.90)]
    prob_ruin   = ruin_count / n_sims * 100

    def pct_change(bal: float) -> str:
        if bal <= 0:
            return "100%"
        chg = (bal / START_BALANCE - 1) * 100
        sign = "+" if chg >= 0 else ""
        return f"{sign}{chg:.1f}%"

    # Simple bar for expected outcome
    exp_outcome = (median_bal / START_BALANCE - 1) * 100
    bar_len = 10
    filled = max(0, min(bar_len, int((exp_outcome + 50) / 10)))  # center at 0%
    bar = "" * filled + "" * (bar_len - filled)

    embed = discord.Embed(
        title=f" Monte Carlo  {n_sims:,} Simulations  {N_TRADES} Trades",
        description=(
            f"Sampling from **{len(closed)} historical trades**: "
            f"WR={win_rate*100:.1f}%  Avg win={avg_win_pct:.2f}%  Avg loss={avg_loss_pct:.2f}%\n"
            f"Starting equity: **${START_BALANCE:,.0f}** (normalized)"
        ),
        color=0x7C4DFF,
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(
        name=" Outcome After 50 Trades",
        value=(
            f" **Median:** ${median_bal:,.1f}  ({pct_change(median_bal)})\n"
            f" **10th pct (bad luck):** ${p10_bal:,.1f}  ({pct_change(p10_bal)})\n"
            f" **90th pct (good luck):** ${p90_bal:,.1f}  ({pct_change(p90_bal)})"
        ),
        inline=False
    )
    ruin_emoji = "" if prob_ruin < 5 else ("" if prob_ruin < 15 else "")
    embed.add_field(name=f"{ruin_emoji} Probability of Ruin", value=f"**{prob_ruin:.1f}%** of simulations went to $0", inline=True)
    embed.add_field(
        name=" Expected Outcome",
        value=f"`{bar}`  {pct_change(median_bal)} (median)",
        inline=False
    )
    embed.add_field(
        name=" Interpretation",
        value=(
            f"Prob of ruin < 5% = low risk of blow-up at current stats.\n"
            f"90th pct shows best-case trajectory; 10th pct shows downside.\n"
            f"Based on historical trade stats  improve WR or R:R to shift distribution right."
        ),
        inline=False
    )
    embed.set_footer(text=f"Chartwise v10.0  Monte Carlo  {n_sims:,} paths  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !montecarlo {n_sims}  WR={win_rate*100:.1f}% median={pct_change(median_bal)} ruin={prob_ruin:.1f}%")


#  v9.7 Feature 2: !ote command 

@bot.command(name="ote")
async def cmd_ote(ctx, pair_arg: str = None):
    """
    v9.7 Feature 2: Show ICT Optimal Trade Entry zone for each pair on 15m and 1H.
    Displays swing high/low, OTE range (61.879% Fib), and current price vs zone.
    Usage: !ote [pair]  (omit pair to show all)
    """
    if pair_arg:
        pa = pair_arg.upper()
        target_pairs = [p for p in DYNAMIC_PAIRS if pa in p["label"].upper()]
        if not target_pairs:
            await ctx.send(f" Unknown pair `{pair_arg}`. Use BTC, SOL, or XRP.")
            return
    else:
        target_pairs = list(DYNAMIC_PAIRS)

    for pair in target_pairs:
        label = pair["label"]
        await ctx.send(f" Computing OTE zones for **{label}**...")
        try:
            candles_15m = await fetch_candles(pair, "15m")
            candles_1h  = await fetch_candles(pair, "1h")

            embed = discord.Embed(
                title=f" ICT Optimal Trade Entry  {label}",
                description="OTE Zone = 61.8%79% Fibonacci retracement of last major swing",
                color=0x7B68EE,
                timestamp=datetime.now(timezone.utc),
            )

            for tf_label, candles in [("15m", candles_15m), ("1H", candles_1h)]:
                if not candles or len(candles) < 20:
                    embed.add_field(name=f" {tf_label}", value="Insufficient data", inline=False)
                    continue

                current_price = candles[-1]["close"]

                for direction in ("long", "short"):
                    ote = detect_ote_zone(candles, direction)
                    if ote is None:
                        continue

                    in_ote = ote["in_ote"]
                    dir_label = "Bullish" if direction == "long" else "Bearish"

                    if in_ote:
                        zone_status = " **IN OTE ZONE**"
                        color = 0x00E676
                    elif (direction == "long" and current_price < ote["ote_low"]):
                        zone_status = " Price below OTE (not yet retraced to zone)"
                    elif (direction == "long" and current_price > ote["ote_high"]):
                        zone_status = " Price above OTE zone"
                    elif (direction == "short" and current_price > ote["ote_high"]):
                        zone_status = " Price above OTE (not yet retraced to zone)"
                    else:
                        zone_status = " Price below OTE zone"

                    dist_low  = (current_price - ote["ote_low"])  / ote["ote_low"]  * 100
                    dist_high = (ote["ote_high"] - current_price) / current_price * 100

                    val_lines = [
                        f"Swing Low: `{price_fmt(label, ote['swing_low'])}`   Swing High: `{price_fmt(label, ote['swing_high'])}`",
                        f"OTE Zone: `{price_fmt(label, ote['ote_low'])}`  `{price_fmt(label, ote['ote_high'])}`",
                        f"Current:  `{price_fmt(label, current_price)}`",
                        f"Status: {zone_status}",
                        f"Swing formed: ~{ote['candles_ago']} candles ago",
                    ]
                    embed.add_field(
                        name=f" {tf_label}  {dir_label}",
                        value="\n".join(val_lines),
                        inline=False
                    )
                    if in_ote:
                        embed.color = 0x00E676  # green when in OTE

            embed.set_footer(text=f"Chartwise v10.0  ICT OTE  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f" {label}: Error computing OTE  {e}")
            print(f"[ERROR] cmd_ote {label}: {e}")


#  v9.7 Feature 4: !po3 command 

@bot.command(name="po3")
async def cmd_po3(ctx, pair_arg: str = None):
    """
    v9.7 Feature 4: Show Power of Three (PO3) phase status for each pair on 15m and 1H.
    Phases: Accumulation  Manipulation  Distribution.
    Usage: !po3 [pair]  (omit pair to show all)
    """
    if pair_arg:
        pa = pair_arg.upper()
        target_pairs = [p for p in DYNAMIC_PAIRS if pa in p["label"].upper()]
        if not target_pairs:
            await ctx.send(f" Unknown pair `{pair_arg}`. Use BTC, SOL, or XRP.")
            return
    else:
        target_pairs = list(DYNAMIC_PAIRS)

    for pair in target_pairs:
        label = pair["label"]
        try:
            candles_15m = await fetch_candles(pair, "15m")
            candles_1h  = await fetch_candles(pair, "1h")

            # Choose embed color based on detection
            embed_color = 0x7B68EE  # default purple
            po3_15m = detect_power_of_three(candles_15m) if candles_15m and len(candles_15m) >= 15 else {"detected": False, "phase": None, "direction": None, "range_high": None, "range_low": None, "confidence": "low", "description": "No data"}
            po3_1h  = detect_power_of_three(candles_1h)  if candles_1h  and len(candles_1h)  >= 15 else {"detected": False, "phase": None, "direction": None, "range_high": None, "range_low": None, "confidence": "low", "description": "No data"}

            if po3_15m.get("detected") and po3_15m.get("phase") == "distribution":
                embed_color = 0x00E676 if po3_15m["direction"] == "long" else 0xFF5252
            elif po3_1h.get("detected") and po3_1h.get("phase") == "distribution":
                embed_color = 0x00E676 if po3_1h["direction"] == "long" else 0xFF5252

            embed = discord.Embed(
                title=f" ICT Power of Three  {label}",
                description="Accumulation  Manipulation  Distribution pattern detection",
                color=embed_color,
                timestamp=datetime.now(timezone.utc),
            )

            for tf_label, po3 in [("15m", po3_15m), ("1H", po3_1h)]:
                phase_emoji = {
                    "accumulation": "",
                    "manipulation": "",
                    "distribution": "",
                    None: "",
                }.get(po3.get("phase"), "")

                conf_emoji = {"high": "", "medium": "", "low": ""}.get(po3.get("confidence", "low"), "")

                if po3.get("range_high") and po3.get("range_low"):
                    range_str = f"`{po3['range_low']:.4f}`  `{po3['range_high']:.4f}`"
                else:
                    range_str = "No range detected"

                dir_str = (" Bullish (long)" if po3.get("direction") == "long"
                           else " Bearish (short)" if po3.get("direction") == "short"
                           else "")

                val_lines = [
                    f"**Phase:** {phase_emoji} {(po3.get('phase') or 'None').title()}",
                    f"**Consolidation Range:** {range_str}",
                    f"**Setup Direction:** {dir_str}",
                    f"**Confidence:** {conf_emoji} {po3.get('confidence', 'low').title()}",
                    f"**Description:** {po3.get('description', '')}",
                ]
                embed.add_field(
                    name=f" {tf_label}",
                    value="\n".join(val_lines),
                    inline=False
                )

            embed.set_footer(text=f"Chartwise v10.0  ICT PO3  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f" {label}: Error computing PO3  {e}")
            print(f"[ERROR] cmd_po3 {label}: {e}")


#  v9.7 Feature 6: !opens command 

@bot.command(name="opens")
async def cmd_opens(ctx):
    """
    v9.7 Feature 6: Show last 7 daily opens and last 4 weekly opens for all pairs.
    Daily/weekly opening prices are key ICT liquidity levels.
    Usage: !opens
    """
    if not DYNAMIC_PAIRS:
        await ctx.send(" No pairs configured.")
        return

    # Fetch current prices for all pairs
    current_prices = {}
    for pair in DYNAMIC_PAIRS:
        try:
            candles = await fetch_candles(pair, "15m")
            if candles:
                current_prices[pair["label"]] = candles[-1]["close"]
        except Exception:
            pass

    embed = discord.Embed(
        title=" Opening Prices  NWOG / NDOG",
        description=(
            "New Week Opening Gap (NWOG) & New Day Opening Gap (NDOG).\n"
            "Key ICT liquidity levels  price often revisits these zones."
        ),
        color=0x7C4DFF,
        timestamp=datetime.now(timezone.utc),
    )

    has_data = False
    for pair in DYNAMIC_PAIRS:
        label = pair["label"]
        cur   = current_prices.get(label, 0)
        lines = []

        # Daily opens (up to 7)
        if label in DAILY_OPENS and DAILY_OPENS[label]:
            d_entries = list(DAILY_OPENS[label])
            lines.append("**Daily Opens (last 7):**")
            for entry in reversed(d_entries):
                dp = entry["price"]
                pct = (cur - dp) / dp * 100 if dp > 0 and cur > 0 else 0
                marker = "  near!" if abs(pct) < 0.3 else ""
                lines.append(f"  `{entry['time_utc'][:10]}`  {price_fmt(label, dp)} ({pct:+.2f}%){marker}")
        else:
            lines.append("**Daily Opens:** No data recorded yet (recorded at 00:00 UTC daily)")

        # Weekly opens (up to 4)
        if label in WEEKLY_OPENS and WEEKLY_OPENS[label]:
            w_entries = list(WEEKLY_OPENS[label])
            lines.append("**Weekly Opens (last 4):**")
            for entry in reversed(w_entries):
                wp = entry["price"]
                pct = (cur - wp) / wp * 100 if wp > 0 and cur > 0 else 0
                marker = "  near!" if abs(pct) < 0.3 else ""
                lines.append(f"  `{entry['time_utc'][:10]}`  {price_fmt(label, wp)} ({pct:+.2f}%){marker}")
        else:
            lines.append("**Weekly Opens:** No data yet (recorded Monday 00:00 UTC)")

        if cur > 0:
            lines.append(f"*Current price: {price_fmt(label, cur)}*")

        embed.add_field(
            name=f" {label}",
            value="\n".join(lines) if lines else "No data",
            inline=False
        )
        has_data = True

    if not has_data:
        embed.description += "\n\n No opening price data yet. Data is recorded automatically at 00:00 UTC."

    embed.set_footer(text=f"Chartwise v10.0  Opens recorded at 00:00 UTC daily  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)


@bot.command(name="add")
async def cmd_add_trade(ctx, pair_arg: str = None, entry_arg: str = None,
                        sl_arg: str = None, t1_arg: str = None, t2_arg: str = None,
                        direction_arg: str = None):
    """
    v9.5 Feature 5: Manually add a trade to active_trades.
    Useful when already in a position before the bot started.
    Usage: !add [pair] [entry] [sl] [t1] [t2] [long|short]
    Example: !add BTC 67500 66800 68200 69000 long
    """
    global _daily_opened

    if not all([pair_arg, entry_arg, sl_arg, t1_arg, t2_arg, direction_arg]):
        await ctx.send(
            " Usage: `!add [pair] [entry] [sl] [t1] [t2] [long|short]`\n"
            "Example: `!add BTC 67500 66800 68200 69000 long`"
        )
        return

    # Resolve pair
    pa = pair_arg.upper().strip()
    pair_obj = next((p for p in DYNAMIC_PAIRS if pa in p["label"] or pa == p["label"].split("/")[0]), None)
    if pair_obj is None:
        await ctx.send(f" Unknown pair `{pair_arg}`. Valid: {', '.join(p['label'] for p in DYNAMIC_PAIRS)}")
        return
    pair_label = pair_obj["label"]

    # Parse numeric values
    try:
        entry = float(entry_arg)
        sl    = float(sl_arg)
        t1    = float(t1_arg)
        t2    = float(t2_arg)
    except ValueError:
        await ctx.send(" Entry, SL, T1, T2 must all be valid numbers.")
        return

    direction_raw = direction_arg.lower().strip()
    if direction_raw not in ("long", "short"):
        await ctx.send(" Direction must be `long` or `short`.")
        return
    direction = direction_raw.upper()

    # Validate logic
    if direction == "LONG":
        if not (sl < entry < t1 < t2):
            await ctx.send(" For LONG: SL < Entry < T1 < T2 required.")
            return
    else:
        if not (t2 < t1 < entry < sl):
            await ctx.send(" For SHORT: T2 < T1 < Entry < SL required.")
            return

    if pair_label in active_trades:
        await ctx.send(f" There is already an active trade for {pair_label}. Close it with `!close {pa}` first.")
        return

    # Build trade dict matching update_active_trades expectations
    sig_id = str(uuid.uuid4())[:8]
    sl_dist = abs(entry - sl)
    trade = {
        "sig_id": sig_id,
        "direction": direction,
        "entry": entry,
        "sl": sl,
        "t1": t1,
        "t2": t2,
        "score": 0,
        "rating": "M",  # Manual
        "reasons": [" Manually added via !add command"],
        "engine": "manual",
        "opened_at": datetime.now(timezone.utc).isoformat(),
        "t1_hit": False,
        "atr": sl_dist,  # approx
        "sl_atr_mult": 1.0,
        "manual": True,
    }
    active_trades[pair_label] = trade
    _daily_opened += 1

    # Log the signal so it appears in !log
    log_signal(pair_label, {
        "direction": direction_raw,
        "score": 0,
        "rating": "M",
        "entry": entry,
        "sl": sl,
        "t1": t1,
        "t2": t2,
        "reasons": [" Manually added via !add command"],
    }, engine="manual", htf_trend="MANUAL")

    color = 0x00E676 if direction == "LONG" else 0xFF5252
    dir_emoji = "" if direction == "LONG" else ""
    embed = discord.Embed(
        title=f" Manual Trade Added  {pair_label}",
        description=f"{dir_emoji} **{direction}** position added to active monitoring.",
        color=color,
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name=" Entry",     value=price_fmt(pair_label, entry), inline=True)
    embed.add_field(name=" Stop Loss", value=price_fmt(pair_label, sl),    inline=True)
    embed.add_field(name=" Target 1",  value=price_fmt(pair_label, t1),    inline=True)
    embed.add_field(name=" Target 2",  value=price_fmt(pair_label, t2),    inline=True)
    sl_pct = abs(entry - sl) / entry * 100 if entry > 0 else 0
    t2_pct = abs(t2 - entry) / entry * 100 if entry > 0 else 0
    rr = abs(t2 - entry) / abs(entry - sl) if abs(entry - sl) > 0 else 0
    embed.add_field(name="SL Distance", value=f"{sl_pct:.2f}%", inline=True)
    embed.add_field(name="R:R to T2",   value=f"1 : {rr:.2f}", inline=True)
    embed.add_field(
        name=" Monitoring",
        value=(
            "This trade is now being monitored by `update_active_trades`.\n"
            "The bot will post SL/T1/T2 alerts as price hits each level.\n"
            "Use `!snapshot` to check status  `!close` to exit manually."
        ),
        inline=False
    )
    embed.set_footer(text=f"Chartwise v10.0  Manual add by {ctx.author}  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
    await ctx.send(embed=embed)
    print(f"[CMD] !add {pair_label} {direction} entry={entry} sl={sl} t1={t1} t2={t2} by {ctx.author}")


#
# v10.0: OUTCOME TRACKER, WEIGHT REBALANCER, LEARNING SYNC
#

import subprocess
import sys as _sys

def rebalance_weights():
    """v10.0: Read pattern_performance and update SCORE_MULTIPLIERS based on win rates."""
    global SCORE_MULTIPLIERS
    for pattern, data in pattern_performance.items():
        wins = data.get("wins", 0)
        losses = data.get("losses", 0)
        total = wins + losses
        if total < 10:
            continue
        wr = wins / total
        current = SCORE_MULTIPLIERS.get(pattern, 1.0)
        if wr > 0.65:
            new_val = min(current + 0.2, 3.0)  # max +2.0 above base 1.0
        elif wr < 0.35:
            new_val = max(current - 0.2, 0.0)  # max -1.0 below base 1.0 (floor 0.0)
        else:
            new_val = current
        SCORE_MULTIPLIERS[pattern] = round(new_val, 2)

    try:
        WEIGHTS_FILE.write_text(json.dumps(SCORE_MULTIPLIERS, indent=2))
        print(f"[REBALANCE] Weights saved to {WEIGHTS_FILE}: {SCORE_MULTIPLIERS}")
    except Exception as e:
        print(f"[WARN] Could not save weights file: {e}")

    # Trigger learning sync to GitHub
    sync_learning_to_github()


def sync_learning_to_github():
    """v10.0: Commit and push chartwise_learning.json and chartwise_weights.json to GitHub."""
    git_exe = r"C:\Program Files\Git\cmd\git.exe" if _sys.platform == "win32" else "git"
    bot_dir = str(Path(__file__).parent)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    try:
        r1 = subprocess.run(
            [git_exe, "add", "chartwise_learning.json", "chartwise_weights.json"],
            cwd=bot_dir, capture_output=True, text=True, timeout=30
        )
        if r1.returncode != 0:
            print(f"[SYNC] git add failed: {r1.stderr.strip()}")
            return False, r1.stderr.strip()

        r2 = subprocess.run(
            [git_exe, "commit", "-m", f"auto: learning sync [{ts}]"],
            cwd=bot_dir, capture_output=True, text=True, timeout=30
        )
        if r2.returncode != 0 and "nothing to commit" not in r2.stdout + r2.stderr:
            print(f"[SYNC] git commit failed: {r2.stderr.strip()}")
            return False, r2.stderr.strip()

        r3 = subprocess.run(
            [git_exe, "push", "origin", "main"],
            cwd=bot_dir, capture_output=True, text=True, timeout=60
        )
        if r3.returncode != 0:
            print(f"[SYNC] git push failed: {r3.stderr.strip()}")
            return False, r3.stderr.strip()

        print(f"[SYNC] Learning data pushed to GitHub at {ts}")
        return True, "OK"
    except Exception as e:
        print(f"[SYNC] Exception during git sync: {e}")
        return False, str(e)


@tasks.loop(minutes=5)
async def outcome_tracker():
    """v10.0: Every 5 min, check open signals against current price and record outcomes."""
    global RESOLVED_OUTCOMES_COUNT
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        return

    signals = _read_signals()
    changed = False

    for sig in signals:
        if sig.get("outcome", "PENDING") != "PENDING":
            continue

        pair_label = sig.get("pair", "")
        pair_conf = next((p for p in DYNAMIC_PAIRS if p["label"] == pair_label), None)
        if pair_conf is None:
            continue

        try:
            candles = await fetch_candles(pair_conf, timeframe="5m")
            if not candles:
                continue
            current_price = candles[-1]["close"]
        except Exception:
            continue

        direction = sig.get("direction", "LONG").upper()
        entry  = sig.get("entry",  0.0)
        sl     = sig.get("sl",     0.0)
        t1     = sig.get("t1",     0.0)
        t2     = sig.get("t2",     0.0)
        t1_hit = sig.get("t1_hit", False)

        outcome = None
        exit_type = None

        if direction == "LONG":
            if current_price <= sl and entry > 0:
                outcome, exit_type = "LOSS", "stop"
            elif current_price >= t2 and t2 > 0:
                outcome, exit_type = "WIN", "t2"
            elif current_price >= t1 and t1 > 0 and not t1_hit:
                outcome, exit_type = "PARTIAL_WIN", "t1"
                sig["t1_hit"] = True
        else:  # SHORT
            if current_price >= sl and entry > 0:
                outcome, exit_type = "LOSS", "stop"
            elif current_price <= t2 and t2 > 0:
                outcome, exit_type = "WIN", "t2"
            elif current_price <= t1 and t1 > 0 and not t1_hit:
                outcome, exit_type = "PARTIAL_WIN", "t1"
                sig["t1_hit"] = True

        if outcome is None:
            continue

        # Only mark final outcomes (WIN/LOSS) as resolved; PARTIAL_WIN stays open
        if outcome in ("WIN", "LOSS"):
            sig["outcome"] = outcome
            sig["exit_type"] = exit_type
            sig["exit_price"] = current_price
            sl_dist = abs(entry - sl)
            sig["pnl_r"] = round(abs(current_price - entry) / max(sl_dist, 1e-9) * (1 if outcome == "WIN" else -1), 2)
        changed = True

        # Update pattern_performance
        for reason in sig.get("reasons", []):
            rl = reason.lower()
            for kw, pk in [("engulfing", "engulfing"), ("hammer", "hammer"), ("pin bar", "pin_bar"),
                           ("pin_bar", "pin_bar"), ("three-line strike", "three_line_strike"),
                           ("inside bar", "inside_bar")]:
                if kw in rl:
                    if outcome in ("WIN", "PARTIAL_WIN"):
                        pattern_performance[pk]["wins"] += 1
                    else:
                        pattern_performance[pk]["losses"] += 1
                    break

        # Increment resolved outcomes counter
        if outcome in ("WIN", "LOSS"):
            RESOLVED_OUTCOMES_COUNT += 1
            if RESOLVED_OUTCOMES_COUNT % 50 == 0:
                rebalance_weights()

        # Post result embed
        try:
            color = 0x00E676 if outcome == "WIN" else (0xFFA500 if outcome == "PARTIAL_WIN" else 0xFF4444)
            emoji = "" if outcome == "WIN" else ("" if outcome == "PARTIAL_WIN" else "")
            embed = discord.Embed(
                title=f"{emoji} Outcome Resolved: {pair_label} {direction}",
                description=f"**{outcome}** — auto-detected by outcome tracker",
                color=color,
            )
            embed.add_field(name="Entry",  value=price_fmt(pair_label, entry),         inline=True)
            embed.add_field(name="Exit",   value=price_fmt(pair_label, current_price), inline=True)
            embed.add_field(name="P&L (R)", value=f"{sig.get('pnl_r', 0):+.2f}R",    inline=True)
            embed.set_footer(text=f"Chartwise v10.0  Outcome Tracker  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
            await channel.send(embed=embed)
        except Exception as e:
            print(f"[OUTCOME] Failed to post embed: {e}")

    if changed:
        _write_signals(signals)
        _save_learning()


@bot.command(name="learnsync")
async def cmd_learnsync(ctx):
    """v10.0: Manually trigger learning sync to GitHub."""
    await ctx.send(" Syncing learning data to GitHub...")
    ok, msg = sync_learning_to_github()
    if ok:
        await ctx.send(" Learning data pushed to GitHub successfully.")
    else:
        await ctx.send(f" Sync failed: `{msg}`")


#
# ENTRY POINT
#

def main():
    global pair_locks
    # Initialize locks at module level so scan_pair can use them before on_ready
    pair_locks = {pair["label"]: asyncio.Lock() for pair in PAIRS}

    # Load adaptive learning weights from disk
    _load_learning()

    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN not set in environment")
    if not CHANNEL_ID:
        raise RuntimeError("CHANNEL_ID not set in environment")

    bot.run(TOKEN)


if __name__ == "__main__":
    main()
