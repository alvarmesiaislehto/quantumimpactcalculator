"""
Crosswalk: World Bank broad sector categories → McKinsey QT Monitor 2026 sector taxonomy.

World Bank reports GDP in three macro buckets: manufacturing (subset of industry),
services, and industry total (which includes manufacturing, construction, mining/energy).
We apply fixed split ratios to allocate these to the nine McKinsey sectors used in
the quantum impact model.

Split ratio sources:
  Manufacturing splits — approximate global average split from OECD STAN 2022 data.
  Services splits      — approximate global average split from OECD STAN / World Bank.
  Industry splits      — derived from IEA energy sector share of industry value-added.

IMPORTANT: These are approximate global average splits.
Refine with OECD STAN database for production use:
  https://stats.oecd.org/Index.aspx?DataSetCode=STAN08BIS
"""

# Approximate global average split — refine with OECD STAN database for production use
MANUFACTURING_SPLITS: dict[str, float] = {
    "Chemicals & Materials": 0.15,
    "Pharma & Life Sciences": 0.10,
    "Advanced Industries": 0.35,
}

# Approximate global average split — refine with OECD STAN database for production use
SERVICES_SPLITS: dict[str, float] = {
    "Financial Services": 0.20,
    "Insurance": 0.05,
    "Telecom": 0.08,
    "Travel, Transport & Logistics": 0.12,
}

# Approximate global average split — refine with OECD STAN database for production use
# Note: industry_gdp includes manufacturing; energy ratios calibrated against the full
# industry base, including manufacturing, to yield plausible energy GDP estimates.
INDUSTRY_SPLITS: dict[str, float] = {
    "Energy — Electric Power": 0.15,
    "Energy — Oil & Gas": 0.10,
}


def apply_crosswalk(gdp_data: dict) -> dict[str, float]:
    """
    Convert World Bank broad sector GDPs to McKinsey QT Monitor sector GDPs.

    Args:
        gdp_data: Output from wb_fetcher.fetch_country_gdp_data(). Expected keys:
                  manufacturing_gdp_b, services_gdp_b, industry_gdp_b (all in $B).

    Returns:
        Dict mapping McKinsey sector name (str) → estimated sector GDP in $B (float).
        All nine sectors in SECTOR_RATES are always present; missing inputs default to 0.

    Note:
        Split ratios are approximate global averages. For country-specific precision,
        replace with OECD STAN bilateral industry statistics.
    """
    mfg = gdp_data.get("manufacturing_gdp_b", 0.0)
    svc = gdp_data.get("services_gdp_b", 0.0)
    ind = gdp_data.get("industry_gdp_b", 0.0)

    sector_gdp: dict[str, float] = {}

    # Approximate global average split — refine with OECD STAN database for production use
    for sector, ratio in MANUFACTURING_SPLITS.items():
        sector_gdp[sector] = mfg * ratio

    for sector, ratio in SERVICES_SPLITS.items():
        sector_gdp[sector] = svc * ratio

    for sector, ratio in INDUSTRY_SPLITS.items():
        sector_gdp[sector] = ind * ratio

    return sector_gdp
