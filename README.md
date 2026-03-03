# missile-alert

Updates your Slack status when a Tseva Adom (Red Alert) is detected in Israel. Restores your previous status 10 minutes after the last alert.

## Setup

### 1. Create a Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From scratch**
2. Under **OAuth & Permissions**, add these **User Token Scopes**:
   - `users.profile:read`
   - `users.profile:write`
3. Click **Install to Workspace** and copy the `xoxp-...` token

### 2. Configure

```bash
cp .env.example .env
# Edit .env and paste your token
```

### 3. Run

```bash
uv run --env-file .env missile_alert.py
```

## Options

```
--city "תל אביב"   Only trigger for alerts in a specific city (Hebrew name)
--test-alert       Set the alert status and exit (for testing)
--test-clear       Restore previous status and exit (for testing)
```

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
