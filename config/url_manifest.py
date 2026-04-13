"""
config/url_manifest.py
Phase 1 (Scope Freeze) deliverable — 20 approved non-PDF web pages.

Crawl priority:
  P1  — Scheme detail pages       (primary fact source)
  P2  — Service + catalogue pages
  P3  — Homepage, portals, AMFI
  P4  — Campaign, corporate portal (lowest factual value)

fetch_method:
  "requests"  — standard HTTP + BeautifulSoup (static HTML)
  "playwright"— headless Chromium (Angular SPA pages)
"""

ALLOWED_DOMAINS = {
    "www.sbimf.com",
    "onlinesbimf.com",
    "online.sbimf.com",
    "esoa.sbimf.com",
    "corporate.sbimf.com",
    "www.sebi.gov.in",
    "www.mutualfundssahihai.com",
}

URL_MANIFEST = [
    # ── P1: Scheme Detail Pages (primary fact sources) ────────────────────────
    {
        "id": "url-007",
        "url": "https://www.sbimf.com/sbimf-scheme-details/sbi-large-cap-fund-(formerly-known-as-sbi-bluechip-fund)-43",
        "document_type": "scheme_page",
        "scheme_name": "SBI Large Cap Fund",
        "crawl_priority": 1,
        "fetch_method": "playwright",
        "access_notes": "Public; static HTML; contains expense ratio, exit load, min SIP, benchmark, riskometer",
    },
    {
        "id": "url-008",
        "url": "https://www.sbimf.com/sbimf-scheme-details/sbi-flexicap-fund-39",
        "document_type": "scheme_page",
        "scheme_name": "SBI Flexicap Fund",
        "crawl_priority": 1,
        "fetch_method": "playwright",
        "access_notes": "Public; static HTML",
    },
    {
        "id": "url-009",
        "url": "https://www.sbimf.com/sbimf-scheme-details/sbi-long-term-equity-fund-(previously-known-as-sbi-magnum-taxgain-scheme)-3",
        "document_type": "scheme_page",
        "scheme_name": "SBI ELSS Tax Saver Fund",
        "crawl_priority": 1,
        "fetch_method": "playwright",
        "access_notes": "Public; static HTML; confirm lock-in = 3 years",
    },
    {
        "id": "url-010",
        "url": "https://www.sbimf.com/sbimf-scheme-details/sbi-equity-hybrid-fund-5",
        "document_type": "scheme_page",
        "scheme_name": "SBI Equity Hybrid Fund",
        "crawl_priority": 1,
        "fetch_method": "playwright",
        "access_notes": "Public; static HTML",
    },

    # ── P2: Catalogue + Service + Regulatory Pages ────────────────────────────
    {
        "id": "url-002",
        "url": "https://www.sbimf.com/factsheets",
        "document_type": "catalogue",
        "scheme_name": None,
        "crawl_priority": 2,
        "fetch_method": "requests",
        "access_notes": "Public; extract linked URLs only — do not create text chunks",
    },
    {
        "id": "url-003",
        "url": "https://www.sbimf.com/offer-document-sid-kim",
        "document_type": "catalogue",
        "scheme_name": None,
        "crawl_priority": 2,
        "fetch_method": "requests",
        "access_notes": "Public; extract linked URLs only — do not create text chunks",
    },
    {
        "id": "url-011",
        "url": "https://www.sbimf.com/forms",
        "document_type": "service",
        "scheme_name": None,
        "crawl_priority": 2,
        "fetch_method": "requests",
        "access_notes": "Public; KYC, SIP, redemption forms listing",
    },
    {
        "id": "url-012",
        "url": "https://www.sbimf.com/smart-statement",
        "document_type": "service",
        "scheme_name": None,
        "crawl_priority": 2,
        "fetch_method": "requests",
        "access_notes": "CAUTION: crawl landing page text only; DO NOT submit PAN+email form",
    },
    {
        "id": "url-013",
        "url": "https://www.sbimf.com/ways-to-invest",
        "document_type": "service",
        "scheme_name": None,
        "crawl_priority": 2,
        "fetch_method": "requests",
        "access_notes": "Public; investment modes overview",
    },
    {
        "id": "url-014",
        "url": "https://www.sbimf.com/nri-corner",
        "document_type": "service",
        "scheme_name": None,
        "crawl_priority": 2,
        "fetch_method": "requests",
        "access_notes": "Public; NRI investment rules and process",
    },
    {
        "id": "url-019",
        "url": "https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doGetFundDetails=yes&mfId=49&type=3",
        "document_type": "sebi",
        "scheme_name": None,
        "crawl_priority": 2,
        "fetch_method": "requests",
        "access_notes": "Public; SEBI official SBI MF regulatory details",
    },

    # ── P3: Homepage + Portals + Category + AMFI ──────────────────────────────
    {
        "id": "url-001",
        "url": "https://www.sbimf.com",
        "document_type": "homepage",
        "scheme_name": None,
        "crawl_priority": 3,
        "fetch_method": "requests",
        "access_notes": "Public; general AMC overview",
    },
    {
        "id": "url-004",
        "url": "https://www.sbimf.com/half-yearly-portfolios-statements",
        "document_type": "catalogue",
        "scheme_name": None,
        "crawl_priority": 3,
        "fetch_method": "requests",
        "access_notes": "Public; half-yearly portfolio disclosures listing",
    },
    {
        "id": "url-005",
        "url": "https://www.sbimf.com/mutual-fund/hybrid-mutual-funds",
        "document_type": "category_page",
        "scheme_name": "SBI Equity Hybrid Fund",
        "crawl_priority": 3,
        "fetch_method": "requests",
        "access_notes": "Public; skip promotional copy and CTAs",
    },
    {
        "id": "url-015",
        "url": "https://onlinesbimf.com",
        "document_type": "portal",
        "scheme_name": None,
        "crawl_priority": 3,
        "fetch_method": "requests",
        "access_notes": "Public landing; extract navigation link labels and descriptions only",
    },
    {
        "id": "url-016",
        "url": "https://online.sbimf.com",
        "document_type": "portal",
        "scheme_name": None,
        "crawl_priority": 3,
        "fetch_method": "requests",
        "access_notes": "Public landing; extract factual navigation text only",
    },
    {
        "id": "url-017",
        "url": "https://esoa.sbimf.com",
        "document_type": "portal",
        "scheme_name": None,
        "crawl_priority": 3,
        "fetch_method": "playwright",
        "access_notes": "Angular SPA — must use Playwright; eSOA portal for electronic statements",
    },
    {
        "id": "url-020",
        "url": "https://www.mutualfundssahihai.com/en/about-us",
        "document_type": "amfi",
        "scheme_name": None,
        "crawl_priority": 3,
        "fetch_method": "requests",
        "access_notes": "Public; AMFI investor education — used for refusal link only",
    },

    # ── P4: Campaign + Corporate Portal ──────────────────────────────────────
    {
        "id": "url-006",
        "url": "https://www.sbimf.com/campaign/balanced-advantage-fund",
        "document_type": "campaign",
        "scheme_name": None,
        "crawl_priority": 4,
        "fetch_method": "requests",
        "access_notes": "Public; informational text only — skip all CTAs and banners",
    },
    {
        "id": "url-018",
        "url": "https://corporate.sbimf.com",
        "document_type": "portal",
        "scheme_name": None,
        "crawl_priority": 4,
        "fetch_method": "playwright",
        "access_notes": "Angular SPA — use Playwright; institutional portal; limited factual text without login",
    },
]


def get_urls_by_priority() -> list[dict]:
    """Return URL manifest sorted by crawl_priority ascending (P1 first)."""
    return sorted(URL_MANIFEST, key=lambda u: u["crawl_priority"])


def get_allowed_domains() -> set[str]:
    return ALLOWED_DOMAINS
