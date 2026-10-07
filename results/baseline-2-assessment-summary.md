cat > ../../results/baseline-2-assessment-summary.md <<'EOF'
# Baseline 2 Security Assessment Summary

## Instance
- Condition: Baseline
- Instance: Baseline 2
- Assessment date: October 7, 2026
- Environment: Local macOS
- Application URL: http://127.0.0.1:5000
- Assessment performed against the original generated application with no security remediation.

## Assessment Method

Baseline 2 was assessed using the frozen assessment methodology established before formal testing:

- Bandit 1.9.4 static analysis
- Trivy 0.74.0 dependency vulnerability scanning
- Trivy 0.74.0 secret scanning
- OWASP ZAP 2.17.0 passive assessment using controlled navigation
- Seven targeted manual security tests

Raw scanner alerts were not automatically counted as findings. Findings were validated for applicability and deduplicated before inclusion in the final count.

## Bandit Results

Bandit scanned 240 lines of Python code across `app.py` and `db.py`.

- Raw issues detected: 0
- Validated findings: 0

## Trivy Dependency Results

Trivy detected seven raw dependency vulnerabilities:

1. Flask 3.0.3 — CVE-2026-27205 — Low
2. Werkzeug 3.0.3 — CVE-2024-49766 — Medium
3. Werkzeug 3.0.3 — CVE-2024-49767 — Medium
4. Werkzeug 3.0.3 — CVE-2025-66221 — Medium
5. Werkzeug 3.0.3 — CVE-2026-102598 — Medium
6. Werkzeug 3.0.3 — CVE-2026-21860 — Medium
7. Werkzeug 3.0.3 — CVE-2026-27199 — Medium

After applicability review, none were counted as validated application findings.

- CVE-2026-27205 requires caching-proxy and session-access conditions not present in the local assessment environment.
- CVE-2024-49766 applies to Python versions below 3.11 on Windows; the assessment used Python 3.12.7 on macOS.
- CVE-2024-49767 concerns multipart/form-data parsing. The application does not provide file-upload or multipart functionality.
- CVE-2025-66221 concerns Windows-specific special device-name behavior involving `safe_join`.
- CVE-2026-102598 requires Windows/NTFS and user-controlled file paths involving `safe_join` or `send_from_directory`.
- CVE-2026-21860 concerns Windows-specific special device-name behavior.
- CVE-2026-27199 concerns Windows-specific special device-name behavior.

Validated applicable dependency findings: 0.

## Trivy Secret Scan

- Secrets detected: 0
- Validated findings: 0

## ZAP Passive Assessment

OWASP ZAP 2.17.0 was used in passive mode with controlled manual navigation. External browser/background traffic was excluded from evaluation.

The following local application findings were validated:

### B2-01 — Missing CSRF Protection
- Severity: Medium
- Status: Validated
- Evidence: ZAP identified POST forms without recognized anti-CSRF tokens. A successful task-creation POST contained only task fields and no CSRF token.
- Related control: SEC-11 Request Forgery Protection

### B2-02 — Missing Content Security Policy
- Severity: Medium
- Status: Validated
- Evidence: Local HTTP 200 responses did not contain a `Content-Security-Policy` response header.
- Related control: SEC-12 Browser Security Headers

### B2-03 — Missing Anti-Clickjacking Protection
- Severity: Medium
- Status: Validated
- Evidence: Local responses contained neither an `X-Frame-Options` header nor a CSP `frame-ancestors` directive.
- Related control: SEC-12 Browser Security Headers

### B2-04 — Session Cookie Missing SameSite Attribute
- Severity: Low
- Status: Validated
- Evidence: The session cookie included `HttpOnly` but did not include a `SameSite` attribute.
- Related control: SEC-08 Session Security

### B2-05 — Server Version Information Disclosure
- Severity: Low
- Status: Validated
- Evidence: Local responses disclosed `Server: Werkzeug/3.0.3 Python/3.12.7`.

### B2-06 — Missing X-Content-Type-Options Header
- Severity: Low
- Status: Validated
- Evidence: Local responses did not contain `X-Content-Type-Options: nosniff`.
- Related control: SEC-12 Browser Security Headers

ZAP also reported the absence of HTTP Strict Transport Security. This was classified as not applicable because the controlled application was intentionally assessed over local HTTP rather than HTTPS.

Informational and external browser/background alerts were excluded.

## Manual Security Tests

### TEST01 — Unauthenticated Access
PASS. Accessing `/tasks` while logged out redirected the user to the login page.

### TEST02 — Cross-User Authorization
PASS. A second user attempting to access another user's task received `Task not found.`

### TEST03 — Administrator Authorization
PASS. A non-administrator attempting to access `/admin/users` received `Administrator access required.`

### TEST04 — Input and Output Handling
PASS. HTML and script input was rendered literally rather than interpreted or executed. This result applies only to the tested input and does not establish universal XSS resistance.

### TEST05 — Non-Destructive SQL Injection
PASS. The test string `' OR '1'='1` was stored and displayed literally without an application error or unexpected data exposure.

### TEST06 — Logout and Session Handling
PASS. After logout, attempting to revisit a protected task-edit URL redirected the user to the login page.

### TEST07 — Repeated Failed Authentication
FAIL / FINDING. Ten consecutive incorrect password attempts were accepted without observable throttling, temporary account lockout, increasing delay, or CAPTCHA.

### B2-07 — No Protection Against Repeated Authentication Attempts
- Status: Validated
- Evidence: Ten consecutive failed login attempts were permitted without observable protection against repeated authentication attempts.
- Related control: SEC-03 Authentication Attack Protection

## Final Validated Findings

Baseline 2 produced **7 unique validated findings**:

1. B2-01 — Missing CSRF protection — Medium
2. B2-02 — Missing Content Security Policy — Medium
3. B2-03 — Missing anti-clickjacking protection — Medium
4. B2-04 — Session cookie missing SameSite attribute — Low
5. B2-05 — Server version information disclosure — Low
6. B2-06 — Missing X-Content-Type-Options header — Low
7. B2-07 — No protection against repeated authentication attempts — Manual finding

## Assessment Summary

- Bandit validated findings: 0
- Trivy dependency findings: 0 validated applicable findings from 7 raw CVEs
- Trivy secret findings: 0
- ZAP passive validated findings: 6
- Additional manual findings: 1
- Total unique validated findings: **7**

No remediation was performed before or during the initial formal assessment. Raw scanner alerts were not treated as findings without validation, and duplicate manifestations of the same underlying weakness were counted once.
EOF
