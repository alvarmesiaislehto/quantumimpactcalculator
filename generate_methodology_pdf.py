"""
Generates METHODOLOGY_REPORT.pdf for the Quantum Economic Impact Calculator.
Run: python3 generate_methodology_pdf.py
"""

from datetime import date
import qri as _qri
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether,
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas as pdfcanvas

# ── Brand colours ─────────────────────────────────────────────────────────────
NAVY  = colors.HexColor("#1F3864")
GOLD  = colors.HexColor("#C9A84C")
LGREY = colors.HexColor("#F4F6FA")
MGREY = colors.HexColor("#E2E8F0")
BODY  = colors.HexColor("#1A1A2E")
MUTED = colors.HexColor("#6B7A9A")
WHITE = colors.white

PAGE_W, PAGE_H = A4
MARGIN = 2 * cm
BODY_W = PAGE_W - 2 * MARGIN


# ── Styles ────────────────────────────────────────────────────────────────────
def make_styles():
    s = {}
    s["body"]    = ParagraphStyle("body",    fontName="Helvetica",         fontSize=10, leading=15, textColor=BODY,  spaceAfter=6, alignment=TA_JUSTIFY)
    s["body_l"]  = ParagraphStyle("body_l",  fontName="Helvetica",         fontSize=10, leading=15, textColor=BODY,  spaceAfter=6)
    s["small"]   = ParagraphStyle("small",   fontName="Helvetica",         fontSize=8.5, leading=13, textColor=BODY, spaceAfter=4)
    s["h2"]      = ParagraphStyle("h2",      fontName="Helvetica-Bold",    fontSize=11, leading=15, textColor=NAVY,  spaceAfter=6,  spaceBefore=12)
    s["h3"]      = ParagraphStyle("h3",      fontName="Helvetica-BoldOblique", fontSize=10, leading=14, textColor=NAVY, spaceAfter=4, spaceBefore=8)
    s["callout"] = ParagraphStyle("callout", fontName="Helvetica-Oblique", fontSize=9.5, leading=14, textColor=NAVY, leftIndent=12, spaceAfter=4)
    s["formula"] = ParagraphStyle("formula", fontName="Courier-Bold",      fontSize=11, leading=16, textColor=NAVY,  alignment=TA_CENTER, spaceAfter=6)
    s["th"]      = ParagraphStyle("th",      fontName="Helvetica-Bold",    fontSize=9,  leading=12, textColor=WHITE)
    s["td"]      = ParagraphStyle("td",      fontName="Helvetica",         fontSize=9,  leading=12, textColor=BODY)
    s["url"]     = ParagraphStyle("url",     fontName="Courier",           fontSize=7,  leading=10, textColor=colors.HexColor("#1A5276"))
    s["footer"]  = ParagraphStyle("footer",  fontName="Helvetica",         fontSize=8,  leading=11, textColor=MUTED, alignment=TA_CENTER)
    return s

ST = make_styles()


# ── Custom flowables ──────────────────────────────────────────────────────────
class H1Band(Flowable):
    """Full-width navy heading band with white text."""
    def __init__(self, text):
        super().__init__()
        self.text = text

    def wrap(self, aw, ah):
        self._w = aw
        return aw, 28

    def draw(self):
        c = self.canv
        c.setFillColor(NAVY)
        c.rect(0, 0, self._w, 28, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(10, 8, self.text)


class LeftBorderBox(Flowable):
    """Light grey callout box with a gold left border."""
    def __init__(self, paragraphs):
        super().__init__()
        self.paragraphs = paragraphs

    def wrap(self, aw, ah):
        self._w = aw
        h = 12
        for p in self.paragraphs:
            _, ph = p.wrap(aw - 20, ah)
            h += ph + 4
        h += 8
        self._h = h
        return aw, h

    def draw(self):
        c = self.canv
        c.setFillColor(LGREY)
        c.roundRect(0, 0, self._w, self._h, 4, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.rect(0, 0, 4, self._h, fill=1, stroke=0)
        y = self._h - 10
        for p in self.paragraphs:
            _, ph = p.wrap(self._w - 20, 9999)
            p.drawOn(c, 14, y - ph)
            y -= ph + 4


# ── Page callbacks ────────────────────────────────────────────────────────────
def draw_cover(c, doc):
    """Draw the cover page entirely with canvas commands."""
    w, h = PAGE_W, PAGE_H

    # Navy background
    c.setFillColor(NAVY)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    # Gold top bar
    c.setFillColor(GOLD)
    c.rect(0, h - 1.4 * cm, w, 1.4 * cm, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN, h - 1.0 * cm, "IQM Quantum Computers")

    # Gold bottom bar
    c.setFillColor(GOLD)
    c.rect(0, 0, w, 0.7 * cm, fill=1, stroke=0)

    # Central content — positioned in upper half
    centre_x = w / 2
    atom_y = h * 0.68

    # Atom symbol
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 44)
    c.drawCentredString(centre_x, atom_y, "⛛")  # atom-like symbol

    # Main title
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 26)
    line1 = "Quantum Economic"
    line2 = "Impact Calculator"
    c.drawCentredString(centre_x, atom_y - 1.4 * cm, line1)
    c.drawCentredString(centre_x, atom_y - 2.4 * cm, line2)

    # Gold rule
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.line(centre_x - 4 * cm, atom_y - 3.1 * cm, centre_x + 4 * cm, atom_y - 3.1 * cm)

    # Subtitle
    c.setFillColor(GOLD)
    c.setFont("Helvetica", 17)
    c.drawCentredString(centre_x, atom_y - 3.9 * cm, "Methodology Report")

    # Tagline
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Oblique", 10.5)
    c.drawCentredString(centre_x, atom_y - 5.1 * cm,
                        "How the model works, where each number comes from,")
    c.drawCentredString(centre_x, atom_y - 5.8 * cm,
                        "and the assumptions that underpin every calculation.")

    # Source & date
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    c.drawCentredString(centre_x, 2.2 * cm,
                        "Based on McKinsey Quantum Technology Monitor 2026")
    c.drawCentredString(centre_x, 1.6 * cm,
                        f"Published {date.today().strftime('%B %Y')}  |  IQM Quantum Computers")


def draw_header_footer(c, doc):
    """Running header and footer for body pages."""
    w = PAGE_W
    c.saveState()
    # Gold rule at top
    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    c.line(MARGIN, PAGE_H - 1.35 * cm, w - MARGIN, PAGE_H - 1.35 * cm)
    # Header text
    c.setFont("Helvetica", 8)
    c.setFillColor(NAVY)
    c.drawString(MARGIN, PAGE_H - 1.1 * cm,
                 "IQM Quantum Computers  •  Quantum Economic Impact Calculator — Methodology")
    c.drawRightString(w - MARGIN, PAGE_H - 1.1 * cm, f"Page {doc.page}")
    # Footer rule
    c.setStrokeColor(MGREY)
    c.setLineWidth(0.5)
    c.line(MARGIN, 1.15 * cm, w - MARGIN, 1.15 * cm)
    # Footer text
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(w / 2, 0.75 * cm,
        "Based on McKinsey Quantum Technology Monitor 2026  •  "
        "For internal and client use  •  IQM Quantum Computers")
    c.restoreState()


