# Source Manifest — SBI Mutual Fund RAG Corpus
**Phase 1 Deliverable | Validated: 2026-04-13**

- AMC: SBI Mutual Fund
- Product context: Groww (UX reference only)
- Schemes: SBI Large Cap Fund · SBI Flexicap Fund · SBI ELSS Tax Saver Fund · SBI Equity Hybrid Fund
- Total URLs: 20 (all non-PDF web pages)
- Validation date: 2026-04-13
- Next refresh due: 2026-05-13 (monthly)

---

## Domain Allowlist

Any URL outside this list is **rejected at ingestion time**.

| Domain | Owner | Allowed |
|---|---|---|
| `www.sbimf.com` | SBI Mutual Fund | ✅ Yes |
| `onlinesbimf.com` | SBI Mutual Fund | ✅ Yes |
| `online.sbimf.com` | SBI Mutual Fund | ✅ Yes |
| `esoa.sbimf.com` | SBI Mutual Fund | ✅ Yes |
| `corporate.sbimf.com` | SBI Mutual Fund | ✅ Yes |
| `www.sebi.gov.in` | SEBI | ✅ Yes |
| `www.mutualfundssahihai.com` | AMFI | ✅ Yes |

---

## URL Manifest

### Group 1 — AMC Homepage

| # | URL | Type | Scheme Tag | Crawl Priority | HTTP Status | Access Notes |
|---|---|---|---|---|---|---|
| 1 | https://www.sbimf.com | homepage | all | P3 | ✅ 200 OK | Fully public; JS-rendered nav, no login required |

### Group 2 — AMC Catalogue and Index Pages

| # | URL | Type | Scheme Tag | Crawl Priority | HTTP Status | Access Notes |
|---|---|---|---|---|---|---|
| 2 | https://www.sbimf.com/factsheets | catalogue | all | P2 | ✅ 200 OK | Public; lists all factsheet PDFs by scheme — extract links only |
| 3 | https://www.sbimf.com/offer-document-sid-kim | catalogue | all | P2 | ✅ 200 OK | Public; lists all SID/KIM PDFs — extract links only |
| 4 | https://www.sbimf.com/half-yearly-portfolios-statements | catalogue | all | P3 | ✅ 200 OK | Public; half-yearly portfolio disclosure listing |
| 5 | https://www.sbimf.com/mutual-fund/hybrid-mutual-funds | category_page | SBI Equity Hybrid Fund | P3 | ✅ 200 OK | Public; hybrid category overview; skip promotional CTAs |
| 6 | https://www.sbimf.com/campaign/balanced-advantage-fund | campaign | none | P4 | ✅ 200 OK | Public; campaign page for BAF — informational text only; skip all CTAs |

### Group 3 — AMC Scheme Detail Pages

| # | URL | Type | Scheme Tag | Crawl Priority | HTTP Status | Access Notes |
|---|---|---|---|---|---|---|
| 7 | https://www.sbimf.com/sbimf-scheme-details/sbi-large-cap-fund-(formerly-known-as-sbi-bluechip-fund)-43 | scheme_page | SBI Large Cap Fund | **P1** | ✅ 200 OK | Public; contains expense ratio, exit load, min SIP, benchmark, riskometer — primary fact source |
| 8 | https://www.sbimf.com/sbimf-scheme-details/sbi-flexicap-fund-39 | scheme_page | SBI Flexicap Fund | **P1** | ✅ 200 OK | Public; primary fact source for Flexicap |
| 9 | https://www.sbimf.com/sbimf-scheme-details/sbi-long-term-equity-fund-(previously-known-as-sbi-magnum-taxgain-scheme)-3 | scheme_page | SBI ELSS Tax Saver Fund | **P1** | ✅ 200 OK | Public; primary fact source for ELSS; confirm lock-in period = 3 years |
| 10 | https://www.sbimf.com/sbimf-scheme-details/sbi-equity-hybrid-fund-5 | scheme_page | SBI Equity Hybrid Fund | **P1** | ✅ 200 OK | Public; primary fact source for Equity Hybrid Fund |

### Group 4 — AMC Investor Service Pages

| # | URL | Type | Scheme Tag | Crawl Priority | HTTP Status | Access Notes |
|---|---|---|---|---|---|---|
| 11 | https://www.sbimf.com/forms | service | all | P2 | ✅ 200 OK | Public; KYC, SIP, redemption forms listing — extract form names and descriptions only |
| 12 | https://www.sbimf.com/smart-statement | service | all | P2 | ✅ 200 OK | ⚠️ PUBLIC PAGE BUT FORM REQUIRES PAN + EMAIL — crawl landing page text only; do NOT extract or log any PAN/email input fields or values |
| 13 | https://www.sbimf.com/ways-to-invest | service | all | P2 | ✅ 200 OK | Public; investment modes overview (online, offline, NRI) |
| 14 | https://www.sbimf.com/nri-corner | service | all | P2 | ✅ 200 OK | Public; NRI investment rules and process — extract factual sections only |

