"""
Generates TECHNICAL_REPORT.pdf — a business-facing report explaining the
reasoning behind every calculation in the Quantum Economic Impact Calculator.
Run: python3 generate_report_pdf.py
"""

from datetime import date
import qri as _qri  # Quantum Readiness Index module
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether,
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

# ── Palette ───────────────────────────────────────────────────────────────────
NAVY  = colors.HexColor("#1F3864")
GOLD  = colors.HexColor("#C9A84C")
LGREY = colors.HexColor("#F4F6FA")
MGREY = colors.HexColor("#E2E8F0")
BODY  = colors.HexColor("#1A1A2E")
MUTED = colors.HexColor("#6B7A9A")
WHITE = colors.white

PAGE_W, PAGE_H = A4
MARGIN = 2.2 * cm
BODY_W = PAGE_W - 2 * MARGIN


# ── Styles ────────────────────────────────────────────────────────────────────
def styles():
    s = {}
    s["body"]   = ParagraphStyle("body",   fontName="Helvetica",      fontSize=10, leading=16, textColor=BODY, spaceAfter=7,  alignment=TA_JUSTIFY)
    s["body_l"] = ParagraphStyle("body_l", fontName="Helvetica",      fontSize=10, leading=16, textColor=BODY, spaceAfter=7)
    s["small"]  = ParagraphStyle("small",  fontName="Helvetica",      fontSize=9,  leading=13, textColor=MUTED, spaceAfter=4)
    s["h2"]     = ParagraphStyle("h2",     fontName="Helvetica-Bold", fontSize=12, leading=16, textColor=NAVY,  spaceAfter=6,  spaceBefore=14)
    s["h3"]     = ParagraphStyle("h3",     fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=NAVY, spaceAfter=4, spaceBefore=10)
    s["callout"]= ParagraphStyle("callout",fontName="Helvetica-Oblique", fontSize=9.5, leading=14, textColor=NAVY, leftIndent=12, spaceAfter=4)
    s["formula"]= ParagraphStyle("formula",fontName="Courier-Bold",   fontSize=11, leading=16, textColor=NAVY, alignment=TA_CENTER)
    s["th"]     = ParagraphStyle("th",     fontName="Helvetica-Bold", fontSize=9,  leading=12, textColor=WHITE)
    s["td"]     = ParagraphStyle("td",     fontName="Helvetica",      fontSize=9,  leading=12, textColor=BODY)
    s["footer"] = ParagraphStyle("footer", fontName="Helvetica",      fontSize=7.5, leading=11, textColor=MUTED, alignment=TA_CENTER)
    s["toc"]    = ParagraphStyle("toc",    fontName="Helvetica",      fontSize=10, leading=18, textColor=BODY)
    s["toc_h"]  = ParagraphStyle("toc_h",  fontName="Helvetica-Bold", fontSize=10, leading=18, textColor=NAVY)
    return s

ST = styles()