def on_first_page(c, doc):
    draw_cover(c, doc)


def on_later_pages(c, doc):
    draw_header_footer(c, doc)


# ── Builder helpers ───────────────────────────────────────────────────────────
def h1(text):
    return [Spacer(1, 0.3 * cm), H1Band(text), Spacer(1, 0.2 * cm)]

def h2(text):
    return [Spacer(1, 0.15 * cm), Paragraph(text, ST["h2"])]

def h3(text):
    return [Paragraph(text, ST["h3"])]

def body(text):
    return [Paragraph(text, ST["body"])]

def sp(n=0.3):
    return [Spacer(1, n * cm)]

def callout(*lines):
    paras = [Paragraph(ln, ST["callout"]) for ln in lines]
    return [Spacer(1, 0.1 * cm), LeftBorderBox(paras), Spacer(1, 0.25 * cm)]

def formula_box(text):
    return [
        Spacer(1, 0.2 * cm),
        Table(
            [[Paragraph(text, ST["formula"])]],
            colWidths=[BODY_W],
            style=TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), LGREY),
                ("BOX",           (0, 0), (-1, -1), 1.5, GOLD),
                ("TOPPADDING",    (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("LEFTPADDING",   (0, 0), (-1, -1), 12),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
            ]),
        ),
        Spacer(1, 0.25 * cm),
    ]

def plain_table(headers, rows, col_widths=None):
    cw = col_widths or ([BODY_W / len(headers)] * len(headers))
    data = [[Paragraph(h, ST["th"]) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), ST["td"]) for c in row])
    tbl = Table(
        data, colWidths=cw, repeatRows=1,
        style=TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  NAVY),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LGREY]),
            ("GRID",          (0, 0), (-1, -1), 0.4, MGREY),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ]),
    )
    return [tbl, Spacer(1, 0.25 * cm)]


