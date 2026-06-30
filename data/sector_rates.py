"""
McKinsey QT Monitor 2026 penetration rates — ground truth.

Source: McKinsey_QT_2026_Impact_Rates.xlsx, Sheet 6 "Model Inputs — Ground Truth".
Consolidated from McKinsey Quantum Technology Monitor 2026, pp.17–26.
Mid rates = (Low + High) / 2 per spreadsheet formula =(D+E)/2.

NOTE: Mid values differ slightly from some secondary sources:
  Financial Services mid = 0.0375, NOT 0.038
  Travel, Transport & Logistics mid = 0.0325, NOT 0.033
"""

# McKinsey QT Monitor 2026, p.17 — Master Value-at-Stake Summary
# Deep dives: Pharma p.19–20, Chemicals p.21–22, Finance p.23–24, TTL p.25–26
SECTOR_RATES = {
    "Chemicals & Materials": {
        "low": 0.050,   # McKinsey QT Monitor 2026, p.22 (Chemicals deep dive)
        "mid": 0.070,   # = (0.050 + 0.090) / 2
        "high": 0.090,  # McKinsey QT Monitor 2026, p.22
        "value_at_stake_low": 450,   # McKinsey QT Monitor 2026, p.17
        "value_at_stake_high": 800,  # McKinsey QT Monitor 2026, p.17
        "mechanism": "Molecular simulation; catalyst design; new material invention",  # p.22
        "phase_2025_2030": "Medium",
        "phase_2030_2035": "High",
    },
    "Financial Services": {
        "low": 0.030,    # McKinsey QT Monitor 2026, p.24 (Finance deep dive)
        "mid": 0.0375,   # = (0.030 + 0.045) / 2
        "high": 0.045,   # McKinsey QT Monitor 2026, p.24
        "value_at_stake_low": 400,   # McKinsey QT Monitor 2026, p.17
        "value_at_stake_high": 600,  # McKinsey QT Monitor 2026, p.17
        "mechanism": "Portfolio/collateral optimisation; risk modelling; PQC/cryptography",  # p.24
        "phase_2025_2030": "Medium",
        "phase_2030_2035": "High",
    },
    "Pharma & Life Sciences": {
        "low": 0.020,   # McKinsey QT Monitor 2026, p.20 (Pharma deep dive)
        "mid": 0.070,   # = (0.020 + 0.120) / 2
        "high": 0.120,  # McKinsey QT Monitor 2026, p.20
        "value_at_stake_low": 50,    # McKinsey QT Monitor 2026, p.17
        "value_at_stake_high": 400,  # McKinsey QT Monitor 2026, p.17
        "mechanism": "Drug discovery simulation; clinical-trial optimisation; personalised medicine",  # p.20
        "phase_2025_2030": "Medium",
        "phase_2030_2035": "High",
    },
    "Travel, Transport & Logistics": {
        "low": 0.020,    # McKinsey QT Monitor 2026, p.26 (TTL deep dive)
        "mid": 0.0325,   # = (0.020 + 0.045) / 2
        "high": 0.045,   # McKinsey QT Monitor 2026, p.26
        "value_at_stake_low": 200,   # McKinsey QT Monitor 2026, p.17
        "value_at_stake_high": 500,  # McKinsey QT Monitor 2026, p.17
        "mechanism": "Route & network optimisation; warehouse scheduling; disruption management",  # p.26
        "phase_2025_2030": "Medium",
        "phase_2030_2035": "High",
    },
    "Advanced Industries": {
        "low": 0.010,   # McKinsey QT Monitor 2026, p.17
        "mid": 0.020,   # = (0.010 + 0.030) / 2
        "high": 0.030,  # McKinsey QT Monitor 2026, p.17
        "value_at_stake_low": 200,   # McKinsey QT Monitor 2026, p.17
        "value_at_stake_high": 500,  # McKinsey QT Monitor 2026, p.17
        "mechanism": "Component simulation; supply-chain optimisation; design optimisation",  # p.17
        "phase_2025_2030": "Low-Medium",
        "phase_2030_2035": "Medium",
    },
    "Energy — Electric Power": {
        "low": 0.010,   # McKinsey QT Monitor 2026, p.17
        "mid": 0.020,   # = (0.010 + 0.030) / 2
        "high": 0.030,  # McKinsey QT Monitor 2026, p.17
        "value_at_stake_low": 50,    # McKinsey QT Monitor 2026, p.17
        "value_at_stake_high": 150,  # McKinsey QT Monitor 2026, p.17
        "mechanism": "Grid optimisation; demand forecasting; energy storage simulation",  # p.17
        "phase_2025_2030": "Low",
        "phase_2030_2035": "Medium",
    },
    "Energy — Oil & Gas": {
        "low": 0.010,   # McKinsey QT Monitor 2026, p.17
        "mid": 0.020,   # = (0.010 + 0.030) / 2
        "high": 0.030,  # McKinsey QT Monitor 2026, p.17
        "value_at_stake_low": 50,    # McKinsey QT Monitor 2026, p.17
        "value_at_stake_high": 150,  # McKinsey QT Monitor 2026, p.17
        "mechanism": "Reservoir simulation; exploration optimisation; logistics",  # p.17
        "phase_2025_2030": "Low",
        "phase_2030_2035": "Medium",
    },
    "Insurance": {
        "low": 0.010,   # McKinsey QT Monitor 2026, p.17
        "mid": 0.015,   # = (0.010 + 0.020) / 2
        "high": 0.020,  # McKinsey QT Monitor 2026, p.17
        "value_at_stake_low": 10,   # McKinsey QT Monitor 2026, p.17
        "value_at_stake_high": 50,  # McKinsey QT Monitor 2026, p.17
        "mechanism": "Risk modelling; actuarial simulation; fraud detection",  # p.17
        "phase_2025_2030": "Medium",
        "phase_2030_2035": "Medium",
    },
    "Telecom": {
        "low": 0.010,   # McKinsey QT Monitor 2026, p.17
        "mid": 0.015,   # = (0.010 + 0.020) / 2
        "high": 0.020,  # McKinsey QT Monitor 2026, p.17
        "value_at_stake_low": 50,    # McKinsey QT Monitor 2026, p.17
        "value_at_stake_high": 100,  # McKinsey QT Monitor 2026, p.17
        "mechanism": "Network optimisation; PQC migration; signal processing",  # p.17
        "phase_2025_2030": "Low",
        "phase_2030_2035": "Medium",
    },
}

