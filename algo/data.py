"""Descarga de precios (yfinance) y resampleo a velas de 4 horas.

yfinance no ofrece intervalo de 4h nativo: se descarga 1h y se agrega a 4h.
El import de yfinance es perezoso para no exigir red al importar el modulo.
"""
from __future__ import annotations

import pandas as pd

_OHLCV = {"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}


def _download(ticker: str, period: str, interval: str) -> pd.DataFrame:
    import yfinance as yf

    df = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
    )
    if df is None or df.empty:
        raise RuntimeError(
            f"Sin datos para {ticker} (interval={interval}, period={period})"
        )
    # Con un solo ticker algunas versiones devuelven columnas MultiIndex.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


def get_weekly(ticker: str, period: str = "5y") -> pd.DataFrame:
    """Velas semanales."""
    return _download(ticker, period, "1wk")


def get_4h(ticker: str, period: str = "720d") -> pd.DataFrame:
    """Velas de 4h, agregadas a partir de datos de 1h."""
    h1 = _download(ticker, period, "1h")
    df4 = h1.resample("4h").agg(_OHLCV).dropna(how="any")
    if df4.empty:
        raise RuntimeError(f"No se pudieron construir velas 4h para {ticker}")
    return df4
