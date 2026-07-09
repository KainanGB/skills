---
name: discord-export
description: Use when the user wants to export, list, inspect, or analyze Discord channel/guild/thread/DM history with DiscordChatExporter CLI while keeping credentials out of logs.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [discord, export, archive, productivity, cli]
    related_skills: []
---

# Discord Export

## Overview

Export Discord history with Tyrrrz DiscordChatExporter CLI, write artifacts to a local export directory, and verify the resulting files before reporting success.

This skill is portable: do not assume the user's binary path, home directory, token variable, or export directory matches yours. Discover them at runtime and use environment variables/placeholders in commands.

## When to Use

Use this skill when the user asks to:

- export a Discord channel, guild/server, thread, or DM history;
- list accessible Discord guilds or channels;
- convert a Discord chat to HTML, JSON, CSV, or plain text;
- analyze an already exported DiscordChatExporter artifact.

Do not use this skill to extract Discord cookies, scrape browser sessions, or print/store raw tokens. Assume the user already has an authorized credential configured locally.

## Portable Configuration

Use these variables when paths are not already known:

```bash
export DISCORD_EXPORT_DIR="${DISCORD_EXPORT_DIR:-$PWD/discord-exports}"
export DISCORD_CHAT_EXPORTER_CMD="${DISCORD_CHAT_EXPORTER_CMD:-DiscordChatExporter.Cli}"
```

If the CLI is installed under a custom path, set `DISCORD_CHAT_EXPORTER_CMD` to the absolute executable path, for example:

```bash
export DISCORD_CHAT_EXPORTER_CMD="$HOME/tools/DiscordChatExporter.Cli/DiscordChatExporter.Cli"
```

Credential convention:

- Prefer `DISCORD_TOKEN` in the process environment.
- If a local wrapper is available, use it only after confirming how it loads and redacts credentials.
- Never pass tokens with `--token`, `-t`, inline environment assignments, or commands that will be recorded in shell history, process lists, or tool output.

On Linux systems with .NET globalization/ICU issues, set:

```bash
export DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1
```

Completion criterion: the command to run DiscordChatExporter is known and the token source is configured without printing the token.

## Golden Path

1. Identify the export target.
   - If the user gives a channel/thread ID, use it directly.
   - If the user gives a Discord URL, extract the guild/channel/thread IDs from the URL.
   - If the user gives only a guild/server name, list guilds first, then list channels for the chosen guild.
   - Completion criterion: a concrete guild/channel/thread/DM ID or export scope is known.

2. Choose the output format.
   - `HtmlDark` for human reading or visual inspection.
   - `Json` for parsing, search, indexing, or downstream analysis.
   - `Csv` or `PlainText` only when explicitly useful.
   - Completion criterion: the format matches the user's next step.

3. Export to a deterministic output path.
   - Prefer `$DISCORD_EXPORT_DIR/<safe-guild-or-scope>/<safe-channel-or-scope>.<ext>`.
   - Create parent directories before export.
   - Completion criterion: the command exits successfully.

4. Verify the artifact.
   - Check the exit code.
   - Confirm the output file or directory exists.
   - Inspect only metadata unless the user asked for content analysis.
   - Completion criterion: exact artifact path and format are known.

5. Report concisely.
   - Include the path, format, and scope exported.
   - Do not include credentials or sensitive message content unless the user explicitly requested analysis.
   - Completion criterion: the user can open or process the artifact.

## Commands

List accessible guilds:

```bash
"$DISCORD_CHAT_EXPORTER_CMD" guilds
```

List channels in a guild:

```bash
"$DISCORD_CHAT_EXPORTER_CMD" channels --guild <GUILD_ID>
```

Export one channel as HTML:

```bash
mkdir -p "$DISCORD_EXPORT_DIR/<guild>"
"$DISCORD_CHAT_EXPORTER_CMD" export \
  --channel <CHANNEL_ID> \
  --format HtmlDark \
  --output "$DISCORD_EXPORT_DIR/<guild>/<channel>.html"
```

Export one channel as JSON:

```bash
mkdir -p "$DISCORD_EXPORT_DIR/<guild>"
"$DISCORD_CHAT_EXPORTER_CMD" export \
  --channel <CHANNEL_ID> \
  --format Json \
  --output "$DISCORD_EXPORT_DIR/<guild>/<channel>.json"
```

Export a whole guild:

```bash
mkdir -p "$DISCORD_EXPORT_DIR/<guild>"
"$DISCORD_CHAT_EXPORTER_CMD" exportguild \
  --guild <GUILD_ID> \
  --format HtmlDark \
  --output "$DISCORD_EXPORT_DIR/<guild>/"
```

