"""
Chartwise Discord Bot — Dual-Engine Signal System
Engines: SMC/ICT (Premium) + EMA Crossover/Breakout Retest (Standard)
"""

import os
import math
import asyncio
import datetime
import statistics
import discord
from discord.ext import commands, tasks
import aiohttp

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

TOKEN      = os.getenv("DISCORD_TOKEN", "")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

MIN_RR          = 1.5   # lowered from 2.0 — more signals pass
MIN_SMC_SCORE   = 4     # lowered from 6 — sweep alone can trigger
MIN_STD_SCORE   = 2     # lowered from 3 — EMA cross + any one confirm fires
DEDUP_THRESHOLD = 0.010 # widened from 0.5% → 1.0% — re-alerts sooner

PAIRS = [
    # ── Crypto via Coinbase ──────────────────────────────────────────────
    {"label": "BTC/USD",     "symbol": "BTC-USD",  "type": "coinbase"},
    {"label": "ETH/USD",     "symbol": "ETH-USD",  "type": "coinbase"},
    {"label": "SOL/USD",     "symbol": "SOL-USD",  "type": "coinbase"},
    {"label": "XRP/USD",     "symbol": "XRP-USD",  "type": "coinbase"},
    {"label": "DOGE/USD",    "symbol": "DOGE-USD", "type": "coinbase"},
    {"label": "AVAX/USD",    "symbol": "AVAX-USD", "type": "coinbase"},
    {"label": "LINK/USD",    "symbol": "LINK-USD", "type": "coinbase"},
    {"label": "LTC/USD",     "symbol": "LTC-USD",  "type": "coinbase"},
    # ── Commodities + Indices + ETFs via Yahoo Finance ───────────────────
    {"label": "GOLD (GC)",   "symbol": "GC=F",     "type": "yahoo"},
    {"label": "SILVER (SI)", "symbol": "SI=F",     "type": "yahoo"},
    {"label": "OIL (CL)",    "symbol": "CL=F",     "type": "yahoo"},
    {"label": "NASDAQ (NQ)", "symbol": "NQ=F",     "type": "yahoo"},
    {"label": "S&P 500 (ES)","symbol": "ES=F",     "type": "yahoo"},
    {"label": "QQQ (ETF)",   "symbol": "QQQ",      "type": "yahoo"},
    {"label": "SPY (ETF)",   "symbol": "SPY",      "type": "yahoo"},
]

# 3 rotating groups of 5
GROUPS = [PAIRS[0:5], PAIRS[5:10], PAIRS[10:15]]

# ─────────────────────────────────────────────
# Session helpers
# ─────────────────────────────────────────────

def is_trading_session(pair=None):
    """Return True if current ET time is within an active session.
    Crypto pairs also trade during Asia session (8pm–3am ET).
    """
    now_utc = datetime.datetime.utcnow()
    et_offset = 4 if is_edt(now_utc) else 5
    now_et = now_utc - datetime.timedelta(hours=et_offset)
    hour = now_et.hour
    # London: 03:00–12:00 ET | New York: 08:00–17:00 ET (all pairs)
    in_main = (3 <= hour < 12) or (8 <= hour < 17)
    if in_main:
        return True
    # Asia session: 20:00–03:00 ET — crypto only (24/7 market)
    is_crypto = pair is not None and pair["type"] == "coinbase"
    if is_crypto and (hour >= 20 or hour < 3):
        return True
    return False


def is_edt(dt_utc):
    """Rough EDT detection: second Sunday March → first Sunday November."""
    year = dt_utc.year

    def nth_sunday(month, n):
        first = datetime.datetime(year, month, 1)
        offset = (6 - first.weekday()) % 7
        return first + datetime.timedelta(days=offset + 7 * (n - 1))

    edt_start = nth_sunday(3, 2)   # 2nd Sunday March
    edt_end   = nth_sunday(11, 1)  # 1st Sunday November
    return edt_start <= dt_utc < edt_end


def session_label():
    now_utc = datetime.datetime.utcnow()
    et_offset = 4 if is_edt(now_utc) else 5
    now_et = now_utc - datetime.timedelta(hours=et_offset)
    hour = now_et.hour
    if 8 <= hour < 17 and 3 <= hour < 12:
        return "London + New York Overlap"
    elif 3 <= hour < 12:
        return "London Session"
    elif 8 <= hour < 17:
        return "New York Session"
    else:
        return "Off-Session"

# ─────────────────────────────────────────────
# Market data fetching
# ─────────────────────────────────────────────

