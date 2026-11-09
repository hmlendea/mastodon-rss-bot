# Mastodon RSS Bot Documentation

## Repository summary

Mastodon RSS Bot is a self-hosted Python command-line application that fetches RSS feed entries and posts them to a Mastodon account. It runs as a scheduled batch pipeline: fetch feed, identify new entries within a configurable age window, enrich each entry with linked-page metadata and media, apply language-aware text transformations, and post the result through the Mastodon API while preventing duplicates.

## Root document map

- [ARCHITECTURE.md](../ARCHITECTURE.md) — High-level architecture, system context, components, data architecture, interfaces, toot construction, cross-cutting concerns, dependencies, deployment, compatibility contracts, testing, design constraints, and extension points
- [SECURITY.md](../SECURITY.md) — Security policy, supported versions, vulnerability reporting, scope, and disclosure policy
- [PRIVACY.md](../PRIVACY.md) — Privacy and personal data handling, self-hosted deployments, data categories, processing, storage, external integrations, data protection, and contact
- [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) — Community conduct standards, expected and unacceptable conduct, participation and moderation, reporting, and enforcement
- [LICENSE](../LICENSE) — GNU General Public License Version 3 or later
- [CONTRIBUTING.md](../CONTRIBUTING.md) — Contribution guidelines, issue reporting, enhancement suggestions, code contributions, code style, and documentation
- [README.md](../README.md) — Usage, systemd deployment, configuration, privacy data table, architecture overview, credits, code of conduct, and security

## Documentation catalogue

### Architecture and overview

- [architecture.md](./architecture.md) — Detailed architecture complementing root ARCHITECTURE.md with implementation-level detail
- [repository-overview.md](./repository-overview.md) — Repository purpose, scope, entry points, and high-level capabilities
- [repository-structure.md](./repository-structure.md) — Source tree layout, module organisation, and file responsibilities

### Configuration and data

- [configuration.md](./configuration.md) — Configuration schema, sources, precedence, and runtime behaviour
- [data-model.md](./data-model.md) — Domain entities, relationships, persistence schema, and state lifecycle
- [dependencies.md](./dependencies.md) — External and internal dependencies with integration boundaries

### Components and flows

- [components/presentation.md](./components/presentation.md) — Main pipeline orchestration, feed parsing, entry iteration, and toot construction
- [components/host-and-composition.md](./components/host-and-composition.md) — Process topology, scheduling, runtime limits, and execution identity
- [components/application-services.md](./components/application-services.md) — Configuration loading, database persistence, and utility services
- [components/browser-state-and-localisation.md](./components/browser-state-and-localisation.md) — Language detection, text replacements, and dynamic tags
- [components/integration-models.md](./components/integration-models.md) — RSS feed, linked pages, Mastodon API, and privacy frontends integration contracts

- [flows/startup-and-rendering.md](./flows/startup-and-rendering.md) — Process startup, configuration load, client initialisation, and feed retrieval
- [flows/calendar-search.md](./flows/calendar-search.md) — Entry iteration, deduplication, age filtering, and enrichment
- [flows/detail-mutation.md](./flows/detail-mutation.md) — Media upload, toot assembly, posting, and cache persistence

### API reference

- [api-reference/INDEX.md](./api-reference/INDEX.md) — API reference index with endpoint summary table
- [api-reference/main-pipeline.md](./api-reference/main-pipeline.md) — Main pipeline orchestration endpoints (CLI arguments, config, database, Mastodon API)
- [api-reference/extensions.md](./api-reference/extensions.md) — Extension interfaces (dynamic_tags, text_replacements)

### Cross-cutting concerns

- [design-decisions.md](./design-decisions.md) — Key architectural and design choices with rationale
- [error-handling.md](./error-handling.md) — Error taxonomy, handling patterns, recovery strategies, and failure semantics
- [logging.md](./logging.md) — Logging framework, levels, structured fields, correlation, sinks, redaction, retention, sampling, performance, error logging, audit logging, and configuration
- [security.md](./security.md) — Security model, threats, mitigations, and secrets management (complements root SECURITY.md)
- [state-and-persistence.md](./state-and-persistence.md) — State management, SQLite cache, migrations, and backup
- [testing.md](./testing.md) — Test strategy, organisation, coverage gaps, and manual verification procedures
- [concurrency-and-scheduling.md](./concurrency-and-scheduling.md) — Threading, async, schedulers, locks, and resource use
- [build-and-deployment.md](./build-and-deployment.md) — Build pipeline, deployment, environments, and systemd integration
- [change-guide.md](./change-guide.md) — How to modify common areas safely with impact analysis

### Reference and support

- [api-usage-examples.md](./api-usage-examples.md) — Example requests and responses for CLI usage and Mastodon API interaction
- [ambiguities-and-open-questions.md](./ambiguities-and-open-questions.md) — Unresolved items, TODOs, known gaps, and areas needing investigation
- [faq.md](./faq.md) — Frequently asked questions
- [troubleshooting.md](./troubleshooting.md) — Common issues and solutions
- [documentation-maintenance.md](./documentation-maintenance.md) — How to keep docs current, ownership, and review cadence
- [invariants.md](./invariants.md) — System-wide invariants and contracts
- [integrations.md](./integrations.md) — External system integrations detail
- [quick-start.md](./quick-start.md) — Getting started guide for newcomers
- [behaviour/entry-processing.md](./behaviour/entry-processing.md) — Entry selection, filtering, enrichment, and posting behavior
- [behaviour/link-processing.md](./behaviour/link-processing.md) — Link transformation pipeline behavior
- [behaviour/media-handling.md](./behaviour/media-handling.md) — Media collection, download, upload, and attachment behavior

## Navigation aids

- **Start here** (newcomers): [quick-start.md](./quick-start.md) → [repository-overview.md](./repository-overview.md) → [configuration.md](./configuration.md)
- **Deep dive** (component owners): [components/](./components/) → [flows/](./flows/) → [data-model.md](./data-model.md)
- **Flows** (debuggers): [flows/startup-and-rendering.md](./flows/startup-and-rendering.md) → [flows/calendar-search.md](./flows/calendar-search.md) → [flows/detail-mutation.md](./flows/detail-mutation.md)

## Maintenance metadata

- Last reviewed: 2026-11-09
- Owner: Repository maintainers
- Coverage status: Initial generation from repository reverse engineering