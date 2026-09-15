# Controlled Application Generation Procedure

## Purpose

This document defines the procedure used to generate application instances
for the formal baseline and security-aware experimental conditions.

The goal is to keep application generation as consistent as practical so
that the primary intentional difference between conditions is the presence
or absence of security-specific requirements.

---

## Experimental Conditions

### Baseline Condition

Applications will be generated from the standardized functional application
specification without additional security-specific requirements.

### Security-Aware Condition

Applications will be generated from the same standardized functional
application specification supplemented with selected generation-time
security requirements from the Lightweight Security Assurance Framework.

---

## Generation Environment

All formal application instances will be generated:

- On the same local macOS environment.
- Using Claude Code as the AI coding environment.
- Using the same model/version when practical.
- Using the same standardized application specification.
- In separate clean application directories.
- Without existing application source code in the generation directory.

The AI coding tool and model/version used for each generation will be
recorded when available.

---

## Application Specification

Every application will implement the same standardized task-management
application defined in:

    specifications/standardized-app-spec.md

The functional requirements will remain identical between experimental
conditions.

---

## Generation Procedure

For each application instance:

1. Create a new empty directory for the application.
2. Start a new AI coding session in that directory.
3. Submit the appropriate frozen experimental prompt.
4. Allow the AI coding agent to generate the application.
5. Do not manually edit generated application source code.
6. Do not provide additional security advice during generation.
7. Allow follow-up interaction only when necessary to make the required
   application functionality run.
8. Record any follow-up interaction with the coding agent.
9. Stop generation once the required application functionality is working.
10. Preserve the generated application in its original pre-assessment state.

---

## Follow-Up Prompt Rule

Follow-up prompts will be minimized because additional interaction could
introduce uncontrolled differences between application instances.

A follow-up prompt may only be used when:

- The application cannot start.
- A required dependency cannot be installed.
- A required functional feature from the standardized specification does
  not work.

Follow-up prompts should describe the functional problem without suggesting
a security implementation or security fix.

All follow-up prompts will be preserved as part of the experimental record.

---

## Manual Intervention

Generated source code will not be manually edited before the initial
security assessment.

If a technical issue requires manual intervention for an application to
run, the intervention will be documented. Where practical, the AI coding
agent will be asked to correct the functional issue instead of manually
changing the code.

No security weakness identified during generation or assessment will be
fixed before the application's initial security assessment is complete.

---

## Completion Criteria

An application is considered ready for assessment when it can run locally
and supports the required functional behaviors:

- User registration
- User login
- User logout
- Multiple user accounts
- Persistent SQLite storage
- Task creation
- Task viewing
- Task editing
- Task deletion
- User-specific task ownership
- Administrator role
- Administrator user-list functionality

Security behavior is not part of the functional completion decision because
security is an experimental outcome.

---

## Experimental Records

For each application instance, preserve:

- Experimental condition
- Application instance identifier
- Date/time of generation
- AI coding tool
- Model/version, when available
- Initial prompt
- Follow-up prompts, if any
- Notes about generation problems
- Approximate generation effort/time
- Generated source code

---

## Formal Application Instances

The planned directory structure is:

    experiment/
        baseline-1/
        baseline-2/
        baseline-3/
        security-aware-1/
        security-aware-2/
        security-aware-3/

The exact number of successfully evaluated instances will be reported in
the final methodology and results.

---

## Methodology Freeze

This generation procedure will be frozen before formal application
generation begins.

Changes after formal generation begins will be avoided unless necessary.
Any unavoidable change will be documented and considered when interpreting
the experimental results.
