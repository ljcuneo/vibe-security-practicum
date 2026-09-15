# Prototype Security Assessment Pilot

## Purpose

The prototype was created as an exploratory application to validate the proposed security assessment methodology before beginning the formal experiment.

The prototype is not part of the formal experimental dataset. Its purpose was to verify that the selected tools and manual testing procedures could identify and validate security weaknesses in a locally generated vibe-coded web application.

The prototype was generated using Claude Code from a functional specification without explicit security requirements. No security fixes were made to the generated application before or during the assessment.

## Prototype Environment

The prototype is a locally hosted task-management web application built with:

- Python
- Flask
- SQLite
- Basic HTML/CSS

The application includes user registration and authentication, multiple user accounts, persistent task storage, task CRUD functionality, user-specific task authorization, and a basic administrator role.

All testing was performed locally using synthetic data.

## Assessment Tools

The following tools were piloted:

- Bandit 1.9.4 — Python static application security testing (SAST)
- Trivy 0.74.0 — dependency vulnerability and secret scanning
- OWASP ZAP 2.17.0 — passive dynamic web application assessment
- Manual application testing — authentication, authorization, input handling, and session behavior

Automated findings were manually reviewed before being classified as validated findings.

## Validated Findings

The pilot identified the following validated security findings:

1. Flask debug mode enabled — High
2. Vulnerable Flask dependency (CVE-2026-27205) — Low
3. Missing anti-CSRF protection — Medium
4. Content Security Policy header missing — Medium
5. Anti-clickjacking protection missing — Medium
6. X-Content-Type-Options header missing — Low
7. Server version information exposed — Low
8. Session cookie missing an explicit SameSite attribute — Low

Findings were counted as unique validated weaknesses rather than individual scanner alerts or affected endpoints.

## Manual Testing Results

Several security-relevant behaviors were also manually tested.

The prototype successfully prevented one user from directly accessing another user's task by changing the task identifier.

A non-administrator account was prevented from accessing the administrator user-list page.

HTML entered into a task field was rendered as text rather than interpreted as executable HTML.

These successful tests are important because the assessment methodology is intended to measure both security weaknesses and the presence of effective security controls.

## Pilot Observations

The pilot demonstrated that no single assessment technique provides a complete view of application security.

Bandit identified an insecure runtime configuration, Trivy identified a vulnerable dependency, and ZAP identified web and session configuration weaknesses. Manual testing was necessary to evaluate application-specific authorization and input-handling behavior.

The pilot also demonstrated that a functionally correct application can contain security weaknesses even when some secure behaviors are present.

Raw scanner alert counts will therefore not be treated as the primary experimental outcome. Findings will be reviewed, validated, categorized, and counted consistently across applications.

## Methodology Refinements

Based on the pilot, the formal assessment procedure will:

- Use the same assessment tools and manual test cases for every application.
- Restrict ZAP assessment results to the locally tested application.
- Exclude unrelated browser and external network traffic.
- Exclude informational alerts from vulnerability counts.
- Count unique validated findings rather than repeated endpoint-level alerts.
- Record findings using consistent categories and severity levels.
- Document findings that are not applicable to the local experimental environment.
- Preserve generated applications without applying security fixes before their initial assessment.

The assessment methodology will be frozen before formal baseline and security-aware application generation begins.

## Pilot Limitations

The prototype represents a single exploratory application and is not intended to provide evidence about the overall security of vibe-coded applications.

Its results will not be included in the formal baseline-versus-security-aware comparison.

The pilot was used only to validate and refine the experimental methodology.

## Next Steps

The next phase of the project is to finalize the security assurance framework, freeze the assessment procedure, define the controlled application-generation procedure, and begin generating the formal baseline and security-aware application instances.
