"""
World Bank API fetcher for GDP and sector breakdown data.

API docs: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
No API key required. Uses mrv=3 to return up to 3 most recent years,
taking the first non-null value to handle reporting lags.

Indicators fetched per country:
  NV.IND.MANF.ZS  → manufacturing % of GDP
  NV.SRV.TOTL.ZS  → services % of GDP
  NV.AGR.TOTL.ZS  → agriculture % of GDP
  NV.IND.TOTL.ZS  → industry total % of GDP (includes manufacturing)
  NY.GDP.MKTP.CD  → GDP in current USD
"""

import requests
import streamlit as st

_WB_URL = "https://api.worldbank.org/v2/country/{iso2}/indicator/{indicator}?format=json&mrv=3"

INDICATORS = {
    "manufacturing_pct": "NV.IND.MANF.ZS",
    "services_pct": "NV.SRV.TOTL.ZS",
    "agriculture_pct": "NV.AGR.TOTL.ZS",
    "industry_pct": "NV.IND.TOTL.ZS",
    "gdp_usd": "NY.GDP.MKTP.CD",
}

# Fallback regional averages used when a World Bank indicator returns null.
# Based on approximate global averages (World Bank World Development Indicators, 2022).
REGIONAL_AVERAGES = {
    "manufacturing_pct": 15.0,
    "services_pct": 60.0,
    "agriculture_pct": 5.0,
    "industry_pct": 28.0,
}

# Country-specific structural overrides for known data gaps or unusual economies.
# Applied before the World Bank fetch; any indicator not listed here is still fetched live.
# Approximate GDP fallbacks in USD (World Bank 2023 estimates) for countries where
# the World Bank API may return null for NY.GDP.MKTP.CD (reporting lag or data gaps).
# Source: World Bank World Development Indicators 2023 / IMF WEO 2024.
GDP_FALLBACKS_USD: dict[str, float] = {
    "US":  2.788e13, "CN": 1.774e13, "DE":  4.456e12, "JP":  4.213e12,
    "GB":  3.086e12, "FR": 2.787e12, "IN":  3.550e12, "IT":  2.170e12,
    "CA":  2.140e12, "KR": 1.712e12, "AU":  1.728e12, "BR":  2.174e12,
    "ES":  1.581e12, "MX": 1.322e12, "ID":  1.371e12, "TR":  1.118e12,
    "NL":  1.118e12, "SA":  1.062e12, "CH":  8.844e11, "AR":  6.406e11,
    "SE":  5.908e11, "PL":  8.090e11, "BE":  6.284e11, "NO":  4.851e11,
    "AT":  4.713e11, "IL":  5.236e11, "SG":  5.009e11, "HK":  3.596e11,
    "MY":  4.302e11, "ZA":  3.993e11, "DK":  4.048e11, "FI":  3.022e11,
    "TH":  5.125e11, "IE":  5.356e11, "CZ":  3.302e11, "NZ":  2.471e11,
    "RO":  3.524e11, "PT":  2.878e11, "HU":  2.124e11, "GR":  2.398e11,
    "AE":  5.046e11, "PH":  4.352e11, "EG":  3.960e11, "VN":  4.335e11,
    "SI":  6.800e10,
    "LU":  8.700e10,  # Luxembourg ~$87B (World Bank 2023)
}

COUNTRY_OVERRIDES = {
    "SG": {  # Singapore: highly services-dominant, negligible agriculture
        "services_pct": 72.0,
        "manufacturing_pct": 20.0,
        "agriculture_pct": 0.1,
        "industry_pct": 24.0,
    },
    "AE": {  # UAE: oil & gas-heavy industry
        "industry_pct": 48.0,
        "manufacturing_pct": 10.0,
        "services_pct": 50.0,
        "agriculture_pct": 0.9,
    },
    "SA": {  # Saudi Arabia: oil-dominant economy
        "industry_pct": 55.0,
        "manufacturing_pct": 12.0,
        "services_pct": 43.0,
        "agriculture_pct": 2.3,
    },
    "QA": {  # Qatar: LNG-heavy
        "industry_pct": 60.0,
        "manufacturing_pct": 8.0,
        "services_pct": 39.0,
        "agriculture_pct": 0.2,
    },
    "KW": {  # Kuwait: oil-dominant
        "industry_pct": 57.0,
        "manufacturing_pct": 6.0,
        "services_pct": 42.0,
        "agriculture_pct": 0.4,
    },
}


def _fetch_indicator(iso2: str, indicator_code: str) -> float | None:
    """
    Fetch a single World Bank indicator for a country.

    Args:
        iso2: ISO 3166-1 alpha-2 country code.
        indicator_code: World Bank indicator ID (e.g. "NV.IND.MANF.ZS").

    Returns:
        Most recent non-null float value, or None on failure / missing data.
    """
    url = _WB_URL.format(iso2=iso2, indicator=indicator_code)
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if len(data) > 1 and isinstance(data[1], list):
            for entry in data[1]:
                if entry.get("value") is not None:
                    return float(entry["value"])
    except Exception:
        pass
    return None


@st.cache_data(ttl=3600)
def fetch_country_gdp_data(iso2: str) -> dict:
    """
    Fetch and derive GDP sector breakdown for a country via World Bank API.

    Applies COUNTRY_OVERRIDES for known structural cases (e.g. Singapore),
    then fetches remaining indicators live. Falls back to REGIONAL_AVERAGES
    for any indicator that returns null.

    Args:
        iso2: ISO 3166-1 alpha-2 country code (e.g. "US", "DE").

    Returns:
        Dict with keys:
          gdp_usd (float)       — GDP in current USD
          gdp_b (float)         — GDP in $B
          manufacturing_pct     — manufacturing % of GDP
          services_pct          — services % of GDP
          agriculture_pct       — agriculture % of GDP
          industry_pct          — industry (incl. manufacturing) % of GDP
          manufacturing_gdp_b   — manufacturing GDP in $B
          services_gdp_b        — services GDP in $B
          agriculture_gdp_b     — agriculture GDP in $B
          industry_gdp_b        — industry GDP in $B
    """
    overrides = COUNTRY_OVERRIDES.get(iso2.upper(), {})
    result: dict = {}

    for field, indicator_code in INDICATORS.items():
        if field == "gdp_usd":
            val = _fetch_indicator(iso2, indicator_code)
            fallback = GDP_FALLBACKS_USD.get(iso2.upper(), 0.0)
            result["gdp_usd"] = val if val is not None else fallback
        else:
            if field in overrides:
                result[field] = overrides[field]
            else:
                val = _fetch_indicator(iso2, indicator_code)
                result[field] = val if val is not None else REGIONAL_AVERAGES.get(field, 0.0)

    gdp_b = result["gdp_usd"] / 1e9
    result["gdp_b"] = gdp_b
    result["manufacturing_gdp_b"] = gdp_b * result.get("manufacturing_pct", 0.0) / 100
    result["services_gdp_b"] = gdp_b * result.get("services_pct", 0.0) / 100
    result["agriculture_gdp_b"] = gdp_b * result.get("agriculture_pct", 0.0) / 100
    result["industry_gdp_b"] = gdp_b * result.get("industry_pct", 0.0) / 100

    return result
