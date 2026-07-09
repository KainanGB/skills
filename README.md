# skills

Reusable Hermes Agent skills.

## Included skills

- `productivity/discord-export` — export Discord channel/guild/thread/DM history with Tyrrrz DiscordChatExporter CLI and verify the resulting artifact.

## Installing a skill

Copy a skill directory into your Hermes skills folder, preserving `SKILL.md`:

```bash
mkdir -p ~/.hermes/skills/productivity
cp -R productivity/discord-export ~/.hermes/skills/productivity/
```

Then start a fresh Hermes session so the skill loader sees it.

## Safety

This repository should contain procedures and templates only. Do not commit `.env` files, tokens, cookies, exported chats, browser profiles, logs, or generated archives.
