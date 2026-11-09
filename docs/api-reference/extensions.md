# API Reference: Extensions

## Overview

This document describes the extension interfaces available in mastodon-rss-bot. Extensions are optional Python modules that can be placed alongside the main application to customize behavior without modifying core code.

## Extension Discovery

Extensions are loaded via `utils.try_import()` at runtime:

```python
# utils.py
def try_import(module_name):
    try:
        return __import__(module_name)
    except ImportError:
        return None
```

**Loading behavior**:
- Import attempted once at module load time
- Returns module object or `None`
- No error if missing (graceful degradation)
- No version checking
- No reloading mechanism

## Available Extension Points

### 1. Dynamic Tags (`dynamic_tags.py`)

**Purpose**: Generate tags dynamically based on entry content.

**Interface**:
```python
# dynamic_tags.py
def get_dynamic_tags(entry, config):
    """
    Generate tags for a feed entry.

    Args:
        entry: feedparser entry object
        config: dict of configuration values

    Returns:
        list[str]: List of tag strings (without # prefix)
    """
    # Implementation here
    return []
```

**Integration Point** (in `main.py`):
```python
dynamic_tags_module = try_import("dynamic_tags")
if dynamic_tags_module:
    dynamic_tags = dynamic_tags_module.get_dynamic_tags(entry, config)
    tags.extend(dynamic_tags)
```

**Input Data** (`entry` object):
| Attribute | Type | Description |
|-----------|------|-------------|
| `entry.title` | str | Entry title |
| `entry.link` | str | Entry URL |
| `entry.summary` | str | Entry summary/description |
| `entry.published` | str | Publication date string |
| `entry.tags` | list | Feed-provided tags (if any) |
| `entry.author` | str | Entry author (if any) |

**Input Data** (`config` dict):
| Key | Type | Description |
|-----|------|-------------|
| All config keys | various | See [Configuration](./configuration.md) |

**Return Value**:
- List of tag strings (e.g., `["tech", "news", "ai"]`)
- Tags are appended to `--tags-to-add` and feed tags
- Duplicate tags are not deduplicated (Mastodon handles it)
- Empty list = no additional tags

**Example Implementation**:
```python
# dynamic_tags.py
def get_dynamic_tags(entry, config):
    tags = []

    # Tag based on domain
    from urllib.parse import urlparse
    domain = urlparse(entry.link).netloc
    if "github.com" in domain:
        tags.append("github")
    elif "youtube.com" in domain:
        tags.append("video")

    # Tag based on title keywords
    title_lower = entry.title.lower()
    if "security" in title_lower:
        tags.append("security")
    if "release" in title_lower:
        tags.append("release")

    return tags
```

**Constraints**:
- Must be pure function (no side effects)
- Must not raise exceptions (caught by caller)
- Must return list of strings
- Execution time adds to per-entry latency

---

### 2. Text Replacements (`text_replacements.py`)

**Purpose**: Apply custom text transformations to entry content before posting.

**Interface**:
```python
# text_replacements.py
def apply_replacements(text, config):
    """
    Apply custom text replacements.

    Args:
        text: str - The assembled status text
        config: dict - Configuration values

    Returns:
        str: Modified text
    """
    # Implementation here
    return text
```

**Integration Point** (in `main.py`):
```python
text_replacements_module = try_import("text_replacements")
if text_replacements_module:
    entry_text = text_replacements_module.apply_replacements(entry_text, config)
```

**Input Data**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | str | Fully assembled status text (after all built-in processing) |
| `config` | dict | Configuration values |

**Return Value**:
- Modified text string
- Returned text replaces the assembled text
- Must not exceed 500 characters (truncation happens after)

**Example Implementation**:
```python
# text_replacements.py
import re

def apply_replacements(text, config):
    # Replace common abbreviations
    replacements = {
        r"\bAI\b": "Artificial Intelligence",
        r"\bML\b": "Machine Learning",
        r"\bAPI\b": "Application Programming Interface",
    }

    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)

    # Add custom footer
    if config.get("add_footer"):
        text += "\n\n#bot #automated"

    return text
```

**Constraints**:
- Must be pure function (no side effects)
- Must not raise exceptions
- Must return string
- Applied after all built-in processing (links, tags, etc.)
- Truncation to 500 chars happens AFTER replacements

---

## Extension Development Guide

### Creating an Extension

1. Create Python file in project root:
   ```
   mastodon-rss-bot/
   ├── main.py
   ├── dynamic_tags.py      # Your extension
   └── text_replacements.py # Your extension
   ```

2. Implement the required function signature

3. Test by running the bot:
   ```bash
   python main.py --rss ... --instance ...
   ```

### Extension Best Practices

| Practice | Reason |
|----------|--------|
| Keep functions pure | Predictable, testable, no side effects |
| Handle missing data gracefully | Entry fields may be absent |
| Use config for customization | Avoid hard-coding values |
| Log via print() | Consistent with main app |
| Keep fast | Runs per entry, adds latency |
| Document assumptions | Future maintainers need context |

### Extension Testing

```python
# test_dynamic_tags.py
from dynamic_tags import get_dynamic_tags

def test_github_tag():
    entry = type('Entry', (), {
        'title': 'New Release',
        'link': 'https://github.com/user/repo/releases/tag/v1.0',
        'summary': '',
        'published': '2024-01-01',
        'tags': [],
        'author': ''
    })()

    config = {}
    tags = get_dynamic_tags(entry, config)
    assert "github" in tags
```

### Extension Distribution

Extensions are not packaged or distributed. They are local files in the deployment directory.

**Deployment**:
```bash
# Copy extension files to deployment directory
cp dynamic_tags.py text_replacements.py /opt/mastodon-rss-bot/
```

**Version Control**:
- Extensions can be in same repo (alongside main.py)
- Or in separate repo (copied during deployment)
- No plugin registry or marketplace

---

## Extension API Reference

### `utils.try_import(module_name)`

**Signature**:
```python
def try_import(module_name: str) -> Optional[ModuleType]
```

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `module_name` | str | Module name (without .py extension) |

**Returns**:
| Type | Description |
|------|-------------|
| ModuleType | Imported module object |
| None | Import failed (module not found) |

**Behavior**:
- Catches `ImportError` only
- Other exceptions propagate
- No caching (re-imports on each call, but called once at module load)

**Usage in main.py**:
```python
dynamic_tags_module = try_import("dynamic_tags")
text_replacements_module = try_import("text_replacements")
```

---

## Future Extension Points (Proposed)

| Extension Point | Purpose | Status |
|-----------------|---------|--------|
| `media_filters.py` | Custom media selection/filtering | Proposed |
| `link_transformers.py` | Additional link transformations | Proposed |
| `pre_post_hooks.py` | Callbacks before/after posting | Proposed |
| `feed_preprocessors.py` | Modify feed before entry iteration | Proposed |
| `language_detectors.py` | Custom language detection | Proposed |

**Proposal Process**: See [Change Guide](./change-guide.md#adding-a-new-extension-point)

---

## Related Documentation

- [API Reference Index](./api-reference/INDEX.md) — All API references
- [Main Pipeline](./api-reference/main-pipeline.md) — Core pipeline API
- [Application Services](./components/application-services.md) — Extension integration
- [Change Guide](./change-guide.md) — Adding extension points
- [Configuration](./configuration.md) — Config available to extensions