async def fetch_coinbase_candles(session: aiohttp.ClientSession, symbol: str, granularity: int = 300, limit: int = 110):
    """Fetch OHLCV candles from Coinbase Advanced Trade API. granularity in seconds."""
    url = f"https://api.exchange.coinbase.com/products/{symbol}/candles"
    params = {"granularity": granularity}
    try:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            # data: list of [time, low, high, open, close, volume]  newest first
            candles = []
            for row in reversed(data[-limit:]):
                candles.append({
                    "time": row[0],
                    "open": float(row[3]),
                    "high": float(row[2]),
                    "low":  float(row[1]),
                    "close": float(row[4]),
                    "volume": float(row[5]),
                })
            return candles if len(candles) >= 50 else None
    except Exception:
        return None


async def fetch_yahoo_candles(session: aiohttp.ClientSession, symbol: str, interval: str = "5m", period: str = "2d"):
    """Fetch OHLCV candles from Yahoo Finance (unofficial v8 endpoint)."""
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + symbol
    params = {"interval": interval, "range": period}
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with session.get(url, params=params, headers=headers) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            result = data["chart"]["result"][0]
            timestamps = result["timestamp"]
            ohlcv = result["indicators"]["quote"][0]
            candles = []
            for i, t in enumerate(timestamps):
                o = ohlcv["open"][i]
                h = ohlcv["high"][i]
                l = ohlcv["low"][i]
                c = ohlcv["close"][i]
                v = ohlcv["volume"][i]
                if None in (o, h, l, c):
                    continue
                candles.append({
                    "time": t,
                    "open": float(o),
                    "high": float(h),
                    "low":  float(l),
                    "close": float(c),
                    "volume": float(v or 0),
                })
            return candles if len(candles) >= 50 else None
    except Exception:
        return None


async def fetch_candles(session: aiohttp.ClientSession, pair: dict, htf: bool = False):
    """Return 5-min candles (or 1H when htf=True) for a pair."""
    if pair["type"] == "coinbase":
        gran = 3600 if htf else 300
        return await fetch_coinbase_candles(session, pair["symbol"], granularity=gran)
    else:
        interval = "1h" if htf else "5m"
        period   = "7d" if htf else "2d"
        return await fetch_yahoo_candles(session, pair["symbol"], interval=interval, period=period)

# ─────────────────────────────────────────────
# Shared math utilities
# ─────────────────────────────────────────────

def ema(values, period):
    """Proper exponential moving average."""
    if len(values) < period:
        return []
    k = 2 / (period + 1)
    result = [sum(values[:period]) / period]
    for v in values[period:]:
        result.append(v * k + result[-1] * (1 - k))
    return result


def rsi(closes, period=14):
    """Standard Wilder RSI."""
    if len(closes) < period + 1:
        return None
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [max(d, 0) for d in deltas]
    losses = [abs(min(d, 0)) for d in deltas]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    rsi_vals = []
    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        if avg_loss == 0:
            rsi_vals.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi_vals.append(100 - 100 / (1 + rs))

    return rsi_vals[-1] if rsi_vals else None


def calc_atr(candles, period=14):
    if len(candles) < period + 1:
        return None
    trs = []
    for i in range(1, len(candles)):
        high = candles[i]["high"]
        low  = candles[i]["low"]
        prev_close = candles[i - 1]["close"]
        trs.append(max(high - low, abs(high - prev_close), abs(low - prev_close)))
    if len(trs) < period:
        return None
    atr = sum(trs[:period]) / period
    for tr in trs[period:]:
        atr = (atr * (period - 1) + tr) / period
    return atr


def get_asset_type(pair: dict) -> str:
    return "crypto" if pair["type"] == "coinbase" else "stock"

# ─────────────────────────────────────────────
# HTF trend filter
# ─────────────────────────────────────────────

async def get_htf_trend(session: aiohttp.ClientSession, pair: dict):
    """Return 'long', 'short', or None based on 1H EMA20 vs EMA50."""
    candles = await fetch_candles(session, pair, htf=True)
    if not candles or len(candles) < 55:
        return None
    closes = [c["close"] for c in candles]
    e20 = ema(closes, 20)
    e50 = ema(closes, 50)
    if not e20 or not e50:
        return None
    if e20[-1] > e50[-1]:
        return "long"
    elif e20[-1] < e50[-1]:
        return "short"
    return None

# ─────────────────────────────────────────────
# SMC / ICT Analysis (Premium Engine)
# ─────────────────────────────────────────────

