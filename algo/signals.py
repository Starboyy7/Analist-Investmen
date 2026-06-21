"""Senal multihorario: RSI semanal (sesgo) + RSI 4h (timing) + direccion (EMA/VWAP).

Logica:
- El RSI **semanal** define el sesgo de fondo (alcista si >= 50, bajista si <).
- El RSI **4h** define el timing: sobreventa (<=30) o sobrecompra (>=70).
- La **direccion** (precio vs EMA, o vs VWAP) confirma la tendencia.
La combinacion de los tres produce la senal compuesta.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import data as data_mod
from .indicators import ema, rsi, vwap


@dataclass
class Params:
    rsi_period: int = 14
    oversold: float = 30.0
    overbought: float = 70.0
    weekly_bull_level: float = 50.0
    ema_period: int = 50
    direction: str = "ema"  # "ema" o "vwap"


DEFAULT = Params()


def zone_4h(value: float, p: Params = DEFAULT) -> str:
    if value <= p.oversold:
        return "sobreventa"
    if value >= p.overbought:
        return "sobrecompra"
    return "neutral"


def classify(rsi_weekly: float, rsi_4h: float, trend: str, p: Params = DEFAULT):
    """Devuelve (senal, confianza, sesgo_semanal, zona_4h)."""
    bias = "alcista" if rsi_weekly >= p.weekly_bull_level else "bajista"
    zona = zone_4h(rsi_4h, p)

    if zona == "sobreventa" and bias == "alcista" and trend == "alcista":
        sig, conf = "COMPRA FUERTE", "alta"
    elif zona == "sobreventa" and (bias == "alcista" or trend == "alcista"):
        sig, conf = "COMPRA", "media"
    elif zona == "sobreventa":
        sig, conf = "REBOTE DEBIL", "baja"  # sobreventa pero sesgo y tendencia en contra
    elif zona == "sobrecompra" and bias == "bajista" and trend == "bajista":
        sig, conf = "VENTA FUERTE", "alta"
    elif zona == "sobrecompra" and (bias == "bajista" or trend == "bajista"):
        sig, conf = "VENTA", "media"
    elif zona == "sobrecompra":
        sig, conf = "TOMAR GANANCIAS", "baja"  # sobrecompra con sesgo y tendencia a favor
    else:
        sig, conf = "NEUTRAL", "baja"
    return sig, conf, bias, zona


def analyze(ticker: str, p: Params = DEFAULT) -> dict:
    """Descarga datos, calcula indicadores y devuelve la senal del ticker."""
    weekly = data_mod.get_weekly(ticker)
    df4 = data_mod.get_4h(ticker)

    rsi_w = rsi(weekly["Close"], p.rsi_period).dropna()
    rsi_4 = rsi(df4["Close"], p.rsi_period).dropna()
    if rsi_w.empty or rsi_4.empty:
        raise RuntimeError(f"Historial insuficiente para {ticker}")

    if p.direction == "vwap":
        dline = vwap(df4)
        dline_name = "vwap_4h"
    else:
        dline = ema(df4["Close"], p.ema_period)
        dline_name = f"ema{p.ema_period}_4h"

    last_close = float(df4["Close"].iloc[-1])
    last_dline = float(dline.iloc[-1])
    trend = "alcista" if last_close >= last_dline else "bajista"

    rw = float(rsi_w.iloc[-1])
    r4 = float(rsi_4.iloc[-1])
    sig, conf, bias, zona = classify(rw, r4, trend, p)

    return {
        "ticker": ticker,
        "timestamp": str(df4.index[-1]),
        "price": round(last_close, 4),
        "rsi": {"4h": round(r4, 2), "weekly": round(rw, 2)},
        "direction": p.direction,
        dline_name: round(last_dline, 4),
        "trend": trend,
        "weekly_bias": bias,
        "zone_4h": zona,
        "signal": sig,
        "confidence": conf,
    }
