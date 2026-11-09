# Security

## Overview

This document describes the security posture of the mastodon-rss-bot application: current state, identified risks, and remediation recommendations.

## Current State

| Property | Value |
|----------|-------|
| Authentication | OAuth Bearer token (Mastodon) |
| Credential storage | CLI args (token), file (app secret), source code (ShrinkMe key) |
| Network | Outbound HTTPS only |
| Input validation | Minimal |
| Dependency scanning | None |
| Security headers | N/A (no web server) |
| Audit logging | None (print statements only) |

## Threat Model

### Assets

| Asset | Sensitivity | Impact if Compromised |
|-------|-------------|----------------------|
| Mastodon access token | High | Unauthorised posting as user |
| Mastodon app credentials | Medium | App impersonation |
| ShrinkMe API key | Medium | Monetisation fraud |
| Cache database | Low | Posting history exposure |
| Configuration file | Low | Operational details |
| Source code | Low | Hard-coded values exposure |

### Threat Actors

| Actor | Capability | Motivation |
|-------|-----------|------------|
| Network attacker (MITM) | Intercept/modify traffic | Token theft, content manipulation |
| Malicious feed operator | Control feed content | XSS via title, phishing links |
| Malicious page operator | Control linked page content | Data exfiltration, malware |
| Local attacker | Read files on host | Credential theft |
| Supply chain attacker | Compromise dependencies | Code execution |

## Identified Risks

### Risk 1: Access Token Exposure via CLI Arguments

**Severity**: HIGH

**Description**: The Mastodon access token is passed as a CLI argument (`--access-token`). CLI arguments are visible in:
- Process listings (`ps aux`)
- Shell history (`~/.bash_history`)
- System logs (auditd, syslog)
- `/proc/<pid>/cmdline`

**Current Code**:
```python
parser.add_argument('--access-token', required=True, help='Mastodon access token')
```

**Impact**: Token theft → unauthorised posting as the user.

**Remediation**:
1. Read token from environment variable (`MASTODON_ACCESS_TOKEN`)
2. Read token from file (`--access-token-file`)
3. Never log the token
4. Mask token in all log output

### Risk 2: Hard-coded ShrinkMe API Key

**Severity**: HIGH

**Description**: The ShrinkMe.io API key is embedded in `main.py` source code:

```python
'https://shrinkme.io/st?api=81ad7e29077269bcae6dc1773d87abbabeaa9aa8&url='
```

**Impact**:
- Key exposed in repository (public or private)
- Key rotation requires code change and redeployment
- Key abuse (click fraud) attributed to operator

**Remediation**:
1. Move key to configuration file or environment variable
2. Rotate the exposed key immediately
3. Never commit API keys to source control

### Risk 3: No Input Validation on Feed Content

**Severity**: MEDIUM

**Description**: Feed entry titles, summaries, and author fields are used without sanitisation. While Mastodon's API handles HTML escaping, the application performs string operations (truncation, replacement) on untrusted input.

**Current Code**:
```python
title = feed_entry.title  # No validation
status = title + " by " + author + " " + link  # Concatenation
```

**Impact**:
- Truncation may cut HTML entities mid-sequence
- Text replacements may interact unexpectedly with malicious content
- Extremely long titles cause memory pressure (no length limit before truncation)

**Remediation**:
1. Validate entry field lengths before processing
2. Sanitize HTML entities before concatenation
3. Apply text replacements after sanitisation
4. Truncate at word boundaries, not mid-character

### Risk 4: No TLS Certificate Verification Configuration

**Severity**: MEDIUM

**Description**: The application relies on library defaults for TLS verification. No explicit certificate verification settings, no certificate pinning, no custom CA bundle configuration.

**Impact**: If library defaults are weakened (e.g., `REQUESTS_CA_BUNDLE` env var manipulation), MITM attacks possible.

**Remediation**:
1. Explicitly set `verify=True` in all HTTP calls
2. Document CA bundle requirements
3. Consider certificate pinning for Mastodon API

### Risk 5: No Rate Limit Awareness

**Severity**: MEDIUM

**Description**: The application does not respect Mastodon API rate limits. A large feed with many entries could trigger rate limiting, causing:
- Failed posts (429 errors)
- Account suspension (if limits repeatedly exceeded)
- IP-based throttling

**Impact**: Service disruption, potential account action.

**Remediation**:
1. Check `X-RateLimit-Remaining` headers
2. Implement backoff on 429 responses
3. Add configurable delay between posts
4. Respect `MAXIMUM_TOOTS_COUNT` strictly

### Risk 6: SQLite Database Without Access Controls

**Severity**: LOW

**Description**: `cache.db` is created with default permissions (typically 0644). Any user on the host can read the posting history.

**Impact**: Information disclosure of posting activity.

**Remediation**:
1. Set file permissions to 0600 after creation
2. Document multi-user host risks
3. Consider encrypted database for sensitive deployments

### Risk 7: No Dependency Vulnerability Scanning