def find_swing_highs_lows(candles, lookback=5):
    highs = []
    lows  = []
    for i in range(lookback, len(candles) - lookback):
        is_high = all(candles[i]["high"] >= candles[j]["high"]
                      for j in range(i - lookback, i + lookback + 1) if j != i)
        is_low  = all(candles[i]["low"]  <= candles[j]["low"]
                      for j in range(i - lookback, i + lookback + 1) if j != i)
        if is_high:
            highs.append((i, candles[i]["high"]))
        if is_low:
            lows.append((i, candles[i]["low"]))
    return highs, lows


def find_order_blocks(candles, direction="long"):
    """Find the most recent bullish/bearish order block."""
    ob = None
    if direction == "long":
        # Last strong bearish candle before a bullish surge
        for i in range(len(candles) - 5, 2, -1):
            c = candles[i]
            if c["close"] < c["open"]:  # bearish body
                subsequent_move = candles[i + 1]["close"] - c["low"]
                if subsequent_move > (c["open"] - c["close"]) * 1.5:
                    ob = {"high": c["open"], "low": c["low"], "idx": i}
                    break
    else:
        # Last strong bullish candle before a bearish surge
        for i in range(len(candles) - 5, 2, -1):
            c = candles[i]
            if c["close"] > c["open"]:  # bullish body
                subsequent_move = c["high"] - candles[i + 1]["close"]
                if subsequent_move > (c["close"] - c["open"]) * 1.5:
                    ob = {"high": c["high"], "low": c["close"], "idx": i}
                    break
    return ob


def check_liquidity_sweep(candles, swing_highs, swing_lows):
    """Detect if price recently swept a swing high/low and reversed."""
    if len(candles) < 3:
        return None
    last = candles[-1]
    prev = candles[-2]

    # Check for bearish sweep (swept high then closed below)
    for idx, level in swing_highs[-3:]:
        if prev["high"] > level and last["close"] < level:
            return "short"

    # Check for bullish sweep (swept low then closed above)
    for idx, level in swing_lows[-3:]:
        if prev["low"] < level and last["close"] > level:
            return "long"

    return None


def check_choch(candles, swing_highs, swing_lows):
    """Change of Character: price breaks last swing in opposite direction."""
    if not swing_highs or not swing_lows:
        return None
    last_close = candles[-1]["close"]

    # Bullish CHoCH: closes above last swing high
    if swing_highs:
        last_sh_level = swing_highs[-1][1]
        if last_close > last_sh_level:
            return "long"

    # Bearish CHoCH: closes below last swing low
    if swing_lows:
        last_sl_level = swing_lows[-1][1]
        if last_close < last_sl_level:
            return "short"

    return None


def analyze(candles):
    """
    SMC/ICT analysis.
    Returns signal dict (with signal_type='premium') or None.
    Scoring 0–10.
    """
    if not candles or len(candles) < 60:
        return None

    atr = calc_atr(candles)
    if not atr or atr == 0:
        return None

    price = candles[-1]["close"]
    swing_highs, swing_lows = find_swing_highs_lows(candles)

    score = 0
    reasons = []
    direction = None

    # 1. Liquidity sweep (3 pts)
    sweep = check_liquidity_sweep(candles, swing_highs, swing_lows)
    if sweep:
        score += 3
        direction = sweep
        reasons.append(f"Liquidity sweep ({sweep})")

    # 2. CHoCH (2 pts)
    choch = check_choch(candles, swing_highs, swing_lows)
    if choch:
        score += 2
        if direction is None:
            direction = choch
        elif direction == choch:
            pass  # consistent
        else:
            score -= 1  # conflicting signals
        reasons.append(f"CHoCH ({choch})")

    # 3. Order block proximity (2 pts)
    if direction:
        ob = find_order_blocks(candles, direction)
        if ob:
            ob_mid = (ob["high"] + ob["low"]) / 2
            if abs(price - ob_mid) / price < 0.005:  # within 0.5%
                score += 2
                reasons.append("Price at OB")

    # 4. Swing structure (1 pt)
    if swing_highs and swing_lows:
        score += 1
        reasons.append("Clear swing structure")

    # 5. Volume confirmation (2 pts)
    volumes = [c["volume"] for c in candles[-11:-1] if c["volume"] > 0]
    if volumes:
        avg_vol = statistics.mean(volumes)
        last_vol = candles[-1]["volume"]
        if last_vol > avg_vol * 1.6:
            score += 2
            reasons.append("Volume spike")

    if score < MIN_SMC_SCORE or direction is None:
        return None

    # ATR-based exits
    sl_dist = atr * 1.2
    t1_dist = atr * 2.0
    t2_dist = atr * 3.5

    if direction == "long":
        sl = price - sl_dist
        t1 = price + t1_dist
        t2 = price + t2_dist
    else:
        sl = price + sl_dist
        t1 = price - t1_dist
        t2 = price - t2_dist

    rr1 = t1_dist / sl_dist
    rr2 = t2_dist / sl_dist

    if rr1 < MIN_RR:
        return None

    return {
        "direction": direction,
        "entry": price,
        "sl": sl,
        "t1": t1,
        "t2": t2,
        "rr1": round(rr1, 2),
        "rr2": round(rr2, 2),
        "score": score,
        "reasons": reasons,
        "signal_type": "premium",
    }

