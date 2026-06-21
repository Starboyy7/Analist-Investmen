"""CLI del motor de RSI multihorario.

Uso:
    python -m algo.run NVDA AMD INTC
    python -m algo.run --universe
    python -m algo.run NVDA --direction vwap --oversold 25 --overbought 75

Escribe ``signals/signals.json`` y ``signals/signals.csv`` (los lee el sub-agente Quant).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from datetime import datetime, timezone

import pandas as pd

from .signals import DEFAULT, Params, analyze

UNIVERSE = [
    "NVDA", "AVGO", "AMD", "QCOM", "TXN", "INTC", "MU", "AMAT", "LRCX",
    "KLAC", "ADI", "MCHP", "MRVL", "MPWR", "TER", "ON", "ENTG", "SWKS",
    "COHR", "NXPI", "QRVO", "ALAB",
]


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="RSI multihorario (semanal + 4h) con direccion EMA/VWAP"
    )
    ap.add_argument("tickers", nargs="*", help="tickers a analizar; vacio => universo por defecto")
    ap.add_argument("--universe", action="store_true", help="usar el universo de 22 semiconductores")
    ap.add_argument("--rsi-period", type=int, default=DEFAULT.rsi_period)
    ap.add_argument("--oversold", type=float, default=DEFAULT.oversold)
    ap.add_argument("--overbought", type=float, default=DEFAULT.overbought)
    ap.add_argument("--weekly-bull-level", type=float, default=DEFAULT.weekly_bull_level)
    ap.add_argument("--ema-period", type=int, default=DEFAULT.ema_period)
    ap.add_argument("--direction", choices=["ema", "vwap"], default=DEFAULT.direction)
    ap.add_argument("--out", default="signals", help="carpeta de salida")
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    tickers = UNIVERSE if (args.universe or not args.tickers) else args.tickers

    p = Params(
        rsi_period=args.rsi_period,
        oversold=args.oversold,
        overbought=args.overbought,
        weekly_bull_level=args.weekly_bull_level,
        ema_period=args.ema_period,
        direction=args.direction,
    )

    results: dict[str, dict] = {}
    errors: dict[str, str] = {}
    print(f"Analizando {len(tickers)} ticker(s) | direccion={p.direction} | "
          f"OS={p.oversold} OB={p.overbought}\n")
    for raw in tickers:
        t = raw.upper().strip()
        try:
            r = analyze(t, p)
            results[t] = r
            print(f"  {t:6s} | RSIsem {r['rsi']['weekly']:5.1f} | RSI4h {r['rsi']['4h']:5.1f} "
                  f"| {r['trend']:8s} | {r['signal']}")
        except Exception as e:  # noqa: BLE001 - seguimos con el resto de tickers
            errors[t] = str(e)
            print(f"  {t:6s} | ERROR: {e}", file=sys.stderr)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "params": asdict(p),
        "tickers": results,
        "errors": errors,
    }

    os.makedirs(args.out, exist_ok=True)
    json_path = os.path.join(args.out, "signals.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    rows = [
        {
            "ticker": t,
            "timestamp": r["timestamp"],
            "price": r["price"],
            "rsi_weekly": r["rsi"]["weekly"],
            "rsi_4h": r["rsi"]["4h"],
            "trend": r["trend"],
            "weekly_bias": r["weekly_bias"],
            "zone_4h": r["zone_4h"],
            "signal": r["signal"],
            "confidence": r["confidence"],
        }
        for t, r in results.items()
    ]
    csv_path = os.path.join(args.out, "signals.csv")
    if rows:
        pd.DataFrame(rows).to_csv(csv_path, index=False)

    print(f"\nGuardado: {json_path}" + (f" y {csv_path}" if rows else ""))
    print(f"OK: {len(results)}  | Errores: {len(errors)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