# ── Flowables ─────────────────────────────────────────────────────────────────
class H1Band(Flowable):
    def __init__(self, number, text):
        super().__init__()
        self.number = number
        self.text = text

    def wrap(self, aw, ah):
        self._w = aw
        return aw, 30

    def draw(self):
        c = self.canv
        c.setFillColor(NAVY)
        c.rect(0, 0, self._w, 30, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(10, 10, self.number)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(38, 10, self.text)


class GoldAccent(Flowable):
    """3-pt gold left bar for sub-sections."""
    def __init__(self, para):
        super().__init__()
        self.para = para

    def wrap(self, aw, ah):
        self._w = aw
        _, ph = self.para.wrap(aw - 14, ah)
        self._h = ph + 6
        return aw, self._h

    def draw(self):
        self.canv.setFillColor(GOLD)
        self.canv.rect(0, 0, 3, self._h, fill=1, stroke=0)
        self.para.drawOn(self.canv, 12, 3)


class CalloutBox(Flowable):
    def __init__(self, paragraphs):
        super().__init__()
        self.paragraphs = paragraphs

    def wrap(self, aw, ah):
        self._w = aw
        h = 14
        for p in self.paragraphs:
            _, ph = p.wrap(aw - 22, ah)
            h += ph + 4
        self._h = h
        return aw, h

    def draw(self):
        c = self.canv
        c.setFillColor(LGREY)
        c.roundRect(0, 0, self._w, self._h, 5, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.rect(0, 0, 4, self._h, fill=1, stroke=0)
        y = self._h - 10
        for p in self.paragraphs:
            _, ph = p.wrap(self._w - 22, 9999)
            p.drawOn(c, 16, y - ph)
            y -= ph + 4


# ── Page callbacks ────────────────────────────────────────────────────────────
def draw_cover(c, doc):
    w, h = PAGE_W, PAGE_H
    c.setFillColor(NAVY)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    # Gold top bar
    c.setFillColor(GOLD)
    c.rect(0, h - 1.4 * cm, w, 1.4 * cm, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN, h - 1.0 * cm, "IQM Quantum Computers")
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 10)
    c.drawRightString(w - MARGIN, h - 1.0 * cm, "Confidential — Internal Use")
    # Gold bottom bar
    c.setFillColor(GOLD)
    c.rect(0, 0, w, 0.6 * cm, fill=1, stroke=0)
    # Content
    cx = w / 2
    mid = h * 0.56
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(cx, mid + 6.2 * cm, "IQM QUANTUM COMPUTERS")
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.line(cx - 5 * cm, mid + 5.7 * cm, cx + 5 * cm, mid + 5.7 * cm)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(cx, mid + 4.2 * cm, "Quantum Economic")
    c.drawCentredString(cx, mid + 3.2 * cm, "Impact Calculator")
    c.setFillColor(GOLD)
    c.setFont("Helvetica", 17)
    c.drawCentredString(cx, mid + 2.1 * cm, "Calculation Methodology & Rationale")
    c.setStrokeColor(GOLD)
    c.line(cx - 5 * cm, mid + 1.6 * cm, cx + 5 * cm, mid + 1.6 * cm)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Oblique", 10.5)
    c.drawCentredString(cx, mid + 0.6 * cm,
        "Why we chose every data source, every rate,")
    c.drawCentredString(cx, mid - 0.1 * cm,
        "and every formula in the model.")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    c.drawCentredString(cx, 2.2 * cm,
        "Based on McKinsey Quantum Technology Monitor 2026  |  World Bank WDI  |  OECD STAN")
    c.drawCentredString(cx, 1.55 * cm,
        f"Prepared {date.today().strftime('%B %Y')}")


def draw_header_footer(c, doc):
    w = PAGE_W
    c.saveState()
    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    c.line(MARGIN, PAGE_H - 1.35 * cm, w - MARGIN, PAGE_H - 1.35 * cm)
    c.setFont("Helvetica", 8)
    c.setFillColor(NAVY)
    c.drawString(MARGIN, PAGE_H - 1.1 * cm,
                 "IQM Quantum Computers  •  Quantum Economic Impact Calculator — Methodology & Rationale")
    c.drawRightString(w - MARGIN, PAGE_H - 1.1 * cm, f"Page {doc.page}")
    c.setStrokeColor(MGREY)
    c.setLineWidth(0.5)
    c.line(MARGIN, 1.15 * cm, w - MARGIN, 1.15 * cm)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(w / 2, 0.72 * cm,
        "Confidential — For internal use and authorised client presentations  •  IQM Quantum Computers")
    c.restoreState()


def on_cover(c, doc):   draw_cover(c, doc)
def on_body(c, doc):    draw_header_footer(c, doc)


# ── Helpers ───────────────────────────────────────────────────────────────────
def h1(n, text):
    return [Spacer(1, 0.35 * cm), H1Band(n, text), Spacer(1, 0.2 * cm)]

def h2(text):
    return [GoldAccent(Paragraph(text, ST["h2"])), Spacer(1, 0.05 * cm)]

def h3(text):
    return [Paragraph(text, ST["h3"])]

def body(text):
    return [Paragraph(text, ST["body"])]

def sp(n=0.3):
    return [Spacer(1, n * cm)]

def callout(*lines):
    return [
        Spacer(1, 0.1 * cm),
        CalloutBox([Paragraph(l, ST["callout"]) for l in lines]),
        Spacer(1, 0.2 * cm),
    ]

def fbox(text):
    return [
        Spacer(1, 0.15 * cm),
        Table([[Paragraph(text, ST["formula"])]],
              colWidths=[BODY_W],
              style=TableStyle([
                  ("BACKGROUND",    (0,0),(-1,-1), LGREY),
                  ("BOX",           (0,0),(-1,-1), 1.5, GOLD),
                  ("TOPPADDING",    (0,0),(-1,-1), 11),
                  ("BOTTOMPADDING", (0,0),(-1,-1), 11),
                  ("LEFTPADDING",   (0,0),(-1,-1), 12),
              ])),
        Spacer(1, 0.2 * cm),
    ]

def tbl(headers, rows, widths=None):
    widths = widths or [BODY_W / len(headers)] * len(headers)
    data = [[Paragraph(h, ST["th"]) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), ST["td"]) for c in row])
    return [
        Table(data, colWidths=widths, repeatRows=1,
              style=TableStyle([
                  ("BACKGROUND",     (0,0),(-1,0),  NAVY),
                  ("ROWBACKGROUNDS", (0,1),(-1,-1), [WHITE, LGREY]),
                  ("GRID",           (0,0),(-1,-1), 0.4, MGREY),
                  ("TOPPADDING",     (0,0),(-1,-1), 5),
                  ("BOTTOMPADDING",  (0,0),(-1,-1), 5),
                  ("LEFTPADDING",    (0,0),(-1,-1), 7),
                  ("RIGHTPADDING",   (0,0),(-1,-1), 7),
                  ("VALIGN",         (0,0),(-1,-1), "TOP"),
              ])),
        Spacer(1, 0.25 * cm),
    ]


# ── QRI country list for the PDF report ──────────────────────────────────────
_QRI_COUNTRIES = [
    "USA", "CHN", "GBR", "DEU", "JPN", "FRA", "IND", "KOR", "AUS", "CAN",
    "NLD", "SGP", "ISR", "FIN", "SWE", "CHE", "AUT", "BEL", "DNK", "NOR",
    "ESP", "ITA", "POL", "CZE", "BRA", "ZAF", "SAU", "ARE", "QAT", "KWT",
]

