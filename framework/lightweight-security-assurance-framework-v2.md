# Lightweight Security Assurance Framework for AI-Assisted Web Applications

**Version:** 2.0  
**Project:** Securing Vibe-Coded Applications: A Lightweight Security Assurance Framework for AI-Assisted Development  
**Status:** Practicum deliverable — proposed framework informed by standards and a six-application experiment

## 1. Purpose, scope, and evidence boundaries

This framework provides a practical **predeployment security assurance process** for small, AI-assisted web applications. It is intended for developers and small teams that use AI coding agents and need a repeatable, auditable way to specify security expectations, identify weaknesses, verify controls, and make risk-informed release decisions.

The framework draws on the **NIST Secure Software Development Framework (SSDF), SP 800-218**, and **OWASP Application Security Verification Standard (ASVS) 5.0.0**. It adapts those established practices into a lightweight workflow; it is **not** a certification of NIST or OWASP compliance and does not replace a formal penetration test or organizational security program.

Three evidence labels are used below:

- **Standards-based (S):** Grounded in NIST SSDF or OWASP ASVS guidance.
- **Experiment-informed (E):** Motivated or illustrated by findings in the six-app practicum evaluation.
- **Proposed operational guidance (P):** A reasonable implementation recommendation **not independently validated** by the experiment.

**Evaluation boundary:** The experiment compared applications generated from functional-only requirements with applications generated from functional **plus explicit security requirements**. It did **not** experimentally test the full five-stage workflow, post-finding remediation, or real-world release approvals.

## 2. The five-stage workflow

`Specify security requirements → Scan → Verify → Triage and remediate → Reverify and decide`

| Stage | Minimum activity | Evidence to retain | Basis |
|---|---|---|---|
| 1. Specify | Document applicable security controls in the generation/development requirements | Security requirements and application threat/feature inventory | S, E |
| 2. Scan | Run source, dependency/secret, and web-response checks appropriate to the stack | Tool versions, configurations, raw reports | S, E |
| 3. Verify | Manually exercise security-sensitive paths; validate and deduplicate alerts | Test cases, outcomes, reproducible evidence | S, E |
| 4. Triage | Assess real-world risk; fix or formally accept each finding | Findings register, owners, remediation/risk rationale | S, P |
| 5. Decide | Retest changes, assess residual risk, authorize or block release | Retest results, exception approvals, release record | S, P |

### Stage 1 — Specify security requirements

1. Record the application stack, data sensitivity, deployment exposure, roles, and security-sensitive features.
2. Identify trust boundaries and likely misuse scenarios (for example, unauthenticated access, cross-user data access, forged state changes, and password guessing). A lightweight STRIDE review can help organize this analysis.
3. Include **applicable** security requirements in the AI-generation prompt, acceptance criteria, or developer specification. Never assume the agent will implement a control correctly merely because it says it has.
4. Record exclusions as **Not Applicable (N/A)** with reasons, rather than silently omitting controls.

**Minimum requirements for an authenticated task-management web app:**

- Server-side authentication; password storage using an appropriate adaptive password-hashing algorithm.
- Server-side role/function authorization **and object-level authorization** on each protected action.
- Protection against repeated login attempts (such as rate limiting or progressive delay), with defined thresholds and observability.
- Secure session lifecycle and cookie attributes (`HttpOnly`, appropriate `SameSite`, and `Secure` when served over HTTPS); logout invalidates access as appropriate.
- CSRF protection for state-changing requests where browser-authenticated sessions make CSRF applicable.
- Context-aware output encoding, input validation, and parameterized database queries.
- Appropriate browser security headers, including a tested Content Security Policy (CSP) and anti-clickjacking protections, plus `X-Content-Type-Options: nosniff`.
- Debug/development features disabled in production; secrets excluded from source and logs; production-suitable server configuration.
- Maintained dependencies and a documented process for reviewing vulnerability alerts.

**Gate:** Do not proceed to release without a documented security requirements baseline. **Basis: S, E.**

### Stage 2 — Scan the application

Select tools appropriate to the technology and threat model. For the practicum's Python Flask applications:

| Check | Practicum tool | What it can and cannot establish |
|---|---|---|
| Python static analysis | Bandit | Flags potentially risky code patterns; findings require context and validation |
| Dependency and secret review | Trivy | Flags potential vulnerable components/secrets; applicability and database freshness matter |
| HTTP/browser security observations | OWASP ZAP (passive scan) | Identifies observable response/security-header concerns; **does not establish resistance to active attacks** |

Record the exact commands/configuration, tool and database versions, scan scope, environment, and output. Treat scanner output as **candidate observations**, not automatically as confirmed vulnerabilities. Deduplicate multiple alerts referring to the same underlying issue. Where possible, integrate checks into CI without making an unreviewed raw-alert count the sole release criterion.

