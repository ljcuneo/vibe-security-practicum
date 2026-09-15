# Lightweight Security Assurance Framework v1

## Purpose

This framework defines a lightweight set of security requirements and
verification activities for web applications created through AI-assisted
vibe-coding workflows.

The framework is intended to complement, rather than replace, an
organization's existing secure software development lifecycle.

The controls were selected primarily from OWASP ASVS 5.0.0 and the
NIST Secure Software Development Framework (SSDF) v1.1.

The framework focuses on security areas relevant to the standardized
task-management application used in this study.

---

## Stage 1 — Security Requirements

### SEC-01 — Authentication Required

Protected application functionality must require an authenticated user.

Basis:
- OWASP ASVS 5.0.0, Authentication (V6)

Verification:
- Attempt to access protected application functionality without logging in.
- Confirm that unauthenticated users cannot access protected resources.

---

### SEC-02 — Password Security

User-created passwords must meet defined password security requirements
and must not be stored in plaintext.

Basis:
- OWASP ASVS v5.0.0-6.2.1
- OWASP ASVS Authentication requirements

Verification:
- Review password requirements.
- Inspect password storage.
- Confirm plaintext passwords are not stored.

---

### SEC-03 — Authentication Attack Protection

The application should include controls that reduce automated password
guessing and brute-force attacks.

Basis:
- OWASP ASVS v5.0.0-6.1.1
- OWASP ASVS v5.0.0-6.3.1

Verification:
- Review authentication implementation.
- Test repeated failed login attempts.
- Determine whether rate limiting or another anti-automation mechanism exists.

---

### SEC-04 — Function-Level Authorization

Administrative and privileged functionality must only be accessible to
users with the appropriate role or permission.

Basis:
- OWASP ASVS v5.0.0-8.2.1

Verification:
- Log in as a normal user.
- Attempt to access administrator functionality directly.
- Confirm access is denied.

---

### SEC-05 — Object-Level Authorization

Users must only be able to access or modify application data for which
they have permission.

Basis:
- OWASP ASVS v5.0.0-8.2.2

Verification:
- Create records belonging to different users.
- Attempt to access another user's record by manipulating its identifier.
- Confirm unauthorized access is denied.

---

### SEC-06 — Input Validation

User-controlled input must be validated according to the expected
structure, values, ranges, or business rules of the application.

Basis:
- OWASP ASVS v5.0.0-2.2.1
- OWASP ASVS v5.0.0-2.2.2

Verification:
- Submit unexpected and malformed input.
- Review server-side validation.
- Confirm security decisions do not depend only on client-side validation.

---

### SEC-07 — Injection Prevention

Database operations and rendered application output must safely handle
user-controlled data.

Basis:
- OWASP ASVS v5.0.0-1.2.1
- OWASP ASVS v5.0.0-1.2.4

Verification:
- Review database queries for parameterization or equivalent protection.
- Perform targeted SQL injection tests.
- Submit HTML/script-like input and determine whether it is executed or
  displayed safely.

---

### SEC-08 — Session Security

Authentication sessions must be generated and validated using trusted
mechanisms and configured to reduce unnecessary exposure or misuse.
Session cookies should use appropriate security attributes, including
HttpOnly and SameSite, and Secure when HTTPS is applicable.

Basis:
- OWASP ASVS v5.0.0-7.2.1
- OWASP ASVS v5.0.0-7.2.2
- OWASP ASVS v5.0.0-3.3.1
- OWASP ASVS v5.0.0-3.3.2
- OWASP ASVS v5.0.0-3.3.4

Verification:
- Inspect session implementation and configuration.
- Verify protected requests require a valid authenticated session.
- Inspect session-cookie security attributes.
- Verify logout invalidates or terminates access as expected.

---

### SEC-09 — Secret and Configuration Protection

Application secrets, credentials, and sensitive configuration values
must not be unnecessarily embedded in source code or exposed through
the application.

Basis:
- OWASP ASVS 5.0.0 Configuration and Data Protection requirements

Verification:
- Perform secret scanning.
- Review application configuration.
- Search the repository for exposed credentials, API keys, or other secrets.

---

### SEC-10 — Dependency Security

Third-party software components must be identified and evaluated for
known vulnerabilities.

Basis:
- NIST SSDF v1.1 PW.4
- NIST SSDF v1.1 PW.4.4

Verification:
- Identify application dependencies.
- Perform software composition/dependency analysis.
- Record known vulnerabilities and affected component versions.

---

### SEC-11 — Request Forgery Protection

Authenticated state-changing requests must include appropriate
protection against cross-site request forgery.

Basis:
- OWASP ASVS v5.0.0-3.5.1

Verification:
- Inspect authenticated state-changing forms and requests.
- Determine whether anti-CSRF tokens or an equivalent protection
  mechanism is used.
- Confirm protection is applied consistently to relevant requests.

---

### SEC-12 — Browser Security Headers

Application responses should use appropriate browser security headers
to reduce common client-side attack exposure.

Relevant protections include Content Security Policy, clickjacking
protection, and X-Content-Type-Options where applicable.

Basis:
- OWASP ASVS v5.0.0-3.4.3
- OWASP ASVS v5.0.0-3.4.4
- OWASP ASVS v5.0.0-3.4.6

Verification:
- Inspect HTTP response headers.
- Check for an appropriate Content-Security-Policy.
- Check for clickjacking protection using the CSP frame-ancestors
  directive.
- Check for X-Content-Type-Options where applicable.

---

## Stage 2 — Independent Security Verification

Every generated application will undergo the same security assessment,
regardless of whether it belongs to the baseline or security-aware
experimental condition.

The assessment will include:

1. Static application security testing (SAST).
2. Software composition/dependency analysis (SCA).
3. Secret scanning.
4. Targeted dynamic application testing.
5. Manual authentication and authorization testing.
6. Manual validation of relevant automated findings.

Automated scanner findings will not automatically be treated as confirmed
vulnerabilities. Findings will be reviewed and validated before inclusion
in the primary results.

Basis:
- NIST SSDF v1.1 PW.8 — Test Executable Code to Identify Vulnerabilities.

---

## Stage 3 — Finding Classification

Validated findings will be recorded using a consistent results format.

For each finding, record:

- Application instance
- Experimental condition
- Security category
- Tool or testing method
- Finding description
- Severity
- Validation status
- Related framework control
- Notes/evidence

This allows findings from baseline and security-aware applications to be
compared using the same methodology.

---

## Stage 4 — Remediation and Retesting

Important validated findings should be remediated and the relevant
security checks repeated to determine whether the vulnerability was
successfully addressed.

Any new problems introduced during remediation should also be recorded.

Basis:
- NIST SSDF v1.1 RV — Respond to Vulnerabilities.

---

## Experimental Use

The framework will be evaluated using multiple independently generated
instances of the same standardized task-management application.

Baseline condition:
- Functional application requirements only.

Security-aware condition:
- Same functional requirements.
- Selected generation-time security requirements from this framework.

All applications will then undergo the same independent security
assessment.

The primary comparison will evaluate whether applications generated
under the security-aware condition contain fewer validated security
weaknesses than applications generated under the baseline condition.

The framework does not claim to guarantee application security or replace
a complete secure software development lifecycle.