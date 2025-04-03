# Contributing to S4

Thank you for your interest in contributing to S4! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Branching Strategy](#branching-strategy)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Documentation](#documentation)
- [Issue Tracking](#issue-tracking)
- [Code Style](#code-style)
- [License](#license)

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- Docker and Docker Compose
- Git

### Fork and Clone the Repository

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/s4.git
   cd s4
   ```
3. Add the upstream repository as a remote:
   ```bash
   git remote add upstream https://github.com/original-org/s4.git
   ```

## Development Environment

### Backend Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run the development server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd s4-ui
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Start the development server:
   ```bash
   npm start
   ```

### Docker Setup

For a complete environment:

```bash
docker-compose up -d
```

## Branching Strategy

We use a simplified Git workflow:

- `main`: The main branch contains the latest stable release
- `develop`: Development branch for integrating features
- Feature branches: Create from `develop` for new features

### Naming Conventions

- Feature branches: `feature/short-description`
- Bug fix branches: `fix/issue-description`
- Documentation branches: `docs/description`
- Release branches: `release/version-number`

## Making Changes

1. Update your fork:
   ```bash
   git checkout develop
   git pull upstream develop
   ```

2. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. Make your changes
4. Commit your changes with clear, descriptive messages:
   ```bash
   git commit -m "feat: add new feature X"
   ```
   We follow [Conventional Commits](https://www.conventionalcommits.org/) format.

## Testing

### Backend Tests

Run the backend tests:

```bash
pytest
```

For coverage report:

```bash
pytest --cov=app
```

### Frontend Tests

Run the frontend tests:

```bash
cd s4-ui
npm test
```

### End-to-End Tests

Run the end-to-end tests:

```bash
npm run cypress:run
```

## Submitting a Pull Request

1. Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Go to the original repository on GitHub and create a Pull Request:
   - Base branch: `develop`
   - Compare branch: your feature branch
   - Include a clear title and description
   - Reference any related issues using the syntax `Fixes #123` or `Relates to #123`

3. Wait for the CI checks to pass and address any feedback from maintainers

## Documentation

- Update documentation for any new features or changes
- Follow the existing documentation style
- Place documentation in the appropriate location:
  - User guides in `docs/`
  - API documentation in docstrings
  - Frontend component documentation in comments

### Documentation Guidelines

- Use clear, concise language
- Include examples where appropriate
- Document all parameters, return values, and exceptions
- Keep documentation up to date with code changes

## Issue Tracking

### Creating an Issue

Before creating an issue, please check for existing issues to avoid duplicates.

When creating a new issue:
1. Choose the appropriate template
2. Provide a clear title and description
3. Add relevant labels
4. Include steps to reproduce for bugs
5. Include any relevant screenshots or logs

### Issue Labels

- `bug`: Something isn't working as expected
- `enhancement`: New feature or improvement
- `documentation`: Documentation-related issues
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is needed

## Code Style

### Python Code Style

We follow PEP 8 with some modifications:

- Line length: 100 characters
- Use 4 spaces for indentation
- Use docstrings for all public methods, classes, and modules

Run linting checks:

```bash
flake8 app tests
black --check app tests
isort --check-only app tests
```

Auto-format code:

```bash
black app tests
isort app tests
```

### JavaScript/TypeScript Code Style

We follow Airbnb JavaScript Style Guide with some modifications:

- Use 2 spaces for indentation
- Use semicolons
- Prefer arrow functions
- Use PropTypes for React components

Run linting:

```bash
cd s4-ui
npm run lint
```

Auto-fix issues:

```bash
cd s4-ui
npm run lint:fix
```

## License

By contributing to S4, you agree that your contributions will be licensed under the project's [MIT License](../LICENSE).

## Questions?

If you have any questions or need help, please:
- Join our [Discord community](https://discord.gg/your-org)
- Ask in the GitHub discussions section
- Contact us at contributors@your-org.com

Thank you for contributing to S4! 