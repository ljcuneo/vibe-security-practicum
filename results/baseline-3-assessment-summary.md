# Baseline 3 — Security Assessment Summary

## 1. Experiment Information

- Application: Baseline 3
- Date assessed: October 14, 2026
- Generation method: Claude Code, Opus 5.5, High effort
- Prompt: prompts/baseline-prompt.md
- Stack: Python, Flask, SQLite, HTML/CSS
- Testing environment: Local macOS, http://127.0.0.1:5001
- Source code modifications: None
- Assessment approach: Bandit, Trivy, OWASP ZAP passive scanning, and targeted manual testing

## 2. Validated Security Findings

### B3-F01 — Missing Content Security Policy (CSP)
- Evidence: OWASP ZAP reported that the CSP header was absent.
- Impact: Reduced browser-side defense against certain injection attacks.
- Status: Identified by passive scanning; no exploit demonstrated.

### B3-F02 — Missing Anti-Clickjacking Header
- Evidence: OWASP ZAP reported the absence of anti-clickjacking protection.
- Impact: Potential exposure to clickjacking if deployed without other protections.
- Status: Identified by passive scanning; no exploit demonstrated.

### B3-F03 — Server Version Disclosure
- Evidence: HTTP responses exposed `Werkzeug/3.1.9 Python/3.12.7`.
- Impact: Reveals implementation and version information.
- Status: Confirmed through HTTP response inspection.

### B3-F04 — Missing X-Content-Type-Options Header
- Evidence: OWASP ZAP reported the header was absent.
- Impact: Reduced protection against MIME-type sniffing.
- Status: Identified by passive scanning.

### B3-F05 — Missing Repeated-Login Protection
- Evidence: Five consecutive incorrect login attempts did not trigger a lockout or visible restriction. Source-code search found no obvious rate-limiting or lockout logic.
- Impact: Increased exposure to automated password-guessing attempts.
- Status: Confirmed within the tested scenario.

## 3. Passed Security Tests

| Security Control | Test Performed | Result |
|---|---|---|
| Authentication | Accessed a private task while logged out | PASS — Redirected to login |
| Function-level authorization | Regular user attempted to access `/admin` | PASS — HTTP 403 |
| Object-level authorization | User 2 attempted to view User 1's task | PASS — HTTP 404 |
| Object-level authorization | User 2 attempted to open User 1's task editor | PASS — HTTP 404 |
| CSRF protection | Submitted login POST without CSRF token | PASS — HTTP 400 |
| Session invalidation | Attempted direct task access after logout | PASS — Redirected to login |
| Session cookie HttpOnly | Inspected Set-Cookie header | PASS — Present |
| Session cookie SameSite | Inspected Set-Cookie header | PASS — Lax |
| Stored XSS | Submitted script payload in task content | NOT REPRODUCED |
| SQL injection | Submitted SQL-like task title and inspected database queries | NOT REPRODUCED — Parameterized queries verified |

## 4. Automated Scanning

### Bandit
- Raw findings: 0
- Output: results/baseline-3-bandit.json

### Trivy Vulnerability Scanning
- Reported vulnerabilities: 0
- Dependency inventory generated from installed Python packages.
- Cached vulnerability database used because a database update failed.
- Result applies to the scanned dependency inventory, not a complete guarantee that the application has no vulnerabilities.
- Output: results/baseline-3-trivy-vuln.json

### Trivy Secret Scanning
- Detected secrets: 0
- Output: results/baseline-3-trivy-secret.json

### OWASP ZAP
- Scanning mode: Passive only
- Several missing-header alerts identified.
- Alerts unrelated to the localhost application were excluded.
- Informational and unverified potential-XSS alerts were not counted as confirmed vulnerabilities.
- No active attack scan performed.

## 5. Additional Observations

- The application generated CSRF protection without explicit security instructions.
- Database queries use parameterized SQL statements.
- Task access is restricted by user ID.
- Session cookies include HttpOnly and SameSite=Lax.
- The Secure cookie attribute was absent in the local HTTP environment; this was documented but not counted as a validated vulnerability.
- The browser displayed a previously visited page after logout, but direct access to a protected task required authentication.

## 6. Limitations

- Testing was conducted against a local development application.
- Manual tests covered selected scenarios rather than exhaustive attack paths.
- Five failed logins demonstrate no restriction within that window, not the absence of every possible rate-limiting mechanism.
- A missing security header does not establish a successful exploit.
- Scanner findings require contextual interpretation.
- No source-code changes were made to remediate findings.

## 7. Preliminary Assessment

Baseline 3 demonstrated stronger default security behavior in several areas than Baselines 1 and 2, particularly CSRF protection.

Five security weaknesses were identified through passive scanning, HTTP inspection, and manual testing. Some represent missing defensive controls rather than demonstrated exploitation.

These results will be compared against Security-Aware 3 using the same assessment methodology.