# ── Document content ──────────────────────────────────────────────────────────
def build_content():
    e = []

    # ── 1. Overview ───────────────────────────────────────────────────────────
    e += h1("1.   Overview")
    e += body(
        "The Quantum Economic Impact Calculator estimates the economic value that quantum "
        "computing could unlock in a given country by a chosen year. It translates the global "
        "sector-level research published in the <b>McKinsey Quantum Technology Monitor 2026</b> "
        "into country-specific dollar figures by combining live GDP data from the World Bank "
        "with McKinsey's quantum penetration rates, an S-curve adoption timeline, and an "
        "optional national quantum readiness modifier."
    )
    e += sp(0.1)
    e += body(
        "The tool was built for <b>IQM Quantum Computers</b> to support client conversations, "
        "market sizing exercises, and internal planning. It covers nine industry sectors across "
        "up to 40 countries and produces estimates for any target year between 2026 and 2035."
    )
    e += callout(
        "<b>Core formula:</b>",
        "Impact ($B) = Sector GDP  x  Penetration Rate  x  Timeline Factor  x  Readiness Score",
        "Applied independently to each of nine McKinsey sectors, then summed for the country total.",
    )

    # ── 2. The formula ────────────────────────────────────────────────────────
    e += h1("2.   The Core Formula")
    e += formula_box("Impact ($B)  =  Sector GDP  x  Penetration Rate  x  Timeline Factor  x  Readiness Score")
    e += body(
        "The formula is evaluated independently for all nine sectors and the results are summed "
        "to produce the country total and its percentage of GDP. Each component is described below."
    )

    e += h2("2.1  Sector GDP")
    e += body(
        "Sector GDP is the estimated size of a McKinsey industry sector within the selected "
        "country, in billions of US dollars. It is derived in two steps: first, broad macro GDP "
        "data is fetched live from the World Bank API; second, a sector crosswalk allocates that "
        "macro GDP to the nine McKinsey sectors using fixed split ratios. Both steps are "
        "described in detail in Sections 4 and 5."
    )

    e += h2("2.2  Penetration Rate")
    e += body(
        "The penetration rate is the fraction of a sector's GDP that quantum computing is "
        "estimated to affect by 2035. Rates come directly from the McKinsey Quantum Technology "
        "Monitor 2026 (pp. 17-26) and vary by sector and scenario. "
        "The <b>Base</b> (mid) rate = (Low + High) / 2, matching the formula in the ground-truth "
        "spreadsheet (McKinsey_QT_2026_Impact_Rates.xlsx, Sheet 6). "
        "Two values that are sometimes cited differently in secondary sources:"
    )
    e += body(
        "Financial Services mid = (0.030 + 0.045) / 2 = <b>0.0375</b>  |  "
        "Travel, Transport &amp; Logistics mid = (0.020 + 0.045) / 2 = <b>0.0325</b>"
    )

    e += h2("2.3  Timeline Factor")
    e += body(
        "A multiplier between 0 and 1 that discounts the full 2035 value down to the selected "
        "year, reflecting the S-curve nature of technology adoption. A factor of 0.35 at 2030 "
        "means 35% of the full 2035 potential is expected to be realised by that year."
    )
    tl_data = [
        [Paragraph(h, ST["th"]) for h in
         ["2026", "2027", "2028", "2029", "2030", "2031", "2032", "2033", "2034", "2035"]],
        [Paragraph(v, ST["td"]) for v in
         ["4%",   "7%",   "13%",  "22%",  "35%",  "50%",  "65%",  "78%",  "90%",  "100%"]],
    ]
    e += [
        Table(
            tl_data,
            colWidths=[BODY_W / 10] * 10,
            style=TableStyle([
                ("BACKGROUND",    (0, 0), (-1, 0),  NAVY),
                ("BACKGROUND",    (0, 1), (-1, 1),  LGREY),
                ("GRID",          (0, 0), (-1, -1), 0.4, MGREY),
                ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]),
        ),
        Spacer(1, 0.15 * cm),
    ]
    e += body(
        "The midpoint is set at approximately 2031, consistent with McKinsey's phase analysis: "
        "sectors rated ++ (Medium) are expected to drive value in 2025-2030, while +++ (High) "
        "sectors accelerate further in 2030-2035."
    )

    e += h2("2.4  Readiness Score")
    e += body(
        "An optional national modifier (0-1) that scales a country's estimate based on its "
        "quantum ecosystem maturity. Applied only when the Country Readiness toggle is enabled. "
        "When the toggle is off, all countries use a score of 1.0 - a pure sector-GDP model "
        "with no country adjustment. Section 6 describes score derivation in full."
    )

    # ── 3. Worked example ─────────────────────────────────────────────────────
    e += h1("3.   Worked Example — Germany at 2030, Base Scenario")
    e += body(
        "The following shows the full calculation for Germany (DE) at the 2030 target year "
        "under the Base scenario with the Country Readiness toggle off (score = 1.0)."
    )

    e += h2("Step 1 — World Bank GDP data (2024, most recent available)")
    e += plain_table(
        ["Indicator", "World Bank Code", "Value"],
        [
            ["Total GDP",                    "NY.GDP.MKTP.CD",  "$4,686B"],
            ["Manufacturing % of GDP",        "NV.IND.MANF.ZS",  "18.0%   ->   Mfg GDP = $843B"],
            ["Services % of GDP",             "NV.SRV.TOTL.ZS",  "64.0%   ->   Svc GDP = $2,999B"],
            ["Industry total % of GDP",       "NV.IND.TOTL.ZS",  "25.6%   ->   Ind GDP = $1,199B"],
        ],
        col_widths=[5.2 * cm, 4.5 * cm, 5.9 * cm],
    )

    e += h2("Step 2 — Crosswalk: macro GDP to McKinsey sectors")
    e += plain_table(
        ["McKinsey Sector", "Source", "Ratio", "Sector GDP ($B)"],
        [
            ["Chemicals & Materials",        "Manufacturing", "15%", "$126.5"],
            ["Pharma & Life Sciences",        "Manufacturing", "10%", "$84.3"],
            ["Advanced Industries",           "Manufacturing", "35%", "$295.1"],
            ["Financial Services",            "Services",      "20%", "$599.8"],
            ["Insurance",                     "Services",       "5%", "$149.9"],
            ["Telecom",                       "Services",       "8%", "$239.9"],
            ["Travel, Transport & Logistics", "Services",      "12%", "$359.9"],
            ["Energy — Electric Power",  "Industry",      "15%", "$179.9"],
            ["Energy — Oil & Gas",       "Industry",      "10%", "$119.9"],
        ],
        col_widths=[5.6 * cm, 3.0 * cm, 1.8 * cm, 3.8 * cm],
    )

    e += h2("Step 3 — Apply rate x timeline factor x readiness (TF = 0.35, R = 1.0)")
    e += plain_table(
        ["Sector", "Sector GDP", "Rate", "x TF (0.35)", "Impact ($B)"],
        [
            ["Chemicals & Materials",        "$126.5B", "7.00%", "0.35", "$3.10"],
            ["Pharma & Life Sciences",        "$84.3B",  "7.00%", "0.35", "$2.07"],
            ["Advanced Industries",           "$295.1B", "2.00%", "0.35", "$2.07"],
            ["Financial Services",            "$599.8B", "3.75%", "0.35", "$7.87"],
            ["Insurance",                     "$149.9B", "1.50%", "0.35", "$0.79"],
            ["Telecom",                       "$239.9B", "1.50%", "0.35", "$1.26"],
            ["Travel, Transport & Logistics", "$359.9B", "3.25%", "0.35", "$4.09"],
            ["Energy — Electric Power",  "$179.9B", "2.00%", "0.35", "$1.26"],
            ["Energy — Oil & Gas",       "$119.9B", "2.00%", "0.35", "$0.84"],
            ["TOTAL", "", "", "", "$23.4B"],
        ],
        col_widths=[5.5 * cm, 2.8 * cm, 2.0 * cm, 2.8 * cm, 2.5 * cm],
    )
    e += callout(
        "<b>Result:</b> Germany's estimated quantum economic impact by 2030 (Base, no readiness) "
        "is approximately $23.4B, or 0.50% of GDP. "
        "By 2035 (Timeline Factor = 1.0), this rises to approximately $66.7B (1.42% of GDP).",
    )

    # ── 4. World Bank data ────────────────────────────────────────────────────
    e += h1("4.   World Bank GDP Data")
    e += body(
        "GDP and sector breakdown data is fetched live from the World Bank's public REST API "
        "at api.worldbank.org (no authentication required). Five indicators are fetched per "
        "country using the mrv=3 parameter, which returns the three most recent annual values; "
        "the first non-null is used to handle the typical 1-2 year reporting lag. "
        "Results are cached in memory for one hour per session."
    )

    e += h2("Fallback hierarchy (applied in order)")
    e += body("<b>1.</b> Country-specific structural override for five economies with unusual sector structures.")
    e += body("<b>2.</b> Live World Bank API value.")
    e += body("<b>3.</b> Hardcoded GDP fallback for 44 countries (2023 World Bank / IMF estimates), used when the GDP indicator returns null.")
    e += body("<b>4.</b> Regional average sector percentages as a last resort (Manufacturing 15%, Services 60%, Industry 28%).")

    e += plain_table(
        ["Country", "Override applied", "Reason"],
        [
            ["Singapore (SG)", "Services 72%, Mfg 20%, Agr 0.1%",
             "Services-dominant city-state; World Bank default understates service share"],
            ["UAE (AE)",        "Industry 48%, Services 50%",
             "Oil & gas-heavy industry; global average underestimates energy sector"],
            ["Saudi Arabia (SA)", "Industry 55%, Services 43%",
             "Oil-dominant economy; ~50% of GDP from hydrocarbons"],
            ["Qatar (QA)",      "Industry 60%, Services 39%",
             "LNG-dominant; industry share among the world's highest"],
            ["Kuwait (KW)",     "Industry 57%, Services 42%",
             "Oil accounts for ~55% of government revenue and GDP"],
        ],
        col_widths=[3.0 * cm, 5.5 * cm, 7.1 * cm],
    )

    # ── 5. Sector crosswalk ───────────────────────────────────────────────────
    e += h1("5.   Sector Crosswalk")
    e += body(
        "The World Bank reports GDP in three macro buckets: manufacturing (a subset of "
        "industry), services, and industry total. McKinsey uses nine specific sectors. "
        "The crosswalk maps between them using fixed global-average split ratios derived "
        "from OECD STAN 2022 bilateral industry data and IEA energy sector statistics."
    )
    e += plain_table(
        ["McKinsey Sector", "Source", "Ratio", "Basis"],
        [
            ["Chemicals & Materials",        "Manufacturing", "15%",
             "Chemicals share of global manufacturing value-added (OECD STAN 2022)"],
            ["Pharma & Life Sciences",        "Manufacturing", "10%",
             "Pharma share of global manufacturing value-added"],
            ["Advanced Industries",           "Manufacturing", "35%",
             "Auto, aerospace, electronics, semiconductors combined"],
            ["Financial Services",            "Services",      "20%",
             "Banking & capital markets share of services GDP"],
            ["Insurance",                     "Services",       "5%",
             "Insurance share of services GDP"],
            ["Telecom",                       "Services",       "8%",
             "Telecoms share of services GDP"],
            ["Travel, Transport & Logistics", "Services",      "12%",
             "Transport & hospitality share of services GDP"],
            ["Energy — Electric Power",  "Industry",      "15%",
             "IEA: electric utilities share of industry value-added"],
            ["Energy — Oil & Gas",       "Industry",      "10%",
             "IEA: oil & gas extraction share of industry value-added"],
        ],
        col_widths=[4.2 * cm, 2.6 * cm, 1.6 * cm, 7.2 * cm],
    )
    e += callout(
        "<b>Key limitation:</b> These are global averages. For production use, replace with "
        "country-specific data from the OECD STAN bilateral industry statistics database "
        "(stats.oecd.org). Countries with unusual sector concentrations (e.g. oil exporters, "
        "financial hubs) will have less accurate sector-level estimates."
    )

    # ── 6. McKinsey penetration rates ─────────────────────────────────────────
    e += h1("6.   McKinsey Penetration Rates")
    e += body(
        "The penetration rates are the most consequential inputs in the model. They represent "
        "McKinsey's estimate of the fraction of each sector's economic output that quantum "
        "computing will influence by 2035. They were extracted directly from the McKinsey "
        "Quantum Technology Monitor 2026 and cross-referenced against the ground-truth "
        "spreadsheet (McKinsey_QT_2026_Impact_Rates.xlsx, Sheet 6)."
    )
    e += plain_table(
        ["Sector", "Low", "Mid (Base)", "High", "Value at Stake", "Source"],
        [
            ["Chemicals & Materials",        "5.0%", "7.00%", "9.0%",  "$450-800B", "p.17, p.22"],
            ["Financial Services",            "3.0%", "3.75%", "4.5%",  "$400-600B", "p.17, p.24"],
            ["Pharma & Life Sciences",        "2.0%", "7.00%", "12.0%", "$50-400B",  "p.17, p.20"],
            ["Travel, Transport & Logistics", "2.0%", "3.25%", "4.5%",  "$200-500B", "p.17, p.26"],
            ["Advanced Industries",           "1.0%", "2.00%", "3.0%",  "$200-500B", "p.17"],
            ["Energy — Electric Power",  "1.0%", "2.00%", "3.0%",  "$50-150B",  "p.17"],
            ["Energy — Oil & Gas",       "1.0%", "2.00%", "3.0%",  "$50-150B",  "p.17"],
            ["Insurance",                     "1.0%", "1.50%", "2.0%",  "$10-50B",   "p.17"],
            ["Telecom",                       "1.0%", "1.50%", "2.0%",  "$50-100B",  "p.17"],
        ],
        col_widths=[4.5 * cm, 1.3 * cm, 2.1 * cm, 1.3 * cm, 2.8 * cm, 2.3 * cm],
    )
    e += callout(
        "<b>Calibration note:</b> McKinsey's sector deep dives use gross output or revenues as "
        "the baseline (e.g. global pharma gross sales ~$3.1T, p.20). This model applies the "
        "same rates to sector GDP (value-added), which is typically 3-5x smaller for "
        "manufacturing sectors. Absolute impact estimates will therefore be conservative "
        "relative to a direct extrapolation of McKinsey's sector value-at-stake figures."
    )

    # ── 7. Country readiness scores ───────────────────────────────────────────
    e += h1("7.   Country Readiness Scores — the QRI Framework")
    e += body(
        "The Country Readiness Score is produced by the <b>Quantum Readiness Index (QRI)</b>, "
        "a transparent, reproducible framework that derives a single 0–1 score from "
        "<b>6 pillars and 18 metrics</b> drawn entirely from public data sources. "
        "It replaces the previous expert-judgement scores with a fully auditable calculation "
        "that can be refreshed automatically as new data becomes available."
    )
    e += body(
        "When the readiness toggle is enabled in the app, each country's QRI score replaces "
        "the value 1.0 in the core formula, scaling the estimate down to reflect how likely "
        "the country is to realise its theoretical quantum potential. When the toggle is off, "
        "all countries use 1.0 — a pure sector-GDP model."
    )

    e += h2("7.1  How the QRI is calculated")
    e += body(
        "All metrics are min-max normalised across the set of assessed countries, so the "
        "top performer on each metric receives 1.0 and the bottom receives 0.0. Pillar scores "
        "are the unweighted mean of their constituent metrics. The final QRI is the weighted "
        "sum of pillar scores using the weights shown below."
    )
    e += plain_table(
        ["Pillar", "Weight", "Metrics included", "Primary sources"],
        [
            ["Scientific Foundation",   "20%",
             "Quantum publications per 10M pop (5-yr); citation impact; "
             "top-100 QS university count (Physics/CS)",
             "OpenAlex API; QS Rankings 2025"],
            ["Talent Pipeline",          "20%",
             "STEM graduates % tertiary; researchers per million pop; "
             "quantum MSc/PhD programme count",
             "UNESCO UIS; World Bank SP.POP.SCIE.RD.P6; IQM seed"],
            ["Government Commitment",    "15%",
             "National quantum strategy (binary); public budget tier "
             "(>$1B=1.0, $100M–$1B=0.7, etc.); active HPC-quantum programmes",
             "McKinsey QTM 2026 pp.42–44; IQM State of Quantum 2026"],
            ["Private Ecosystem",        "20%",
             "Quantum companies per 10M pop; VC investment per $1B GDP "
             "(2023–2025); digital adoption proxy",
             "IQM SoQ 2026 + Dealroom; World Bank IT.NET.USER.ZS"],
            ["Infrastructure",           "15%",
             "Installed QPU count (tiered score); Top500 supercomputer count; "
             "R&D expenditure % GDP",
             "IQM SoQ 2026; TOP500 Nov 2024; World Bank GB.XPD.RSDV.GD.ZS"],
            ["Absorptive Capacity",      "10%",
             "High-tech exports % manufactured exports; "
             "ICT service exports % total service exports",
             "World Bank TX.VAL.TECH.MF.ZS; BX.GSR.CCIS.ZS"],
        ],
        col_widths=[3.5 * cm, 1.4 * cm, 6.3 * cm, 4.4 * cm],
    )
    e += callout(
        "<b>Data freshness:</b> World Bank indicators are fetched live with a 30-day local "
        "cache (qri_cache.json). The module runs fully offline using seed dictionaries if "
        "no internet connection is available. All seed sources are cited inline in qri.py.",
    )

    e += h2("7.2  Computed QRI scores — all assessed countries")
    e += body(
        "Scores are computed live at report generation time. Countries are ranked by QRI. "
        "Sci = Scientific Foundation, Tal = Talent Pipeline, Gov = Government Commitment, "
        "Eco = Private Ecosystem, Inf = Infrastructure, Abs = Absorptive Capacity."
    )

    # QRI scores table — injected at build time via the _qri_results argument
    # (populated in build() below; None → fallback notice)
    _qri_results = build_content._qri_results  # passed in via closure
    if _qri_results:
        _pk = ["Scientific Foundation", "Talent Pipeline", "Government Commitment",
               "Private Ecosystem", "Infrastructure", "Absorptive Capacity"]
        rows = []
        for iso3, res in sorted(_qri_results.items(), key=lambda x: x[1]["qri"], reverse=True):
            name = _qri.ISO3_TO_NAME.get(iso3, iso3)
            row = [name, f"{res['qri']:.3f}"]
            for k in _pk:
                row.append(f"{res['pillars'].get(k, 0):.2f}")
            rows.append(row)
        e += plain_table(
            ["Country", "QRI", "Sci", "Tal", "Gov", "Eco", "Inf", "Abs"],
            rows,
            col_widths=[3.9*cm, 1.3*cm, 1.4*cm, 1.4*cm, 1.3*cm, 1.4*cm, 1.3*cm, 1.3*cm],
        )

        e += h2("7.3  What the scores mean — selected countries")
        for iso3 in ("USA", "DEU", "FIN", "JPN", "IND", "BRA"):
            if iso3 in _qri_results:
                e += body(_qri.explain_qri(iso3, _qri_results))
    else:
        e += callout(
            "<b>Note:</b> QRI scores could not be computed for this run. "
            "Run with an active internet connection or ensure qri_cache.json is present."
        )

    # ── 8. Global validation ──────────────────────────────────────────────────
    e += h1("8.   Global Validation")
    e += body(
        "The app includes a built-in validation check. Running the model for 30 major "
        "economies at the 2035 Base scenario without the readiness modifier produces a "
        "combined quantum economic impact of approximately <b>$1.29 trillion</b>."
    )
    e += plain_table(
        ["Parameter", "Value"],
        [
            ["Countries sampled",                              "30 major economies"],
            ["Collective share of world GDP",                  "~82%"],
            ["Target year",                                    "2035"],
            ["Scenario",                                       "Base (mid penetration rates)"],
            ["Readiness modifier",                             "Off (score = 1.0 for all countries)"],
            ["Validation result",                              "~$1.29T"],
            ["Validation pass range (GDP-based model)",        "$0.9T - $2.5T"],
            ["McKinsey global range (gross output baseline)",  "$1.28T - $2.7T"],
        ],
        col_widths=[9 * cm, 6.6 * cm],
    )
    e += body(
        "The result of $1.29T is consistent with expectations for a GDP-based model. "
        "McKinsey's $1.28T-$2.7T global range is calibrated against sector revenues, which "
        "are larger than value-added GDP. The model's implied global total "
        "($1.29T / 0.82 = $1.57T) falls within the McKinsey range, confirming correct order-"
        "of-magnitude calibration."
    )

    # ── 9. Limitations ────────────────────────────────────────────────────────
    e += h1("9.   Limitations and Assumptions")
    limitations = [
        ("Sector crosswalk uses global averages",
         "Split ratios are global estimates, not country-specific. Countries with unusual "
         "sector concentrations (e.g. oil exporters, financial hubs) will have less accurate "
         "sector-level estimates. "
         "<b>Direction: uncertain.</b> "
         "Refinement: replace with OECD STAN country-level industry data."),
        ("GDP (value-added) vs gross output calibration gap",
         "McKinsey rates are calibrated against sector revenues; this model uses value-added "
         "GDP, which is 3-5x smaller for manufacturing sectors. "
         "<b>Direction: understatement for Chemicals, Pharma, Advanced Industries.</b> "
         "Refinement: add sector-specific gross-output multipliers."),
        ("World Bank data lag",
         "GDP data is typically 1-2 years behind. The most recent available year is used. "
         "<b>Direction: minor impact; GDP is relatively stable year-on-year.</b>"),
        ("No sector overlap adjustment",
         "Some quantum use cases span multiple sectors (e.g. supply-chain optimisation "
         "benefits both Advanced Industries and Travel/Logistics). "
         "<b>Direction: potential overstatement.</b>"),
        ("Global penetration rates applied uniformly",
         "The same McKinsey rates are applied to all countries regardless of their quantum "
         "sector readiness. A country's pharma sector may differ markedly from the global average. "
         "<b>Direction: uncertain.</b>"),
        ("Readiness scores are coarse proxies",
         "Single national scores with no sub-national or sector-specific variation. "
         "<b>Direction: uncertain.</b>"),
        ("Single S-curve applied to all sectors",
         "In reality, Financial Services will likely adopt earlier than Pharma or Chemicals, "
         "which require fault-tolerant quantum hardware. "
         "<b>Direction: overstatement for Pharma/Chemicals pre-2030; understatement for Finance.</b>"),
        ("Static GDP base",
         "Current GDP figures are used without projecting economic growth to the target year. "
         "<b>Direction: understatement for high-growth economies.</b>"),
    ]
    for i, (title, desc) in enumerate(limitations, 1):
        e += [KeepTogether([
            Paragraph(f"<b>{i}.  {title}</b>", ST["h3"]),
            Paragraph(desc, ST["body"]),
            Spacer(1, 0.1 * cm),
        ])]

    # ── 10. Per-country calculations & verification ───────────────────────────
    e += h1("10.  Per-Country Calculations and Verification")
    e += body(
        "This section provides a complete, step-by-step calculation for each of the four "
        "countries in the tool — Germany, United States, Finland and Italy — at the "
        "<b>2030 target year, Base scenario, Country Readiness toggle off</b> (modifier = 1.0). "
        "All GDP figures are fetched live from the World Bank Open Data API; the values "
        "shown here were retrieved on <b>7 June 2026</b> and may differ slightly if the "
        "World Bank updates its dataset. The penetration rates and crosswalk ratios are "
        "fixed model constants (Sections 5 and 6) and do not change between runs."
    )

    e += h2("10.1  How to verify the results independently")
    e += body(
        "You can replicate every number in this document using a browser and a calculator. "
        "The three-step process is:"
    )
    e += body(
        "<b>Step 1 — Fetch GDP from the World Bank.</b> Open one of the API URLs in the "
        "table below. The JSON response contains the country's GDP in USD and the sector "
        "percentages. Divide GDP in USD by 1,000,000,000 to get $B."
    )
    e += body(
        "<b>Step 2 — Apply the crosswalk.</b> Multiply the macro GDP ($B) by the relevant "
        "sector percentage to get the sector GDP. Then multiply that by the crosswalk ratio "
        "(e.g. 20% of Services GDP for Financial Services, Section 5)."
    )
    e += body(
        "<b>Step 3 — Apply the formula.</b> Sector GDP × Penetration Rate × Timeline Factor. "
        "For 2030 Base: rate from the table in Section 6, Timeline Factor = 0.35."
    )

    e += h2("10.2  World Bank API verification links")
    e += body(
        "Each link below opens the raw JSON response from the World Bank API — the exact "
        "data the model reads. The first non-null value in the response is what is used. "
        "<b>Click any link in a PDF reader, or copy the URL into a browser.</b>"
    )

    def _wb_link_para(iso2, code):
        """Return a Paragraph with a correctly-escaped clickable World Bank API link."""
        # Raw URL (used as the actual href destination in the PDF)
        raw = f"https://api.worldbank.org/v2/country/{iso2}/indicator/{code}?mrv=3&format=json"
        # &amp; escaping is required inside ReportLab XML markup so the parser
        # doesn't treat '&' as an XML entity opener — both in href and visible text.
        xml = raw.replace("&", "&amp;")
        return Paragraph(
            f'<a href="{xml}" color="#1A5276"><u>{xml}</u></a>',
            ST["url"],
        )

    # Build the verification table manually so the URL column uses the url style
    _vrows = [
        [Paragraph(h, ST["th"]) for h in ["Country", "Indicator", "WB Code", "Live API link (clickable)"]],
    ]
    _link_data = [
        ("Germany",       "DE", "NY.GDP.MKTP.CD",  "Total GDP (USD)"),
        ("Germany",       "DE", "NV.IND.MANF.ZS",  "Manufacturing % of GDP"),
        ("Germany",       "DE", "NV.SRV.TOTL.ZS",  "Services % of GDP"),
        ("Germany",       "DE", "NV.IND.TOTL.ZS",  "Industry % of GDP"),
        ("United States", "US", "NY.GDP.MKTP.CD",  "Total GDP (USD)"),
        ("United States", "US", "NV.IND.MANF.ZS",  "Manufacturing % of GDP"),
        ("United States", "US", "NV.SRV.TOTL.ZS",  "Services % of GDP"),
        ("United States", "US", "NV.IND.TOTL.ZS",  "Industry % of GDP"),
        ("Finland",       "FI", "NY.GDP.MKTP.CD",  "Total GDP (USD)"),
        ("Finland",       "FI", "NV.IND.MANF.ZS",  "Manufacturing % of GDP"),
        ("Finland",       "FI", "NV.SRV.TOTL.ZS",  "Services % of GDP"),
        ("Finland",       "FI", "NV.IND.TOTL.ZS",  "Industry % of GDP"),
        ("Italy",         "IT", "NY.GDP.MKTP.CD",  "Total GDP (USD)"),
        ("Italy",         "IT", "NV.IND.MANF.ZS",  "Manufacturing % of GDP"),
        ("Italy",         "IT", "NV.SRV.TOTL.ZS",  "Services % of GDP"),
        ("Italy",         "IT", "NV.IND.TOTL.ZS",  "Industry % of GDP"),
    ]
    for country, iso2, code, label in _link_data:
        _vrows.append([
            Paragraph(country, ST["td"]),
            Paragraph(label,   ST["td"]),
            Paragraph(code,    ST["td"]),
            _wb_link_para(iso2, code),
        ])
    _vtbl = Table(
        _vrows,
        colWidths=[2.3*cm, 3.3*cm, 2.9*cm, 7.1*cm],
        repeatRows=1,
        style=TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  NAVY),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LGREY]),
            ("GRID",          (0, 0), (-1, -1), 0.4, MGREY),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ]),
    )
    e += [_vtbl, Spacer(1, 0.25 * cm)]

    # Also add the World Bank Open Data portal links (human-friendly)
    e += body(
        "You can also browse each country's full data profile on the "
        "<b>World Bank Open Data portal</b>:"
    )
    _portal_data = [
        ("Germany",       "https://data.worldbank.org/country/germany"),
        ("United States", "https://data.worldbank.org/country/united-states"),
        ("Finland",       "https://data.worldbank.org/country/finland"),
        ("Italy",         "https://data.worldbank.org/country/italy"),
    ]
    for country, url in _portal_data:
        e += [Paragraph(
            f'<b>{country}:</b>  '
            f'<a href="{url}" color="#1A5276"><u>{url}</u></a>',
            ST["body_l"],
        )]
    e += sp(0.2)

    # ── Country helper: 3-table layout (WB data, crosswalk, impacts) ─────────
    def country_calc(sec_num, country_name, iso2, gdp_b, mfg_pct, svc_pct, ind_pct, data_year,
                     mfg_b, svc_b, ind_b, sectors_xwalk, sectors_impact, total_b, pct_gdp):
        out = []
        out += h2(f"10.{sec_num}  {country_name} ({iso2}) — 2030, Base, no readiness")
        out += body(
            f"World Bank data year: <b>{data_year}</b>.  "
            f"Total GDP: <b>${gdp_b:,.1f}B</b>.  "
            f"Manufacturing: {mfg_pct:.2f}% → ${mfg_b:.1f}B  |  "
            f"Services: {svc_pct:.2f}% → ${svc_b:.1f}B  |  "
            f"Industry: {ind_pct:.2f}% → ${ind_b:.1f}B."
        )
        # Crosswalk table
        out += [Paragraph("Crosswalk (Section 5 ratios applied to macro GDP):", ST["h3"])]
        out += plain_table(
            ["McKinsey Sector", "Source macro", "Ratio", "Sector GDP ($B)"],
            sectors_xwalk,
            col_widths=[5.6*cm, 3.2*cm, 1.8*cm, 3.6*cm],
        )
        # Impact table
        out += [Paragraph(
            "Quantum impact = Sector GDP × Penetration Rate × Timeline Factor (0.35):",
            ST["h3"]
        )]
        out += plain_table(
            ["McKinsey Sector", "Sector GDP ($B)", "Rate (Base)", "Impact ($B)"],
            sectors_impact,
            col_widths=[5.6*cm, 3.2*cm, 2.4*cm, 3.4*cm],
        )
        out += callout(
            f"<b>{country_name} result — 2030 Base:</b>  "
            f"Total quantum impact = <b>${total_b:.3f}B</b> ({pct_gdp:.3f}% of GDP).  "
            f"By 2035 (Timeline Factor = 1.0): <b>${total_b/0.35:.1f}B</b> ({pct_gdp/0.35:.2f}% of GDP).",
        )
        return out

    # ─── Germany ──────────────────────────────────────────────────────────────
    # World Bank 2024: GDP=$4,685.6B, Mfg=18.007%, Svc=64.046%, Ind=25.623%
    e += country_calc(
        3, "Germany", "DE",
        gdp_b=4685.6, mfg_pct=18.007, svc_pct=64.046, ind_pct=25.623,
        data_year="2024",
        mfg_b=843.8, svc_b=3001.4, ind_b=1200.7,
        sectors_xwalk=[
            ["Chemicals & Materials",        "Manufacturing", "15%", "126.6"],
            ["Pharma & Life Sciences",        "Manufacturing", "10%", "84.4"],
            ["Advanced Industries",           "Manufacturing", "35%", "295.3"],
            ["Financial Services",            "Services",      "20%", "600.3"],
            ["Insurance",                     "Services",       "5%", "150.1"],
            ["Telecom",                       "Services",       "8%", "240.1"],
            ["Travel, Transport & Logistics", "Services",      "12%", "360.2"],
            ["Energy — Electric Power",       "Industry",      "15%", "180.1"],
            ["Energy — Oil & Gas",            "Industry",      "10%", "120.1"],
        ],
        sectors_impact=[
            ["Financial Services",            "600.3",  "3.75%", "7.879"],
            ["Travel, Transport & Logistics", "360.2",  "3.25%", "4.097"],
            ["Chemicals & Materials",         "126.6",  "7.00%", "3.101"],
            ["Pharma & Life Sciences",        "84.4",   "7.00%", "2.067"],
            ["Advanced Industries",           "295.3",  "2.00%", "2.067"],
            ["Energy — Electric Power",       "180.1",  "2.00%", "1.261"],
            ["Telecom",                       "240.1",  "1.50%", "1.261"],
            ["Energy — Oil & Gas",            "120.1",  "2.00%", "0.841"],
            ["Insurance",                     "150.1",  "1.50%", "0.788"],
            ["TOTAL (all 9 sectors)",         "",       "",      "23.362"],
        ],
        total_b=23.362, pct_gdp=0.499,
    )

    # ─── United States ────────────────────────────────────────────────────────
    # World Bank GDP 2024, sectoral %s from 2021 (most recent non-null):
    # GDP=$28,751.0B, Mfg=10.710%, Svc=77.599%, Ind=17.885%
    e += [Paragraph(
        "<i>Note: The World Bank's sectoral breakdown for the United States (Manufacturing, "
        "Services, Industry as % of GDP) was last updated in 2021. The total GDP figure is "
        "from 2024. The model applies the most recent non-null values for each indicator "
        "independently, using mrv=3 in the API call.</i>",
        ST["small"],
    )]
    e += country_calc(
        4, "United States", "US",
        gdp_b=28751.0, mfg_pct=10.710, svc_pct=77.599, ind_pct=17.885,
        data_year="2024 (GDP) / 2021 (sector %s)",
        mfg_b=3079.4, svc_b=22309.9, ind_b=5141.8,
        sectors_xwalk=[
            ["Chemicals & Materials",        "Manufacturing", "15%", "461.9"],
            ["Pharma & Life Sciences",        "Manufacturing", "10%", "307.9"],
            ["Advanced Industries",           "Manufacturing", "35%", "1,077.8"],
            ["Financial Services",            "Services",      "20%", "4,461.9"],
            ["Insurance",                     "Services",       "5%", "1,115.5"],
            ["Telecom",                       "Services",       "8%", "1,784.8"],
            ["Travel, Transport & Logistics", "Services",      "12%", "2,677.2"],
            ["Energy — Electric Power",       "Industry",      "15%", "771.3"],
            ["Energy — Oil & Gas",            "Industry",      "10%", "514.2"],
        ],
        sectors_impact=[
            ["Financial Services",            "4,461.9", "3.75%", "58.564"],
            ["Travel, Transport & Logistics", "2,677.2", "3.25%", "30.453"],
            ["Chemicals & Materials",         "461.9",   "7.00%", "11.317"],
            ["Telecom",                       "1,784.8", "1.50%", "9.370"],
            ["Pharma & Life Sciences",        "307.9",   "7.00%", "7.544"],
            ["Advanced Industries",           "1,077.8", "2.00%", "7.544"],
            ["Insurance",                     "1,115.5", "1.50%", "5.856"],
            ["Energy — Electric Power",       "771.3",   "2.00%", "5.399"],
            ["Energy — Oil & Gas",            "514.2",   "2.00%", "3.599"],
            ["TOTAL (all 9 sectors)",         "",        "",      "139.646"],
        ],
        total_b=139.646, pct_gdp=0.486,
    )

    # ─── Finland ─────────────────────────────────────────────────────────────
    # World Bank 2024: GDP=$298.7B, Mfg=14.233%, Svc=62.214%, Ind=22.784%
    e += country_calc(
        5, "Finland", "FI",
        gdp_b=298.7, mfg_pct=14.233, svc_pct=62.214, ind_pct=22.784,
        data_year="2024",
        mfg_b=42.5, svc_b=185.9, ind_b=68.1,
        sectors_xwalk=[
            ["Chemicals & Materials",        "Manufacturing", "15%", "6.4"],
            ["Pharma & Life Sciences",        "Manufacturing", "10%", "4.3"],
            ["Advanced Industries",           "Manufacturing", "35%", "14.9"],
            ["Financial Services",            "Services",      "20%", "37.2"],
            ["Insurance",                     "Services",       "5%", "9.3"],
            ["Telecom",                       "Services",       "8%", "14.9"],
            ["Travel, Transport & Logistics", "Services",      "12%", "22.3"],
            ["Energy — Electric Power",       "Industry",      "15%", "10.2"],
            ["Energy — Oil & Gas",            "Industry",      "10%", "6.8"],
        ],
        sectors_impact=[
            ["Financial Services",            "37.2",  "3.75%", "0.488"],
            ["Travel, Transport & Logistics", "22.3",  "3.25%", "0.254"],
            ["Chemicals & Materials",         "6.4",   "7.00%", "0.156"],
            ["Pharma & Life Sciences",        "4.3",   "7.00%", "0.104"],
            ["Advanced Industries",           "14.9",  "2.00%", "0.104"],
            ["Telecom",                       "14.9",  "1.50%", "0.078"],
            ["Energy — Electric Power",       "10.2",  "2.00%", "0.072"],
            ["Insurance",                     "9.3",   "1.50%", "0.049"],
            ["Energy — Oil & Gas",            "6.8",   "2.00%", "0.048"],
            ["TOTAL (all 9 sectors)",         "",      "",      "1.353"],
        ],
        total_b=1.353, pct_gdp=0.453,
    )
    e += callout(
        "<b>Finland context:</b> Finland's relatively small economy ($298.7B) produces a "
        "modest absolute impact ($1.35B by 2030), but its quantum readiness is among the "
        "highest in Europe. Finland is home to IQM Quantum Computers (Helsinki), hosts "
        "a 5-qubit superconducting QPU at VTT, and has the highest quantum company "
        "density per capita in the EU. When Country Readiness is enabled (QRI = 0.82), "
        "the model adjusts for ecosystem maturity — in this case reflecting that Finland "
        "punches well above its economic weight in quantum infrastructure."
    )

    # ─── Italy ───────────────────────────────────────────────────────────────
    # World Bank 2024: GDP=$2,380.8B, Mfg=14.824%, Svc=65.048%, Ind=22.332%
    e += country_calc(
        6, "Italy", "IT",
        gdp_b=2380.8, mfg_pct=14.824, svc_pct=65.048, ind_pct=22.332,
        data_year="2024",
        mfg_b=352.9, svc_b=1548.6, ind_b=531.7,
        sectors_xwalk=[
            ["Chemicals & Materials",        "Manufacturing", "15%", "52.9"],
            ["Pharma & Life Sciences",        "Manufacturing", "10%", "35.3"],
            ["Advanced Industries",           "Manufacturing", "35%", "123.5"],
            ["Financial Services",            "Services",      "20%", "309.7"],
            ["Insurance",                     "Services",       "5%", "77.4"],
            ["Telecom",                       "Services",       "8%", "123.9"],
            ["Travel, Transport & Logistics", "Services",      "12%", "185.8"],
            ["Energy — Electric Power",       "Industry",      "15%", "79.8"],
            ["Energy — Oil & Gas",            "Industry",      "10%", "53.2"],
        ],
        sectors_impact=[
            ["Financial Services",            "309.7", "3.75%", "4.065"],
            ["Travel, Transport & Logistics", "185.8", "3.25%", "2.114"],
            ["Chemicals & Materials",         "52.9",  "7.00%", "1.297"],
            ["Pharma & Life Sciences",        "35.3",  "7.00%", "0.865"],
            ["Advanced Industries",           "123.5", "2.00%", "0.865"],
            ["Telecom",                       "123.9", "1.50%", "0.650"],
            ["Energy — Electric Power",       "79.8",  "2.00%", "0.559"],
            ["Insurance",                     "77.4",  "1.50%", "0.407"],
            ["Energy — Oil & Gas",            "53.2",  "2.00%", "0.372"],
            ["TOTAL (all 9 sectors)",         "",      "",      "11.194"],
        ],
        total_b=11.194, pct_gdp=0.470,
    )

    e += h2("10.7  Cross-country comparison — 2030 Base, no readiness")
    e += plain_table(
        ["Country", "GDP ($B)", "Mfg %", "Svc %", "Ind %",
         "Top sector", "Top impact ($B)", "Total impact ($B)", "% of GDP"],
        [
            ["Germany",       "4,685.6", "18.0%", "64.0%", "25.6%",
             "Financial Svcs", "7.879", "23.362", "0.499%"],
            ["United States", "28,751.0", "10.7%", "77.6%", "17.9%",
             "Financial Svcs", "58.564", "139.646", "0.486%"],
            ["Finland",       "298.7",  "14.2%", "62.2%", "22.8%",
             "Financial Svcs", "0.488",  "1.353",  "0.453%"],
            ["Italy",         "2,380.8", "14.8%", "65.0%", "22.3%",
             "Financial Svcs", "4.065",  "11.194", "0.470%"],
        ],
        col_widths=[2.4*cm, 2.4*cm, 1.4*cm, 1.4*cm, 1.4*cm, 2.8*cm, 2.2*cm, 2.3*cm, 1.7*cm],
    )
    e += callout(
        "<b>Pattern:</b> Financial Services is the largest sector in all four countries, "
        "driven by its combination of a high penetration rate (3.75%) and a large share "
        "of a modern service economy (20% of Services GDP). "
        "Impact as a % of GDP is closely similar across all four countries (0.45–0.50%) "
        "because the crosswalk and penetration rates are global averages — the absolute "
        "dollar figure scales directly with total GDP size.",
    )

    # ── 11. References ────────────────────────────────────────────────────────
    e += h1("11.  References")
    refs = [
        "McKinsey &amp; Company. <i>Quantum Technology Monitor 2026.</i> McKinsey Global Institute, 2026. "
        "Pages 17–26 (sector deep dives), 42–44 (government investment map).",
        "IQM Quantum Computers. <i>State of Quantum 2026.</i> Appendix: QPU installations and "
        "HPC-quantum programme data.",
        "World Bank. <i>World Development Indicators.</i> World Bank Open Data API.  "
        '<a href="https://data.worldbank.org/" color="#1A5276"><u>https://data.worldbank.org/</u></a>'
        " — indicators NY.GDP.MKTP.CD, NV.IND.MANF.ZS, NV.SRV.TOTL.ZS, NV.IND.TOTL.ZS, "
        "SP.POP.SCIE.RD.P6, GB.XPD.RSDV.GD.ZS, TX.VAL.TECH.MF.ZS, BX.GSR.CCIS.ZS, IT.NET.USER.ZS.",
        "OpenAlex. <i>Open scholarly metadata API.</i>  "
        '<a href="https://api.openalex.org" color="#1A5276"><u>https://api.openalex.org</u></a>'
        " — quantum computing works (concept C21447398), publication counts and citation data, 2020–2024.",
        "QS Quacquarelli Symonds. <i>QS World University Rankings by Subject 2025 — "
        "Physics and Computer Science.</i>  "
        '<a href="https://www.topuniversities.com/subject-rankings" color="#1A5276">'
        "<u>https://www.topuniversities.com/subject-rankings</u></a>",
        "UNESCO Institute for Statistics. <i>Education: Graduates by field of study.</i>  "
        '<a href="http://data.uis.unesco.org" color="#1A5276"><u>http://data.uis.unesco.org</u></a>'
        " — indicator EDU_GRAD_FIELD.",
        "TOP500 Project. <i>TOP500 Supercomputer List, November 2024.</i>  "
        '<a href="https://top500.org/" color="#1A5276"><u>https://top500.org/</u></a>',
        "Dealroom.co / IQM. <i>Quantum computing company density by country, 2025.</i>",
        "OECD. <i>STAN: Structural Analysis Statistics.</i>  "
        '<a href="https://stats.oecd.org/Index.aspx?DataSetCode=STAN08BIS" color="#1A5276">'
        "<u>https://stats.oecd.org/Index.aspx?DataSetCode=STAN08BIS</u></a>",
        "International Energy Agency. <i>World Energy Balances.</i> IEA, 2023.  "
        '<a href="https://www.iea.org/data-and-statistics" color="#1A5276">'
        "<u>https://www.iea.org/data-and-statistics</u></a>",
        "IMF. <i>World Economic Outlook Database, April 2024.</i>  "
        '<a href="https://www.imf.org/en/Publications/WEO" color="#1A5276">'
        "<u>https://www.imf.org/en/Publications/WEO</u></a>",
    ]
    for ref in refs:
        e += [Paragraph(f"•   {ref}", ST["body_l"]), Spacer(1, 0.1 * cm)]

    e += sp(0.4)
    e += [HRFlowable(width=BODY_W, thickness=1, color=GOLD), Spacer(1, 0.3 * cm)]
    e += [Paragraph(
        f"Document generated {date.today().strftime('%d %B %Y')}  ·  "
        "IQM Quantum Computers  ·  "
        "Based on McKinsey Quantum Technology Monitor 2026  ·  "
        "For internal and client use",
        ST["footer"],
    )]
    return e


