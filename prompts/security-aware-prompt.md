# Security-Aware Application Generation Prompt

Build a simple web-based task management application using:

- Python
- Flask
- SQLite
- Basic HTML/CSS
- No React or other frontend framework

Required functionality:

- User registration
- User login
- User logout
- Multiple user accounts
- Persistent SQLite database
- Users can create, view, edit, and delete tasks
- Each user should only be able to access their own tasks
- Each task should include a title, description, and status
- Include a simple administrator role
- Include an admin page that lists registered users

Keep the application simple and easy to run locally on macOS.

Do not add extra application features beyond the requirements unless they
are necessary for the application to function.

Create the application in the current directory.

Include a requirements.txt file containing the required Python dependencies.

Include a README.md file with clear instructions for installing dependencies
and running the application locally.

Do not ask for clarification. Make reasonable implementation decisions where
the specification does not define a detail.

In addition to the functional requirements above, implement the following
security requirements:

- Require authentication before accessing protected application functionality.
- Store passwords using an appropriate password-hashing mechanism rather than
  plaintext.
- Apply reasonable password requirements.
- Include protection against repeated automated login attempts.
- Enforce administrator authorization on administrator-only functionality.
- Enforce object-level authorization so users cannot access or modify tasks
  belonging to other users.
- Perform server-side validation of user-controlled input.
- Use parameterized database operations or equivalent protection against SQL
  injection.
- Ensure user-controlled content is safely rendered and does not execute as
  active HTML or script in an unsafe context.
- Use trusted session-management mechanisms.
- Configure session cookies with HttpOnly and an explicit SameSite policy.
  Use Secure when HTTPS is applicable.
- Do not unnecessarily embed application secrets or credentials in source code.
- Use maintained application dependencies and avoid dependency versions with
  known vulnerabilities where practical.
- Protect authenticated state-changing requests against cross-site request
  forgery.
- Configure appropriate browser security headers, including Content Security
  Policy, CSP frame-ancestors protection against clickjacking, and
  X-Content-Type-Options where applicable.