# ─────────────────────────────────────────────
# 5-Minute Entry Confirmation
# ─────────────────────────────────────────────

async def confirm_5m_entry(http: aiohttp.ClientSession, pair: dict, direction: str) -> bool:
    """Pull 5m candles and confirm entry trigger in signal direction.
    Checks: EMA9 vs EMA21 alignment + RSI side + engulfing candle.
    Returns True if at least 2 of 3 confirm — keeps signal volume up.
    """
    try:
        if pair["type"] == "coinbase":
            candles_5m = await fetch_coinbase_candles(http, pair["symbol"], granularity=300, limit=60)
        else:
            candles_5m = await fetch_yahoo_candles(http, pair["symbol"], interval="5m", period="1d")

        if not candles_5m or len(candles_5m) < 25:
            return True  # no data — don't block the signal

        closes = [c["close"] for c in candles_5m]
        fast   = ema(closes, 9)
        slow   = ema(closes, 21)
        rsi_val = rsi(closes, 14)
        last   = candles_5m[-1]
        prev   = candles_5m[-2]

        confirms = 0

        # 1. EMA alignment
        if fast and slow:
            if direction == "long"  and fast[-1] > slow[-1]: confirms += 1
            if direction == "short" and fast[-1] < slow[-1]: confirms += 1

        # 2. RSI side
        if rsi_val is not None:
            if direction == "long"  and rsi_val > 45: confirms += 1
            if direction == "short" and rsi_val < 55: confirms += 1

        # 3. Engulfing candle in direction
        if direction == "long":
            bullish_engulf = last["close"] > last["open"] and last["close"] > prev["high"]
            if bullish_engulf: confirms += 1
        else:
            bearish_engulf = last["close"] < last["open"] and last["close"] < prev["low"]
            if bearish_engulf: confirms += 1

        return confirms >= 2  # need 2 of 3 — keeps volume high

    except Exception:
        return True  # on error, don't block

# ─────────────────────────────────────────────
# EMA Crossover + Breakout Retest (Standard Engine)
# ─────────────────────────────────────────────

_STANDARD_PARAMS = {
    "crypto": {
        "ema_fast": 9,
        "ema_slow": 21,
        "vol_mult": 1.3,   # lowered from 1.8 — catches more moves
        "rsi_period": 14,
        "rsi_ob": 65,
        "rsi_os": 35,
        "breakout_lookback": 20,
        "min_score": MIN_STD_SCORE,
    },
    "stock": {
        "ema_fast": 8,
        "ema_slow": 20,
        "vol_mult": 1.1,   # lowered from 1.4
        "rsi_period": 14,
        "rsi_ob": 60,
        "rsi_os": 40,
        "breakout_lookback": 15,
        "min_score": MIN_STD_SCORE,
    },
}


