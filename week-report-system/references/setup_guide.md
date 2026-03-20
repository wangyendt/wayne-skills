# Environment Setup Guide

This guide walks through setting up the three required environment variables for the Week Report System, and shows how to write them permanently to the user's shell profile.

## Required Variables

| Variable | Description | Example |
|---|---|---|
| `WEEK_REPORT_GIT_USERNAME` | GitHub username | `zhangsan` |
| `WEEK_REPORT_GIT_PERSONAL_TOKEN` | GitHub Personal Access Token | `ghp_xxxxxxxxxxxx` |
| `WEEK_REPORT_GIT_REPO` | Repository path (`username/repo`) | `zhangsan/week-reports` |

---

## Step 1: Create a GitHub Repository

Tell the user:

> Please create a new GitHub repository to store your work logs:
>
> 1. Go to https://github.com/new
> 2. Repository name: `week-reports` (or any name you like)
> 3. Visibility: **Private** (recommended — work logs are personal)
> 4. **Leave all "Initialize" options unchecked** (empty repo)
> 5. Click **"Create repository"**
> 6. Note the full path: `{your-username}/week-reports`

---

## Step 2: Create a Personal Access Token

Tell the user:

> Now create a token so the system can read and write to this repository:
>
> 1. Go to https://github.com/settings/tokens
> 2. Click **"Generate new token"** → **"Generate new token (classic)"**
> 3. Note field: `Week Report System`
> 4. Expiration: 90 days (or "No expiration" for convenience)
> 5. Scopes: check **`repo`** (full control of private repositories)
> 6. Click **"Generate token"**
> 7. **Copy the token immediately** — GitHub won't show it again!
>    Format: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## Step 3: Write Variables to Shell Profile

Once the user provides all three values, detect the shell and write them permanently.

### Detect shell and profile file

```bash
# Detect shell profile
if [ -n "$ZSH_VERSION" ] || [ "$SHELL" = "/bin/zsh" ] || [ "$SHELL" = "/usr/bin/zsh" ]; then
    PROFILE_FILE="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ] || [ "$SHELL" = "/bin/bash" ]; then
    PROFILE_FILE="$HOME/.bashrc"
    # macOS uses .bash_profile for login shells
    [ "$(uname)" = "Darwin" ] && PROFILE_FILE="$HOME/.bash_profile"
else
    PROFILE_FILE="$HOME/.profile"
fi
echo "Will write to: $PROFILE_FILE"
```

### Write the variables

Replace `YOUR_USERNAME`, `YOUR_TOKEN`, `YOUR_REPO` with the user's actual values:

```bash
# Remove any existing entries to avoid duplicates
sed -i'' -e '/WEEK_REPORT_GIT_USERNAME/d' \
         -e '/WEEK_REPORT_GIT_PERSONAL_TOKEN/d' \
         -e '/WEEK_REPORT_GIT_REPO/d' \
         "$PROFILE_FILE"

# Append new values
cat >> "$PROFILE_FILE" << 'ENVEOF'

# Week Report System Configuration
export WEEK_REPORT_GIT_USERNAME="YOUR_USERNAME"
export WEEK_REPORT_GIT_PERSONAL_TOKEN="YOUR_TOKEN"
export WEEK_REPORT_GIT_REPO="YOUR_REPO"
ENVEOF

echo "Written to $PROFILE_FILE"
```

### Load immediately in current session

```bash
export WEEK_REPORT_GIT_USERNAME="YOUR_USERNAME"
export WEEK_REPORT_GIT_PERSONAL_TOKEN="YOUR_TOKEN"
export WEEK_REPORT_GIT_REPO="YOUR_REPO"
```

### Verify

```bash
echo "Username: $WEEK_REPORT_GIT_USERNAME"
echo "Token set: $([ -n \"$WEEK_REPORT_GIT_PERSONAL_TOKEN\" ] && echo 'YES' || echo 'NO')"
echo "Repo: $WEEK_REPORT_GIT_REPO"
```

---

## Windows Setup

### PowerShell (User-level, persistent)

```powershell
[Environment]::SetEnvironmentVariable("WEEK_REPORT_GIT_USERNAME", "YOUR_USERNAME", "User")
[Environment]::SetEnvironmentVariable("WEEK_REPORT_GIT_PERSONAL_TOKEN", "YOUR_TOKEN", "User")
[Environment]::SetEnvironmentVariable("WEEK_REPORT_GIT_REPO", "YOUR_REPO", "User")
```

Restart your terminal after running these.

### Command Prompt

```cmd
setx WEEK_REPORT_GIT_USERNAME "YOUR_USERNAME"
setx WEEK_REPORT_GIT_PERSONAL_TOKEN "YOUR_TOKEN"
setx WEEK_REPORT_GIT_REPO "YOUR_REPO"
```

---

## Security Best Practices

1. **Keep your token secret** — never commit it to any repository
2. **Use a private repository** — work logs are personal
3. **Rotate tokens regularly** — regenerate every 90 days
4. **Revoke compromised tokens** — GitHub Settings → Tokens → Revoke

---

## Troubleshooting

| Error | Likely Cause | Fix |
|---|---|---|
| Authentication failed | Token expired or wrong scope | Regenerate with `repo` scope |
| Repository not found | Wrong `WEEK_REPORT_GIT_REPO` format | Must be `username/repo-name` |
| Variables not loading | Terminal not restarted | Run `source ~/.zshrc` or open new terminal |
| Permission denied | Token missing `repo` scope | Regenerate token and check scopes |
