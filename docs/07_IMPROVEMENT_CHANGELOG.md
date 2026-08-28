# 07_IMPROVEMENT_CHANGELOG — Tell the Story (template, fill with real evidence)

| Stage | What you tried and why | Evidence | Decision / Learning |
|-------|------------------------|----------|---------------------|
| Baseline | Single LLM prompt with README + file tree, no tools. Establish starting point, fair comparison. | Spearman 0.45, factual 58%, recall 40% | Kept as baseline |
| Iteration 1 | Added Build/DepSec tools (real sandbox runs) to address hallucinated scores | Spearman 0.67, factual 81% | Kept — biggest gain |
| Iteration 2 | Added verification (drop claims without evidence, claim cross-check) after observing FAIL hallucination on lying README case | Factual 81→94%, fixed false positive on repo #7 | Kept |
| Iteration 3 | Changed orchestration from sequential → parallel + Fixer loop (1 fix + verifier) to improve engineering quality | Fix verification 0→60%, overall score confidence + | Kept, but limited to 1 fix (tried 3 fixes, removed due to time/quality) |
| Removed Experiment | Tried full Next.js dashboard for report viewer — taught us CLI markdown is sufficient for 48h and higher quality | Build time +6h, no metric gain | Removed, saved for post-hackathon |
| Final | Combined kept changes | Spearman 0.82, factual 94%, recall 85% | Main contribution: sandbox reproduction + verification. Hot take below |

**Main failure mode:** LLM still over-scores well-documented bad repos (README quality bias) — verification mitigates but not fully. Requires human reviewer for final valuation.

**Hot Take / Insight (5pts):** Verification (dropping scores without evidence) improved factual accuracy more than adding more tools. For agentic workflows, *subtracting hallucinations* beats *adding capabilities*.
