# Contributing to Mastodon RSS Bot

This document covers the guidelines and processes for contributing to this project, including how to report issues, suggest enhancements, submit code changes, and follow project standards.

## 📑 Table of Contents

- [Contributing](#-contributing)
  - [Reporting Issues](#reporting-issues)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Code Contributions](#code-contributions)
    - [Prerequisites](#prerequisites)
    - [Development Setup](#development-setup)
    - [Making Changes](#making-changes)
    - [Pull Request Guidelines](#pull-request-guidelines)
  - [Code Style](#code-style)
  - [Documentation](#documentation)
- [License](#-license)
- [Getting Assistance](#-getting-assistance)

## 🤝 Contributing

### Reporting Issues

- Search existing issues first.
- Use the issue templates if available.
- Provide clear reproduction steps.
- Include environment details.

### Suggesting Enhancements

- Check the existing discussions.
- Explain the use case and expected conduct.
- Consider the implementation complexity.

### Code Contributions

#### Prerequisites

- Python 3.8 or later
- Git

#### Development Setup

```bash
# Clone the repository
git clone https://github.com/hmlendea/mastodon-rss-bot.git
cd mastodon-rss-bot

# Install dependencies
python -m pip install -r requirements.txt
```

#### Making Changes

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes.
4. Commit with clear and descriptive messages.
5. Push to your fork.
6. Open a Pull Request.

#### Pull Request Guidelines

- Target the `master` branch.
- Keep PRs focused and atomic.
- Revise documentation if applicable.
- Include tests for any new functionality.
- Ensure the CI checks pass.

### Code Style

Follow the project's coding standards:
- PEP 8 with 4-space indentation
- Run `python -m black .` before committing.

### Documentation

- Revise relevant docs for changes.
- Follow the documentation style guide.
- Preview changes locally if possible.

## 📄 License

By contributing, you agree that your contributions will be licensed under the GNU General Public License Version 3 or later.

## 📜 Code of Conduct

This project follows the [Code of Conduct](./CODE_OF_CONDUCT.md).

## 🔒 Security

Mastodon RSS Bot follows a coordinated disclosure policy for security vulnerabilities.

For information on reporting security vulnerabilities, see the [Security Policy](./SECURITY.md).

## ❓ Getting Assistance

- Check existing discussions and documentation first.
- Open an issue for problems or suggestions.