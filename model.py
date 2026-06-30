"""
Quantum Economic Impact Calculator — core model logic.

Formula (McKinsey QT Monitor 2026, p.17):
  impact = sector_gdp × penetration_rate × timeline_factor × readiness_score

Steps:
  1. Fetch GDP and sector percentages from World Bank API.
  2. Apply crosswalk to estimate McKinsey sector GDPs in $B.
  3. For each sector: multiply sector GDP by scenario penetration rate,
     S-curve timeline factor, and (optionally) country readiness score.
  4. Sum across all sectors for total impact.
"""

import pandas as pd

from data.sector_rates import SECTOR_RATES, TIMELINE_FACTORS, GLOBAL_SECTOR_GDP_B
from data.wb_fetcher import fetch_country_gdp_data
from data.crosswalk import apply_crosswalk
from data.readiness import get_readiness_score

SCENARIO_MAP: dict[str, str] = {
    "Conservative": "low",
    "Base": "mid",
    "Optimistic": "high",
}


def calculate_quantum_impact(
    country_iso2: str,
    year: int,
    scenario: str,
    apply_readiness: bool,
) -> tuple[list[dict], float, float]:
    """
    Estimate quantum economic impact for a country in a given year.

    Formula: impact = sector_gdp × penetration_rate × timeline_factor × readiness_score
    Source: McKinsey QT Monitor 2026, p.17.

    Args:
        country_iso2: ISO 3166-1 alpha-2 country code (e.g. "US", "FI").
        year: Target year in range 2026–2035.
        scenario: One of "Conservative", "Base", "Optimistic".
                  Maps to McKinsey low / mid / high penetration rates respectively.
        apply_readiness: If True, multiplies by country readiness score (0–1).
                         If False, readiness_score = 1.0 for all countries.

    Returns:
        (sector_results, total_impact_b, pct_of_gdp) where:
          sector_results   — list of dicts, one per McKinsey sector, with keys:
                             sector, sector_gdp_b, penetration_rate, timeline_factor,
                             readiness_score, quantum_impact_b, pct_of_sector_gdp
          total_impact_b   — sum of quantum impact across all sectors, in $B
          pct_of_gdp       — total_impact_b / total_GDP_b × 100
    """
    rate_key = SCENARIO_MAP.get(scenario, "mid")
    timeline_factor = TIMELINE_FACTORS.get(year, 1.0)
    readiness = get_readiness_score(country_iso2, apply_readiness)

    gdp_data = fetch_country_gdp_data(country_iso2)
    sector_gdps = apply_crosswalk(gdp_data)
    total_gdp_b = gdp_data.get("gdp_b", 0.0)

    sector_results: list[dict] = []
    total_impact = 0.0

    for sector, rates in SECTOR_RATES.items():
        s_gdp = sector_gdps.get(sector, 0.0)

        # Step 1 & 2 — McKinsey global QC value-at-stake for this scenario ($B)
        vas_low  = rates["value_at_stake_low"]
        vas_high = rates["value_at_stake_high"]
        if rate_key == "low":
            qc_global_b = float(vas_low)
        elif rate_key == "high":
            qc_global_b = float(vas_high)
        else:
            qc_global_b = (vas_low + vas_high) / 2.0

        # Step 2 — global sector GDP (world GDP × crosswalk ratios)
        global_s_gdp = GLOBAL_SECTOR_GDP_B.get(sector, 1.0)

        # Step 3 — effective rate = (global_sector + QC) / global_sector − 1
        #                         = QC_global / global_sector_GDP
        effective_rate = qc_global_b / global_s_gdp

        impact = s_gdp * effective_rate * timeline_factor * readiness
        total_impact += impact

        pct_of_sector = (impact / s_gdp * 100) if s_gdp > 0 else 0.0

        sector_results.append({
            "sector": sector,
            "sector_gdp_b": s_gdp,
            "qc_global_b": qc_global_b,
            "global_sector_gdp_b": global_s_gdp,
            "effective_rate": effective_rate,
            "penetration_rate": effective_rate,   # alias kept for compatibility
            "timeline_factor": timeline_factor,
            "readiness_score": readiness,
            "quantum_impact_b": impact,
            "pct_of_sector_gdp": pct_of_sector,
        })

    pct_of_gdp = (total_impact / total_gdp_b * 100) if total_gdp_b > 0 else 0.0

    return sector_results, total_impact, pct_of_gdp


def calculate_timeline_series(
    country_iso2: str,
    scenario: str,
    apply_readiness: bool,
) -> pd.DataFrame:
    """
    Calculate the quantum impact S-curve from 2026 to 2035.

    Calls calculate_quantum_impact for each year in 2026–2035 with the
    same scenario and readiness settings, building a time series.

    Args:
        country_iso2: ISO 3166-1 alpha-2 country code.
        scenario: One of "Conservative", "Base", "Optimistic".
        apply_readiness: Whether to apply the country readiness modifier.

    Returns:
        DataFrame with columns:
          year (int)           — calendar year
          total_impact_b (float) — total quantum impact in $B
          pct_of_gdp (float)   — impact as % of total GDP
    """
    rows = []
    for yr in range(2026, 2036):
        _, impact, pct = calculate_quantum_impact(country_iso2, yr, scenario, apply_readiness)
        rows.append({"year": yr, "total_impact_b": impact, "pct_of_gdp": pct})
    return pd.DataFrame(rows)
