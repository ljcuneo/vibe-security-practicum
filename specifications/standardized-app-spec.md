# Standardized Application Specification

## Purpose

This specification defines the standardized web application used in the experimental evaluation. The same functional requirements will be used for all application instances generated during the study.

## Application

A simple web-based task management application.

## Technology Stack

- Python
- Flask
- SQLite
- Basic HTML/CSS
- No JavaScript frontend framework

## Functional Requirements

The application must allow users to:

1. Register a user account.
2. Log in using their account.
3. Log out.
4. Create tasks.
5. View their tasks.
6. Edit their tasks.
7. Delete their tasks.
8. Assign a title, description, and status to each task.

The application must support multiple user accounts.

Users should only be able to view and manage tasks associated with their own account.

## Administrative Functionality

The application must support an administrator role.

Administrators must have access to an administrative page that displays registered users.

Normal users should not have access to administrator-only functionality.

## Data Storage

User accounts and tasks must be stored in a persistent SQLite database.

## Application Environment

The application must:

- Run locally.
- Provide instructions for installing required dependencies.
- Provide instructions for starting the application.
- Be usable through a standard web browser.
- Remain small enough to generate and evaluate within the scope of the experiment.

## Scope

The application does not require:

- Cloud deployment
- Payment processing
- Email functionality
- External authentication providers
- Third-party APIs
- Complex frontend frameworks
- Production infrastructure

Synthetic test data will be used during evaluation.