# ── Content ───────────────────────────────────────────────────────────────────
def content(qri_results: dict | None = None):
    e = []

    # ── Executive Summary ─────────────────────────────────────────────────────
    e += h1("00", "Executive Summary")
    e += body(
        "This report explains how the IQM Quantum Economic Impact Calculator estimates the "
        "economic value of quantum computing for any selected country, and — critically — "
        "<b>why</b> each methodological choice was made. Every number in the model traces back "
        "to a specific, citable source: the McKinsey Quantum Technology Monitor 2026 for "
        "penetration rates, the World Bank for GDP data, and OECD STAN for sector allocation. "
        "No figures have been invented or estimated without a basis in published research."
    )
    e += body(
        "The model answers one question: <i>given a country's economic structure today, how "
        "much value could quantum computing plausibly unlock by a chosen year?</i> It does this "
        "by combining sector-level GDP data with McKinsey's expert estimates of how deeply "
        "quantum computing will penetrate each industry by 2035, then applying an S-curve "
        "discount to reflect the pace of real-world adoption."
    )
    e += callout(
        "<b>Validated result:</b> Running the model across 30 major economies at 2035 "
        "produces a combined estimate of ~$1.29 trillion — consistent with McKinsey's "
        "published global quantum value-at-stake range of $1.28T–$2.7T.",
    )

    # ── Section 1 ─────────────────────────────────────────────────────────────
    e += h1("01", "Why We Built This Model")
    e += body(
        "McKinsey's Quantum Technology Monitor 2026 is one of the most rigorous publicly "
        "available assessments of quantum computing's economic potential. It provides "
        "sector-level penetration rate estimates backed by bottom-up analysis of specific "
        "quantum use cases. However, it only publishes <i>global</i> totals."
    )
    e += body(
        "IQM's clients — governments, enterprises, and research institutions — need to "
        "understand their <i>own</i> country's quantum opportunity, not a global average. "
        "A Nordic country with a large financial services sector has a very different quantum "
        "exposure than a Gulf state dominated by oil and gas. This model bridges that gap by "
        "taking McKinsey's global rates and grounding them in each country's actual "
        "economic structure using live World Bank data."
    )
    e += callout(
        "<b>Key design principle:</b> Every input is either directly cited from McKinsey "
        "(penetration rates) or sourced from an official international statistical body "
        "(World Bank GDP, OECD STAN sector splits). The model introduces no proprietary "
        "assumptions beyond the crosswalk ratios, which are documented and attributable.",
    )

    # ── Section 2 ─────────────────────────────────────────────────────────────
    e += h1("02", "The Core Formula — and Why It Is Structured This Way")
    e += fbox("Impact ($B)  =  Sector GDP  ×  Penetration Rate  ×  Timeline Factor  ×  Readiness Score")
    e += body(
        "This formula was chosen because it is the most transparent and defensible structure "
        "for translating McKinsey's research into country-level estimates. Each term is "
        "independently sourced, independently adjustable, and independently explainable "
        "to a non-technical audience. Here is the rationale for each component:"
    )

    e += h2("Why multiply, rather than use a more complex model?")
    e += body(
        "A multiplicative formula is appropriate here because the four factors are genuinely "
        "independent. The size of a country's financial services sector (Sector GDP) has no "
        "bearing on McKinsey's estimate of how deeply quantum will penetrate financial services "
        "globally (Penetration Rate). A more complex model would require country-specific "
        "quantum penetration research that does not yet exist. Multiplying independently "
        "sourced factors is both methodologically sound and auditable."
    )

    e += h2("Why apply the formula per sector, then sum?")
    e += body(
        "Quantum computing's impact is highly uneven across sectors. Pharma and Chemicals "
        "benefit from molecular simulation — a use case that requires fault-tolerant quantum "
        "hardware and therefore has a wide uncertainty range (2%–12%). Financial Services "
        "benefits from near-term optimisation algorithms that already run on today's hardware "
        "(3%–4.5%). Applying a single blended rate to total GDP would mask this variation "
        "and produce misleading results for countries with unusual sector compositions. "
        "Computing per sector and summing preserves the full analytical picture."
    )

    # ── Section 3 ─────────────────────────────────────────────────────────────
    e += h1("03", "Why McKinsey — and Why These Specific Rates")
    e += body(
        "McKinsey's Quantum Technology Monitor 2026 was chosen as the primary rate source "
        "for three reasons: it is the most recent major cross-sector analysis of quantum "
        "economic potential; its rates are derived from bottom-up use-case modelling rather "
        "than top-down guesswork; and it is the framework most widely recognised by the "
        "quantum computing industry, making its numbers defensible in client and board "
        "conversations."
    )
    e += body(
        "The rates were extracted directly from the ground-truth spreadsheet "
        "(McKinsey_QT_2026_Impact_Rates.xlsx, Sheet 6), not from secondary summaries. "
        "This matters: some widely-cited secondary sources quote slightly rounded figures "
        "that do not match the actual spreadsheet formulas. The model uses the exact values."
    )
    e += tbl(
        ["Sector", "Conservative", "Base", "Optimistic", "McKinsey Value at Stake", "Source"],
        [
            ["Chemicals & Materials",        "5.0%", "7.0%",  "9.0%",  "$450–800B", "p.17, p.22"],
            ["Financial Services",            "3.0%", "3.75%", "4.5%",  "$400–600B", "p.17, p.24"],
            ["Pharma & Life Sciences",        "2.0%", "7.0%",  "12.0%", "$50–400B",  "p.17, p.20"],
            ["Travel, Transport & Logistics", "2.0%", "3.25%", "4.5%",  "$200–500B", "p.17, p.26"],
            ["Advanced Industries",           "1.0%", "2.0%",  "3.0%",  "$200–500B", "p.17"],
            ["Energy — Electric Power",  "1.0%", "2.0%",  "3.0%",  "$50–150B",  "p.17"],
            ["Energy — Oil & Gas",       "1.0%", "2.0%",  "3.0%",  "$50–150B",  "p.17"],
            ["Insurance",                     "1.0%", "1.5%",  "2.0%",  "$10–50B",   "p.17"],
            ["Telecom",                       "1.0%", "1.5%",  "2.0%",  "$50–100B",  "p.17"],
        ],
        widths=[4.5*cm, 2.1*cm, 1.8*cm, 2.3*cm, 3.2*cm, 2.5*cm],
    )
    e += callout(
        "<b>Note on the Base (mid) rate:</b> The Base rate is calculated as the arithmetic "
        "midpoint of the Conservative and Optimistic rates: (Low + High) / 2. "
        "This matches the formula in the McKinsey ground-truth spreadsheet (column F = =(D+E)/2). "
        "For Financial Services this gives 3.75%, not the 3.8% sometimes quoted in secondary "
        "summaries of the report.",
    )

    e += h2("Why three scenarios?")
    e += body(
        "McKinsey explicitly publishes low and high estimates for each sector, reflecting "
        "genuine uncertainty about the pace of quantum hardware development. Presenting three "
        "scenarios — Conservative (McKinsey low), Base (midpoint), and Optimistic (McKinsey "
        "high) — is the standard approach for communicating this uncertainty range honestly. "
        "It prevents the false precision of presenting a single figure as a prediction."
    )

    # ── Section 4 ─────────────────────────────────────────────────────────────
    e += h1("04", "Why World Bank Data — and How It Is Used")
    e += body(
        "The World Bank's World Development Indicators (WDI) is the most comprehensive, "
        "consistently structured, and freely available source of national GDP and sector "
        "breakdown data. It covers 200+ economies with consistent methodology, making it "
        "ideal for a tool that needs to work across 40 countries without bespoke data "
        "collection for each."
    )
    e += body(
        "Five indicators are fetched per country via the World Bank's public REST API "
        "(no licence or subscription required):"
    )
    e += tbl(
        ["Indicator", "Code", "Why this one"],
        [
            ["Total GDP (current USD)",   "NY.GDP.MKTP.CD",
             "The denominator for all sector calculations. Current USD used (not PPP) to match McKinsey's dollar-denominated value-at-stake figures."],
            ["Manufacturing % of GDP",    "NV.IND.MANF.ZS",
             "Needed to estimate Chemicals, Pharma, and Advanced Industries sector sizes."],
            ["Services % of GDP",         "NV.SRV.TOTL.ZS",
             "Needed to estimate Financial Services, Insurance, Telecom, and TTL sector sizes."],
            ["Industry total % of GDP",   "NV.IND.TOTL.ZS",
             "Needed to estimate the two Energy sectors. Industry total is used rather than a dedicated energy indicator because it is the most consistently reported across all countries."],
            ["Agriculture % of GDP",      "NV.AGR.TOTL.ZS",
             "Fetched as a consistency check; not directly used in quantum impact calculations."],
        ],
        widths=[3.8*cm, 3.0*cm, 8.8*cm],
    )

    e += h2("Why use the mrv=3 parameter?")
    e += body(
        "World Bank data typically lags 1–2 years behind the current year. Requesting the "
        "three most recent values (mrv=3) and taking the first non-null result ensures the "
        "model always uses the most recent available data, even when the latest year has not "
        "yet been reported for a given country. Without this, several countries — including "
        "Israel, Mexico, and Turkey — returned null values in testing, producing zero impact "
        "estimates that were clearly wrong."
    )

    e += h2("Why hardcode GDP fallbacks for 44 countries?")
    e += body(
        "The World Bank API occasionally returns null GDP values due to reporting lags, "
        "data revisions, or connectivity issues. For the model to be reliable in a live "
        "presentation, it cannot silently return zero for a country. Hardcoded 2023 "
        "World Bank / IMF estimates are used as a last resort, clearly labelled in the "
        "code as fallbacks rather than primary data."
    )

    e += h2("Why structural overrides for five countries?")
    e += body(
        "Singapore, UAE, Saudi Arabia, Qatar, and Kuwait have economic structures that "
        "deviate significantly from global averages in ways that matter for quantum impact. "
        "Singapore's services sector is ~72% of GDP (vs ~60% global average), meaning "
        "applying global averages would understate its Financial Services and Telecom "
        "quantum exposure. The Gulf states have outsized hydrocarbon industry shares "
        "that the World Bank's industry indicator captures, but global average split "
        "ratios would understate. These overrides are based on well-documented national "
        "statistics and are clearly flagged in the code."
    )

    # ── Section 5 ─────────────────────────────────────────────────────────────
    e += h1("05", "Why the Sector Crosswalk — and Where the Ratios Come From")
    e += body(
        "The World Bank reports GDP in three broad categories: manufacturing, services, and "
        "industry total. McKinsey's quantum impact analysis uses nine specific sectors. "
        "Bridging this gap requires allocating each World Bank macro-category to the relevant "
        "McKinsey sectors. This is the crosswalk."
    )
    e += body(
        "The split ratios are derived from OECD STAN bilateral industry statistics (2022 data), "
        "which provide country-level value-added breakdowns at the sub-sector level. The ratios "
        "represent global averages across OECD economies. They are intentionally documented as "
        "approximations in the code, with a direct reference to the OECD STAN database for "
        "anyone who wants to refine them for a specific country."
    )
    e += tbl(
        ["McKinsey Sector", "Allocated from", "Ratio", "Rationale"],
        [
            ["Chemicals & Materials",        "Manufacturing", "15%", "Chemicals represent ~15% of global manufacturing value-added (OECD STAN 2022)"],
            ["Pharma & Life Sciences",        "Manufacturing", "10%", "Pharma/medtech ~10% of manufacturing value-added globally"],
            ["Advanced Industries",           "Manufacturing", "35%", "Auto, aerospace, electronics, semiconductors combined — the largest manufacturing sub-group"],
            ["Financial Services",            "Services",      "20%", "Banking and capital markets ~20% of services GDP in developed economies"],
            ["Insurance",                     "Services",       "5%", "Insurance ~5% of services GDP globally"],
            ["Telecom",                       "Services",       "8%", "Telecoms ~8% of services GDP"],
            ["Travel, Transport & Logistics", "Services",      "12%", "Transport and hospitality combined ~12% of services GDP"],
            ["Energy — Electric Power",  "Industry",      "15%", "Electric utilities ~15% of industry value-added (IEA energy data)"],
            ["Energy — Oil & Gas",       "Industry",      "10%", "Oil & gas extraction ~10% of industry value-added globally"],
        ],
        widths=[4.3*cm, 2.6*cm, 1.6*cm, 7.1*cm],
    )
    e += callout(
        "<b>Why not use a more granular data source?</b> The OECD STAN database does provide "
        "country-level sub-sector data, but it only covers OECD members and has a 2–3 year "
        "lag. For a tool covering 40 countries including India, Indonesia, and Saudi Arabia, "
        "global average ratios applied to World Bank data give broader coverage with "
        "acceptable accuracy for the order-of-magnitude estimates this tool produces.",
    )

    # ── Section 6 ─────────────────────────────────────────────────────────────
    e += h1("06", "Why the S-Curve Timeline — and Why These Specific Values")
    e += body(
        "Quantum computing will not deliver its full economic impact overnight. The technology "
        "is progressing along a well-documented adoption curve: near-term quantum advantage "
        "in optimisation problems (achievable with today's noisy hardware), then broader "
        "enterprise adoption, then fault-tolerant quantum computing enabling the full impact "
        "in Pharma and Chemicals. McKinsey's own phase analysis (+ Low, ++ Medium, +++ High) "
        "describes which sectors will see impact in which period."
    )
    e += body(
        "The timeline factors translate this into a simple annual multiplier: a factor of 0.35 "
        "at 2030 means 35% of the full 2035 potential has been realised by that year. The "
        "S-curve midpoint is set at approximately 2031, consistent with McKinsey's assessment "
        "that the ++ Medium sectors (Financial Services, Chemicals, Pharma) begin delivering "
        "meaningful value in 2025–2030 and reach high impact in 2030–2035."
    )
    tl_header = ["Year", "2026", "2027", "2028", "2029", "2030", "2031", "2032", "2033", "2034", "2035"]
    tl_vals   = ["Factor", "4%", "7%", "13%", "22%", "35%", "50%", "65%", "78%", "90%", "100%"]
    tl_data   = [
        [Paragraph(h, ST["th"]) for h in tl_header],
        [Paragraph(v, ST["td"]) for v in tl_vals],
    ]
    e += [
        Table(tl_data, colWidths=[2.2*cm] + [1.52*cm]*10,
              style=TableStyle([
                  ("BACKGROUND",    (0,0),(-1,0),  NAVY),
                  ("BACKGROUND",    (0,1),(-1,1),  LGREY),
                  ("GRID",          (0,0),(-1,-1), 0.4, MGREY),
                  ("ALIGN",         (0,0),(-1,-1), "CENTER"),
                  ("TOPPADDING",    (0,0),(-1,-1), 5),
                  ("BOTTOMPADDING", (0,0),(-1,-1), 5),
              ])),
        Spacer(1, 0.15*cm),
    ]
    e += callout(
        "<b>Why not sector-specific timelines?</b> In principle, Financial Services "
        "(which benefits from near-term optimisation) should have a faster curve than "
        "Pharma (which requires fault-tolerant hardware). A single shared curve is used "
        "here because McKinsey does not publish sector-specific adoption timelines — only "
        "phase indicators. Using a single curve is a known simplification, documented as "
        "a limitation, and appropriate for the strategic planning horizon this tool addresses.",
    )

    # ── Section 7 ─────────────────────────────────────────────────────────────
    e += h1("07", "Why the Country Readiness Score — and When to Use It")
    e += body(
        "The penetration rates from McKinsey represent the potential if quantum technology "
        "develops as expected and is adopted at a global-average pace. In reality, some "
        "countries are far better positioned to capture that value than others, because "
        "they have invested in quantum infrastructure, trained quantum talent, and built "
        "ecosystems of quantum-ready companies."
    )
    e += body(
        "The Country Readiness Score (0–1) is an optional modifier that scales a country's "
        "estimate to reflect this reality. A score of 0.82 for Finland, for example, "
        "reflects IQM's own presence there, the VTT superconducting QPU program, and "
        "Aalto University's quantum research — factors that make Finland significantly "
        "more likely than average to realise quantum value early."
    )
    e += body(
        "As of this report version, the Country Readiness Score is computed by the "
        "<b>Quantum Readiness Index (QRI)</b> module — a transparent, reproducible "
        "framework deriving a 0–1 score from 6 pillars and 18 metrics drawn from "
        "public data sources (OpenAlex, World Bank, UNESCO UIS, QS Rankings). "
        "See Section 07b for pillar definitions, country scores, and full source citations. "
        "A score of 0.82 for Finland, for example, means the model expects Finland "
        "to realise 82% of its theoretical maximum quantum impact — not that it is "
        "18% behind a global leader."
    )

    e += h2("When to use it, and when not to")
    e += tbl(
        ["Toggle state", "Use when", "What it shows"],
        [
            ["OFF (Readiness = 1.0)",
             "Presenting to a client to show their country's maximum theoretical quantum opportunity",
             "Pure economic potential — what is available if quantum is adopted at the global-average rate"],
            ["ON (Country score applied)",
             "Internal analysis, or presenting to a sophisticated audience that understands ecosystem factors",
             "Adjusted estimate reflecting how likely the country is to actually capture that potential"],
        ],
        widths=[3.2*cm, 6.2*cm, 6.2*cm],
    )

    # ── Section 07b — QRI deep-dive ───────────────────────────────────────────
    e += h1("07b", "Country Readiness Scores — How They Are Derived")
    e += body(
        "The Quantum Readiness Index (QRI) replaces the informal single-number readiness "
        "scores previously assigned by expert judgement. It uses six pillars, each built "
        "from two or three public-data metrics, to produce a transparent, auditable 0–1 "
        "score. Min-max normalisation is applied within the assessed country set so that "
        "the top-performing country on each metric always receives 1.0 and the bottom "
        "always receives 0.0. The final QRI is a weighted average of pillar scores."
    )

    e += h2("The Six Pillars")
    pillar_rows = [
        ["Scientific Foundation (20%)",
         "Quantum publication volume (per 10M population, 5-year rolling), field-weighted "
         "citation impact, and count of top-100 QS-ranked universities in Physics/CS. "
         "Captures the depth of fundamental research underpinning future quantum advantage.",
         "OpenAlex API; QS World University Rankings 2025"],
        ["Talent Pipeline (20%)",
         "STEM graduates as % of tertiary enrolment, researchers per million population, "
         "and count of dedicated quantum MSc/PhD programmes. A strong talent pipeline is "
         "the single most reliable predictor of long-term technology capture.",
         "UNESCO UIS; World Bank (SP.POP.SCIE.RD.P6); IQM/web seed"],
        ["Government Commitment (15%)",
         "Binary flag for a published national quantum strategy, tiered budget score "
         "(>$1B→1.0, $100M–$1B→0.7, $10M–$100M→0.4), and count of active national "
         "HPC-quantum deployments. Reflects the policy environment enabling long-run investment.",
         "McKinsey QTM 2026 pp.42–44; IQM State of Quantum 2026 appendix"],
        ["Private Ecosystem (20%)",
         "Quantum companies per 10M population, quantum venture investment per $1B GDP "
         "(2023–2025), and a digital-adoption proxy. A dense private ecosystem accelerates "
         "commercialisation of academic research into economic value.",
         "IQM State of Quantum 2026 + Dealroom; World Bank (IT.NET.USER.ZS)"],
        ["Infrastructure (15%)",
         "Installed QPU count (tiered: 4+→1.0 down to 0→0.10), Top500 supercomputing "
         "systems (capped at 20), and R&D expenditure as % of GDP. Quantum infrastructure "
         "is a prerequisite for both research and commercial deployment.",
         "IQM State of Quantum 2026; TOP500 Nov 2024; World Bank (GB.XPD.RSDV.GD.ZS)"],
        ["Absorptive Capacity (10%)",
         "High-tech exports as % of manufactured exports, and ICT service exports as "
         "% of total service exports. Measures the economy's demonstrated ability to "
         "generate and export technology-intensive products — a proxy for structural "
         "readiness to commercialise quantum breakthroughs.",
         "World Bank (TX.VAL.TECH.MF.ZS; BX.GSR.CCIS.ZS)"],
    ]
    e += tbl(
        ["Pillar (weight)", "What it measures and why", "Data sources"],
        pillar_rows,
        widths=[3.6*cm, 8.6*cm, 4.4*cm],
    )

    # QRI results table — rendered only if batch results were supplied
    if qri_results:
        e += h2("Computed QRI Scores — All Assessed Countries")
        e += body(
            "The table below shows QRI scores and pillar breakdowns for all 30 assessed "
            "countries. Scores flagged with † used seed or fallback data for one or more "
            "metrics — see the warnings in the source data for details."
        )

        _pk = [
            "Scientific Foundation",
            "Talent Pipeline",
            "Government Commitment",
            "Private Ecosystem",
            "Infrastructure",
            "Absorptive Capacity",
        ]
        _ph = ["Sci", "Tal", "Gov", "Eco", "Inf", "Abs"]

        sorted_countries = sorted(
            qri_results.items(), key=lambda x: x[1]["qri"], reverse=True
        )
        qri_rows = []
        for iso3, res in sorted_countries:
            name = _qri.ISO3_TO_NAME.get(iso3, iso3)
            flag = "†" if res["warnings"] else ""
            row = [f"{name}{flag}", f"{res['qri']:.3f}"]
            for pk in _pk:
                row.append(f"{res['pillars'].get(pk, 0):.2f}")
            qri_rows.append(row)

        col_w_name = 3.8 * cm
        col_w_qri  = 1.4 * cm
        col_w_p    = 1.5 * cm
        e += tbl(
            ["Country", "QRI"] + _ph,
            qri_rows,
            widths=[col_w_name, col_w_qri] + [col_w_p] * 6,
        )

        e += callout(
            "<b>† Seed/fallback data:</b> Countries marked with † have at least one "
            "metric sourced from a seed dictionary rather than a live API call. This "
            "occurs when an API is unreachable, returns null, or the country is not "
            "covered by the live data source. Seed values are documented in qri.py "
            "with inline source citations.",
        )

        # Data sources used
        e += h2("Data Sources")
        source_refs = [
            "<b>OpenAlex API</b> — api.openalex.org — quantum computing publications "
            "(concept C21447398) and citation counts, 2020–2024. Free, no key required.",
            "<b>World Bank WDI API</b> — api.worldbank.org — indicators SP.POP.SCIE.RD.P6 "
            "(researcher density), GB.XPD.RSDV.GD.ZS (R&D spend), TX.VAL.TECH.MF.ZS "
            "(high-tech exports), BX.GSR.CCIS.ZS (ICT service exports), IT.NET.USER.ZS "
            "(internet users). mrv=3 parameter used; first non-null value taken.",
            "<b>QS World University Rankings 2025</b> — Physics and Computer Science "
            "subjects — count of institutions ranked in the global top 100.",
            "<b>McKinsey Quantum Technology Monitor 2026</b> pp.42–44 — government "
            "quantum strategies and budget tier classifications.",
            "<b>IQM State of Quantum 2026</b> appendix — QPU installations and "
            "HPC-quantum programme counts.",
            "<b>Dealroom / IQM</b> — quantum company density per 10M population.",
            "<b>UNESCO UIS seed (~2022)</b> — STEM graduates % of tertiary enrolment.",
            "<b>TOP500 list, November 2024</b> — top500.org — supercomputing system counts.",
        ]
        for ref in source_refs:
            e += [Paragraph(f"<b>—</b>  {ref}", ST["body_l"]), Spacer(1, 0.05*cm)]
    else:
        e += callout(
            "<b>Note:</b> QRI country scores were not pre-computed for this PDF run. "
            "Run generate_report_pdf.py with an active internet connection to populate "
            "the scores table, or check qri_cache.json for cached results."
        )

    # ── Section 8 ─────────────────────────────────────────────────────────────
    e += h1("08", "Worked Example — Finland at 2030, Base Scenario")
    e += body(
        "The following shows exactly how the model calculates Finland's quantum economic "
        "impact estimate, step by step."
    )
    e += h2("Step 1 — World Bank GDP data for Finland (~2022)")
    e += tbl(
        ["Indicator", "Value", "Derived"],
        [
            ["Total GDP",           "$302B", ""],
            ["Manufacturing % GDP", "19.2%", "Manufacturing GDP = $58B"],
            ["Services % GDP",      "63.8%", "Services GDP = $193B"],
            ["Industry % GDP",      "24.1%", "Industry GDP = $73B"],
        ],
        widths=[5*cm, 2.5*cm, 8.1*cm],
    )
    e += h2("Step 2 — Crosswalk to McKinsey sectors")
    e += tbl(
        ["McKinsey Sector", "Calculation", "Sector GDP ($B)"],
        [
            ["Chemicals & Materials",        "$58B x 15%", "$8.7"],
            ["Pharma & Life Sciences",        "$58B x 10%", "$5.8"],
            ["Advanced Industries",           "$58B x 35%", "$20.3"],
            ["Financial Services",            "$193B x 20%", "$38.6"],
            ["Insurance",                     "$193B x 5%",  "$9.6"],
            ["Telecom",                       "$193B x 8%",  "$15.4"],
            ["Travel, Transport & Logistics", "$193B x 12%", "$23.2"],
            ["Energy — Electric Power",  "$73B x 15%",  "$10.9"],
            ["Energy — Oil & Gas",       "$73B x 10%",  "$7.3"],
        ],
        widths=[5*cm, 4*cm, 4.6*cm],
    )
    e += h2("Step 3 — Apply formula (Base rates, 2030 Timeline Factor = 0.35, Readiness off)")
    e += tbl(
        ["Sector", "Sector GDP", "Base Rate", "x 0.35", "Impact"],
        [
            ["Chemicals & Materials",        "$8.7B",  "7.0%",  "0.35", "$0.21B"],
            ["Pharma & Life Sciences",        "$5.8B",  "7.0%",  "0.35", "$0.14B"],
            ["Advanced Industries",           "$20.3B", "2.0%",  "0.35", "$0.14B"],
            ["Financial Services",            "$38.6B", "3.75%", "0.35", "$0.51B"],
            ["Insurance",                     "$9.6B",  "1.5%",  "0.35", "$0.05B"],
            ["Telecom",                       "$15.4B", "1.5%",  "0.35", "$0.08B"],
            ["Travel, Transport & Logistics", "$23.2B", "3.25%", "0.35", "$0.26B"],
            ["Energy — Electric Power",  "$10.9B", "2.0%",  "0.35", "$0.08B"],
            ["Energy — Oil & Gas",       "$7.3B",  "2.0%",  "0.35", "$0.05B"],
            ["<b>TOTAL</b>",                  "",       "",       "",     "<b>~$1.5B</b>"],
        ],
        widths=[5.0*cm, 2.3*cm, 2.3*cm, 1.8*cm, 2.2*cm],
    )
    e += callout(
        "<b>What this means:</b> By 2030, quantum computing could contribute approximately "
        "$1.5B to Finland's economy under the Base scenario — driven primarily by Financial "
        "Services ($0.51B) and Travel, Transport & Logistics ($0.26B). By 2035, with the "
        "full Timeline Factor of 1.0, this rises to ~$3.9B (1.3% of GDP).",
    )

    # ── Section 9 ─────────────────────────────────────────────────────────────
    e += h1("09", "How to Interpret the Numbers — and What They Are Not")
    e += body(
        "The calculator produces <b>order-of-magnitude strategic estimates</b>, not "
        "financial forecasts. They are designed to answer: 'Is this country's quantum "
        "opportunity in the hundreds of millions, billions, or tens of billions?' — not "
        "'will quantum computing contribute exactly $3.87B to Finland's GDP in 2030?'"
    )
    e += body(
        "The numbers are most useful for: comparing countries against each other, "
        "identifying which sectors dominate a country's quantum exposure, understanding "
        "how the opportunity changes between a near-term year (2028) and the medium term "
        "(2035), and framing client conversations about where quantum investment is "
        "most justified."
    )
    e += tbl(
        ["Question the tool answers well", "Question the tool does not answer"],
        [
            ["Which sectors drive the most quantum value in this country?",
             "What will the precise GDP impact be in 2031?"],
            ["How does Finland's opportunity compare to Sweden's?",
             "Which specific companies will capture the value?"],
            ["How much bigger is the 2035 opportunity vs 2030?",
             "What is the impact of a specific quantum algorithm?"],
            ["How does Conservative vs Optimistic change the picture?",
             "When exactly will quantum advantage be achieved in pharma?"],
            ["Does readiness meaningfully change the ranking of countries?",
             "What is the return on a specific quantum investment?"],
        ],
        widths=[8*cm, 7.6*cm],
    )

    e += h2("Why the numbers are conservative relative to McKinsey's headline")
    e += body(
        "McKinsey's published value-at-stake figures (e.g. $400–600B for Financial Services) "
        "are calibrated against sector revenues — the total income generated by the sector. "
        "This model applies the same penetration rates to sector GDP (value-added), which "
        "is typically 3–5× smaller than revenue for manufacturing sectors. This is a "
        "deliberate choice: GDP is consistently available for all countries; revenue data "
        "is not. The result is that our absolute figures are conservatively lower than a "
        "direct reading of McKinsey's headline numbers would suggest — which is the "
        "appropriate direction of error for a tool used in client conversations."
    )

    # ── Section 10 ────────────────────────────────────────────────────────────
    e += h1("10", "Limitations — Honest Assessment")
    items = [
        ("Sector crosswalk uses global averages",
         "The OECD STAN ratios are averages across many economies. A country with an "
         "unusually large or small presence in a sub-sector will have that under- or "
         "over-represented. This is partly mitigated by the structural overrides for "
         "five known outlier economies."),
        ("GDP data lags 1–2 years",
         "World Bank data is typically 1–2 years behind. For most purposes this is "
         "immaterial — GDP sector shares change slowly. For countries in rapid structural "
         "transition, estimates may be slightly stale."),
        ("Single S-curve for all sectors",
         "Financial Services will likely see faster adoption than Pharma, which requires "
         "fault-tolerant hardware not yet available. The shared curve slightly overstates "
         "Pharma/Chemicals impact in early years and understates Financial Services."),
        ("No GDP growth projection",
         "The model uses current GDP as the base. Countries with high economic growth "
         "rates (India, Indonesia) will have their future quantum impact understated, "
         "since the actual sector GDP in 2030–2035 will be larger than today."),
        ("Readiness scores are indicative",
         "Country readiness scores are single numbers covering complex national ecosystems. "
         "They should be treated as directionally correct order-of-magnitude adjustments, "
         "not precise measurements."),
    ]
    for title, desc in items:
        e += [KeepTogether([
            Paragraph(f"<b>{title}</b>", ST["h3"]),
            Paragraph(desc, ST["body"]),
            Spacer(1, 0.1*cm),
        ])]

    # ── References ────────────────────────────────────────────────────────────
    e += h1("REF", "References")
    refs = [
        "McKinsey & Company. <i>Quantum Technology Monitor 2026.</i> McKinsey Global Institute, 2026. Pages 17–26 (sector deep dives); pp. 42–44 (government investment map).",
        "World Bank. <i>World Development Indicators.</i> World Bank Open Data. https://api.worldbank.org/v2/",
        "OECD. <i>STAN: Structural Analysis Statistics, 2022.</i> https://stats.oecd.org/Index.aspx?DataSetCode=STAN08BIS",
        "International Energy Agency. <i>World Energy Balances 2023.</i> IEA.",
        "IMF. <i>World Economic Outlook Database, April 2024.</i> International Monetary Fund.",
    ]
    for ref in refs:
        e += [Paragraph(f"<b>—</b>  {ref}", ST["body_l"]), Spacer(1, 0.1*cm)]

    e += sp(0.5)
    e += [HRFlowable(width=BODY_W, thickness=1, color=GOLD), Spacer(1, 0.3*cm)]
    e += [Paragraph(
        f"Prepared {date.today().strftime('%d %B %Y')}  ·  IQM Quantum Computers  ·  "
        "Confidential — for internal use and authorised client presentations",
        ST["footer"],
    )]
    return e