**Gate:** Reports are saved and candidate findings are ready for validation. **Basis: S, E, P.**

### Stage 3 — Verify controls and validate findings

Execute the checklist in Section 3. For each test, record **Pass / Fail / N/A / Not Tested**, the expected result, observed result, and evidence (request/response, code reference, or screenshot). Verify both positive and negative access cases.

A pass applies **only to the tested scenario**. A small number of failed-login attempts, for example, cannot establish the complete absence or adequacy of all possible anti-automation controls. Likewise, passive scanning cannot replace active security testing when the application risk requires it.

Review each automated alert for reachability, deployment applicability, exploit preconditions, duplicates, and compensating controls. Record why a candidate alert was excluded rather than silently deleting it.

**Gate:** Security-sensitive functions have documented test outcomes and findings are validated. **Basis: S, E.**

### Stage 4 — Prioritize and remediate

For each **validated** finding, evaluate:

1. **Impact:** Consequences for confidentiality, integrity, availability, and users.
2. **Exploitability:** Realistic prerequisites, attack complexity, and available mitigations.
3. **Exposure:** Internet-facing versus internal-only, authentication requirements, and production configuration.
4. **Affected scope:** Sensitive data, affected users, and recurrence across components.

Assign a contextual priority (Critical / High / Medium / Low) and document the rationale. **These priorities are framework guidance, not severity labels retroactively assigned to the experiment's original findings.** A reachable production debug console, for example, may warrant blocking release; a low-impact version banner may be tracked or accepted under an approved policy.

- **Critical / High:** Normally block release until remediated, unless an authorized exception process explicitly permits otherwise.
- **Medium:** Remediate before release or obtain time-bound, documented risk acceptance with mitigating controls.
- **Low:** Fix when practical or track/accept with an owner and review date.

Track an owner, proposed fix, target date, and verification evidence for each finding. **Basis: S, P; E supplies illustrative finding types.**

### Stage 5 — Reverify and decide

1. Retest the specific failed case after a fix.
2. Rerun relevant automated checks and regression tests.
3. Confirm the production deployment configuration, not only local development behavior.
4. Record remaining risks and authorized exceptions.
5. Document the release outcome: **Approve**, **Approve with documented exceptions**, or **Block**.

**Minimum release rule (proposed):** No unresolved Critical or High findings without an explicit, authorized exception; applicable high-impact controls must be tested; residual risk must have an owner. The organization—not the AI agent—defines approval authority and risk appetite.

**Gate:** A reviewer signs off on a traceable release record. **Basis: S, P.**

## 3. Predeployment security checklist

Use **Pass / Fail / N/A / Not Tested** and link evidence for every row. This checklist is a minimum starting point, not a complete ASVS assessment.

| ID | Check | Suggested verification | Basis |
|---|---|---|---|
| REQ-01 | Security-sensitive features, roles, data, and exposure documented | Review requirements and threat/feature inventory | S, P |
| AUTH-01 | Protected pages and endpoints reject unauthenticated access | Direct request without session | S, E |
| AUTH-02 | Users cannot read/change another user's objects | Attempt cross-user object access | S, E |
| AUTH-03 | Non-admin users cannot perform admin operations | Invoke admin endpoint as ordinary user | S, E |
| AUTH-04 | Repeated failed logins receive meaningful protection | Controlled repeated-attempt test; review thresholds/logs | S, E |
| SESS-01 | Session cookies have appropriate `HttpOnly`, `SameSite`, and HTTPS `Secure` settings | Inspect `Set-Cookie` under intended deployment | S, E |
| SESS-02 | Logout prevents reuse of the invalidated session | Replay protected request after logout | S, E |
| CSRF-01 | Applicable state-changing requests reject missing/invalid CSRF tokens | Submit POST without valid token | S, E |
| INPUT-01 | Output encoding/input handling prevents tested injection paths | Targeted input/output tests | S, P |
| DATA-01 | Database access uses parameterized queries | Code review and targeted test | S, P |
| HDR-01 | Appropriate CSP, anti-clickjacking, and `nosniff` protections are present | Inspect response headers and browser behavior | S, E |
| CONF-01 | Debug mode and unsafe development settings are disabled for production | Review deployment config and responses | S, E |
| CONF-02 | Production server/TLS settings and sensitive response banners reviewed | Inspect production-like configuration/headers | S, E |
| DEP-01 | Dependencies and secret exposure reviewed | Trivy plus contextual review | S, E |
| FIND-01 | Candidate alerts validated, deduplicated, and prioritized | Review findings register | S, E |
| REL-01 | Remediation retested and residual risk signed off | Review release decision record | S, P |