def analyze_standard(candles, asset_type):
    """
    EMA Crossover + Breakout Retest signal engine.
    Returns signal dict (with signal_type='standard') or None.
    Scoring 0–5.
    """
    if asset_type not in _STANDARD_PARAMS:
        asset_type = "stock"

    p = _STANDARD_PARAMS[asset_type]
    needed = max(p["ema_slow"], p["breakout_lookback"]) + 10
    if not candles or len(candles) < needed:
        return None

    atr = calc_atr(candles)
    if not atr or atr == 0:
        return None

    closes  = [c["close"] for c in candles]
    volumes = [c["volume"] for c in candles]
    price   = closes[-1]

    # ── EMA series ────────────────────────────────────────────────────────
    fast_series = ema(closes, p["ema_fast"])
    slow_series = ema(closes, p["ema_slow"])
    if len(fast_series) < 4 or len(slow_series) < 4:
        return None

    # Check crossover in last 3 candles
    # fast_series and slow_series are aligned to the same tail of candles
    # Index -1 is current, -2 is prev, -3 is two candles ago
    cross_long  = False
    cross_short = False
    for i in [-3, -2, -1]:
        try:
            f_cur  = fast_series[i]
            s_cur  = slow_series[i]
            f_prev = fast_series[i - 1]
            s_prev = slow_series[i - 1]
        except IndexError:
            continue
        if f_prev <= s_prev and f_cur > s_cur:
            cross_long  = True
        if f_prev >= s_prev and f_cur < s_cur:
            cross_short = True

    if not cross_long and not cross_short:
        return None

    # Determine candidate direction
    if cross_long and cross_short:
        # Both within 3 candles — conflicting, skip
        return None

    direction = "long" if cross_long else "short"

    score   = 0
    reasons = []

    # ── Criterion 1: EMA crossover (2 pts) ───────────────────────────────
    score += 2
    reasons.append(f"EMA {p['ema_fast']}/{p['ema_slow']} crossover ({direction})")

    # ── Criterion 2: RSI confirmation (1 pt) ─────────────────────────────
    rsi_val = rsi(closes, p["rsi_period"])
    if rsi_val is not None:
        # Rising/falling check: compare last two RSI values
        rsi_prev = rsi(closes[:-1], p["rsi_period"])
        rsi_rising  = rsi_prev is not None and rsi_val > rsi_prev
        rsi_falling = rsi_prev is not None and rsi_val < rsi_prev

        if direction == "long"  and rsi_val > 50 and rsi_rising:
            score += 1
            reasons.append(f"RSI {rsi_val:.1f} >50 and rising")
        elif direction == "short" and rsi_val < 50 and rsi_falling:
            score += 1
            reasons.append(f"RSI {rsi_val:.1f} <50 and falling")

    # ── Criterion 3: Volume spike on crossover candle (1 pt) ─────────────
    vol_window = volumes[-11:-1]
    valid_vols = [v for v in vol_window if v and v > 0]
    if valid_vols:
        avg_vol  = statistics.mean(valid_vols)
        last_vol = volumes[-1]
        if last_vol and avg_vol > 0 and last_vol >= avg_vol * p["vol_mult"]:
            score += 1
            reasons.append(f"Volume spike ({last_vol/avg_vol:.1f}×)")

    # ── Criterion 4: Breakout retest (1 pt) ──────────────────────────────
    lb = p["breakout_lookback"]
    lookback_candles = candles[-(lb + 5):-5] if len(candles) >= lb + 5 else candles[:-5]
    if lookback_candles:
        if direction == "long":
            breakout_level = max(c["high"] for c in lookback_candles)
            retest = abs(price - breakout_level) / breakout_level <= 0.005
            if retest:
                score += 1
                reasons.append(f"Breakout retest near {breakout_level:.4f}")
        else:
            breakout_level = min(c["low"] for c in lookback_candles)
            retest = abs(price - breakout_level) / breakout_level <= 0.005
            if retest:
                score += 1
                reasons.append(f"Breakdown retest near {breakout_level:.4f}")

    if score < p["min_score"]:
        return None

    # ── ATR exits (slightly tighter than SMC) ────────────────────────────
    sl_dist = atr * 1.0
    t1_dist = atr * 1.8
    t2_dist = atr * 3.0

    if direction == "long":
        sl = price - sl_dist
        t1 = price + t1_dist
        t2 = price + t2_dist
    else:
        sl = price + sl_dist
        t1 = price - t1_dist
        t2 = price - t2_dist

    rr1 = t1_dist / sl_dist
    rr2 = t2_dist / sl_dist

    if rr1 < MIN_RR:
        return None

    return {
        "direction": direction,
        "entry": price,
        "sl": sl,
        "t1": t1,
        "t2": t2,
        "rr1": round(rr1, 2),
        "rr2": round(rr2, 2),
        "score": score,
        "reasons": reasons,
        "signal_type": "standard",
    }

# ─────────────────────────────────────────────
# Signal deduplication
# ─────────────────────────────────────────────

recent_signals = {}  # pair_label -> {"direction": str, "entry": float, "signal_type": str}


def is_duplicate(pair_label: str, signal: dict) -> bool:
    prev = recent_signals.get(pair_label)
    if not prev:
        return False
    if prev["direction"] != signal["direction"]:
        return False
    entry_diff = abs(signal["entry"] - prev["entry"]) / prev["entry"]
    return entry_diff < DEDUP_THRESHOLD


def record_signal(pair_label: str, signal: dict):
    recent_signals[pair_label] = {
        "direction": signal["direction"],
        "entry": signal["entry"],
        "signal_type": signal["signal_type"],
    }

# ─────────────────────────────────────────────
# Active trade tracking (exit monitoring)
# ─────────────────────────────────────────────

active_trades = {}  # pair_label -> signal dict


