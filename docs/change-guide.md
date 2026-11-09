# Change Guide

## Overview

This document provides guidance for making changes to the mastodon-rss-bot codebase: development workflow, change categories, testing requirements, and release procedures.

## Development Workflow

### Local Development

```bash
# 1. Clone and setup
git clone <repository-url>
cd mastodon-rss-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Create test configuration
cp sample.config.json config.json
# Edit config.json for local testing

# 3. Run with test feed
python main.py --rss https://example.com/test-feed.xml \
  --instance mastodon.social \
  --username test@example.com \
  --access-token "$TEST_TOKEN" \
  --days-to-check 1
```

### Change Categories

| Category | Description | Review Required | Testing Required |
|----------|-------------|-----------------|------------------|
| **Bug fix** | Correct incorrect behavior | Yes | Unit + integration |
| **Feature** | New functionality | Yes | Unit + integration + e2e |
| **Refactor** | Code structure improvement | Yes | Unit (regression) |
| **Config** | New/changed configuration | Yes | Unit |
| **Dependency** | Add/update/remove package | Yes | Full test suite |
| **Documentation** | Docs only | Light | None |
| **Security** | Vulnerability fix | Yes (urgent) | Full test suite |

### Branch Strategy

```
main (protected)
  ├── feature/<name>     # New features
  ├── fix/<name>         # Bug fixes
  ├── refactor/<name>    # Refactoring
  ├── security/<name>    # Security fixes
  └── docs/<name>        # Documentation
```

**Rules**:
- All changes via pull request
- `main` branch protected (no direct push)
- CI must pass before merge
- Squash merge preferred

## Making Changes

### 1. Configuration Changes

**Files**: `sample.config.json`, `config.py`, `configuration.md`

**Process**:
1. Add key to `sample.config.json` with default value
2. Update `config.py` to extract key with `.get(key, default)`
3. Update `configuration.md` with key documentation
4. Add unit test for new config key

**Example**:
```json
// sample.config.json
{
  "new_feature_enabled": true
}
```

```python
# config.py
NEW_FEATURE_ENABLED = config.get("new_feature_enabled", True)
```

### 2. Core Logic Changes (`main.py`)

**Areas**:
- Feed parsing
- Entry processing loop
- Media handling
- Link processing
- Status assembly
- Mastodon API calls

**Requirements**:
- Add unit tests for pure functions
- Add integration tests for pipeline changes
- Update flow documentation (`docs/flows/`)
- Update component documentation (`docs/components/`)

**Testing**:
```bash
# Run unit tests
pytest tests/unit/test_main.py -v

# Run integration tests
pytest tests/integration/test_pipeline.py -v
```

### 3. Database Changes (`database.py`)

**Schema Changes**:
1. Create migration script (no migration framework exists)
2. Update `init_db()` with new schema
3. Handle backward compatibility
4. Update `data-model.md`

**Example Migration**:
```python
def migrate_v1_to_v2(db):
    cursor = db.cursor()
    cursor.execute("ALTER TABLE entries ADD COLUMN entry_summary TEXT")
    db.commit()
```

### 4. Utility Changes (`utils.py`)

**Functions**:
- `detect_language()`
- `try_import()`

**Requirements**:
- Pure functions only (no side effects)
- Comprehensive unit tests
- No external dependencies

### 5. Dependency Changes

**Adding Dependency**:
1. Add to `requirements.txt` with pinned version
2. Update `dependencies.md` with integration boundary
3. Run `pip-audit` on new dependency
4. Add to CI dependency scanning

**Updating Dependency**:
1. Update version in `requirements.txt`
2. Run full test suite
3. Check for breaking changes
4. Update `dependencies.md` if interface changed

**Removing Dependency**:
1. Verify no imports in codebase
2. Remove from `requirements.txt`
3. Update `dependencies.md`
4. Run full test suite

### 6. Documentation Changes

**Files**: All `.md` files in `docs/` and root

**Requirements**:
- Follow [GitHub Markdown Instructions](vscode-userdata:/home/horatiu/.config/Code%20-%20OSS/User/prompts/instructions/github/github.markdown.instructions.md)
- Verify repository-relative links
- Update `INDEX.md` if adding new documents
- Update `ARCHITECTURE.md` if architecture changes

