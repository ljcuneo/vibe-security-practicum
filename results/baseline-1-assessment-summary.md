# Baseline 1 Security Assessment Summary

## Application

- Condition: Baseline
- Instance: Baseline 1
- Assessment date: September 17, 2026
- Environment: Local macOS controlled environment
- Application stack: Python, Flask, SQLite
- AI generation environment: Claude Code 2.1.269, Sonnet 5, High effort
- Security guidance included during generation: No
- Manual source-code modifications before assessment: None

This application was generated from the frozen baseline prompt and assessed using the frozen project assessment methodology. No remediation was performed before or during the initial assessment.

---

## 1. Bandit SAST

Tool version: Bandit 1.9.4

### B1-01 — Flask Debug Mode Enabled

- Tool: Bandit
- Location: `app.py:298`
- Severity: High
- Confidence: Medium
- CWE: CWE-94
- Status: Validated
- Category: Insecure configuration
- Evidence: The application starts using `app.run(debug=True)`.

Bandit reported one security issue in the application source, which was independently reviewed and retained as a validated finding.

---

## 2. Trivy Dependency and Secret Assessment

Tool version: Trivy 0.74.0

Installed dependencies included:

- Flask 3.0.3
- Werkzeug 3.0.3

### Raw Dependency Alerts

Trivy reported six dependency vulnerability alerts:

- Flask CVE-2026-27205 — Low
- Werkzeug CVE-2024-49766 — Medium
- Werkzeug CVE-2024-49767 — Medium
- Werkzeug CVE-2025-66221 — Medium
- Werkzeug CVE-2026-21860 — Medium
- Werkzeug CVE-2026-27199 — Medium

Raw scanner alerts were not automatically counted as validated application findings. Each alert was reviewed for applicability to the tested application and controlled environment.

### Dependency Applicability Review

**CVE-2026-27205 — Flask**

Status: Not validated/applicable under the tested configuration.

The vulnerability involves conditions related to improper caching of session data. The Baseline 1 application was directly served in the local controlled environment without a caching proxy. The conditions required to demonstrate this weakness were therefore not present in the tested configuration.

**CVE-2024-49766 — Werkzeug**

Status: Not applicable.

The reported weakness concerns Windows-specific `safe_join` behavior. The controlled experimental environment is macOS.

**CVE-2024-49767 — Werkzeug**

Status: Not applicable to the tested application functionality.

The reported weakness concerns resource exhaustion involving multipart form-data parsing. Baseline 1 does not implement file-upload or multipart functionality. Source review for `multipart`, `request.files`, file input elements, and `FileStorage` returned no relevant functionality.

**CVE-2025-66221 — Werkzeug**

Status: Not applicable.

The reported weakness concerns Windows device names in path segments. The controlled experimental environment is macOS.

**CVE-2026-21860 — Werkzeug**

Status: Not applicable.

The reported weakness concerns Windows special device names in `safe_join()` behavior. The controlled experimental environment is macOS.

**CVE-2026-27199 — Werkzeug**

Status: Not applicable.

The reported weakness concerns Windows special device names in `safe_join()` behavior. The controlled experimental environment is macOS.

### Dependency Assessment Result

- Raw dependency alerts: 6
- Validated applicable dependency findings: 0

The raw Trivy output is preserved as experimental evidence even though the alerts were not included in the validated-finding count.

### Secret Scan

Trivy secret scanning detected no secrets.

- Validated secret findings: 0

---

## 3. OWASP ZAP Passive Assessment

Tool version: OWASP ZAP 2.17.0

ZAP was used in passive mode with controlled manual navigation of the local application. No ZAP active scan was performed.

The navigation included registration, authentication, task creation, viewing, editing and deletion, admin functionality, logout, a second user account, and second-user task activity.

### B1-02 — Missing Anti-CSRF Protection

- Severity: Medium
- Status: Validated
- CWE: CWE-352
- Framework mapping: SEC-11 Request Forgery Protection
- Evidence: An authenticated `POST /tasks/new` request successfully created a task without a CSRF token or equivalent request-specific anti-CSRF value.

The captured state-changing request contained the authenticated session cookie and task form values but no anti-CSRF token.

This finding establishes the absence of an anti-CSRF control on the tested authenticated state-changing request. A complete cross-origin exploitation proof-of-concept was not performed.

### B1-03 — Content Security Policy Missing

- Severity: Medium
- Status: Validated
- Framework mapping: SEC-12 Browser Security Headers
- Evidence: The inspected application response did not contain a `Content-Security-Policy` header.

### B1-04 — Clickjacking Protection Missing

- Severity: Medium
- Status: Validated
- Framework mapping: SEC-12 Browser Security Headers
- Evidence: The inspected application response did not contain an observed framing restriction such as CSP `frame-ancestors`.

### B1-05 — X-Content-Type-Options Missing

- Severity: Low
- Status: Validated
- Framework mapping: SEC-12 Browser Security Headers
- Evidence: The inspected application response did not contain an `X-Content-Type-Options` header.

### B1-06 — Server Version Information Disclosure

- Severity: Low
- Status: Validated
- Category: Information disclosure / configuration
- Evidence: The HTTP response disclosed:

`Server: Werkzeug/3.0.3 Python/3.12.7`

### B1-07 — Session Cookie Missing Explicit SameSite Attribute

- Severity: Low
- Status: Validated
- Framework mapping: SEC-08 Session Security
- Evidence: The observed session cookie contained `HttpOnly; Path=/` but did not contain an explicit `SameSite` attribute.

### ZAP Observations Not Counted as Validated Findings

The following ZAP observations were excluded from the validated-finding count:

- Strict-Transport-Security Header Not Set — Not applicable to the controlled local HTTP environment.
- Authentication Request Identified — Informational.
- Session Management Response Identified — Informational.
- Technology detection alerts — Informational and/or outside the finding-count criteria.
- Re-examine Cache-Control Directives — Not counted without independent validation.
- External or background observations — Excluded under the local-application-only assessment scope.

---

## 4. Manual Security Tests

### TEST-01 — Unauthenticated Access to Protected Functionality

Protected application functionality required authentication.

**Result: PASS**

No unauthenticated-access weakness was demonstrated by this test.

### TEST-02 — Cross-User Object Authorization

An administrator-owned task was created as Task 3.

While authenticated as `user2`, the following administrator-owned task endpoint was requested:

`/tasks/3/edit`

The application returned:

`404 Not Found`

The other user's task was not exposed.

**Result: PASS**

No object-level authorization weakness was demonstrated by this test.

### TEST-03 — Admin Function Authorization

While authenticated as non-admin `user2`, the following endpoint was requested:

`/admin/users`

The application returned:

`403 Forbidden`

The administrator account was able to access the admin functionality.

**Result: PASS**

No function-level authorization weakness was demonstrated by this test.

### TEST-04 — Input and Output Handling

A task was created using the following title:

`<h1>Test</h1>`

and description:

`<script>alert('test')</script>`

The application rendered both values as literal text. The HTML was not interpreted as markup and the JavaScript did not execute.

**Result: PASS**

This result applies only to the tested task fields and payloads. It does not establish that every application output is resistant to cross-site scripting.

### TEST-05 — Non-Destructive SQL Injection Test

The following input was submitted as a task title:

`' OR '1'='1`

The application stored and displayed the value as ordinary data. No SQL error, unexpected data access, or other abnormal behavior was observed.

**Result: PASS**

The tested input did not demonstrate SQL injection. This result does not establish that every database operation in the application is immune to SQL injection.

### TEST-06 — Logout and Session Access

While authenticated as `user2`, a protected task edit endpoint was accessed.

The user then logged out and attempted to revisit:

`/tasks/2/edit`

The application redirected the request to:

`/login?next=/tasks/2/edit`

The protected resource was not accessible without authenticating again.

**Result: PASS**

### TEST-07 — Repeated Failed Authentication

Ten consecutive login attempts were performed against the `user2` account using an incorrect password.

All attempts continued to return invalid credentials. No observable rate limiting, increasing delay, temporary account lockout, CAPTCHA, or other automated-login protection was triggered.

**Result: FAIL — Validated Finding**

### B1-08 — No Observable Protection Against Repeated Login Attempts

- Status: Validated
- Framework mapping: SEC-03 Authentication Attack Protection
- Evidence: Ten consecutive failed authentication attempts against the same account were accepted without observable throttling, temporary lockout, or other automated-attack protection.

This finding is counted once regardless of the number of failed login attempts used during validation.

---

## 5. Validated Finding Summary

| ID | Finding | Severity | Source |
|---|---|---|---|
| B1-01 | Flask debug mode enabled | High | Bandit |
| B1-02 | Missing anti-CSRF protection | Medium | ZAP + manual validation |
| B1-03 | Content Security Policy missing | Medium | ZAP + header validation |
| B1-04 | Clickjacking protection missing | Medium | ZAP + header validation |
| B1-05 | X-Content-Type-Options missing | Low | ZAP + header validation |
| B1-06 | Server version information disclosure | Low | ZAP + header validation |
| B1-07 | Session cookie missing explicit SameSite attribute | Low | ZAP + header validation |
| B1-08 | No observable protection against repeated login attempts | Not assigned | Manual |

**Final Baseline 1 validated count: 8 unique findings.**

Trivy produced six raw dependency alerts, but none were retained as validated applicable findings after applicability review.

---

## 6. Manual Test Summary

| Test | Result |
|---|---|
| TEST-01 Unauthenticated access | PASS |
| TEST-02 Cross-user authorization | PASS |
| TEST-03 Admin authorization | PASS |
| TEST-04 Input/output handling | PASS |
| TEST-05 Non-destructive SQL injection | PASS |
| TEST-06 Logout/session access | PASS |
| TEST-07 Repeated failed authentication | FAIL / Validated finding |

Manual testing therefore identified one additional validated weakness while also documenting security controls that operated successfully in the tested scenarios.

---

## 7. Assessment Totals

- Bandit validated findings: 1
- Trivy raw dependency alerts: 6
- Trivy validated applicable dependency findings: 0
- Trivy secret findings: 0
- ZAP/manual-validation findings: 6
- Additional manual-test findings: 1
- Total unique validated findings: 8

The validated-finding total represents unique confirmed weaknesses rather than raw scanner-alert counts.

---

## 8. Assessment Notes

- Only synthetic test accounts and data were used.
- Testing was limited to the local controlled environment.
- The same frozen assessment methodology will be used for subsequent formal application instances.
- ZAP was used passively; no active scan was performed.
- Scanner alerts were not automatically treated as validated vulnerabilities.
- Findings were independently reviewed and validated where required.
- Duplicate observations of the same underlying weakness are counted once.
- Findings determined to be outside the tested platform or application functionality were not included in the validated-finding count.
- No remediation was performed before completion of the initial assessment.
- No manual source-code changes were made to the generated application before assessment.
- The exploratory prototype is excluded from the formal experimental dataset.
- Baseline 1 represents one independently generated application instance and is not by itself used to draw conclusions about differences between the baseline and security-aware experimental conditions.

**TEST-07 retrospective clarification (November 2026):** The assessor confirms that the standardized TEST-07 procedure involved 10 consecutive failed-login attempts for this application. This statement clarifies the intended and reported testing procedure; the original observations above remain unchanged. Where the original record describes fewer attempts, a lockout, or no numeric count, the outcomes of unrecorded attempts are not inferred.