def update_active_trades(pair_label: str, candles, signal_channel):
    """
    Check if price hit T1, T2, or SL for an active trade.
    Returns a list of exit embed coroutines to send.
    """
    if pair_label not in active_trades:
        return []

    trade = active_trades[pair_label]
    price = candles[-1]["close"]
    direction = trade["direction"]

    exits = []

    if direction == "long":
        if price <= trade["sl"]:
            exits.append(("stop", price, trade))
            del active_trades[pair_label]
        elif price >= trade["t2"]:
            exits.append(("t2", price, trade))
            del active_trades[pair_label]
        elif price >= trade["t1"] and not trade.get("t1_hit"):
            exits.append(("t1", price, trade))
            active_trades[pair_label]["t1_hit"] = True
    else:
        if price >= trade["sl"]:
            exits.append(("stop", price, trade))
            del active_trades[pair_label]
        elif price <= trade["t2"]:
            exits.append(("t2", price, trade))
            del active_trades[pair_label]
        elif price <= trade["t1"] and not trade.get("t1_hit"):
            exits.append(("t1", price, trade))
            active_trades[pair_label]["t1_hit"] = True

    return exits

# ─────────────────────────────────────────────
# Discord Embeds
# ─────────────────────────────────────────────

def price_fmt(val: float) -> str:
    if val >= 1000:
        return f"{val:,.2f}"
    elif val >= 1:
        return f"{val:.4f}"
    else:
        return f"{val:.6f}"


def make_premium_embed(pair_label: str, signal: dict, htf_trend: str, counter_trend: bool = False) -> discord.Embed:
    direction = signal["direction"]
    color = 0x00C853 if direction == "long" else 0xFF1744

    ct_tag = " ⚠️ COUNTER-TREND" if counter_trend else ""
    embed = discord.Embed(
        title=f"🔥 CHARTWISE · {pair_label} · PREMIUM SETUP{ct_tag}",
        color=color,
        timestamp=datetime.datetime.utcnow(),
    )

    banner = "▲ LONG SIGNAL" if direction == "long" else "▼ SHORT SIGNAL"
    if counter_trend:
        banner += "  ⚠️ *trades against 1H trend — size down*"
    embed.add_field(name="Direction", value=banner, inline=False)

    score = signal["score"]
    score_bar = "█" * min(score, 10) + "░" * (10 - min(score, 10))
    embed.add_field(name="SMC Score", value=f"`{score_bar}` {score}/10", inline=False)

    embed.add_field(name="Entry",  value=price_fmt(signal["entry"]), inline=True)
    embed.add_field(name="Stop",   value=price_fmt(signal["sl"]),    inline=True)
    embed.add_field(name="​", value="​",                   inline=True)

    embed.add_field(name="T1",  value=f"{price_fmt(signal['t1'])} (R/R {signal['rr1']}×)", inline=True)
    embed.add_field(name="T2",  value=f"{price_fmt(signal['t2'])} (R/R {signal['rr2']}×)", inline=True)
    embed.add_field(name="​", value="​",                                          inline=True)

    reasons_text = "\n".join(f"• {r}" for r in signal["reasons"])
    embed.add_field(name="Confluence", value=reasons_text, inline=False)

    embed.add_field(name="HTF Trend", value=htf_trend.upper() if htf_trend else "N/A", inline=True)

    embed.set_footer(text="SMC/ICT · High confluence · Not financial advice")
    return embed


def make_standard_embed(pair_label: str, signal: dict, htf_trend: str, counter_trend: bool = False) -> discord.Embed:
    direction = signal["direction"]
    color = 0x5865F2  # Discord blurple

    ct_tag = " ⚠️ COUNTER-TREND" if counter_trend else ""
    embed = discord.Embed(
        title=f"⚡ CHARTWISE · {pair_label} · STANDARD SIGNAL{ct_tag}",
        color=color,
        timestamp=datetime.datetime.utcnow(),
    )

    banner = "▲ LONG SIGNAL" if direction == "long" else "▼ SHORT SIGNAL"
    if counter_trend:
        banner += "  ⚠️ *trades against 1H trend — size down*"
    embed.add_field(name="Direction", value=banner, inline=False)

    score = signal["score"]
    score_bar = "█" * score + "░" * (5 - score)
    embed.add_field(name="EMA Score", value=f"`{score_bar}` {score}/5", inline=False)

    embed.add_field(name="Entry",  value=price_fmt(signal["entry"]), inline=True)
    embed.add_field(name="Stop",   value=price_fmt(signal["sl"]),    inline=True)
    embed.add_field(name="​", value="​",                   inline=True)

    embed.add_field(name="T1",  value=f"{price_fmt(signal['t1'])} (R/R {signal['rr1']}×)", inline=True)
    embed.add_field(name="T2",  value=f"{price_fmt(signal['t2'])} (R/R {signal['rr2']}×)", inline=True)
    embed.add_field(name="​", value="​",                                          inline=True)

    reasons_text = "\n".join(f"• {r}" for r in signal["reasons"])
    embed.add_field(name="Reasons", value=reasons_text, inline=False)

    embed.add_field(name="HTF Trend", value=htf_trend.upper() if htf_trend else "N/A", inline=True)

    embed.set_footer(text="EMA/Breakout · Active signal · Not financial advice")
    return embed


