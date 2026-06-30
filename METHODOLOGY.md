# Quantum Economic Impact Calculator — Methodology

**Prepared for IQM Quantum Computers**
**Framework: McKinsey Quantum Technology Monitor 2026**

---

## What this tool estimates

The calculator estimates how much economic value quantum computing could unlock in a selected country by a chosen year. The output is expressed in billions of US dollars ($B) and as a percentage of the country's GDP.

This is an *illustrative model* — a structured way to translate McKinsey's global research into country-level context. It is not a financial forecast and should not be used as a basis for investment decisions.

---

## The formula

```
Quantum Impact ($B) = Sector GDP × Penetration Rate × Timeline Factor × Readiness Score
```

This is applied independently to each of the nine McKinsey sectors and the results are summed.

**Each component explained:**

| Component | What it is | Source |
|---|---|---|
| **Sector GDP** | The estimated size of that sector in the selected country, in $B | World Bank API + OECD STAN crosswalk |
| **Penetration Rate** | The fraction of sector GDP that quantum computing could affect by 2035 | McKinsey QT Monitor 2026, pp.17–26 |
| **Timeline Factor** | An S-curve multiplier (0–1) that scales the 2035 full value down to the selected year | McKinsey QT Monitor 2026, Phase analysis pp.17–26 |
| **Readiness Score** | A national modifier (0–1) reflecting a country's quantum ecosystem maturity | McKinsey QT Monitor 2026, pp.42–44 |

---

## Data sources

### 1. Penetration rates — McKinsey Quantum Technology Monitor 2026

McKinsey provides low and high penetration rate estimates for each sector, derived from sector-specific deep dives:

| Sector | Low | High | Mid (used in Base) |
|---|---|---|---|
| Chemicals & Materials | 5.0% | 9.0% | 7.0% |
| Financial Services | 3.0% | 4.5% | 3.75% |
| Pharma & Life Sciences | 2.0% | 12.0% | 7.0% |
| Travel, Transport & Logistics | 2.0% | 4.5% | 3.25% |
| Advanced Industries | 1.0% | 3.0% | 2.0% |
| Energy — Electric Power | 1.0% | 3.0% | 2.0% |
| Energy — Oil & Gas | 1.0% | 3.0% | 2.0% |
| Insurance | 1.0% | 2.0% | 1.5% |
| Telecom | 1.0% | 2.0% | 1.5% |

- **Conservative scenario** = McKinsey Low estimate
- **Base scenario** = arithmetic midpoint of Low and High
- **Optimistic scenario** = McKinsey High estimate

### 2. Sector GDP — World Bank API

The app fetches live GDP data from the World Bank's public API (no key required). It retrieves:
- Total GDP in current US dollars
- Manufacturing as % of GDP
- Services as % of GDP
- Agriculture as % of GDP
- Industry (total) as % of GDP

For countries where the World Bank data has gaps (e.g. Singapore's services-heavy structure, Gulf states' oil dominance), the app applies pre-set structural overrides based on IMF and World Bank structural economy profiles.

### 3. Sector crosswalk — OECD STAN approximation

The World Bank only reports broad macro categories. The app uses fixed split ratios — calibrated against OECD STAN bilateral industry data — to allocate World Bank sectors to the McKinsey taxonomy:

| McKinsey Sector | Derived from | Split ratio |
|---|---|---|
| Chemicals & Materials | Manufacturing GDP | 15% |
| Pharma & Life Sciences | Manufacturing GDP | 10% |
| Advanced Industries | Manufacturing GDP | 35% |
| Financial Services | Services GDP | 20% |
| Insurance | Services GDP | 5% |
| Telecom | Services GDP | 8% |
| Travel, Transport & Logistics | Services GDP | 12% |
| Energy — Electric Power | Industry GDP | 15% |
| Energy — Oil & Gas | Industry GDP | 10% |

