"""
qri.py — Quantum Readiness Index (QRI) module.

Computes a reproducible, transparent 0–1 readiness score for any country,
derived from 6 pillars and 18 metrics drawn from public data sources.

Main entry points:
  compute_qri_batch(country_iso3_list)  →  dict[iso3 → result_dict]
  get_qri(country_iso3)                 →  result_dict
  explain_qri(country_iso3, batch)      →  str

Result dict keys:
  qri      float 0–1
  pillars  dict pillar_name → float 0–1
  metrics  dict metric_key  → raw value
  sources  dict metric_key  → source string
  warnings list of str

Python 3.9+. External deps: requests only (already in requirements.txt).
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)

# ── Cache ─────────────────────────────────────────────────────────────────────
_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(_DIR, "qri_cache.json")
CACHE_MAX_AGE_DAYS = 30
_cache: Optional[dict] = None  # module-level cache store


def _load_cache() -> dict:
    global _cache
    if _cache is not None:
        return _cache
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                _cache = json.load(f)
            return _cache
    except Exception:
        pass
    _cache = {}
    return _cache


def _save_cache(cache: dict) -> None:
    global _cache
    _cache = cache
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    except Exception as exc:
        logger.warning("Could not save QRI cache: %s", exc)


def _cache_get(cache: dict, key: str) -> tuple[Any, bool]:
    """Return (value, hit). Hit=True only if entry exists and is fresh."""
    entry = cache.get(key)
    if entry is None:
        return None, False
    age_days = (time.time() - entry.get("ts", 0)) / 86400
    if age_days > CACHE_MAX_AGE_DAYS:
        return None, False
    return entry["v"], True


def _cache_set(cache: dict, key: str, value: Any) -> None:
    cache[key] = {"v": value, "ts": time.time()}


# ── ISO / geography tables ────────────────────────────────────────────────────
ISO3_TO_ISO2: dict[str, str] = {
    "USA": "US", "GBR": "GB", "DEU": "DE", "NLD": "NL", "AUS": "AU",
    "CAN": "CA", "FIN": "FI", "SWE": "SE", "CHN": "CN", "JPN": "JP",
    "SGP": "SG", "ISR": "IL", "FRA": "FR", "CHE": "CH", "AUT": "AT",
    "BEL": "BE", "DNK": "DK", "NOR": "NO", "ESP": "ES", "ITA": "IT",
    "POL": "PL", "CZE": "CZ", "IND": "IN", "KOR": "KR", "BRA": "BR",
    "ZAF": "ZA", "SAU": "SA", "ARE": "AE", "QAT": "QA", "KWT": "KW",
    "LUX": "LU",
}

ISO3_TO_NAME: dict[str, str] = {
    "USA": "United States", "GBR": "United Kingdom", "DEU": "Germany",
    "NLD": "Netherlands",   "AUS": "Australia",      "CAN": "Canada",
    "FIN": "Finland",       "SWE": "Sweden",          "CHN": "China",
    "JPN": "Japan",         "SGP": "Singapore",       "ISR": "Israel",
    "FRA": "France",        "CHE": "Switzerland",     "AUT": "Austria",
    "BEL": "Belgium",       "DNK": "Denmark",         "NOR": "Norway",
    "ESP": "Spain",         "ITA": "Italy",           "POL": "Poland",
    "CZE": "Czech Republic","IND": "India",           "KOR": "South Korea",
    "BRA": "Brazil",        "ZAF": "South Africa",   "SAU": "Saudi Arabia",
    "ARE": "UAE",           "QAT": "Qatar",           "KWT": "Kuwait",
    "LUX": "Luxembourg",
}

# Population in millions — World Bank 2023 estimates
POPULATION_M: dict[str, float] = {
    "USA": 331.5, "GBR": 67.2,  "DEU": 83.2,  "NLD": 17.6, "AUS": 25.7,
    "CAN": 38.2,  "FIN": 5.5,   "SWE": 10.4,  "CHN": 1411.8,"JPN": 125.7,
    "SGP": 5.7,   "ISR": 9.4,   "FRA": 67.4,  "CHE": 8.7,  "AUT": 9.0,
    "BEL": 11.6,  "DNK": 5.9,   "NOR": 5.4,   "ESP": 47.4, "ITA": 60.3,
    "POL": 37.8,  "CZE": 10.7,  "IND": 1380.0,"KOR": 51.7, "BRA": 214.3,
    "ZAF": 60.0,  "SAU": 35.0,  "ARE": 9.9,   "QAT": 2.9,  "KWT": 4.3,
    "LUX": 0.66,
}

# ── Seed data (inline-cited sources) ─────────────────────────────────────────

# Source: prompt spec / IQM internal + web search 2025
QUANTUM_PROGRAMS_SEED: dict[str, int] = {
    "USA": 28, "GBR": 12, "DEU": 10, "NLD": 8,  "AUS": 7,
    "CAN": 9,  "FIN": 4,  "SWE": 5,  "CHN": 15, "JPN": 8,
    "SGP": 4,  "ISR": 5,  "FRA": 7,  "CHE": 6,  "AUT": 3,
    "BEL": 3,  "DNK": 3,  "NOR": 2,  "ESP": 4,  "ITA": 4,
    "POL": 3,  "CZE": 2,  "IND": 6,  "KOR": 5,  "BRA": 3,
    "ZAF": 2,  "SAU": 1,  "ARE": 1,  "QAT": 1,  "KWT": 0,
}

# Source: McKinsey QTM 2026 pp.42–44 + national strategy docs
NATIONAL_STRATEGY: dict[str, int] = {
    "USA": 1, "GBR": 1, "DEU": 1, "FRA": 1, "NLD": 1, "AUS": 1,
    "CAN": 1, "JPN": 1, "CHN": 1, "KOR": 1, "SGP": 1, "ISR": 1,
    "IND": 1, "FIN": 1, "SWE": 1, "CHE": 1, "AUT": 1, "BEL": 1,
    "DNK": 1, "NOR": 1, "ESP": 1, "ITA": 1, "POL": 1, "CZE": 1,
    "SAU": 1, "ARE": 1, "BRA": 0, "ZAF": 0, "QAT": 0, "KWT": 0,
}

# Source: McKinsey QTM 2026 pp.42–44
# Tiers: >$1B→1.0, $100M–$1B→0.7, $10M–$100M→0.4, <$10M→0.1, unknown→0.2
GOV_BUDGET_TIER: dict[str, float] = {
    "USA": 1.0, "CHN": 1.0, "DEU": 0.7, "GBR": 0.7, "FRA": 0.7,
    "JPN": 0.7, "KOR": 0.7, "IND": 0.7, "AUS": 0.7, "NLD": 0.7,
    "CAN": 0.7, "SGP": 0.7, "ISR": 0.7, "FIN": 0.7, "SWE": 0.4,
    "CHE": 0.4, "AUT": 0.4, "BEL": 0.4, "DNK": 0.4, "NOR": 0.4,
    "ESP": 0.4, "ITA": 0.4, "POL": 0.4, "CZE": 0.4, "SAU": 0.4,
    "ARE": 0.4, "BRA": 0.2, "ZAF": 0.2, "QAT": 0.2, "KWT": 0.1,
}

# Source: IQM State of Quantum 2026 appendix
HPC_QUANTUM_PROGRAMS: dict[str, int] = {
    "JPN": 6, "DEU": 5, "ESP": 4, "FIN": 3, "FRA": 3,
    "ITA": 2, "USA": 2, "AUS": 1, "CHN": 1, "CZE": 1,
    "IND": 1, "LUX": 1, "NLD": 1, "POL": 1, "KOR": 1,
}

# Source: IQM State of Quantum 2026 + Dealroom (companies per 10M population)
QC_COMPANIES_PER_10M: dict[str, float] = {
    "USA": 8.2,  "GBR": 5.1, "CAN": 3.8, "AUS": 3.2, "ISR": 6.1,
    "NLD": 4.4,  "SWE": 3.9, "FIN": 5.2, "DEU": 2.8, "CHE": 4.1,
    "FRA": 2.3,  "AUT": 2.1, "BEL": 1.9, "DNK": 2.7, "NOR": 1.8,
    "SGP": 7.3,  "JPN": 1.2, "KOR": 1.4, "CHN": 0.4, "IND": 0.3,
    "ESP": 1.1,  "ITA": 0.9, "POL": 0.7, "CZE": 1.2, "BRA": 0.2,
    "ZAF": 0.3,  "SAU": 0.2, "ARE": 0.5, "QAT": 0.3, "KWT": 0.1,
}

# Source: IQM State of Quantum 2026; VC investment 2023–2025 per $1B GDP (USD M)
# Derived from regional totals (Americas $2.8B, Europe $1.4B, APAC $1.6B,
# ME $0.3B, Africa $0.05B) distributed by GDP weight within each region.
QVC_PER_GDP: dict[str, float] = {
    "USA": 0.142, "GBR": 0.178, "CAN": 0.082, "AUS": 0.062, "ISR": 0.382,
    "DEU": 0.071, "FRA": 0.091, "NLD": 0.121, "CHN": 0.088, "JPN": 0.041,
    "SGP": 0.218, "KOR": 0.072, "IND": 0.038, "FIN": 0.162, "SWE": 0.108,
    "CHE": 0.078, "AUT": 0.052, "BEL": 0.062, "DNK": 0.089, "NOR": 0.051,
    "ESP": 0.048, "ITA": 0.041, "POL": 0.031, "CZE": 0.038, "BRA": 0.022,
    "ZAF": 0.018, "SAU": 0.039, "ARE": 0.058, "QAT": 0.028, "KWT": 0.011,
}

# Source: World Bank / ITU Digital Development Dashboard 2023
DIGITAL_ADOPTION_SEED: dict[str, float] = {
    "USA": 0.88, "GBR": 0.91, "DEU": 0.84, "NLD": 0.93, "AUS": 0.87,
    "CAN": 0.86, "FIN": 0.92, "SWE": 0.93, "CHN": 0.79, "JPN": 0.89,
    "SGP": 0.95, "ISR": 0.88, "FRA": 0.85, "CHE": 0.91, "AUT": 0.86,
    "BEL": 0.88, "DNK": 0.92, "NOR": 0.93, "ESP": 0.83, "ITA": 0.80,
    "POL": 0.78, "CZE": 0.81, "IND": 0.54, "KOR": 0.93, "BRA": 0.65,
    "ZAF": 0.59, "SAU": 0.84, "ARE": 0.88, "QAT": 0.87, "KWT": 0.85,
}

# Source: IQM State of Quantum 2026 appendix (active + installing QPUs)
QPU_INSTALLED: dict[str, int] = {
    "JPN": 7, "DEU": 5, "FRA": 4, "ESP": 4, "FIN": 3,
    "USA": 3, "ITA": 2, "AUS": 1, "CHN": 1, "CZE": 1,
    "IND": 1, "NLD": 1, "POL": 1, "LUX": 1, "KOR": 1,
    "GBR": 1, "CAN": 1,
}

# Source: TOP500 list, November 2024 edition (top500.org)
TOP500_SEED: dict[str, int] = {
    "USA": 150, "CHN": 86,  "DEU": 18,  "JPN": 17,  "FRA": 14,
    "GBR": 11,  "NLD": 6,   "ITA": 6,   "AUS": 5,   "CAN": 5,
    "CHE": 5,   "KOR": 5,   "SGP": 4,   "SWE": 4,   "ESP": 4,
    "FIN": 3,   "NOR": 3,   "AUT": 2,   "BEL": 2,   "DNK": 2,
    "POL": 2,   "CZE": 1,   "IND": 1,   "ISR": 1,   "BRA": 1,
    "SAU": 1,   "ARE": 1,
}

# Source: UNESCO UIS ~2022 — STEM graduates % of total tertiary graduates
STEM_GRADUATES_SEED: dict[str, float] = {
    "USA": 21.5, "GBR": 24.3, "DEU": 31.2, "NLD": 27.8, "AUS": 22.7,
    "CAN": 21.8, "FIN": 30.1, "SWE": 29.4, "CHN": 38.2, "JPN": 34.7,
    "SGP": 35.8, "ISR": 28.6, "FRA": 28.9, "CHE": 30.5, "AUT": 27.3,
    "BEL": 26.1, "DNK": 28.4, "NOR": 27.9, "ESP": 25.6, "ITA": 23.4,
    "POL": 28.7, "CZE": 31.5, "IND": 32.8, "KOR": 35.6, "BRA": 18.9,
    "ZAF": 22.3, "SAU": 25.1, "ARE": 24.7, "QAT": 23.8, "KWT": 20.4,
}

# Source: QS World University Rankings 2025 — Physics + CS subjects, top-100
QS_UNIVERSITY_SEED: dict[str, int] = {
    "USA": 5, "CHN": 4, "GBR": 5, "DEU": 3, "AUS": 3,
    "CHE": 3, "SGP": 2, "JPN": 2, "FRA": 2, "CAN": 3,
    "NLD": 2, "ISR": 1, "SWE": 1, "KOR": 1, "NOR": 1,
    "DNK": 1, "FIN": 1, "AUT": 0, "BEL": 1, "IND": 1,
    "ITA": 1, "ESP": 0, "POL": 0, "CZE": 0, "BRA": 0,
    "ZAF": 0, "SAU": 0, "ARE": 0, "QAT": 0, "KWT": 0,
}

# Default batch used by get_qri() for normalisation reference
DEFAULT_BATCH = list({
    "USA", "GBR", "DEU", "NLD", "AUS", "CAN", "FIN", "SWE", "CHN", "JPN",
    "SGP", "ISR", "FRA", "CHE", "AUT", "BEL", "DNK", "NOR", "ESP", "ITA",
    "POL", "CZE", "IND", "KOR", "BRA", "ZAF", "SAU", "ARE", "QAT", "KWT",
})

# ── World Bank API fetching ───────────────────────────────────────────────────
_WB_URL = (
    "https://api.worldbank.org/v2/country/{iso2}/indicator/{indicator}"
    "?format=json&mrv=3"
)


def _fetch_wb(iso3: str, indicator: str, cache: dict) -> tuple[Optional[float], str]:
    """
    Fetch a World Bank indicator for a country.
    Returns (value, source_label). Falls back gracefully.
    """
    iso2 = ISO3_TO_ISO2.get(iso3)
    if not iso2:
        return None, "no_iso2_mapping"

    cache_key = f"wb_{iso3}_{indicator}"
    cached_val, hit = _cache_get(cache, cache_key)
    if hit:
        return cached_val, "cache"

    try:
        url = _WB_URL.format(iso2=iso2, indicator=indicator)
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if len(data) > 1 and isinstance(data[1], list):
            for entry in data[1]:
                if entry.get("value") is not None:
                    val = float(entry["value"])
                    _cache_set(cache, cache_key, val)
                    return val, "World Bank API (live)"
        _cache_set(cache, cache_key, None)
        return None, "World Bank API (null result)"
    except Exception as exc:
        logger.debug("WB fetch failed %s %s: %s", iso3, indicator, exc)
        return None, "World Bank API (error)"


# ── OpenAlex API fetching ─────────────────────────────────────────────────────
# Concept ID C21447398 = "quantum computing" in OpenAlex taxonomy
_OPENALEX_URL = (
    "https://api.openalex.org/works"
    "?filter=concepts.id:C21447398,"
    "authorships.institutions.country_code:{iso2},"
    "from_publication_date:2020-01-01,"
    "to_publication_date:2024-12-31"
    "&per_page=1&mailto=iqm-tool@iqm-quantum.com"
)
_OPENALEX_CITE_URL = (
    "https://api.openalex.org/works"
    "?filter=concepts.id:C21447398,"
    "authorships.institutions.country_code:{iso2},"
    "from_publication_date:2020-01-01,"
    "to_publication_date:2024-12-31"
    "&select=cited_by_count&per_page=200&mailto=iqm-tool@iqm-quantum.com"
)


def _fetch_openalex(iso3: str, cache: dict) -> tuple[Optional[float], Optional[float], str]:
    """
    Fetch quantum publication count and mean citation impact from OpenAlex.
    Returns (pub_count_per_10m_pop, citation_impact, source_label).

    Note: OpenAlex uses lowercase ISO 3166-1 alpha-2 country codes in filters.
    """
    iso2 = ISO3_TO_ISO2.get(iso3)
    if not iso2:
        return None, None, "no_iso2_mapping"

    cache_key = f"openalex_{iso3}"
    cached_val, hit = _cache_get(cache, cache_key)
    if hit:
        # Treat a cached [0.0, 0.0] as stale — likely fetched with wrong (uppercase)
        # country code before the lowercase fix was applied. Re-fetch instead.
        if cached_val and (cached_val[0] > 0 or cached_val[1] > 0):
            return cached_val[0], cached_val[1], "cache"

    try:
        # OpenAlex requires lowercase ISO-2 country codes in API filters
        iso2_lc = iso2.lower()
        url = _OPENALEX_URL.format(iso2=iso2_lc)
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        total = data.get("meta", {}).get("count", 0)

        if total == 0:
            # If we get 0 publications, don't cache — might be a transient API issue
            logger.debug("OpenAlex returned 0 publications for %s", iso3)
            return None, None, "OpenAlex API (zero result — will use mean fallback)"

        # Fetch citation sample (up to 200 works)
        cite_url = _OPENALEX_CITE_URL.format(iso2=iso2_lc)
        cresp = requests.get(cite_url, timeout=15)
        cresp.raise_for_status()
        cdata = cresp.json()
        works = cdata.get("results", [])
        mean_cite = (
            sum(w.get("cited_by_count", 0) for w in works) / len(works)
            if works else 0.0
        )

        pop = POPULATION_M.get(iso3, 10.0)
        pub_per_10m = total / pop * 10 if pop > 0 else 0.0

        _cache_set(cache, cache_key, [pub_per_10m, mean_cite])
        return pub_per_10m, mean_cite, "OpenAlex API (live)"

    except Exception as exc:
        logger.debug("OpenAlex fetch failed %s: %s", iso3, exc)
        return None, None, "OpenAlex API (error)"


# ── Raw metric collection ─────────────────────────────────────────────────────

def _collect_raw(iso3: str, cache: dict) -> dict:
    """
    Collect raw (un-normalised) metric values for one country.
    Returns dict with keys: metrics_raw, sources, warnings.
    """
    raw: dict[str, Optional[float]] = {}
    sources: dict[str, str] = {}
    warnings: list[str] = []

    # ── Pillar 1: Scientific Foundation ───────────────────────────────────────
    pub_per_10m, cite_impact, oa_src = _fetch_openalex(iso3, cache)

    if pub_per_10m is not None:
        raw["sci_publications"] = pub_per_10m
        sources["sci_publications"] = oa_src
    else:
        raw["sci_publications"] = None  # filled with mean later
        sources["sci_publications"] = "seed/mean_fallback"
        warnings.append(f"{iso3}: sci_publications — OpenAlex unavailable, will use cross-country mean")

    if cite_impact is not None:
        raw["sci_citation_impact"] = cite_impact
        sources["sci_citation_impact"] = oa_src
    else:
        raw["sci_citation_impact"] = None
        sources["sci_citation_impact"] = "seed/mean_fallback"
        warnings.append(f"{iso3}: sci_citation_impact — OpenAlex unavailable, will use cross-country mean")

    # QS university ranking (seed, capped at 5)
    qs_val = QS_UNIVERSITY_SEED.get(iso3, 0)
    raw["sci_university_rank"] = min(qs_val, 5)
    sources["sci_university_rank"] = "QS World University Rankings 2025 (seed)"

    # ── Pillar 2: Talent Pipeline ─────────────────────────────────────────────
    # STEM graduates % — UNESCO UIS (try WB proxy ED.TER.GRAD.FE.SI.ZS if available)
    stem_live, stem_src = _fetch_wb(iso3, "SE.TER.GRAD.FE.SI.ZS", cache)
    if stem_live is not None:
        raw["talent_stem_graduates"] = stem_live
        sources["talent_stem_graduates"] = f"World Bank (SE.TER.GRAD.FE.SI.ZS): {stem_src}"
    else:
        seed_val = STEM_GRADUATES_SEED.get(iso3)
        if seed_val is not None:
            raw["talent_stem_graduates"] = seed_val
            sources["talent_stem_graduates"] = "UNESCO UIS seed (~2022)"
        else:
            raw["talent_stem_graduates"] = None
            sources["talent_stem_graduates"] = "seed/mean_fallback"
            warnings.append(f"{iso3}: talent_stem_graduates — no data, will use cross-country mean")

    # Researcher density — World Bank SP.POP.SCIE.RD.P6
    rd_live, rd_src = _fetch_wb(iso3, "SP.POP.SCIE.RD.P6", cache)
    if rd_live is not None:
        raw["talent_researcher_density"] = rd_live
        sources["talent_researcher_density"] = f"World Bank (SP.POP.SCIE.RD.P6): {rd_src}"
    else:
        raw["talent_researcher_density"] = None
        sources["talent_researcher_density"] = "seed/mean_fallback"
        warnings.append(f"{iso3}: talent_researcher_density — WB returned null, will use cross-country mean")

    # Quantum programs (seed, capped at 10)
    qp_val = QUANTUM_PROGRAMS_SEED.get(iso3, 0)
    raw["talent_quantum_programs"] = min(qp_val, 10)
    sources["talent_quantum_programs"] = "IQM/web seed (prompt spec)"

    # ── Pillar 3: Government Commitment ───────────────────────────────────────
    # Binary: national strategy exists (already 0/1 normalised)
    raw["gov_strategy_exists"] = float(NATIONAL_STRATEGY.get(iso3, 0))
    sources["gov_strategy_exists"] = "McKinsey QTM 2026 pp.42–44 (seed)"

    # Budget tier (already tiered-normalised 0.1/0.2/0.4/0.7/1.0)
    raw["gov_budget_tier"] = GOV_BUDGET_TIER.get(iso3, 0.2)
    sources["gov_budget_tier"] = "McKinsey QTM 2026 pp.42–44 (seed)"

    # HPC-quantum programs (seed, capped at 6)
    hpc_val = HPC_QUANTUM_PROGRAMS.get(iso3, 0)
    raw["gov_hpc_programs"] = min(hpc_val, 6)
    sources["gov_hpc_programs"] = "IQM State of Quantum 2026 appendix (seed)"

    # ── Pillar 4: Private Ecosystem ───────────────────────────────────────────
    # QC companies per 10M population (seed)
    raw["eco_companies_per_capita"] = QC_COMPANIES_PER_10M.get(iso3, 0.0)
    sources["eco_companies_per_capita"] = "IQM State of Quantum 2026 + Dealroom (seed)"

    # VC investment per $1B GDP (seed)
    raw["eco_vc_investment"] = QVC_PER_GDP.get(iso3, 0.01)
    sources["eco_vc_investment"] = "IQM State of Quantum 2026 regional totals (seed)"

    # Digital adoption — WB 4G coverage proxy (TX.MOB.COV.4G.ZS), else seed
    dig_live, dig_src = _fetch_wb(iso3, "IT.NET.USER.ZS", cache)
    if dig_live is not None:
        # Internet user % → rescale to 0–1 proxy
        raw["eco_digital_adoption"] = min(dig_live / 100.0, 1.0)
        sources["eco_digital_adoption"] = f"World Bank (IT.NET.USER.ZS): {dig_src}"
    else:
        seed_val = DIGITAL_ADOPTION_SEED.get(iso3)
        if seed_val is not None:
            raw["eco_digital_adoption"] = seed_val
            sources["eco_digital_adoption"] = "World Bank / ITU DAI seed 2023"
        else:
            raw["eco_digital_adoption"] = None
            sources["eco_digital_adoption"] = "seed/mean_fallback"
            warnings.append(f"{iso3}: eco_digital_adoption — no data, will use cross-country mean")

    # ── Pillar 5: Infrastructure ──────────────────────────────────────────────
    # QPU count — tiered scoring (already normalised, do NOT min-max)
    qpu = QPU_INSTALLED.get(iso3, 0)
    if qpu >= 4:
        raw["infra_qpu_count"] = 1.00
    elif qpu == 3:
        raw["infra_qpu_count"] = 0.85
    elif qpu == 2:
        raw["infra_qpu_count"] = 0.65
    elif qpu == 1:
        raw["infra_qpu_count"] = 0.40
    else:
        raw["infra_qpu_count"] = 0.10
    sources["infra_qpu_count"] = "IQM State of Quantum 2026 appendix (seed)"

    # TOP500 supercomputers (seed, capped at 20)
    top500_val = TOP500_SEED.get(iso3, 0)
    raw["infra_top500_count"] = min(top500_val, 20)
    sources["infra_top500_count"] = "TOP500 list Nov 2024 (seed, top500.org)"

    # R&D spend % GDP — World Bank GB.XPD.RSDV.GD.ZS
    rd_gdp_live, rd_gdp_src = _fetch_wb(iso3, "GB.XPD.RSDV.GD.ZS", cache)
    if rd_gdp_live is not None:
        raw["infra_rd_spend_pct_gdp"] = rd_gdp_live
        sources["infra_rd_spend_pct_gdp"] = f"World Bank (GB.XPD.RSDV.GD.ZS): {rd_gdp_src}"
    else:
        raw["infra_rd_spend_pct_gdp"] = None
        sources["infra_rd_spend_pct_gdp"] = "seed/mean_fallback"
        warnings.append(f"{iso3}: infra_rd_spend_pct_gdp — WB returned null, will use cross-country mean")

    # ── Pillar 6: Absorptive Capacity ─────────────────────────────────────────
    # High-tech exports % manufactured exports — World Bank TX.VAL.TECH.MF.ZS
    ht_live, ht_src = _fetch_wb(iso3, "TX.VAL.TECH.MF.ZS", cache)
    if ht_live is not None:
        raw["abs_hightech_exports"] = ht_live
        sources["abs_hightech_exports"] = f"World Bank (TX.VAL.TECH.MF.ZS): {ht_src}"
    else:
        raw["abs_hightech_exports"] = None
        sources["abs_hightech_exports"] = "seed/mean_fallback"
        warnings.append(f"{iso3}: abs_hightech_exports — WB returned null, will use cross-country mean")

    # ICT service exports % total services — World Bank BX.GSR.CCIS.ZS
    ict_live, ict_src = _fetch_wb(iso3, "BX.GSR.CCIS.ZS", cache)
    if ict_live is not None:
        raw["abs_ict_exports"] = ict_live
        sources["abs_ict_exports"] = f"World Bank (BX.GSR.CCIS.ZS): {ict_src}"
    else:
        raw["abs_ict_exports"] = None
        sources["abs_ict_exports"] = "seed/mean_fallback"
        warnings.append(f"{iso3}: abs_ict_exports — WB returned null, will use cross-country mean")

    return {"metrics_raw": raw, "sources": sources, "warnings": warnings}


# ── Normalisation helpers ─────────────────────────────────────────────────────

# Metrics that are already on a 0–1 scale (tiered/binary) — skip min-max
_PRENORM_METRICS = {"gov_strategy_exists", "gov_budget_tier", "infra_qpu_count"}


def _fill_means(all_raw: dict[str, dict]) -> None:
    """
    For each metric, fill None values with the cross-country mean.
    Mutates all_raw in place.
    """
    metric_keys = list(next(iter(all_raw.values()))["metrics_raw"].keys())
    for key in metric_keys:
        vals = [
            d["metrics_raw"][key]
            for d in all_raw.values()
            if d["metrics_raw"].get(key) is not None
        ]
        mean_val = sum(vals) / len(vals) if vals else 0.5
        for iso3, d in all_raw.items():
            if d["metrics_raw"].get(key) is None:
                d["metrics_raw"][key] = mean_val
                d["warnings"].append(
                    f"{iso3}: {key} — missing, filled with cross-country mean {mean_val:.3f}"
                )


def _build_ranges(all_raw: dict[str, dict]) -> dict[str, tuple[float, float]]:
    """Compute (min, max) for each metric that needs min-max normalisation."""
    metric_keys = [
        k for k in next(iter(all_raw.values()))["metrics_raw"].keys()
        if k not in _PRENORM_METRICS
    ]
    ranges: dict[str, tuple[float, float]] = {}
    for key in metric_keys:
        vals = [d["metrics_raw"][key] for d in all_raw.values()]
        lo, hi = min(vals), max(vals)
        ranges[key] = (lo, hi)
    return ranges


def _normalise_metric(val: float, lo: float, hi: float) -> float:
    """Min-max normalise to [0, 1]. If range is zero, return 0.5."""
    if hi == lo:
        return 0.5
    return max(0.0, min(1.0, (val - lo) / (hi - lo)))


def _compute_qri_from_raw(
    iso3: str,
    raw_entry: dict,
    ranges: dict[str, tuple[float, float]],
) -> dict:
    """Build the final result dict for one country given normalisation ranges."""
    r = raw_entry["metrics_raw"]

    def norm(key: str) -> float:
        if key in _PRENORM_METRICS:
            return float(r[key])
        lo, hi = ranges.get(key, (0.0, 1.0))
        return _normalise_metric(r[key], lo, hi)

    # Pillar 1 — Scientific Foundation (weight 0.20)
    p1 = (norm("sci_publications") + norm("sci_citation_impact") + norm("sci_university_rank")) / 3

    # Pillar 2 — Talent Pipeline (weight 0.20)
    p2 = (norm("talent_stem_graduates") + norm("talent_researcher_density") + norm("talent_quantum_programs")) / 3

    # Pillar 3 — Government Commitment (weight 0.15)
    p3 = (norm("gov_strategy_exists") + norm("gov_budget_tier") + norm("gov_hpc_programs")) / 3

    # Pillar 4 — Private Ecosystem (weight 0.20)
    p4 = (norm("eco_companies_per_capita") + norm("eco_vc_investment") + norm("eco_digital_adoption")) / 3

    # Pillar 5 — Infrastructure (weight 0.15)
    p5 = (norm("infra_qpu_count") + norm("infra_top500_count") + norm("infra_rd_spend_pct_gdp")) / 3

    # Pillar 6 — Absorptive Capacity (weight 0.10)
    p6 = (norm("abs_hightech_exports") + norm("abs_ict_exports")) / 2

    pillars = {
        "Scientific Foundation": round(p1, 4),
        "Talent Pipeline":       round(p2, 4),
        "Government Commitment": round(p3, 4),
        "Private Ecosystem":     round(p4, 4),
        "Infrastructure":        round(p5, 4),
        "Absorptive Capacity":   round(p6, 4),
    }

    qri = (
        0.20 * p1 +
        0.20 * p2 +
        0.15 * p3 +
        0.20 * p4 +
        0.15 * p5 +
        0.10 * p6
    )
    qri = round(max(0.0, min(1.0, qri)), 4)
    assert 0.0 <= qri <= 1.0, f"QRI out of range for {iso3}: {qri}"

    return {
        "qri": qri,
        "pillars": pillars,
        "metrics": {k: round(v, 4) if isinstance(v, float) else v
                    for k, v in r.items()},
        "sources": raw_entry["sources"],
        "warnings": raw_entry["warnings"],
    }


# ── Public API ────────────────────────────────────────────────────────────────

def compute_qri_batch(
    country_iso3_list: list[str],
    year: int = None,
) -> dict[str, dict]:
    """
    Compute QRI for all countries simultaneously.

    Min-max normalisation is applied across the full supplied country set,
    so results are only comparable within the same batch call.

    Returns dict of iso3 → result dict with keys:
      qri, pillars, metrics, sources, warnings
    """
    cache = _load_cache()

    # Pass 1 — collect raw metrics for every country
    all_raw: dict[str, dict] = {}
    for iso3 in country_iso3_list:
        all_raw[iso3] = _collect_raw(iso3, cache)

    _save_cache(cache)

    # Pass 2 — fill missing values with cross-country means
    _fill_means(all_raw)

    # Pass 3 — build normalisation ranges
    ranges = _build_ranges(all_raw)

    # Pass 4 — compute normalised scores and QRI
    results: dict[str, dict] = {}
    for iso3 in country_iso3_list:
        results[iso3] = _compute_qri_from_raw(iso3, all_raw[iso3], ranges)

    return results


def get_qri(country_iso3: str, year: int = None) -> dict:
    """
    Compute QRI for a single country, using DEFAULT_BATCH as the
    normalisation reference set so results are consistent across calls.

    Returns the same result dict structure as compute_qri_batch values.
    """
    batch = country_iso3 if country_iso3 in DEFAULT_BATCH else DEFAULT_BATCH[:]
    if isinstance(batch, str):
        batch = DEFAULT_BATCH[:]
    if country_iso3 not in batch:
        batch = [country_iso3] + list(batch)
    results = compute_qri_batch(batch, year=year)
    return results[country_iso3]


# ── Explainability ────────────────────────────────────────────────────────────

def explain_qri(country_iso3: str, batch_results: dict) -> str:
    """
    Return a plain-English paragraph suitable for a client presentation,
    explaining why country_iso3 got its QRI score.

    Args:
        country_iso3:  ISO 3166-1 alpha-3 code (must be in batch_results).
        batch_results: Output of compute_qri_batch().
    """
    if country_iso3 not in batch_results:
        return f"No QRI data available for {country_iso3}."

    res = batch_results[country_iso3]
    qri = res["qri"]
    pillars = res["pillars"]
    name = ISO3_TO_NAME.get(country_iso3, country_iso3)

    # Rank the country within the batch
    all_scores = sorted([v["qri"] for v in batch_results.values()], reverse=True)
    rank = all_scores.index(qri) + 1
    n = len(all_scores)
    pct_rank = rank / n
    if pct_rank <= 0.25:
        quartile = "top quartile"
    elif pct_rank <= 0.50:
        quartile = "second quartile"
    elif pct_rank <= 0.75:
        quartile = "third quartile"
    else:
        quartile = "bottom quartile"

    # Sort pillars best → worst
    sorted_pillars = sorted(pillars.items(), key=lambda x: x[1], reverse=True)
    top2 = sorted_pillars[:2]
    bottom = sorted_pillars[-1]

    # Strength descriptions per pillar
    pillar_desc = {
        "Scientific Foundation": (
            "driven by quantum publication output and university research ranking"
        ),
        "Talent Pipeline": (
            "reflecting a strong pipeline of STEM graduates, research density, and "
            "quantum-specific academic programmes"
        ),
        "Government Commitment": (
            "supported by a national quantum strategy, public budget commitment, and "
            "active HPC-quantum deployments"
        ),
        "Private Ecosystem": (
            "evidenced by above-average quantum company density, venture investment, "
            "and digital infrastructure"
        ),
        "Infrastructure": (
            "anchored in installed quantum processing units, Top500 supercomputing "
            "presence, and R&D expenditure"
        ),
        "Absorptive Capacity": (
            "reflecting high-tech export strength and ICT service competitiveness"
        ),
    }

    weakness_desc = {
        "Scientific Foundation": (
            "a smaller academic research base relative to assessed peers"
        ),
        "Talent Pipeline": (
            "a more limited pipeline of quantum-ready talent compared with leading nations"
        ),
        "Government Commitment": (
            "earlier-stage public investment and fewer active government programmes"
        ),
        "Private Ecosystem": (
            "a developing private quantum ecosystem with scope for further venture "
            "capital and company formation"
        ),
        "Infrastructure": (
            "fewer installed quantum systems and lower R&D intensity than top-ranked peers"
        ),
        "Absorptive Capacity": (
            "a relatively smaller high-tech export base and economy scale rather than "
            "any fundamental structural weakness"
        ),
    }

    top1_name, top1_score = top2[0]
    top2_name, top2_score = top2[1]
    bot_name, bot_score = bottom

    para = (
        f"{name}'s QRI of {qri:.2f} ranks it {rank} of {n} assessed countries "
        f"({quartile}). "
        f"Its strongest dimensions are {top1_name} ({top1_score:.2f}), "
        f"{pillar_desc.get(top1_name, '')}, and {top2_name} ({top2_score:.2f}), "
        f"{pillar_desc.get(top2_name, '')}. "
        f"The relatively lower {bot_name} score ({bot_score:.2f}) reflects "
        f"{weakness_desc.get(bot_name, 'a gap relative to peers')}."
    )
    return para
