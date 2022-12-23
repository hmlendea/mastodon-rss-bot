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

# Credits
[cquest/tootbot](https://github.com/cquest/tootbot) the original script this bot is based on
