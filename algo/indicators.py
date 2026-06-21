"""Indicadores tecnicos puros (sin red): RSI de Wilder, EMA y VWAP.

Todas las funciones operan sobre pandas Series/DataFrame y son deterministas,
de modo que se pueden testear sin descargar datos.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _rsi_from_avgs(avg_gain: float, avg_loss: float) -> float:
    if avg_loss == 0 and avg_gain == 0:
        return 50.0
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - 100.0 / (1.0 + rs)


def rsi(close, period: int = 14) -> pd.Series:
    """RSI de Wilder (0-100).

    Usa semilla SMA + suavizado de Wilder (RMA), igual que la funcion
    ``ta.rsi`` de TradingView, por lo que los valores coinciden con lo que
    se ve en el grafico.
    """
    close = pd.Series(close).astype(float)
    delta = close.diff()
    gain = delta.clip(lower=0.0).to_numpy()
    loss = (-delta).clip(lower=0.0).to_numpy()

    n = len(close)
    out = np.full(n, np.nan)
    if n <= period:
        return pd.Series(out, index=close.index, name="rsi")

    # gain[0]/loss[0] son NaN (vienen de diff); las variaciones reales
    # empiezan en el indice 1. Semilla = media simple de las primeras
    # `period` variaciones (indices 1..period).
    avg_gain = float(np.nanmean(gain[1:period + 1]))
    avg_loss = float(np.nanmean(loss[1:period + 1]))
    out[period] = _rsi_from_avgs(avg_gain, avg_loss)

    for i in range(period + 1, n):
        avg_gain = (avg_gain * (period - 1) + gain[i]) / period
        avg_loss = (avg_loss * (period - 1) + loss[i]) / period
        out[i] = _rsi_from_avgs(avg_gain, avg_loss)

    return pd.Series(out, index=close.index, name="rsi")


def ema(series, period: int) -> pd.Series:
    """Media movil exponencial (EMA)."""
    return pd.Series(series).astype(float).ewm(span=period, adjust=False).mean()


def vwap(df: pd.DataFrame, window: int | None = None) -> pd.Series:
    """VWAP (precio medio ponderado por volumen).

    Requiere columnas High, Low, Close y Volume.
    - ``window=None``: VWAP anclado (acumulado desde el inicio de los datos).
    - ``window=N``: VWAP movil sobre las ultimas N velas.
    """
    typical = (df["High"] + df["Low"] + df["Close"]) / 3.0
    pv = typical * df["Volume"]
    if window:
        return pv.rolling(window).sum() / df["Volume"].rolling(window).sum()
    return pv.cumsum() / df["Volume"].cumsum()