### Group 5 — AMC Investor Portals

| # | URL | Type | Scheme Tag | Crawl Priority | HTTP Status | Access Notes |
|---|---|---|---|---|---|---|
| 15 | https://onlinesbimf.com | portal | all | P3 | ✅ 200 OK | Public landing; shows quick links (account statements, capital gains, NAV) — extract link labels and descriptions only |
| 16 | https://online.sbimf.com | portal | all | P3 | ✅ 200 OK | Public landing (SBIMF title); extract factual navigation text only |
| 17 | https://esoa.sbimf.com | portal | all | P3 | ✅ 200 OK | ⚠️ ANGULAR SPA — renders raw JS shell without JS execution; requires Playwright headless browser for meaningful text extraction |
| 18 | https://corporate.sbimf.com | portal | all | P4 | ✅ 200 OK | ⚠️ ANGULAR SPA — same as above; institutional portal; use Playwright; factual content may be minimal without login |

### Group 6 — SEBI Regulatory

| # | URL | Type | Scheme Tag | Crawl Priority | HTTP Status | Access Notes |
|---|---|---|---|---|---|---|
| 19 | https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doGetFundDetails=yes&mfId=49&type=3 | sebi | SBI MF | P2 | ✅ 200 OK | Public; SEBI's official SBI MF regulatory details — use for refusal and educational answers |

### Group 7 — AMFI Investor Education

| # | URL | Type | Scheme Tag | Crawl Priority | HTTP Status | Access Notes |
|---|---|---|---|---|---|---|
| 20 | https://www.mutualfundssahihai.com/en/about-us | amfi | general | P3 | ✅ 200 OK | Public; AMFI investor education — primary link for advisory refusal responses |

---

## Crawl Priority Reference

| Priority | Label | Used for |
|---|---|---|
| P1 | High | 4 scheme detail pages — primary fact sources |
| P2 | Medium-High | Catalogues, service pages, SEBI regulatory page |
| P3 | Medium | Homepage, portals, category pages, AMFI |
| P4 | Low | Campaign pages, corporate portal (limited factual value) |

Crawl order: P1 → P2 → P3 → P4

---

## Access Flags and Ingestion Rules

| Flag | URLs | Ingestion Rule |
|---|---|---|
| ⚠️ SPA (Angular) | esoa.sbimf.com, corporate.sbimf.com | Use Playwright headless browser — standard HTML crawler will return empty content |
| ⚠️ Form on page | smart-statement | Crawl landing page text only; never capture, log, or process PAN or email field values |
| ℹ️ Links-only | factsheets, offer-document-sid-kim, half-yearly-portfolios-statements | Extract hyperlinks and section headings only; do not embed raw PDF listing tables as chunks |
| ℹ️ Skip CTAs | campaign/balanced-advantage-fund, mutual-fund/hybrid-mutual-funds | Chunk only informational paragraphs; discard promotional copy, banners, and CTA buttons |

---

## Scheme-to-URL Cross-Reference

| Scheme | Primary Page | Catalogue Links |
|---|---|---|
| SBI Large Cap Fund | URL #7 | SID/KIM via URL #3; Factsheet via URL #2 |
| SBI Flexicap Fund | URL #8 | SID/KIM via URL #3; Factsheet via URL #2 |
| SBI ELSS Tax Saver Fund | URL #9 | SID/KIM via URL #3; Factsheet via URL #2 |
| SBI Equity Hybrid Fund | URL #10 | SID/KIM via URL #3; Factsheet via URL #2 |

---

## Phase 1 Checklist

- [x] AMC confirmed: SBI Mutual Fund
- [x] 4 schemes confirmed with category diversity (Large Cap, Flexi Cap, ELSS, Hybrid)
- [x] All 20 URLs validated — HTTP 200 OK on all
- [x] No login walls on landing pages
- [x] SPA pages flagged for Playwright-based extraction
- [x] Smart Statement privacy flag documented
- [x] Domain allowlist finalized (7 domains)
- [x] Crawl priority assigned (P1–P4)
- [x] Scheme-to-URL cross-reference complete
- [x] Source manifest file created

**Phase 1 is complete. Ready to proceed to Phase 2: Ingestion and Metadata Extraction.**
