# Security Control–Standards–Evidence Mapping

**Project:** Securing Vibe-Coded Applications: A Lightweight Security Assurance Framework for AI-Assisted Development  
**Companion:** [`lightweight-security-assurance-framework-v2.md`](lightweight-security-assurance-framework-v2.md)  
**Standards:** NIST SP 800-218 (SSDF v1.1); OWASP ASVS **v5.0.0** (stable release)  
**Status:** Targeted traceability mapping, **not** a claim of full ASVS or SSDF compliance

## How to read this mapping

- **Direct observation (E):** The six-app experiment included relevant assessment evidence. A passing test supports only the tested case, not comprehensive conformance to an ASVS requirement.
- **Standards-based / proposed (S/P):** The control is grounded in a standard and recommended for operational adoption, but the experiment did not independently validate the full control or workflow.
- **Partial (E/P):** Some aspect was observed, but the full requirement, intended production environment, or operational process was not tested.
- **N/A:** An ASVS identifier is not assigned where the checklist row describes a broader workflow rather than a single application-level requirement.

ASVS identifiers are version-pinned (`v5.0.0-...`). The mappings indicate **relevant requirements**, not a one-to-one equivalence between the framework's abbreviated check and every obligation in the standard. NIST SSDF references identify supporting *practices*, not evidence of formal compliance.

## Control-level traceability

| Framework ID | Requirement / verification focus | OWASP ASVS 5.0.0 reference(s) | NIST SSDF supporting practice(s) | Practicum evidence and boundary | Classification |
|---|---|---|---|---|---|
| REQ-01 | Document sensitive features, roles, exposure and security expectations | `v5.0.0-8.1.1` (authorization rules); `v5.0.0-6.1.1` (anti-automation documentation) | PO.1; PW.1 | Common task-app specification and security-aware prompt; not a full documented threat model for each app | E/P |
| AUTH-01 | Reject unauthenticated access to protected endpoints | `v5.0.0-8.2.1`; `v5.0.0-8.3.1` | PW.1; PW.8 | Targeted unauthenticated-access tests in the assessments; no exhaustive endpoint coverage | E |
| AUTH-02 | Enforce object-level permissions | `v5.0.0-8.2.2` | PW.1; PW.8 | Cross-user task-access tests; limited objects and roles | E |
| AUTH-03 | Enforce admin/function-level permissions | `v5.0.0-8.2.1`; `v5.0.0-8.3.1` | PW.1; PW.8 | Admin-route access tests with ordinary users; not all operations tested | E |
| AUTH-04 | Resist repeated failed login attempts | `v5.0.0-6.1.1`; `v5.0.0-6.3.1` | PW.1; PW.8 | All three baseline apps lacked observable protection within limited attempts; security-aware apps showed protections in tested cases; no distributed-attack testing | E |
| SESS-01 | Set session-cookie flags appropriate to intended deployment | `v5.0.0-3.3.1` (`Secure`); `v5.0.0-3.3.2` (`SameSite`); `v5.0.0-3.3.4` (`HttpOnly`) | PW.9; PW.8 | `SameSite` absent in two baseline apps; security-aware cookie attributes inspected; local HTTP does not verify production HTTPS/Secure behavior | E/P |
| SESS-02 | Invalidate session at logout | `v5.0.0-7.4.1` | PW.8 | Logout access checks in assessment summaries; limited to tested session behavior | E |
| CSRF-01 | Prevent cross-origin forged state changes when applicable | `v5.0.0-3.5.1`; `v5.0.0-3.5.2` (alternative preflight-dependent design, **if used**) | PW.1; PW.8 | Missing CSRF protection validated in baseline 1 and 2; security-aware apps rejected selected tokenless requests; not a complete cross-origin attack simulation | E |
| INPUT-01 | Use appropriate validation and context-aware output encoding | `v5.0.0-2.2.1`; `v5.0.0-1.2.1` | PW.1; PW.8 | Targeted XSS/input tests did not reproduce exploitation; this does not prove broad injection resistance | E/P |
| DATA-01 | Protect database queries from injection | `v5.0.0-1.2.4` | PW.1; PW.8 | Selected SQL-like inputs and query inspection; not an exhaustive SQL-injection assessment | E/P |
| HDR-01 | Apply CSP, anti-framing policy and `nosniff` | `v5.0.0-3.4.3` (CSP); `v5.0.0-3.4.6` (`frame-ancestors`); `v5.0.0-3.4.4` (`nosniff`) | PW.9; PW.8 | All three baseline apps lacked these observed protections; security-aware apps had them in assessed responses. Header presence alone does not establish policy quality | E |
| CONF-01 | Disable production debug functionality | `v5.0.0-13.4.2`; `v5.0.0-15.2.3` | PW.9 | Debug mode enabled in baseline 1; security-aware configuration reviewed; production deployment not tested | E/P |
| CONF-02 | Review production server, transport security and version banners | `v5.0.0-13.4.6` (backend version details); `v5.0.0-3.4.1` (HSTS on HTTPS) | PW.9 | All six apps disclosed Werkzeug/Python versions; production TLS/HSTS/server setup was not evaluated | E/P |
| DEP-01 | Review vulnerable components and potential secrets | `v5.0.0-15.1.1` (component remediation timeframes); `v5.0.0-15.1.2` (component inventory) | PW.4; RV.1; RV.2 | Trivy reports reviewed for applicability; some DB updates unavailable; an SBOM and production supply-chain assurance were not established by this experiment | E/P |
| FIND-01 | Validate, deduplicate and prioritize findings | **N/A — assurance workflow** | PW.7; PW.8; RV.1; RV.2 | Six assessment summaries distinguish candidate alerts from validated findings; this was part of the research assessment process | E |
| REL-01 | Retest fixes and document release decision | **N/A — assurance workflow** | PW.8; RV.2; PO.4 | Proposed stage only: no controlled post-remediation experiment or organizational release approval was conducted | S/P |

