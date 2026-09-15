# Security Assessment Plan

## Purpose

This document defines the security assessment procedure that will be
applied consistently to every application instance generated during
the formal experiment.

The purpose of defining and freezing the procedure before formal data
collection is to ensure that baseline and security-aware applications
are evaluated using the same methods and criteria.

Automated findings will not automatically be considered confirmed
security weaknesses. Findings will be reviewed and validated before
being included in the primary experimental results.

---

## Assessment Pipeline

Each application will undergo the following assessment stages:

1. Static application security testing
2. Dependency vulnerability scanning
3. Secret scanning
4. Dynamic/passive web application assessment
5. Manual security testing
6. Finding validation and classification

The same tools, configurations, test cases, and validation criteria will
be used for every formal application instance.

---

## 1. Static Application Security Testing

### Tool

Bandit 1.9.4

### Purpose

Bandit will be used to identify common security issues in the Python
source code generated for each application.

### Procedure

Run Bandit recursively against the application source code while
excluding local virtual-environment directories.

Example:

    bandit -r . --exclude ./venv -f json -o bandit-results.json

The generated JSON report will be preserved as raw assessment evidence.

### Recorded Information

For each relevant finding, record:

- Bandit test ID
- CWE, when available
- Tool-reported severity
- Confidence
- File and line
- Description
- Validation status
- Evidence or validation notes

---

## 2. Dependency Vulnerability Scanning

### Tool

Trivy 0.74.0

### Purpose

Trivy will be used to identify known vulnerabilities in third-party
software dependencies used by each generated application.

### Procedure

Run a filesystem vulnerability scan against the application directory.

Example:

    trivy fs --scanners vuln . > trivy-vulnerabilities.txt

If the local Docker credential configuration interferes with the scan,
the same isolated Docker configuration used during pilot testing will
be used consistently.

### Recorded Information

Record:

- Vulnerable dependency
- Installed version
- Vulnerability identifier
- Tool-reported severity
- Fixed version, when available
- Validation/relevance status
- Evidence or notes

---

## 3. Secret Scanning

### Tool

Trivy 0.74.0

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
- Tool-reported severity
- Description
- Validation status
- Evidence or notes

Test credentials, synthetic values, or non-sensitive example values will
not automatically be counted as validated security findings.

---

## 4. Dynamic/Passive Web Application Assessment

### Tool

OWASP ZAP 2.17.0

### Purpose

ZAP will be used to observe HTTP requests and responses and identify
web-application and configuration weaknesses while the locally running
application is exercised.

### Procedure

Each application will be started locally and accessed through ZAP using
the same controlled navigation sequence.

The navigation sequence will exercise, where supported by the generated
application:

1. Registration and login pages
2. Registration of the first test account
3. Login
4. User dashboard
5. Task creation
6. Task viewing
7. Task editing
8. Task deletion
9. Administrator functionality
10. Logout
11. Login with a second test account
12. Second-user task functionality
13. Logout

ZAP passive scanning will be allowed to process the traffic generated
during this sequence.

Only findings associated with the locally tested application will be
included in the experimental results. Browser background traffic,
external domains, update services, and unrelated requests will be
excluded.

ZAP informational alerts will be preserved when useful as raw evidence
but will not be counted as security weaknesses.

### Recorded Information

Record:

- ZAP alert
- Tool-reported risk level
- Vulnerability category/CWE, when available
- Affected application behavior or endpoint
- Validation status
- Evidence or notes

Repeated occurrences of the same underlying weakness across multiple
endpoints will not automatically be counted as separate validated
findings.

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

Access is denied and the task is not modified.

---

### TEST-03 — Administrator Authorization

Log in as a normal user and directly navigate to administrator-only
functionality.

Expected secure behavior:

Access is denied.

---

### TEST-04 — Input and Output Handling

Submit predefined HTML or script-like content through user-controlled
fields such as the task title or description.

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

Perform the same predefined number of unsuccessful login attempts
against each application.

Observe whether the application implements protection against repeated
authentication attempts.

The observed behavior will be recorded consistently across all
application instances.

---

## 6. Finding Validation

Automated findings will be reviewed before being counted as validated
security weaknesses.

Each candidate finding will receive one of the following statuses:

- Validated
- Not validated
- Not applicable
- Duplicate

Where practical, validation will use source-code review, application
behavior, HTTP request/response evidence, or a combination of these
methods.

A scanner alert alone is not sufficient for inclusion in the primary
validated-finding count.

---

## 7. Finding Classification and Counting

Validated findings will be recorded using a common results format.

Fields will include:

- Application instance
- Experimental condition
- Assessment method
- Tool/test identifier
- Framework control, when applicable
- Vulnerability category
- Finding description
- Tool-reported severity
- Validation status
- Evidence/notes

The primary comparison will use unique validated security findings
rather than raw scanner-alert totals.

Repeated instances of the same underlying weakness within one
application will normally be counted once. Distinct security weaknesses,
even when identified by the same tool, may be counted separately.

Results may also be summarized by vulnerability category, severity, and
framework-control outcome to avoid relying on a single aggregate count.

---

## 8. Experimental Consistency

To preserve comparability:

- Every application will receive the same automated scans.
- Every application will receive the same manual test cases.
- Tool versions and configurations will remain constant when practical.
- The same ZAP navigation procedure will be used for every application.
- Only traffic associated with the local experimental application will
  be included in ZAP results.
- Informational scanner alerts will not be counted as vulnerabilities.
- The same finding-validation and counting criteria will be used across
  experimental conditions.
- Test accounts and application data will be synthetic.
- Applications will run in the same controlled local environment.
- Generated applications will not be manually secured or remediated
  before their initial assessment.

Any unavoidable methodology change after formal data collection begins
will be documented, justified, and applied consistently where possible.

---

## 9. Pilot Testing and Methodology Freeze

A disposable prototype was used to install, configure, and pilot the
assessment methodology.

The pilot demonstrated that the selected techniques identify different
classes of security weaknesses and that manual validation is necessary
to distinguish meaningful findings from raw scanner output.

Pilot results are documented separately and will not be included in the
formal experimental dataset.

Following completion of the pilot, this assessment procedure is treated
as the frozen methodology for the initial formal baseline and
security-aware comparison.

Changes will be avoided after formal application assessment begins
unless a technical issue makes a change necessary. Any such change will
be documented as a methodological limitation.