## Testing Requirements

### Pre-Commit Checklist

- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Coverage maintained or improved
- [ ] No new linting errors
- [ ] Documentation updated

### Test Commands

```bash
# Full test suite
pytest tests/ --cov=. --cov-report=term-missing

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Specific module
pytest tests/unit/test_config.py -v

# With coverage threshold
pytest tests/ --cov=. --cov-fail-under=80
```

### Test Data

Use standard test values from [test-values standards](vscode-userdata:/home/horatiu/.config/Code%20-%20OSS/User/prompts/instructions/common/common.test-values.instructions.md):

| Category | Value |
|----------|-------|
| Username | `IlarionPintilie` |
| Author | `Ilarion Pintilie` |
| Feed URL | `https://example.com/feed.xml` |
| Instance | `mastodon.social` |
| Days to check | `7` |

## Release Procedure

### Versioning

**Scheme**: Semantic Versioning (MAJOR.MINOR.PATCH)

| Change Type | Version Bump |
|-------------|--------------|
| Breaking change | MAJOR |
| New feature (backward compatible) | MINOR |
| Bug fix | PATCH |
| Security fix | PATCH (or MINOR if breaking) |

### Release Steps

1. **Update version** in `pyproject.toml` (future) or tag
2. **Update CHANGELOG.md** (future) with release notes
3. **Run full test suite** including integration
4. **Create release tag**: `git tag v1.2.3`
5. **Push tag**: `git push origin v1.2.3`
6. **GitHub Release** created automatically (future workflow)
7. **Deploy** to production (manual or CI)

### Release Notes Template

```markdown
## v1.2.3 - YYYY-MM-DD

### Added
- New feature X

### Changed
- Modified behavior Y

### Fixed
- Bug Z

### Security
- Vulnerability fix

### Dependencies
- Updated package A to vX.Y.Z
```

## Code Review Guidelines

### Reviewer Checklist

- [ ] Change matches issue/requirement
- [ ] Tests added/updated appropriately
- [ ] Documentation updated
- [ ] No hard-coded secrets
- [ ] No sensitive data in logs
- [ ] Error handling follows [error-handling.md](./error-handling.md)
- [ ] Logging follows [logging.md](./logging.md)
- [ ] Security considerations addressed
- [ ] Performance impact assessed
- [ ] Backward compatibility maintained

### Author Responsibilities

- [ ] Self-review before requesting review
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] Branch up to date with `main`

## Common Change Patterns

### Adding a New Feed Source Type

1. Add detection logic in entry loop
2. Add media collection function
3. Add unit tests
4. Update `dependencies.md` if new library needed
5. Update `integration-models.md`

### Adding a New Link Transformation

1. Add to link processing pipeline in `main.py`
2. Make configurable via `config.json`
3. Add unit tests
4. Update `configuration.md`
5. Update `application-services.md`

### Adding a New Mastodon API Feature

1. Add to status posting logic
2. Handle API errors per [error-handling.md](./error-handling.md)
3. Add integration test with mocked API
4. Update `integration-models.md`

### Modifying the Cache Schema

1. Create migration function in `database.py`
2. Update `init_db()` for new installs
3. Handle both old and new schemas
4. Update `data-model.md`
5. Add integration test for migration

## Rollback Procedures

### Code Rollback

```bash
# Revert specific commit
git revert <commit-hash>

# Reset to previous tag
git checkout v1.2.2
```

### Configuration Rollback

```bash
# Restore previous config
cp config.json.backup config.json
```

### Database Rollback

```bash
# Restore from backup
sqlite3 cache.db ".restore cache.db.backup"
```

## Related Documentation

- [Architecture](./architecture.md) — System context for changes
- [Testing](./testing.md) — Test requirements
- [Error Handling](./error-handling.md) — Error handling patterns
- [Logging](./logging.md) — Logging requirements
- [Security](./security.md) — Security considerations
- [Dependencies](./dependencies.md) — Dependency management
- [Build and Deployment](./build-and-deployment.md) — Deployment impact