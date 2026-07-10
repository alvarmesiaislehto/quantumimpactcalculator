"""
Country quantum readiness scores (0.0 to 1.0).

Derived from McKinsey Quantum Technology Monitor 2026, pp.42–44
(government investment map and national quantum ecosystem strength assessment).
Scores reflect: public investment commitment, academic/research base,
industry ecosystem maturity, and quantum talent availability.

Default score for unlisted countries: 0.5 (global median estimate).
"""

# McKinsey QT Monitor 2026, pp.42–44 — government investment and ecosystem strength
READINESS_SCORES: dict[str, float] = {
    "US": 0.95,  # NQIA, NSF, DOE programs; largest private quantum ecosystem
    "CN": 0.90,  # Multi-billion RMB national quantum initiative; state-backed investment
    "DE": 0.85,  # €2B federal quantum program; Fraunhofer, FZJ, DLR institutes
    "GB": 0.85,  # £2.5B national quantum strategy; NQTP; strong universities
    "JP": 0.82,  # National quantum initiative; RIKEN, QST; IBM Q Network hub
    "CA": 0.78,  # NSERC/NRC programs; strong academic base (IQC Waterloo, Mila)
    "FR": 0.75,  # €1.8B national plan; CEA, CNRS; Pasqal, Alice & Bob ecosystem
    "NL": 0.75,  # Quantum Delta NL (€615M); QuTech (TU Delft / TNO)
    "AU": 0.72,  # National quantum strategy; UNSW, ANU; Silicon Quantum Computing
    "KR": 0.80,  # K-Quantum initiative; ETRI, KAIST; Samsung / SK Hynix involvement
    "FI": 0.82,  # IQM HQ country; VTT superconducting QPU; Aalto; strong Nordic ecosystem
    "SE": 0.78,  # Wallenberg Centre for Quantum Technology (WACQT); Chalmers
    "DK": 0.75,  # Danish quantum computing program; Niels Bohr Institute; NordIQuEst
    "IL": 0.78,  # National quantum initiative; Weizmann, Hebrew U; defense tech base
    "SG": 0.80,  # National Quantum Office; CQT (NUS); strong regional hub
    "CH": 0.77,  # ETH Zurich; PSI; IBM Q Hub Zurich; European quantum corridor
    "IN": 0.65,  # National Quantum Mission (~₹6,000 Cr); TIFR, IISc; growing ecosystem
    "BR": 0.50,  # Early-stage national programs; CBPF; limited dedicated funding
    "ZA": 0.45,  # Limited dedicated quantum investment; CSIR early programs
    "MX": 0.48,  # Nascent academic programs; UNAM quantum group
    "NO": 0.68,  # Nordic quantum collaboration; SINTEF; part of NordIQuEst
    "ES": 0.60,  # National plan; CSIC programs; BSC; Barcelona quantum hub forming
    "IT": 0.62,  # PNRR quantum programs (€130M); CNR; Quantum FLAGSHIP participation
    "PL": 0.58,  # EU-funded quantum programs; Warsaw University; QCI-POLAND
    "ID": 0.42,  # Early-stage; limited national quantum policy
    "MY": 0.45,  # Early-stage; MOSTI tech programs; limited quantum infrastructure
    "TH": 0.40,  # Early-stage; NSTDA programs; very limited quantum ecosystem
    "SA": 0.52,  # KACST; Vision 2030 tech investment; KAUST quantum research
    "AE": 0.55,  # UAE quantum program; Quantum.tech initiative; NYUAD research
    "TR": 0.52,  # TÜBITAK quantum programs; academic research base growing
    "AR": 0.48,  # CONICET quantum groups; limited national investment
    "BE": 0.68,  # imec (Leuven) superconducting research; EuroQCI participation
    "AT": 0.70,  # Vienna; long history in quantum optics (Zeilinger); AIT programs
    "IE": 0.62,  # Tyndall National Institute; QuSys group; EU quantum flagship node
    "PT": 0.55,  # IT (Instituto de Telecomunicações); EU quantum participation
    "LU": 0.53,  # LuxQuantum initiative; Uni Luxembourg; EU quantum flagship node
    "CZ": 0.58,  # ELI Beamlines; Prague quantum group; EU quantum flagship
    "GR": 0.52,  # Foundation for Research & Technology Hellas; growing
    "SI": 0.50,  # University of Ljubljana quantum group; EU quantum flagship participation
    "HU": 0.54,  # Budapest quantum research; ELI NP; EU participation
    "RO": 0.48,  # Limited dedicated investment; EU participation only
    "NZ": 0.60,  # University of Auckland; Victoria; aligned with AU programs
}

DEFAULT_READINESS: float = 0.5  # Global median for unlisted countries


def get_readiness_score(iso2: str, apply_readiness: bool) -> float:
    """
    Return the quantum readiness modifier for a country.

    When apply_readiness=False the function returns 1.0, meaning no country
    modifier is applied — the model runs as pure sector-GDP × penetration-rate.
    When apply_readiness=True, the country's readiness score (0–1) is returned
    and applied as a multiplier in the impact formula.

    Args:
        iso2: ISO 3166-1 alpha-2 country code (e.g. "US", "FI").
        apply_readiness: If False, always returns 1.0 (modifier disabled).

    Returns:
        Float in [0.0, 1.0]. Defaults to DEFAULT_READINESS for unlisted countries.

    Source: McKinsey QT Monitor 2026, pp.42–44.
    """
    if not apply_readiness:
        return 1.0
    return READINESS_SCORES.get(iso2.upper(), DEFAULT_READINESS)
