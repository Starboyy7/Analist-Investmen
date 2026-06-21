# Analist-Investmen

Sistema de analisis de acciones (foco: semiconductores / IA) compuesto por:

1. **Motor de senales** (`algo/`): RSI multihorario (semanal + 4h) con direccion EMA/VWAP.
2. **Mesa de Analisis** (`.claude/agents/`): 5 sub-agentes de Claude Code que investigan
   un ticker (entrada, crecimiento, valoracion, catalizadores y la senal algoritmica).

## Instalacion

```bash
pip install -r requirements.txt
```

## Motor de RSI multihorario

| Componente   | Temporalidad | Rol |
|--------------|--------------|-----|
| RSI semanal  | 1 semana     | Sesgo de fondo (alcista si >= 50) |
| RSI 4h       | 4 horas      | Timing: sobreventa <=30 / sobrecompra >=70 |
| EMA (o VWAP) | 4 horas      | Direccion de la tendencia (precio vs linea) |

### Senal compuesta

| RSI 4h      | Sesgo semanal + Tendencia | Senal |
|-------------|---------------------------|-------|
| sobreventa  | ambos alcistas            | **COMPRA FUERTE** |
| sobreventa  | uno alcista               | **COMPRA** |
| sobreventa  | ambos bajistas            | REBOTE DEBIL |
| sobrecompra | ambos bajistas            | **VENTA FUERTE** |
| sobrecompra | uno bajista               | **VENTA** |
| sobrecompra | ambos alcistas            | TOMAR GANANCIAS |
| neutral     | cualquiera                | NEUTRAL |

### Uso

```bash
# Uno o varios tickers
PYTHONPATH=. python3 -m algo.run NVDA AMD INTC

# Universo por defecto (22 semiconductores)
PYTHONPATH=. python3 -m algo.run --universe

# Opciones
PYTHONPATH=. python3 -m algo.run NVDA --direction vwap --oversold 25 --overbought 75 --ema-period 50
```

Genera `signals/signals.json` y `signals/signals.csv`, que lee el sub-agente **Quant**.

### Datos y red

Usa **yfinance** (Yahoo Finance, gratis, sin API key). El intervalo de 4h se construye
agregando velas de 1h (yfinance no ofrece 4h nativo).

> En entornos con egress restringido (p. ej. las sesiones web) Yahoo puede estar
> bloqueado. Para validar el pipeline sin red:
> `PYTHONPATH=. python3 scripts/demo_offline.py` (datos **sinteticos**, no reales).
> En tu maquina local corre con datos reales sin problema.

## Tests

```bash
PYTHONPATH=. python3 -m pytest -q
```

## Estructura

```
algo/                 motor: indicators.py, data.py, signals.py, run.py
scripts/demo_offline.py   demo sin red (datos sinteticos)
tests/                tests de indicadores y logica de senal
signals/              salida generada (signals.json / .csv)
.claude/agents/       los 5 sub-agentes (ver su README)
```

---
⚠️ Proyecto con fines informativos y educativos. **No es asesoria financiera.**