def make_exit_embed(exit_type: str, pair_label: str, price: float, trade: dict) -> discord.Embed:
    colors = {"t1": 0xFFD700, "t2": 0x00E676, "stop": 0xFF5252}
    labels = {"t1": "🎯 T1 Hit", "t2": "✅ T2 Hit — Full Target", "stop": "🛑 Stop Loss Hit"}

    signal_type_label = "PREMIUM" if trade.get("signal_type") == "premium" else "STANDARD"

    embed = discord.Embed(
        title=f"{labels[exit_type]} · {pair_label} [{signal_type_label}]",
        color=colors.get(exit_type, 0xFFFFFF),
        timestamp=datetime.datetime.utcnow(),
    )
    embed.add_field(name="Exit Price", value=price_fmt(price),            inline=True)
    embed.add_field(name="Entry",      value=price_fmt(trade["entry"]),   inline=True)
    embed.add_field(name="Direction",  value=trade["direction"].upper(),  inline=True)
    embed.set_footer(text="Chartwise Exit Monitor · Not financial advice")
    return embed


def make_status_embed(tick: int, group_idx: int) -> discord.Embed:
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    session = session_label()
    group_pairs = [p["label"] for p in GROUPS[group_idx]]
    active_count = len(active_trades)

    embed = discord.Embed(
        title="📊 CHARTWISE · System Status",
        color=0x2F3136,
        timestamp=datetime.datetime.utcnow(),
    )
    embed.add_field(name="Session",       value=session,                         inline=True)
    embed.add_field(name="Active Trades", value=str(active_count),               inline=True)
    embed.add_field(name="Scan Tick",     value=str(tick),                       inline=True)
    embed.add_field(name="Active Group",  value=", ".join(group_pairs),          inline=False)
    if active_trades:
        trade_lines = []
        for label, t in active_trades.items():
            t1_flag = " (T1 ✓)" if t.get("t1_hit") else ""
            stype = "🔥" if t.get("signal_type") == "premium" else "⚡"
            trade_lines.append(f"{stype} {label} {t['direction'].upper()}{t1_flag}")
        embed.add_field(name="Open Trades", value="\n".join(trade_lines), inline=False)
    embed.set_footer(text=f"Chartwise · Dual Engine · {now}")
    return embed

# ─────────────────────────────────────────────
# Bot setup
# ─────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

tick_counter    = 0
group_index     = 0
status_tick_ctr = 0  # 6 ticks × 5 min = 30-min status update

# ─────────────────────────────────────────────
# Main scan loop
# ─────────────────────────────────────────────

