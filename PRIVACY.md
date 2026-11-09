# Privacy and Personal Data

This document describes how Mastodon RSS Bot, a self-hosted command-line application that posts RSS feed entries to a Mastodon account, handles personal data. The application is operated by the user who runs it; no hosted service is provided by the project maintainers.

## 📑 Table of Contents

- [🔎 What This Document Covers](#-what-this-document-covers)
- [🏠 Self-Hosted Deployments](#-self-hosted-deployments)
- [📥 Data We Handle](#-data-we-handle)
  - [Data Provided to the Application](#data-provided-to-the-application)
  - [Data Generated or Collected by the Application](#data-generated-or-collected-by-the-application)
  - [Data Received from Integrations](#data-received-from-integrations)
- [🧭 Processing and Use](#-processing-and-use)
- [🗄️ Storage, Retention, and Deletion](#-storage-retention-and-deletion)
- [🔗 External Processing and Integrations](#-external-processing-and-integrations)
- [🛡️ Data Protection and Security](#-data-protection-and-security)
- [🔄 Document Changes](#-document-changes)
- [📬 Contact](#-contact)

## 🔎 What This Document Covers

This document describes how Mastodon RSS Bot at https://github.com/hmlendea/mastodon-rss-bot manages personal data. It covers the application conduct and verified integrations described below. Where the software is self-hosted, the instance operator may have separate responsibilities described below.

## 🏠 Self-Hosted Deployments

This document covers both the project maintainers and self-hosted operators. The application is designed to be run by the operator on their own infrastructure, and the operator controls their deployment's configuration, local storage, logs, backups, access controls, preservation, and request handling.

The application has no built-in telemetry, update checks, crash reports, email, authentication, reverse-proxy, object-storage, or monitoring integrations that transmit data to the project maintainers. The only outbound network activity is the operator-configured retrieval of RSS feeds and linked pages, the interaction with the operator's chosen Mastodon instance, and the optional link monetisation and privacy-frontend rewrites described below.

## 📥 Data We Handle

### Data Provided to the Application

- Command-line arguments supplied by the operator: the RSS feed URL, the Mastodon instance URL, the Mastodon username, the Mastodon access token, the tags to add, and the number of days to check.
- The operator's `config.json` file, created from `sample.config.json`, which controls whether the author, link, and link thumbnail are included, whether privacy frontends and shortlinks are used, whether links are monetised, and the maximum number of toots per run.
- The Mastodon application credentials stored in `app_<instance>.secret`, created by the application on first run.

### Data Generated or Collected by the Application

- The local SQLite database `cache.db`, which stores the hashed feed entry identifier, the resulting toot identifier, the RSS feed URL, the Mastodon username, and the Mastodon instance for each posted entry.
- Standard output log messages printed to the console during a run, including feed entry identifiers, dates, ages, and processing status.

### Data Received from Integrations

- The RSS feed content retrieved from the operator-supplied feed URL, including entry titles, summaries, links, authors, and media enclosures.
- The linked page content retrieved for each feed entry when the link thumbnail is enabled, including the page title, Open Graph image, and shortlink.
- No personal data is received from the project maintainers or from any third-party service beyond the operator-configured sources above.

## 🧭 Processing and Use

The application processes the data described above for these verified functions:
- RSS feed retrieval and entry parsing — RSS feed URL, entry titles, summaries, links, authors, and media enclosures
- Duplicate-post prevention — hashed feed entry identifier, toot identifier, RSS feed URL, Mastodon username, and Mastodon instance stored in `cache.db`
- Mastodon authentication and posting — Mastodon instance URL, Mastodon username, Mastodon access token, and the application credentials in `app_<instance>.secret`
- Media upload — linked page thumbnails, feed media enclosures, and Twitter or Reddit media URLs rewritten to privacy frontends
- Link rewriting and monetisation — feed entry links rewritten to privacy frontends or shortlinks, and optionally routed through the ShrinkMe monetisation service when `monetise_links` is enabled
- Content shortening — entry titles and bodies shortened to fit the 500-character Mastodon limit

## 🗄️ Storage, Retention, and Deletion

All application data is stored locally in the operator's working directory. The SQLite database `cache.db` retains one row per posted feed entry, containing the hashed entry identifier, the toot identifier, the RSS feed URL, the Mastodon username, and the Mastodon instance. The Mastodon application credentials are stored in `app_<instance>.secret`. The operator controls storage, deletion, and backups for these files. The application does not delete `cache.db` entries automatically; the operator may remove the file to reset the posting history.

## 🔗 External Processing and Integrations

The application transmits data to the following external services when the corresponding operator configuration is active:

| Service or integration | Purpose | Data involved | Configuration or documentation |
|-----------------------|---------|---------------|--------------------------------|
| The operator's Mastodon instance | Authentication and posting of toots and media | Mastodon username, access token, toot body, media files, and the configured tags | Mastodon API documentation at https://docs.joinmastodon.org/ |
| RSS feed host | Retrieval of feed entries | The operator-supplied feed URL | Operator-provided feed URL |
| Linked page host | Retrieval of page titles, Open Graph images, and shortlinks | The feed entry link URL | Operator-supplied feed entry links |
| Nitter, Libreddit, and YouTube frontends | Privacy-frontend link rewriting when `use_privacy_frontends` is enabled | Rewritten feed entry links | `sample.config.json` setting `use_privacy_frontends` |
| ShrinkMe | Link monetisation when `monetise_links` is enabled | The rewritten feed entry link URL | `sample.config.json` setting `monetise_links` |

The application has no built-in external data transfer beyond the operator-configured flows above.

## 🛡️ Data Protection and Security

The application stores the Mastodon access token and application credentials in local files within the operator's working directory and transmits them only to the operator's chosen Mastodon instance over HTTPS. The operator is responsible for restricting access to the working directory, the `cache.db` database, the `app_<instance>.secret` file, and the `config.json` file, and for keeping the application and its dependencies updated. The application does not promise absolute security.

The original maintainers are not responsible for changes, modifications, or privacy issues introduced by downstream forks.

## 🔄 Document Changes

Update this document when application data processes, storage, integrations, or deployment responsibilities change. The current version is published at https://github.com/hmlendea/mastodon-rss-bot/blob/master/PRIVACY.md.

## 📬 Contact

For questions about application data handling, contact the project maintainers. For a self-hosted deployment, contact the instance operator, unless the project explicitly manages the request. Include the deployment URL or the relevant feed entry identifier; do not send passwords, access tokens, or other secrets.