**Severity**: MEDIUM

**Description**: No CI pipeline, no `pip-audit`, no Dependabot. Dependencies are unpinned (`requirements.txt` has no version constraints), so a compromised package update could introduce malicious code.

**Impact**: Supply chain attack → arbitrary code execution on host.

**Remediation**:
1. Pin dependency versions
2. Add `pip-audit` to CI
3. Enable GitHub Dependabot
4. Review dependencies before updates

### Risk 8: Fake-Useragent Upstream Fetch

**Severity**: LOW

**Description**: `fake-useragent` fetches its User-Agent list from an upstream server on first use. If the upstream is compromised, the library could return malicious data (though it only returns strings).

**Impact**: Low — strings only, no code execution. But upstream unavailability breaks the bot.

**Remediation**:
1. Cache User-Agent list locally
2. Provide fallback static list
3. Consider replacing with static UA rotation

### Risk 9: Privacy Frontend Availability

**Severity**: LOW

**Description**: Hard-coded privacy frontend instances (libreddit.kavin.rocks, nitter.net, yewtu.be) may be unavailable, blocked, or compromised. Links rewritten to these instances may fail or serve malicious content.

**Impact**: Broken links in toots, potential phishing if frontend compromised.

**Remediation**:
1. Make frontend instances configurable
2. Add health checks
3. Provide fallback to original domains

### Risk 10: No Audit Logging

**Severity**: LOW

**Description**: No structured audit trail of what was posted, when, and by whom. `print()` statements are not persistent.

**Impact**: Cannot investigate incidents, cannot prove what was posted.

**Remediation**:
1. Implement structured logging (see [Logging](../logging.md))
2. Log all posted statuses with content hash
3. Retain logs per policy

## Security Controls

### Current Controls

| Control | Status | Notes |
|---------|--------|-------|
| HTTPS for all external calls | ✅ Present | Library defaults |
| OAuth token authentication | ✅ Present | Mastodon API |
| Append-only cache | ✅ Present | Prevents accidental re-posts |
| Ad filter | ✅ Present | Crude but functional |

### Missing Controls

| Control | Priority | Effort |
|---------|----------|--------|
| Token via env var/file | High | Low |
| API key externalisation | High | Low |
| Input validation | Medium | Medium |
| Rate limit awareness | Medium | Medium |
| Dependency pinning | Medium | Low |
| Dependency scanning | Medium | Low |
| Structured audit logging | Medium | Medium |
| DB file permissions | Low | Low |
| TLS verification explicit | Low | Low |

## Secure Development Guidelines

### Adding New External Integrations

1. **Never hard-code credentials** — Use config file or env vars
2. **Validate all responses** — Check status codes, content types
3. **Set timeouts** — All HTTP calls must have timeout
4. **Log minimally** — No sensitive data in logs
5. **Handle errors gracefully** — Don't crash on transient failures

### Adding New Configuration Keys

1. **Update `sample.config.json`** — Add key with safe default
2. **Update `config.py`** — Extract with `.get()` and default
3. **Document in `configuration.md`** — Describe purpose and values
4. **Avoid secrets in config** — Prefer env vars for secrets

### Adding New Dependencies

1. **Pin version** — `package==X.Y.Z` in requirements.txt
2. **Check for vulnerabilities** — `pip-audit` before adding
3. **Minimise dependencies** — Prefer stdlib where possible
4. **Document purpose** — Add to `dependencies.md`

## Incident Response

### Suspected Token Compromise

1. Revoke token on Mastodon instance (Settings → Development)
2. Generate new token
3. Update deployment with new token
4. Review posted content for unauthorised posts
5. Rotate ShrinkMe key if same environment

### Suspected Key Compromise (ShrinkMe)

1. Log in to ShrinkMe.io
2. Regenerate API key
3. Update source code (after externalising to config)
4. Monitor for abnormal click patterns

### Suspected Supply Chain Compromise

1. Freeze deployments
2. Audit `requirements.txt` against known-good versions
3. Run `pip-audit`
4. Review dependency hashes
5. Rebuild from clean environment

## Compliance Considerations

### GDPR (if processing EU personal data)

- **Data processed**: Feed entry titles, links, authors (public data)
- **Storage**: SQLite cache (local only)
- **Retention**: Unbounded (no deletion mechanism)
- **Recommendation**: Implement cache TTL and deletion

### Mastodon ToS

- **Rate limits**: Respect instance limits
- **Automation**: Disclose bot status in profile
- **Spam**: Avoid excessive posting (use `MAXIMUM_TOOTS_COUNT`)

## Related Documentation

- [Logging](../logging.md) — Audit logging requirements
- [Error Handling](../error-handling.md) — Error information disclosure
- [Dependencies](../dependencies.md) — Dependency security
- [Build and Deployment](../build-and-deployment.md) — Secure deployment
- [PRIVACY.md](../PRIVACY.md) — Data handling statement
- [SECURITY.md](../SECURITY.md) — Vulnerability reporting