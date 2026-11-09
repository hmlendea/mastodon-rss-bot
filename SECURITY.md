# Security Policy

This document describes the security policy for the Mastodon RSS Bot project, including supported versions, vulnerability reporting procedures, and disclosure expectations.

## 📑 Table of Contents

- [Supported Versions](#-supported-versions)
- [Reporting a Vulnerability](#-reporting-a-vulnerability)
- [Scope](#-scope)
- [Disclosure Policy](#-disclosure-policy)

## 🛡️ Supported Versions

Use this table to indicate which project versions currently receive security maintenance.

| Version | Distribution Channel | Supported |
|---------|--------------------|-----------|
| Latest version | GitHub Releases | ✅ |
| Latest version | Source (main branch) | ✅ |
| Preceding versions | Any distribution channel | ❌ |

## 🚨 Reporting a Vulnerability

Please do not disclose suspected vulnerabilities publicly before maintainers have had an opportunity to validate and remediate them.

To report a vulnerability:
- [GitHub Security Advisories](https://github.com/hmlendea/mastodon-rss-bot/security/advisories)
- Contact the maintainers directly

## 📌 Scope

The original maintainers are not responsible for changes, modifications, or security issues introduced by downstream forks.

The subsequent report categories are in scope for this repository:
- Application code (main.py, config.py, database.py, utils.py)
- Configuration handling and secrets management
- Dependency vulnerabilities in declared requirements
- RSS feed parsing and content processing
- Mastodon API interaction and authentication

The subsequent categories are out of scope unless explicitly stated to the contrary:
- Mastodon instance security or API changes
- Third-party service availability (RSS feeds, URL shorteners, privacy frontends)
- Downstream forks or modified distributions
- Operating system or Python runtime vulnerabilities
- Network-level attacks outside application control

## 📢 Disclosure Policy

This project follows coordinated disclosure:
1. Vulnerabilities are investigated privately.
2. A remediation plan is prepared and validated.
3. Public disclosure is published after a fix, mitigation, or agreed risk decision is available.
4. Credit is attributed in accordance with reporter preference and project policy.