# ── Build ─────────────────────────────────────────────────────────────────────
def build():
    out = "METHODOLOGY_REPORT.pdf"

    # Compute QRI scores (uses 30-day cache — safe offline after first run)
    qri_results = None
    try:
        print("Computing QRI scores...")
        _QRI_COUNTRIES = [
            "USA", "CHN", "GBR", "DEU", "JPN", "FRA", "IND", "KOR", "AUS", "CAN",
            "NLD", "SGP", "ISR", "FIN", "SWE", "CHE", "AUT", "BEL", "DNK", "NOR",
            "ESP", "ITA", "POL", "CZE", "BRA", "ZAF", "SAU", "ARE", "QAT", "KWT",
        ]
        qri_results = _qri.compute_qri_batch(_QRI_COUNTRIES)
        print(f"  QRI computed for {len(qri_results)} countries.")
    except Exception as exc:
        print(f"  Warning: QRI computation failed ({exc}). Scores table will be omitted.")

    # Pass QRI results into build_content via function attribute (simple closure trick)
    build_content._qri_results = qri_results

    doc = SimpleDocTemplate(
        out,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.9 * cm, bottomMargin=1.6 * cm,
        title="Quantum Economic Impact Calculator — Methodology Report",
        author="IQM Quantum Computers",
        subject="Calculation methodology based on McKinsey QT Monitor 2026",
    )
    # Cover is drawn by on_first_page callback; PageBreak pushes body to page 2
    story = [PageBreak()] + build_content()
    doc.build(story, onFirstPage=on_first_page, onLaterPages=on_later_pages)
    print(f"Generated: {out}")


if __name__ == "__main__":
    build()