**Important caveat:** These are approximate global averages. Country-specific structures vary considerably (e.g. Saudi Arabia has a much larger oil sector than the global average would suggest). For production-grade analysis, replace these splits with country-level data from the OECD STAN database.

### 4. Timeline factor — S-curve adoption

Quantum computing adoption follows an S-curve: slow early adoption, acceleration in the late 2020s, and broader value realisation by 2035. The factors represent the percentage of the full 2035 value that will be realised by each year:

| Year | Timeline Factor |
|---|---|
| 2026 | 4% |
| 2027 | 7% |
| 2028 | 13% |
| 2029 | 22% |
| 2030 | 35% |
| 2031 | 50% |
| 2032 | 65% |
| 2033 | 78% |
| 2034 | 90% |
| 2035 | 100% |

These are consistent with McKinsey's phase analysis: sectors rated "++" (Medium adoption) drive value in 2025–2030; sectors rated "+++" (High) accelerate further in 2030–2035.

### 5. Country readiness scores

When the "Country Readiness" toggle is enabled, the model applies a national quantum readiness modifier derived from McKinsey's government investment map (pp.42–44) and broader ecosystem strength indicators including:
- Public quantum investment commitments
- Academic and research infrastructure
- Industry ecosystem maturity
- Quantum talent pipeline

Scores range from 0.0 (no quantum ecosystem) to 1.0 (globally leading). Selected examples:
- United States: 0.95 (NQIA, NSF, DOE programs; largest private ecosystem)
- Finland: 0.82 (IQM HQ; VTT superconducting QPU; Aalto University)
- China: 0.90 (major state investment; national quantum initiative)
- India: 0.65 (National Quantum Mission; growing academic base)

When the toggle is **off**, the readiness modifier = 1.0 for all countries (pure sector-GDP model).

---

## Validation

The app includes a built-in validation check. Running the model for 30 major economies at 2035 Base scenario without readiness modifier should produce a combined total of **$1.3T – $2.7T** — consistent with McKinsey's published global quantum computing value-at-stake range (p.17). These 30 economies collectively represent approximately 80% of global GDP, so the sampled total should fall comfortably within the global range.

---

## Key limitations

1. **Sector crosswalk is approximate.** The split ratios converting World Bank macro data to McKinsey sectors are global averages. Countries with unusual economic structures (e.g. major oil exporters, financial hubs) will have less accurate sector-level estimates.

2. **World Bank data lags.** GDP data is typically 1–2 years behind. The app uses the most recent available value and caches results for 1 hour.

3. **Penetration rates are not forecasts.** McKinsey's rates represent the *potential* quantum impact if development and adoption proceed as expected. Actual realisation depends on hardware maturity, software ecosystem, regulatory environment, and organisational readiness.

4. **No overlap adjustment.** Some quantum use cases span multiple sectors (e.g. supply-chain optimisation benefits both Advanced Industries and Travel/Logistics). This model does not adjust for cross-sector overlap, which could cause slight double-counting.

5. **GDP as proxy for sector output.** The model uses sector GDP (value-added) as the baseline, while McKinsey's deep dives sometimes use gross sales or revenue. This can understate impact in sectors with high revenue-to-GDP ratios (e.g. Chemicals).

6. **This is illustrative, not predictive.** The model is suitable for client conversations and internal planning. It should not be used as a standalone basis for strategic investment decisions without additional analysis.

---

## How to update the model

- **Penetration rates:** Update `data/sector_rates.py` when new McKinsey reports are published.
- **Country structure:** Refine `data/crosswalk.py` split ratios using OECD STAN bilateral data for specific countries.
- **Readiness scores:** Update `data/readiness.py` as national quantum strategies evolve.
- **Timeline factors:** Adjust `TIMELINE_FACTORS` in `data/sector_rates.py` if adoption accelerates or decelerates relative to current expectations.

---

*Version 1.0 — May 2026*
*Based on McKinsey Quantum Technology Monitor 2026*
*Built for IQM Quantum Computers*
