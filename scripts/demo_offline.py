"""Demo SIN RED: genera datos sinteticos y ejecuta el motor de senales.

Util para validar el pipeline cuando no hay acceso a Yahoo Finance (por
ejemplo en entornos con egress restringido). Los valores son ARTIFICIALES;
NO son senales reales de mercado.

Uso:  PYTHONPATH=. python3 scripts/demo_offline.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import algo.data as data_mod
from algo import run


def _synthetic(seed: int, n_weekly: int = 160, n_4h: int = 900,
               drift: float = 0.05, dip: bool = False):
    rng = np.random.default_rng(seed)

    w_close = np.maximum(50 + np.cumsum(rng.normal(drift, 1.0, n_weekly)), 1.0)
    widx = pd.date_range("2023-01-01", periods=n_weekly, freq="W")
    weekly = pd.DataFrame(
        {"Open": w_close, "High": w_close * 1.02, "Low": w_close * 0.98,
         "Close": w_close, "Volume": 1_000_000.0},
        index=widx,
    )

    h_close = w_close[-1] + np.cumsum(rng.normal(drift / 10, 0.5, n_4h))
    if dip:  # caida reciente para forzar sobreventa en 4h
        h_close[-10:] = h_close[-10:] - np.linspace(0, 8, 10)
    h_close = np.maximum(h_close, 1.0)
    hidx = pd.date_range("2025-01-01", periods=n_4h, freq="4h")
    df4 = pd.DataFrame(
        {"Open": h_close, "High": h_close * 1.01, "Low": h_close * 0.99,
         "Close": h_close, "Volume": 100_000.0},
        index=hidx,
    )
    return weekly, df4


def main() -> int:
    fixtures = {
        "DEMO_BULL_DIP": _synthetic(1, drift=0.15, dip=True),
        "DEMO_BEAR": _synthetic(2, drift=-0.15, dip=False),
        "DEMO_NEUTRAL": _synthetic(3, drift=0.0, dip=False),
    }
    data_mod.get_weekly = lambda t, period="5y": fixtures[t][0]
    data_mod.get_4h = lambda t, period="720d": fixtures[t][1]
    run.UNIVERSE = list(fixtures)

    print(">>> DEMO OFFLINE — datos sinteticos, NO son senales reales\n")
    return run.main(["--universe", "--out", "signals"])


if __name__ == "__main__":
    raise SystemExit(main())
