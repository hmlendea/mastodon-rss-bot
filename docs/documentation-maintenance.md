# Documentation Maintenance

## Overview

This document describes how to maintain the documentation in the `docs/` directory: structure, conventions, update procedures, and quality standards.

## Documentation Structure

```
docs/
├── INDEX.md                          # Master index and navigation
├── architecture.md                   # System architecture
├── repository-overview.md            # High-level repository summary
├── repository-structure.md           # File tree and module descriptions
├── configuration.md                  # Configuration reference
├── data-model.md                     # Database schema
├── dependencies.md                   # External dependencies
├── flows/
│   ├── startup-and-rendering.md      # Pipeline flow
│   ├── calendar-search.md            # (Placeholder)
│   └── detail-mutation.md            # (Placeholder)
├── components/
│   ├── host-and-composition.md       # Entry point and composition
│   ├── application-services.md       # Core services
│   ├── browser-state-and-localisation.md  # (Placeholder)
│   ├── integration-models.md         # External integrations
│   └── presentation.md               # Output formatting
├── api-reference/
│   ├── INDEX.md                      # API reference index
│   ├── main-pipeline.md              # main.py functions
│   └── extensions.md                 # Extension interfaces
├── logging.md                        # Logging requirements
├── error-handling.md                 # Error handling patterns
├── testing.md                        # Testing strategy
├── security.md                       # Security considerations
├── build-and-deployment.md           # Deployment guide
├── change-guide.md                   # Change process
├── concurrency-and-scheduling.md     # Concurrency model
├── state-and-persistence.md          # State management
├── design-decisions.md               # Design decision records
├── api-usage-examples.md             # Code examples
├── ambiguities-and-open-questions.md # Unresolved items
├── faq.md                            # Frequently asked questions
├── troubleshooting.md                # Issue resolution
├── documentation-maintenance.md      # This file
├── invariants.md                     # System invariants
├── integrations.md                   # External integrations
└── quick-start.md                    # Getting started guide
```

## Naming Conventions

| Rule | Example |
|------|---------|
| Kebab-case filenames | `build-and-deployment.md` |
| Lowercase only | `api-reference/` not `API-Reference/` |
| Descriptive names | `error-handling.md` not `errors.md` |
| Singular for concepts | `configuration.md` not `configurations.md` |
| Plural for collections | `dependencies.md` not `dependency.md` |

## Content Standards

### Required Sections

Every document should include:

1. **Overview** — Purpose and scope
2. **Main content** — Organized with clear headings
3. **Related Documentation** — Links to related docs

### Formatting

- Use ATX headings (`#`, `##`, `###`)
- Tables for structured data
- Code blocks with language hints
- Mermaid diagrams for architecture/flows
- Bold for emphasis, not italics
- Repository-relative links (e.g., `./configuration.md`)

### Link Validation

Before committing, verify all links:

```bash
# Check for broken links (requires markdown-link-check)
npx markdown-link-check docs/**/*.md
```

Or manually verify key links.

## Update Procedures

### When to Update Documentation

| Trigger | Documents to Update |
|---------|---------------------|
| New feature | Relevant component/flow/API docs, INDEX.md |
| Configuration change | `configuration.md`, `configuration.md` |
| Schema change | `data-model.md`, `state-and-persistence.md` |
| New dependency | `dependencies.md`, `architecture.md` |
| Architecture change | `architecture.md`, affected component docs |
| New extension point | `api-reference/extensions.md`, `components/application-services.md` |
| Security fix | `security.md`, `build-and-deployment.md` |
| Deployment change | `build-and-deployment.md`, `quick-start.md` |

### Update Process

1. **Identify affected documents** using the trigger table
2. **Make changes** following content standards
3. **Update INDEX.md** if new documents added or structure changed
4. **Verify links** work correctly
5. **Review for consistency** with existing docs
6. **Commit with descriptive message**: `docs: update configuration for new feature X`

### INDEX.md Maintenance

The `INDEX.md` is the master navigation document. Update it when:

- Adding new documents → Add to appropriate section
- Removing documents → Remove from index
- Renaming documents → Update link and text
- Restructuring → Reorganize sections

**INDEX.md Sections**:
1. Repository Summary
2. Root Document Map
3. Documentation Catalogue (by category)
4. Navigation Aids
5. Maintenance Metadata

## Quality Checks

### Automated Checks

```bash
# 1. Link validation
npx markdown-link-check docs/**/*.md

# 2. Spell check (optional)
npx cspell docs/**/*.md

# 3. Markdown lint
npx markdownlint docs/**/*.md
```

### Manual Reviews

| Check | Frequency |
|-------|-----------|
| All links resolve | On change |
| Code examples run | On change |
| Diagrams render | On change |
| Cross-references accurate | Quarterly |
| Outdated content flagged | Quarterly |

## Versioning

Documentation is versioned with the code (same repository, same commits).

**No separate versioning** — docs reflect the current `main` branch state.

For released versions, tag the commit: `git tag v1.2.3` includes docs at that version.

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) and [Change Guide](./change-guide.md#documentation-changes).

### Documentation PR Checklist

- [ ] Follows naming conventions
- [ ] Includes Overview and Related Documentation
- [ ] Uses repository-relative links
- [ ] Code examples tested
- [ ] Links verified
- [ ] INDEX.md updated if needed
- [ ] No broken cross-references

## Tools

### Recommended Tooling

| Tool | Purpose | Install |
|------|---------|---------|
| `markdown-link-check` | Validate links | `npm install -g markdown-link-check` |
| `markdownlint` | Lint markdown | `npm install -g markdownlint-cli` |
| `cspell` | Spell check | `npm install -g cspell` |
| `mermaid-cli` | Render diagrams | `npm install -g @mermaid-js/mermaid-cli` |

### VS Code Extensions

- Markdown All in One
- Markdown Preview Mermaid Support
- markdownlint
- Code Spell Checker

## Metrics

### Documentation Health Indicators

| Metric | Target | Measurement |
|--------|--------|-------------|
| Link validity | 100% | Automated check |
| Coverage (public APIs) | 100% | Manual review |
| Example correctness | 100% | Test execution |
| Freshness (days since update) | < 90 | Git log |

### Reporting

Include documentation status in release notes:
- New documents added
- Major updates
- Known gaps

## Related Documentation

- [Change Guide](./change-guide.md#documentation-changes) — Change process
- [INDEX.md](./INDEX.md) — Master index
- [Architecture](./architecture.md) — System context
- [GitHub Markdown Instructions](vscode-userdata:/home/horatiu/.config/Code%20-%20OSS/User/prompts/instructions/github/github.markdown.instructions.md) — Formatting rules