**Applicability note:** HTTPS, HSTS, cookie `Secure`, production server choice, and related controls must be assessed against the intended **production-like environment**. Local HTTP tests alone do not demonstrate production transport security.

## 4. Findings register and release record templates

### Findings register (one row per unique validated weakness)

| Finding ID | Control/check | Evidence | Impact / exploitability / exposure | Priority | Owner | Action / exception | Retest status |
|---|---|---|---|---|---|---|---|
| Example | CONF-01 | Debug mode enabled in application configuration | High potential impact if exposed in production | Context-dependent | Assigned developer | Disable and verify | Pending |

### Release decision record

- **Application/version/commit:**
- **Environment and intended exposure:**
- **Assessor and review date:**
- **Security requirements version:**
- **Tools, versions, and scan report links:**
- **Manual test evidence and exclusions:**
- **Unresolved Critical / High / Medium / Low findings:**
- **Accepted risks, owners, approval authority, and expiration dates:**
- **Decision:** Approve / Approve with exceptions / Block
- **Approver and date:**

## 5. Practicum evaluation: evidence informing the framework

Six independently generated Python Flask task-management applications were assessed under two conditions: **three functional-requirements-only baseline apps** and **three apps generated with explicit security requirements**. The assessment combined Bandit, Trivy, ZAP **passive** observations, and targeted manual tests. Findings were reviewed and deduplicated.

| Matched comparison | Baseline validated findings | Security-aware validated findings |
|---|---:|---:|
| Pair 1 (Sonnet 5, High effort) | 8 | 1 |
| Pair 2 (Opus 5.5, High effort) | 7 | 1 |
| Pair 3 (Opus 5.5, High effort) | 5 | 1 |
| **Total** | **20** | **3** |

The observed aggregate difference is **17 fewer findings (85% lower count)** in the security-aware condition. This is a **descriptive comparison of six applications**, not a statistical estimate of the effect of the complete framework or a proof of causation.

**Observed recurring baseline weaknesses:** Missing CSP, clickjacking protection, and `X-Content-Type-Options` across all three baseline apps; no observable protection within the limited repeated-login test window across all three; missing CSRF protection and explicit `SameSite` cookie configuration in two; debug mode enabled in one. The baseline apps were not identical: Baseline 3 implemented some security protections without explicit security requirements.

**Persistent weakness:** All six applications disclosed Werkzeug/Python server version information in HTTP response headers, including all three security-aware applications. This demonstrates the value of verification even when security requirements are specified.

**Limits of inference:** The study used one application specification, six local test instances, selected tests, and passive rather than active ZAP scanning. Model and Claude Code versions varied between some runs, though model family was held constant **within each matched pair**. Tool database freshness and deployment applicability affected interpretation of some dependency alerts. No post-remediation comparison or production deployment approval was tested.

**Interpretation:** Explicit security requirements were **associated with fewer validated findings in these test cases**. The other framework stages are justified primarily through standards and proposed practice, not direct experimental validation.

## 6. Adoption and future evaluation

For adoption, place the requirements checklist in the issue template or AI-generation prompt; retain scan artifacts in CI; require a short manual verification record for authentication/authorization and state-changing functionality; and attach a signed release decision to each deployment. Scale testing to data sensitivity and deployment exposure. Applications handling regulated data, payments, or high-impact functions need deeper review.

Future evaluation should test multiple app types, model configurations, coding agents, and production-like deployments; include authorized active testing; and measure assessment effort, true/false positives, remediation time, post-fix defect rates, and reviewer consistency. This would test the **whole workflow**, rather than only the generation-requirements component.

## 7. References and traceability

1. NIST, **SP 800-218**, *Secure Software Development Framework (SSDF) Version 1.1* (2022). https://csrc.nist.gov/pubs/sp/800/218/final — overarching support for defining security requirements, reviewing/testing software, managing vulnerabilities, and improving release practices.
2. OWASP Foundation, **Application Security Verification Standard (ASVS) 5.0.0**. https://owasp.org/www-project-application-security-verification-standard/ — verification requirements for authentication, authorization, session management, request handling, and application configuration. **Control-level identifiers should be checked against the official version before claiming a formal ASVS mapping.**
3. Practicum assessment records: `baseline-1-assessment-summary.md`, `baseline-2-assessment-summary.md`, `baseline-3-assessment-summary.md`, `security-aware-1-assessment-summary.md`, `security-aware-2-assessment-summary.md`, and `security-aware-3-assessment-summary.md` (repository results/evidence). These support the **E** annotations and numerical observations above.

**Traceability rule:** Standards establish normative security practices; experimental findings show what occurred in the six tested apps; proposed gates, prioritization thresholds, and adoption steps are operational recommendations. Do not present one type of evidence as another.