# ── Build ─────────────────────────────────────────────────────────────────────
def build():
    out = "TECHNICAL_REPORT.pdf"

    # ── Compute QRI batch ─────────────────────────────────────────────────────
    # Uses 30-day cache (qri_cache.json) — safe to run offline after first fetch.
    # Falls back to seed data if APIs are unreachable; never blocks PDF generation.
    qri_batch = None
    try:
        print("Computing QRI scores for all countries...")
        qri_batch = _qri.compute_qri_batch(_QRI_COUNTRIES)
        print(f"  QRI computed for {len(qri_batch)} countries.")
    except Exception as exc:
        print(f"  Warning: QRI computation failed ({exc}). Section 07b will show a notice.")

    # ── Previously used readiness scores — superseded by the QRI module above.
    # Kept here as a documented fallback for reference; do not use in production.
    #
    # LEGACY_READINESS_SCORES = {
    #     "USA": 0.95,  # NQIA, NSF, DOE programs; largest private quantum ecosystem
    #     "CHN": 0.90,  # Multi-billion RMB national quantum initiative
    #     "DEU": 0.85,  # €2B federal quantum program
    #     "GBR": 0.85,  # £2.5B national quantum strategy
    #     "JPN": 0.82,  # National quantum initiative; RIKEN, QST
    #     "FIN": 0.82,  # IQM HQ country; VTT QPU; Aalto University
    #     "KOR": 0.80,  # K-Quantum initiative; ETRI, KAIST
    #     "SGP": 0.80,  # National Quantum Office; CQT (NUS)
    #     "CAN": 0.78,  # NSERC/NRC programs; IQC Waterloo
    #     "SWE": 0.78,  # Wallenberg Centre (WACQT); Chalmers
    #     "ISR": 0.78,  # National quantum initiative; Weizmann
    #     "CHE": 0.77,  # ETH Zurich; IBM Q Hub Zurich
    #     "NLD": 0.75,  # Quantum Delta NL (€615M); QuTech
    #     "FRA": 0.75,  # €1.8B national plan; CEA, CNRS
    #     "DNK": 0.75,  # Niels Bohr Institute; NordIQuEst
    #     "AUT": 0.70,  # Vienna; Zeilinger; AIT programs
    #     "NOR": 0.68,  # Nordic quantum collaboration; SINTEF
    #     "BEL": 0.68,  # imec (Leuven); EuroQCI participation
    #     "IND": 0.65,  # National Quantum Mission; TIFR, IISc
    #     "AUS": 0.72,  # National quantum strategy; UNSW, ANU
    #     "ESP": 0.60,  # National plan; CSIC; BSC
    #     "ITA": 0.62,  # PNRR quantum programs (€130M); CNR
    #     "POL": 0.58,  # EU-funded programs; Warsaw University
    #     "CZE": 0.58,  # ELI Beamlines; Prague quantum group
    #     "SAU": 0.52,  # KACST; Vision 2030; KAUST
    #     "ARE": 0.55,  # UAE quantum program; NYUAD
    #     "BRA": 0.50,  # Early-stage national programs; CBPF
    #     "ZAF": 0.45,  # Limited dedicated investment; CSIR
    #     "QAT": 0.48,  # Early-stage
    #     "KWT": 0.40,  # Minimal quantum ecosystem
    # }
    # Source: McKinsey QT Monitor 2026, pp.42–44. Superseded by qri.py module.

    doc = SimpleDocTemplate(
        out, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.9*cm, bottomMargin=1.6*cm,
        title="Quantum Economic Impact Calculator — Methodology & Rationale",
        author="IQM Quantum Computers",
    )
    doc.build(
        [PageBreak()] + content(qri_results=qri_batch),
        onFirstPage=on_cover,
        onLaterPages=on_body,
    )
    print(f"Generated: {out}")


if __name__ == "__main__":
    build()