@tasks.loop(minutes=5)
async def scan_loop():
    global tick_counter, group_index, status_tick_ctr

    tick_counter    += 1
    status_tick_ctr += 1

    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"[ERROR] CHANNEL_ID {CHANNEL_ID} not found")
        return

    async with aiohttp.ClientSession() as http:
        # ── Rotate group every 2 ticks (10 min) ─────────────────────────
        if tick_counter % 2 == 0:
            group_index = (group_index + 1) % len(GROUPS)
            print(f"[ROTATE] Group {group_index}: {[p['label'] for p in GROUPS[group_index]]}")

        active_group = GROUPS[group_index]

        # ── Exit monitoring — ALL pairs every tick ───────────────────────
        for pair_label in list(active_trades.keys()):
            pair = next((p for p in PAIRS if p["label"] == pair_label), None)
            if not pair:
                continue
            candles = await fetch_candles(http, pair)
            if not candles:
                continue
            exits = update_active_trades(pair_label, candles, channel)
            for exit_type, exit_price, trade in exits:
                embed = make_exit_embed(exit_type, pair_label, exit_price, trade)
                await channel.send(embed=embed)

        # ── Entry scans — active group, per-pair session check ───────────
        for pair in active_group:
            pair_label = pair["label"]

            if not is_trading_session(pair):
                print(f"[SLEEP] {pair_label} — outside session")
                continue

            if pair_label in active_trades:
                print(f"[SKIP] {pair_label} — trade active")
                continue

            candles = await fetch_candles(http, pair)
            if not candles:
                continue

            htf_trend  = await get_htf_trend(http, pair)
            asset_type = get_asset_type(pair)

            # ── Try Premium (SMC) first ──────────────────────────────────
            smc_signal = analyze(candles)
            fired = False

            if smc_signal:
                counter = htf_trend is not None and htf_trend != smc_signal["direction"]
                confirmed = await confirm_5m_entry(http, pair, smc_signal["direction"])
                if confirmed and not is_duplicate(pair_label, smc_signal):
                    record_signal(pair_label, smc_signal)
                    active_trades[pair_label] = {**smc_signal, "label": pair_label, "t1_hit": False}
                    embed = make_premium_embed(pair_label, smc_signal, htf_trend, counter_trend=counter)
                    await channel.send(embed=embed)
                    fired = True
                    print(f"[🔥 PREMIUM] {pair_label} {smc_signal['direction'].upper()} score={smc_signal['score']} counter={counter}")

            # ── If no premium, try Standard (EMA) ───────────────────────
            if not fired:
                std_signal = analyze_standard(candles, asset_type)
                if std_signal:
                    counter = htf_trend is not None and htf_trend != std_signal["direction"]
                    confirmed = await confirm_5m_entry(http, pair, std_signal["direction"])
                    if confirmed and not is_duplicate(pair_label, std_signal):
                        record_signal(pair_label, std_signal)
                        active_trades[pair_label] = {**std_signal, "label": pair_label, "t1_hit": False}
                        embed = make_standard_embed(pair_label, std_signal, htf_trend, counter_trend=counter)
                        await channel.send(embed=embed)
                        print(f"[⚡ STANDARD] {pair_label} {std_signal['direction'].upper()} score={std_signal['score']} counter={counter}")

    # ── 30-min status embed ──────────────────────────────────────────────
    if status_tick_ctr >= 6:
        status_tick_ctr = 0
        embed = make_status_embed(tick_counter, group_index)
        await channel.send(embed=embed)


# ─────────────────────────────────────────────
# Commands
# ─────────────────────────────────────────────

@bot.command(name="status")
async def cmd_status(ctx):
    """Display current bot and trade status."""
    embed = make_status_embed(tick_counter, group_index)
    await ctx.send(embed=embed)


@bot.command(name="scan")
async def cmd_scan(ctx):
    """Run both signal engines on all 15 pairs immediately."""
    await ctx.send("🔍 Running dual-engine scan on all 15 pairs…")

    results = []

    async with aiohttp.ClientSession() as http:
        for pair in PAIRS:
            candles = await fetch_candles(http, pair)
            if not candles:
                results.append(f"❌ `{pair['label']}` — no data")
                continue

            htf_trend  = await get_htf_trend(http, pair)
            asset_type = get_asset_type(pair)
            pair_label = pair["label"]

            smc_signal = analyze(candles)
            std_signal = analyze_standard(candles, asset_type)

            htf_label = f"HTF={htf_trend.upper()}" if htf_trend else "HTF=?"

            if smc_signal:
                ct = "⚠️CT" if htf_trend and htf_trend != smc_signal["direction"] else "✅"
                results.append(
                    f"🔥 `{pair_label}` — PREMIUM {smc_signal['direction'].upper()} "
                    f"score={smc_signal['score']}/10 {ct} {htf_label}"
                )
            elif std_signal:
                ct = "⚠️CT" if htf_trend and htf_trend != std_signal["direction"] else "✅"
                results.append(
                    f"⚡ `{pair_label}` — STANDARD {std_signal['direction'].upper()} "
                    f"score={std_signal['score']}/5 {ct} {htf_label}"
                )
            else:
                results.append(f"— `{pair_label}` — No signal ({htf_label})")

    # Split into chunks to avoid embed 6000-char limit
    chunk = []
    for line in results:
        chunk.append(line)
        if len(chunk) == 5:
            embed = discord.Embed(
                description="\n".join(chunk),
                color=0x2F3136,
                timestamp=datetime.datetime.utcnow(),
            )
            await ctx.send(embed=embed)
            chunk = []
    if chunk:
        embed = discord.Embed(
            description="\n".join(chunk),
            color=0x2F3136,
            timestamp=datetime.datetime.utcnow(),
        )
        embed.set_footer(text="Chartwise Dual-Engine Scan · Not financial advice")
        await ctx.send(embed=embed)


# ─────────────────────────────────────────────
# Bot events
# ─────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f"Chartwise Bot online as {bot.user}")
    scan_loop.start()


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    bot.run(TOKEN)
