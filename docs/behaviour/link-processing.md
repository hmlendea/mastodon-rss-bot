# Link Processing Behaviour

## Overview

This document describes the observable behavior of the link processing pipeline: how URLs in entry text are transformed before posting.

## Pipeline Order

Links are processed through a fixed sequence of transformations:

```
Original URL
    │
    ▼
┌─────────────────┐
│ 1. Shortlink    │  (if USE_SHORTLINK)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. Privacy      │  (if USE_PRIVACY_FRONTENDS)
│    Frontends    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. Cleanup      │  (always)
│    (tracking    │
│     params)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. Monetisation │  (if MONETISE_LINKS)
└────────┬────────┘
         │
         ▼
Final URL
```

**Important**: The order matters. Each transformation operates on the output of the previous one.

## Stage 1: Shortlink

**Condition**: `USE_SHORTLINK` is `true` in config.json.

**Behavior**: URL sent to ShrinkMe API, replaced with shortened URL.

**Observable**:
- HTTP GET to `https://shrinkme.io/api?api=<key>&url=<original>`
- Response body (plain text) replaces original URL
- API key hard-coded in source

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| ShrinkMe down | Exception, run crashes |
| Invalid API key | Error response, shortlink fails |
| URL already short | Still shortened (no check) |
| ShrinkMe rate limit | Undefined |

**Example**:
```
Input:  https://example.com/very/long/article/title
Output: https://shrinkme.io/abc123
```

## Stage 2: Privacy Frontends

**Condition**: `USE_PRIVACY_FRONTENDS` is `true` in config.json.

**Behavior**: Known tracking domains replaced with privacy-respecting frontends.

**Observable**:
- Domain matching against hard-coded list
- URL rewritten with frontend domain
- Path and query preserved

**Supported Mappings**:
| Original Domain | Frontend | Notes |
|-----------------|----------|-------|
| `twitter.com` | `nitter.net` | Hard-coded |
| `x.com` | `nitter.net` | Hard-coded |
| `reddit.com` | Redlib instance | Hard-coded |
| `youtube.com` | Invidious instance | Hard-coded |
| `medium.com` | Scribe | Hard-coded |

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| Unknown domain | No transformation |
| Frontend down | Link broken (no fallback) |
| Subdomain (e.g., `www.twitter.com`) | May not match (exact domain check) |
| Already frontend URL | No transformation (idempotent) |

**Example**:
```
Input:  https://twitter.com/user/status/123456789
Output: https://nitter.net/user/status/123456789
```

## Stage 3: Cleanup (Tracking Parameters)

**Condition**: Always applied (no config toggle).

**Behavior**: Known tracking query parameters removed from URL.

**Observable**:
- URL parsed, query parameters inspected
- Known tracking parameters removed
- URL reconstructed without them

**Removed Parameters**:
| Parameter | Source |
|-----------|--------|
| `utm_source` | Google Analytics |
| `utm_medium` | Google Analytics |
| `utm_campaign` | Google Analytics |
| `utm_term` | Google Analytics |
| `utm_content` | Google Analytics |
| `utm_id` | Google Analytics |
| `fbclid` | Facebook |
| `gclid` | Google Ads |
| `msclkid` | Microsoft Ads |

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| No query string | No change |
| Only tracking params | Query string removed entirely |
| Mixed params | Only tracking params removed |
| Fragment (#) | Preserved |
| URL-encoded params | Decoded before check |

**Example**:
```
Input:  https://example.com/article?utm_source=twitter&utm_medium=social&id=123
Output: https://example.com/article?id=123
```

## Stage 4: Monetisation

**Condition**: `MONETISE_LINKS` is `true` in config.json (default: true).

**Behavior**: Affiliate/referral tags added to URLs.

**Observable**:
- URL matched against hard-coded affiliate program list
- Matching URLs get affiliate tag appended
- Non-matching URLs unchanged

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| URL already has affiliate tag | May duplicate (no check) |
| URL already has query string | Tag appended with `&` |
| URL has no query string | Tag appended with `?` |
| Unknown domain | No transformation |

**Example**:
```
Input:  https://example.com/product
Output: https://example.com/product?ref=affiliate123
```

## Combined Example

**Input**: `https://twitter.com/user/status/123456789?utm_source=feed&fbclid=abc`

**Processing**:
1. **Shortlink** (if enabled): `https://shrinkme.io/xyz789`
2. **Privacy frontend** (if enabled): No change (already shortened, domain not matched)
3. **Cleanup**: `https://shrinkme.io/xyz789` (no tracking params)
4. **Monetisation** (if enabled): No change (unknown domain)

**Final**: `https://shrinkme.io/xyz789`

**Note**: Shortening before privacy frontend means the frontend transformation may not apply (shortened URL hides original domain). This is a known interaction issue.

## Configuration Interactions

| USE_SHORTLINK | USE_PRIVACY_FRONTENDS | MONETISE_LINKS | Result |
|---------------|----------------------|----------------|--------|
| false | false | false | Original URL + cleanup only |
| true | false | false | Shortened + cleanup |
| false | true | false | Frontend + cleanup |
| false | false | true | Original + cleanup + affiliate |
| true | true | false | Shortened (frontend may not apply) |
| true | true | true | Shortened + affiliate (frontend may not apply) |
| false | true | true | Frontend + cleanup + affiliate |
| true | false | true | Shortened + cleanup + affiliate |

## Observable Behavior Summary

| Property | Value |
|----------|-------|
| **Deterministic** | Yes — same input URL → same output URL |
| **Idempotent** | Mostly — re-processing may add duplicate affiliate tags |
| **Reversible** | No — original URL lost after shortening |
| **Configurable** | Partially — 3 toggles, cleanup always on |
| **Logged** | No — transformations not logged |

## Edge Cases and Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Shortener hides original domain | Privacy frontend not applied | Disable shortlink, or reorder pipeline |
| Affiliate tag duplication | Ugly URL, possible tracking | Check for existing tag before appending |
| Frontend outage | Broken links | Disable privacy frontends |
| Shortener outage | Run crashes | Disable shortlink |
| Tracking param variations | Params not removed | Extend parameter list |

## Related Documentation

- [Configuration](./configuration.md) — Link processing toggles
- [Pipeline Flow](./flows/startup-and-rendering.md) — Link processing in pipeline context
- [Integrations](./integrations.md) — External services
- [Security](./security.md) — Privacy considerations
- [Ambiguities](./ambiguities-and-open-questions.md) — Undefined behaviors