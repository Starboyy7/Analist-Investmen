"""Tests de los indicadores y de la logica de senal (no requieren red)."""
import numpy as np
import pandas as pd

from algo.indicators import ema, rsi, vwap
from algo.signals import classify


def test_rsi_bounds():
    rng = np.random.default_rng(0)
    serie = pd.Series(100 + rng.standard_normal(300).cumsum())
    r = rsi(serie, 14).dropna()
    assert ((r >= 0) & (r <= 100)).all()


def test_rsi_monotonic_up_is_100():
    serie = pd.Series(np.arange(1, 60, dtype=float))
    assert rsi(serie, 14).iloc[-1] == 100.0


def test_rsi_monotonic_down_is_0():
    serie = pd.Series(np.arange(60, 1, -1, dtype=float))
    assert rsi(serie, 14).iloc[-1] == 0.0


def test_rsi_known_values_period3():
    # Calculado a mano: semilla SMA + suavizado de Wilder, periodo 3.
    serie = pd.Series([10, 11, 10, 11, 12], dtype=float)
    r = rsi(serie, 3)
    assert abs(r.iloc[3] - 66.6667) < 1e-3
    assert abs(r.iloc[4] - 77.7778) < 1e-3


def test_ema_constant():
    serie = pd.Series([5.0] * 50)
    assert abs(ema(serie, 10).iloc[-1] - 5.0) < 1e-9


def test_vwap_basic():
    df = pd.DataFrame(
        {
            "High": [11, 12, 13],
            "Low": [9, 10, 11],
            "Close": [10, 11, 12],
            "Volume": [100, 100, 100],
        }
    )
    v = vwap(df)
    # typical == close (H,L,C simetricos) y volumen constante => media acumulada
    assert abs(v.iloc[-1] - 11.0) < 1e-9


def test_classify_matrix():
    assert classify(60, 25, "alcista")[0] == "COMPRA FUERTE"
    assert classify(60, 25, "bajista")[0] == "COMPRA"
    assert classify(40, 25, "bajista")[0] == "REBOTE DEBIL"
    assert classify(40, 75, "bajista")[0] == "VENTA FUERTE"
    assert classify(60, 75, "bajista")[0] == "VENTA"
    assert classify(60, 75, "alcista")[0] == "TOMAR GANANCIAS"
    assert classify(55, 50, "alcista")[0] == "NEUTRAL"