# ── Global sector GDP baseline ──────────────────────────────────────────────
# World GDP ~$105T (World Bank "1W", NY.GDP.MKTP.CD, 2024).
# Macro splits: Manufacturing 16%, Services 60%, Industry 28% (global averages).
# Crosswalk ratios from crosswalk.py applied to world macro GDPs.
# Used to derive the effective penetration rate from McKinsey's dollar value-at-stake:
#   effective_rate = McKinsey_QC_value_global_$B / global_sector_gdp_$B
WORLD_GDP_B: float = 105_000.0   # $105T in $B

GLOBAL_SECTOR_GDP_B: dict[str, float] = {
    # Manufacturing sectors  (world mfg GDP = $105,000B × 0.16 = $16,800B)
    "Chemicals & Materials":         16_800 * 0.15,   # $2,520B
    "Pharma & Life Sciences":         16_800 * 0.10,   # $1,680B
    "Advanced Industries":            16_800 * 0.35,   # $5,880B
    # Services sectors       (world services GDP = $105,000B × 0.60 = $63,000B)
    "Financial Services":             63_000 * 0.20,   # $12,600B
    "Insurance":                      63_000 * 0.05,   # $3,150B
    "Telecom":                        63_000 * 0.08,   # $5,040B
    "Travel, Transport & Logistics":  63_000 * 0.12,   # $7,560B
    # Industry sectors       (world industry GDP = $105,000B × 0.28 = $29,400B)
    "Energy — Electric Power":        29_400 * 0.15,   # $4,410B
    "Energy — Oil & Gas":             29_400 * 0.10,   # $2,940B
}

# S-curve adoption timeline factors — % of 2035 full value realised by that year.
# Rationale: McKinsey ++ (medium) phase = 2025–30, +++ (high) = 2030–35.
# S-curve midpoint ~2031. Source: McKinsey_QT_2026_Impact_Rates.xlsx, Sheet 6.
TIMELINE_FACTORS = {
    2026: 0.04,
    2027: 0.07,
    2028: 0.13,
    2029: 0.22,
    2030: 0.35,
    2031: 0.50,
    2032: 0.65,
    2033: 0.78,
    2034: 0.90,
    2035: 1.00,
}