List and export DMs when the authenticated account can access them:

```bash
"$DISCORD_CHAT_EXPORTER_CMD" dm
mkdir -p "$DISCORD_EXPORT_DIR/dm"
"$DISCORD_CHAT_EXPORTER_CMD" exportdm --format Json --output "$DISCORD_EXPORT_DIR/dm/"
```

Include threads in a channel export when needed:

```bash
mkdir -p "$DISCORD_EXPORT_DIR/<guild>"
"$DISCORD_CHAT_EXPORTER_CMD" export \
  --channel <CHANNEL_ID> \
  --format Json \
  --include-threads All \
  --output "$DISCORD_EXPORT_DIR/<guild>/<channel>.json"
```

Filter by date:

```bash
mkdir -p "$DISCORD_EXPORT_DIR/<guild>"
"$DISCORD_CHAT_EXPORTER_CMD" export \
  --channel <CHANNEL_ID> \
  --format Json \
  --after "2025-01-01" \
  --before "2025-12-31" \
  --output "$DISCORD_EXPORT_DIR/<guild>/<channel>.json"
```

## Local Wrapper Pattern

If the user maintains a wrapper script, it should:

- load the token from a local secret store or env file that is not committed;
- pass the credential to the child process via environment, not argv;
- redact the credential from combined stdout/stderr before printing;
- set `DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1` on Linux if needed;
- add a default export directory when no `--output` is supplied.

If the wrapper behavior is unknown, read the wrapper source before using it. Completion criterion: the wrapper does not expose credentials in argv or output.

This skill includes a portable wrapper template at `templates/discord-chat-exporter-wrapper.py`. Use it only after the user configures `DISCORD_CHAT_EXPORTER_BIN` or has `DiscordChatExporter.Cli` on `PATH`, and configures either `DISCORD_TOKEN` or `DISCORD_TOKEN_FILE`.

## After Export: Analysis Handoff

If the user asks to analyze an HTML export:

1. Verify the file exists. Watch for `.htm` vs `.html` mismatches.
2. Preserve the raw export unchanged.
3. Extract messages to a structured intermediate format such as `.messages.tsv` or `.json`.
4. Write analysis beside the export, e.g. `<channel>.analysis.md`.
5. Report raw and derived artifact paths separately.

Completion criterion: raw export, structured intermediate, and analysis artifact paths are all identified.

## Troubleshooting

### `forbidden` / HTTP 403

DiscordChatExporter can return forbidden even when the token is otherwise valid.

1. Query the channel directly via Discord API to confirm access and discover metadata, without printing the credential:

```bash
curl -s \
  -H "Authorization: [REDACTED_IN_EXAMPLE_USE_ENV_IN_REAL_COMMAND]" \
  -H "User-Agent: Mozilla/5.0" \
  "https://discord.com/api/v9/channels/<CHANNEL_ID>"
```

2. If the API returns channel info including `guild_id` and `name`, retry the export.
3. If the API also returns 403, the authenticated account cannot access that channel/server.

In real commands, use an environment variable or local wrapper; do not paste the token into the command text.

### Token missing or invalid

- Confirm the expected token environment variable exists without printing its value.
- User/session credentials can expire after logout, password change, account security action, or session invalidation.
- Revalidate by calling Discord `/users/@me` through a wrapper or script that redacts the credential.

### Output path surprises

If `--output` points to a directory, DiscordChatExporter may choose generated names such as:

```text
<guild-name> - <channel-name> [<channel-id>].json
```

Search under `$DISCORD_EXPORT_DIR` after export if the exact filename is not obvious.

### CLI missing

If `DiscordChatExporter.Cli` is not on `PATH`, ask for its install path or install/download it according to the user's OS and package policy. Do not assume a fixed path.

## Safety Rules

- Never expose Discord tokens, cookies, authorization headers, or raw env-file contents in chat.
- Do not commit credentials, exported chats, browser profiles, logs, or generated archives.
- Prefer environment variables or a redacting wrapper over inline credentials.
- If tool output includes a secret, redact it before summarizing.

## Verification Checklist

- [ ] Target guild/channel/thread/DM scope identified.
- [ ] CLI path or wrapper discovered; no hardcoded local path assumed.
- [ ] Token source configured without printing or committing the token.
- [ ] Output format chosen for the downstream task.
- [ ] Export command exited successfully.
- [ ] Output artifact exists under the chosen export directory.
- [ ] Response includes artifact path and omits credentials.
