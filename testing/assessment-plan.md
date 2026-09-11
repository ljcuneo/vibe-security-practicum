# Security Assessment Plan

## Purpose

This document defines the security assessment procedure that will be
applied consistently to every application instance generated during
the experiment.

The purpose of defining the procedure in advance is to ensure that
baseline and security-aware applications are evaluated using the same
methods and criteria.

Automated findings will not automatically be considered confirmed
vulnerabilities. Findings will be reviewed and validated before being
included in the primary experimental results.

---

## Assessment Pipeline

Each application will undergo the following assessment stages:

1. Static application security testing
2. Dependency vulnerability scanning
3. Secret scanning
4. Dynamic application security testing
5. Manual security testing
6. Finding validation and classification

The same tools, configurations, and testing procedures will be used
for every application instance.

---

## 1. Static Application Security Testing

### Tool

Bandit

### Purpose

Bandit will be used to identify common security issues in the
Python source code generated for each application.

### Procedure

Run Bandit recursively against the application source code.

Example:

    bandit -r . -f json -o bandit-results.json

The generated JSON report will be preserved for analysis.

### Recorded Information

For each relevant finding, record:

- Bandit test ID
- CWE, when available
- Severity
- Confidence
- File and line
- Description
- Validation status

---

## 2. Dependency Vulnerability Scanning

### Tool

Trivy

### Purpose

Trivy will be used to identify known vulnerabilities in third-party
software dependencies used by the generated application.

### Procedure

Run a filesystem vulnerability scan against the application directory.

Example:

    trivy fs --scanners vuln . > trivy-vulnerabilities.txt

Where useful, structured output may also be preserved for later analysis.

### Recorded Information

Record:

- Vulnerable dependency
- Installed version
- Vulnerability identifier
- Severity
- Fixed version, when available
- Validation/relevance status

---

## 3. Secret Scanning

### Tool

Trivy

### Purpose

The application source will be checked for potentially exposed
credentials, API keys, tokens, private keys, and other secrets.

### Procedure

Run:

    trivy fs --scanners secret . > trivy-secrets.txt

### Recorded Information

Record:

- Secret category
- File/location
- Severity
- Description
- Validation status

Test credentials or non-sensitive example values will not automatically
be counted as confirmed security findings.

---

## 4. Dynamic Application Security Testing

### Tool

OWASP ZAP

### Purpose

ZAP will provide repeatable dynamic analysis against the running
web application.

### Initial Procedure

Each application will be started locally using the same general
execution procedure.

The initial automated dynamic assessment will use the ZAP Baseline Scan
against the local application.

The exact ZAP configuration will be finalized during pilot testing and
then held constant for all formal experimental applications.

### Recorded Information

Record:

- ZAP alert
- Risk level
- Affected endpoint
- Description
- Validation status

---

## 5. Manual Security Testing

Automated scanners may not identify authorization and application-logic
weaknesses. Each application will therefore undergo the same targeted
manual security tests.

### TEST-01 — Unauthenticated Access

Attempt to access protected application functionality without logging in.

Expected secure behavior:

Access is denied or the user is redirected to authentication.

---

### TEST-02 — Cross-User Object Access

Create accounts for User A and User B.

Create a task belonging to User A.

While authenticated as User B, attempt to access or modify User A's
task by manipulating the task identifier.

Expected secure behavior:

Access is denied.

---

### TEST-03 — Administrator Authorization

Log in as a normal user and directly navigate to administrator-only
functionality.

Expected secure behavior:

Access is denied.

---

### TEST-04 — Input and Output Handling

Submit HTML or script-like content through user-controlled fields such
as the task title or description.

Observe how the application displays the stored value.

Expected secure behavior:

User-controlled content is not executed as active script or markup in
an unsafe context.

---

### TEST-05 — Injection Handling

Submit a small predefined set of non-destructive SQL injection test
inputs to relevant application fields.

Observe whether input changes query behavior, produces database errors,
bypasses authentication, or exposes unauthorized data.

Expected secure behavior:

Input does not alter the intended database query behavior.

---

### TEST-06 — Logout and Session Access

Authenticate normally, access protected functionality, log out, and
attempt to access protected functionality again.

Expected secure behavior:

The logged-out session cannot continue accessing protected resources.

---

### TEST-07 — Repeated Failed Authentication

Perform a predefined number of unsuccessful login attempts.

Observe whether the application implements any protection against
repeated automated authentication attempts.

Record the observed behavior consistently across all application
instances.

---

## 6. Finding Validation

Automated findings will be reviewed before being counted as validated
security weaknesses.

Each finding will receive one of the following statuses:

- Validated
- Not validated
- Not applicable
- Duplicate

Where practical, validation will use source-code review, application
behavior, or both.

---

## 7. Finding Classification

Validated findings will be recorded using a common results format.

Fields will include:

- Application instance
- Experimental condition
- Assessment method
- Tool/test identifier
- Framework control
- Vulnerability category
- Finding description
- Severity
- Validation status
- Evidence/notes

---

## 8. Experimental Consistency

To preserve comparability:

- Every application will receive the same automated scans.
- Every application will receive the same manual test cases.
- Tool configurations will remain constant after pilot testing.
- The same finding-validation criteria will be used across conditions.
- Test data will be synthetic.
- Applications will run in the same controlled local environment.

Changes to the assessment methodology after formal data collection
begins will be documented and avoided unless necessary.

---

## Pilot Testing

The disposable prototype may be used to install, configure, and test
the assessment tools.

Results obtained from the prototype will not be included in the formal
experimental dataset.

The formal assessment procedure will be frozen after pilot testing and
before official baseline and security-aware application instances are
evaluated.