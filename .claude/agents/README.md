# Mesa de Analisis — Sub-agentes

Equipo de 5 sub-agentes de Claude Code para analizar un activo (ticker) y decidir
si es buen momento de compra. Viven en `.claude/agents/` y se invocan con el Agent tool.

## El equipo

| # | Agente (name)          | Codename   | Labor |
|---|------------------------|------------|-------|
| 1 | `analista-entrada`     | Centinela  | ¿El precio actual es buen punto de entrada? (rango 52s, MAs, soportes) |
| 2 | `analista-crecimiento` | Vidente    | Variacion futura, **PEG** y **P/E** (trailing) |
| 3 | `analista-valoracion`  | Oraculo    | **Forward P/E** + sintetiza a los colegas → **decision de compra** |
| 4 | `analista-catalizadores`| Vigia     | Noticias y eventos proximos que muevan el precio |
| 5 | `analista-algoritmico` | Quant      | Lee los indicadores algoritmicos (RSI multihorario) — *pendiente del algoritmo* |

## Flujo de orquestacion

```
        ┌─ Centinela (entrada) ─┐
ticker ─┼─ Vidente  (crecimiento)┼──► Oraculo (forward P/E + sintesis) ──► DECISION
        ├─ Vigia    (catalizadores)
        └─ Quant    (algoritmo) ─┘   (PENDIENTE hasta crear el algoritmo)
```

- **Centinela, Vidente, Vigia y Quant** se pueden correr en paralelo (son independientes).
- **Oraculo** depende de los cuatro: consume sus veredictos y emite la decision final ponderada.
- **Quant** devolvera "PENDIENTE" hasta que construyamos el motor de RSI multihorario.

## Contrato de salida

Cada agente termina con un bloque `VEREDICTO`/`DECISION`, un nivel de confianza,
una nota "⚠️ Analisis informativo, no es asesoria financiera." y sus fuentes con fecha.
Esto permite que Oraculo combine los resultados de forma homogenea.

## Universo por defecto

Nucleo de semiconductores (presentes en ≥3 de SMH/SOXX/QQQ/XLK/VGT):

```
NVDA, AVGO, AMD, QCOM, TXN, INTC, MU, AMAT, LRCX, KLAC, ADI,
MCHP, MRVL, MPWR, TER, ON, ENTG, SWKS, COHR, NXPI, QRVO, ALAB
```

## Pendiente

- Construir el algoritmo de **RSI multihorario** cuya salida leera `Quant`
  (rutas esperadas: `indicators/`, `signals/`, `output/` en JSON/CSV).
