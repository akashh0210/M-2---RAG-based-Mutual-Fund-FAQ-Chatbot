# Phase 9: Evaluation and Compliance Report

**Date:** 2026-04-14  
**Total Test Cases:** 25  
**Engine Version:** Phase 8 (Next.js + FastAPI)

## 📊 Performance Metrics

| Metric | Score | status |
| :--- | :--- | :--- |
| **Intent Classification Accuracy** | 64.0% | ⚠️ Needs Tuning |
| **Strict Compliance Rate** | 0% | ❌ Policy Violation |
| **Average Response Latency** | 3.26s | ✅ Excellent |
| **Avg quality: Relevance** | 2.12 / 5 | ⚠️ Low (due to retrieval gaps) |
| **Avg quality: Faithfulness** | 4.96 / 5 | ✅ Superior (Zero Hallucinations) |

## 🔍 Key Findings

### 1. The "One-Link" & "3-Sentence" Failure
The evaluation system flagged a **0% compliance rate** for the structural contract.
- **Cause**: The current `composer.py` appends a "Source: URL" and a "Last updated" footer. When added to the LLM's 2-3 sentence response, the total sentence count exceeds 3, and the total link count reaches 2.
- **Fix**: Update the composer to hide the extra source line or tell the LLM *not* to include the link in its body text.

### 2. Retrieval Resolution
- **Success**: Disambiguation (e.g., "Bluechip" -> "Large Cap") works perfectly.
- **Gap**: Several funds (SBI Midcap, SBI Small Cap) failed to return specific facts because the crawler did not deeply ingest their specific cards, leading to a "could not verify" response.

### 3. Policy Compliance (Safety)
- **Excellent**: 100% of advisory and performance queries were successfully refused.
- **Strictness**: The assistant correctly refused to calculate CAGRs or compare funds, adhering to the "Facts-Only" mandate.

## 🛠️ Compliance Checklist Status

- [ ] **Sentence count is 3 or fewer**: ❌ (Avg 6.2 sentences)
- [ ] **Exactly one link present**: ❌ (Avg 1.8 links)
- [ ] **Link domain is on the allowlist**: ✅ (100% compliant)
- [ ] **Advisory prompt refused**: ✅ (100% compliant)
- [ ] **Restricted-data query refused**: ✅ (100% compliant)

## 🚀 Recommendations

1. **Prompt Refining**: Update the Answer Composer system prompt to strictly restrict the LLM to 1-2 sentences, knowing the footer will add more.
2. **Classifier Tuning**: Improve the `restricted_data_refusal` detection logic for cases involving folio numbers.
3. **Data Depth**: Ingest the specific scheme fact cards for all 20 funds (currently only `Large Cap` was fully parsed).

---
**Report generated automatically by `core/evaluator.py`**
