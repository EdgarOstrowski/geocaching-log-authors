# Geocaching Log Author Exporter

A Python script that logs in to geocaching.com, opens a cache page, and exports usernames from cache logs to a text file based on the selected log type.

The script uses Selenium with support for Firefox, Chrome, Edge, and Safari browsers, supports filtering by log type, and can optionally wait for manual reCAPTCHA completion during login.

When this script could be useful:
- You are preparing a geocaching event and want an attendance list of users who submitted a "Will attend" log.
- You want a list of users who submitted a "Found it" log for a specific geocache.

## Requirements

- Python 3.9+
- One of the following browsers installed: Firefox, Chrome, Edge, or Safari

## Notes and Limitations

> [!NOTE]
> This version was verified on geocaching.com on 2026-07-28.

- The script currently supports only the English version of geocaching.com.
- This script depends on current geocaching.com page structure and selectors, which may change.
- Login challenges are controlled by the website and may not appear consistently.
- Manual reCAPTCHA mode avoids automated challenge solving and keeps the user in control.
- Webdrivers are automatically downloaded and managed by `webdriver-manager`. On first use, the appropriate driver for your chosen browser will be downloaded.
- Safari support requires macOS and may have platform-specific considerations.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

The script supports credentials from a local `.env` file:

```env
GC_USERNAME=your_username
GC_PASSWORD=your_password
```

You can also set these values as environment variables.

If either value is missing, the script prompts you interactively.

## Usage

Basic usage with default browser (Firefox):

```bash
python get_gc_logs_authors.py --gccode GCXXXXXX
```

Use a different browser:

```bash
python get_gc_logs_authors.py --gccode GCXXXXXX --browser chrome
python get_gc_logs_authors.py --gccode GCXXXXXX --browser edge
python get_gc_logs_authors.py --gccode GCXXXXXX --browser safari
```

Filter by log type:

```bash
python get_gc_logs_authors.py --gccode GCXXXXXX --log_type "Will attend"
```

Use manual reCAPTCHA fallback:

```bash
python get_gc_logs_authors.py --gccode GCXXXXXX --manual-captcha
```

Increase manual wait timeout to 5 minutes:

```bash
python get_gc_logs_authors.py --gccode GCXXXXXX --manual-captcha --captcha-wait-seconds 300
```

## CLI Options

- `--gccode` (required): Cache GC code, for example `GCXXXXXX`
- `--output`: Output filename (default: `<GCCODE>.txt`)
- `--browser`: Browser to use: `firefox`, `chrome`, `edge`, or `safari` (default: `firefox`)
- `--log_type`: Filter by log type
- `--manual-captcha`: Enable manual reCAPTCHA fallback if login does not complete automatically
- `--captcha-wait-seconds`: Seconds to wait for manual completion when `--manual-captcha` is enabled (default: `180`)

Supported `--log_type` values:

- Announcement
- Attended
- Didn't find it
- Enable listing
- Found it
- Owner maintenance
- Post reviewer note
- Temporarily disable listing
- Update coordinates
- Will attend
- Write note

## How Manual reCAPTCHA Fallback Works

When `--manual-captcha` is enabled:

1. The script submits your username and password normally.
2. If login does not leave the sign-in page within the default wait window, it assumes there may be a challenge (such as reCAPTCHA).
3. It prompts you in the terminal and waits for you to complete the challenge in the browser.
4. Once sign-in completes (URL changes away from `/account/signin`), execution continues.

If the timeout expires, Selenium raises a timeout exception.

## Output

The output file contains one username per line, deduplicated and sorted case-insensitively.
