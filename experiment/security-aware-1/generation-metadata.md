# Security-Aware 1 Generation Metadata

- Condition: Security-Aware
- Instance: Security-Aware 1
- Generation date: September 17, 2026
- Environment: Local macOS
- AI coding tool: Claude Code 2.1.274
- Model: Sonnet 5
- Effort: High
- Plan: Claude Pro
- Starting directory: Empty
- Prompt: Frozen `prompts/security-aware-prompt.md`
- Security requirements included: Yes — frozen framework security requirements
- Manual source-code edits: None
- Follow-up prompts: None
- Generation time reported by Claude Code: 4 minutes 9 seconds

## Environment Note

Claude Code automatically updated from version 2.1.269, which was used for Baseline 1, to version 2.1.274 before Security-Aware 1 generation. The model (Sonnet 5) and effort setting (High) remained unchanged. This version difference is documented as an experimental environment variation.

## Generation Result

Claude Code reported successful implementation and functional testing of the required task-management application, including registration, authentication, per-user task CRUD, and administrator functionality.

Claude Code also reported implementing security controls corresponding to the security-aware prompt, including password hashing and password requirements, authentication attack protection, function- and object-level authorization, parameterized database access, output escaping, CSRF protection, session-cookie protections, secret handling, security headers, and dependency version selection.

These generation-time claims are recorded for provenance only. They are not treated as validated security results. Security controls and weaknesses will be independently evaluated using the project's frozen assessment methodology.