## Experimental evidence summary

| Pair | Baseline validated findings | Security-aware validated findings | Model family (both apps in pair) |
|---|---:|---:|---|
| 1 | 8 | 1 | Sonnet 5 |
| 2 | 7 | 1 | Opus 5.5 |
| 3 | 5 | 1 | Opus 5.5 |
| **Total** | **20** | **3** | |

**Observed difference:** 17 fewer unique validated findings, or **85% fewer** in the security-aware condition. This is a descriptive result from six applications; it is **not** a measured 85% improvement attributable to the complete five-stage framework.

### Findings most relevant to the control mapping

| Validated finding category | Baseline apps affected | Security-aware apps affected | Mapped control |
|---|---:|---:|---|
| Missing CSP | 3 | 0 | HDR-01 |
| Missing anti-clickjacking protection | 3 | 0 | HDR-01 |
| Missing `X-Content-Type-Options` | 3 | 0 | HDR-01 |
| Server version disclosure | 3 | 3 | CONF-02 |
| Missing CSRF protection | 2 | 0 | CSRF-01 |
| Missing explicit `SameSite` | 2 | 0 | SESS-01 |
| No observable login throttling within test window | 3 | 0 | AUTH-04 |
| Debug mode enabled | 1 | 0 | CONF-01 |
| **Unique validated findings** | **20** | **3** | |

**Interpretation:** The security-aware generation condition was associated with fewer findings in all three matched pairs. Model/tool version differences, small sample size, local environment, selected tests, and passive-only ZAP limit causal and external-validity claims. A baseline app also implemented some protections without explicit security prompting. The persistent version banner across all six apps illustrates the need for independent assessment even when security requirements are supplied.

## Suggested use in the final report and presentation

1. **Framework artifact:** Refer to this table as the traceability companion to Framework v2; it connects a lightweight checklist to specific standards and observed results.
2. **Evaluation:** Report the paired counts and validated finding categories, not raw scanner alert totals.
3. **Scope:** State that the experiment directly evaluated **security-aware generation requirements** and the selected assessment procedure, **not** the effectiveness of remediation and release gates.
4. **Future work:** Test complete framework adoption in production-like settings, including actual remediation/retesting, effort, and release decisions.

## Primary sources

- NIST, *Secure Software Development Framework (SSDF) Version 1.1*, SP 800-218 (2022): https://csrc.nist.gov/pubs/sp/800/218/final
- OWASP, *Application Security Verification Standard (ASVS) 5.0.0*, official version-pinned requirement CSV: https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/docs_en/OWASP_Application_Security_Verification_Standard_5.0.0_en.csv
- Practicum assessment summaries: `baseline-1-assessment-summary.md`, `baseline-2-assessment-summary.md`, `baseline-3-assessment-summary.md`, `security-aware-1-assessment-summary.md`, `security-aware-2-assessment-summary.md`, and `security-aware-3-assessment-summary.md`.

**Important:** These are selected, relevant standards references, not proof that every subrequirement was tested or satisfied. The checklist should be adapted to the application and intended production environment.
