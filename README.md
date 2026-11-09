# Usage

## Running in the background

### Using `systemd`

**Timer unit**:
```gitconfig
[Unit]
Description=Periodically activates the RSS bot for Mastodon

[Timer]
OnBootSec=15min
OnUnitActiveSec=25min

[Install]
WantedBy=timers.target
```

**Service unit**:
```gitconfig
[Unit]
Description=RSS bot for Mastodon
After=network.target

[Service]
WorkingDirectory=/home/horatiu/bots/mastodon-rss-bot
ExecStart=/bin/bash /home/horatiu/bots/mastodon-rss-bot/run.sh
User=horatiu
RuntimeMaxSec=60

[Install]
WantedBy=multi-user.target
```

## 🤝 Contributing

You are welcome to submit any suggestion, feedback, or modification to this project.

When doing so, please:
- Maintain cross-platform compatibility
- Submit focused pull requests that conform to the existing code style
- Maintain your branch synchronised with `master`
- Revise the documentation when functionality changes
- Raise a new [issue](https://github.com/hmlendea/mastodon-rss-bot/issues) for problems or suggestions

See the [Contributing Guidelines](./CONTRIBUTING.md) for details on how to report issues, suggest enhancements, and submit changes.

## 🛡️ Privacy and Data

Mastodon RSS Bot is a self-hosted command-line application that posts RSS feed entries to a Mastodon account. The operator controls all configuration, local storage, logs, backups, and access controls. The application has no built-in telemetry, update checks, or crash reports to project maintainers.

For the detailed description of how the application handles privacy and personal data, see the [Privacy Statement](./PRIVACY.md).

| Data | Purpose | Storage | Retention | Optional |
|------|---------|---------|-----------|----------|
| Command-line arguments and config.json | Operator configuration for feed, instance, and posting behaviour | Local files in working directory | Until operator deletes or overwrites | Yes |
| Mastodon access token and app credentials | Authentication to the operator's Mastodon instance | `app_<instance>.secret` in working directory | Until operator deletes or rotates | No |
| SQLite cache.db | Duplicate-post prevention (hashed entry ID, toot ID, feed URL, username, instance) | Local file in working directory | Until operator deletes | No |
| RSS feed content and linked pages | Source material for toots | Transient in memory during run | Not persisted by application | No |
| Console log output | Run-time status and debugging | Standard output | Not persisted by application | No |

# Credits
[cquest/tootbot](https://github.com/cquest/tootbot) the original script this bot is based on
