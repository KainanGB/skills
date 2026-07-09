#!/usr/bin/env python3
"""Portable, redacting wrapper template for Tyrrrz DiscordChatExporter CLI.

Configure with environment variables:

  DISCORD_CHAT_EXPORTER_BIN=/absolute/path/to/DiscordChatExporter.Cli
  DISCORD_TOKEN_FILE=$HOME/.config/discord-chat-exporter/token
  DISCORD_TOKEN_ENV=DISCORD_TOKEN
  DISCORD_EXPORT_DIR=$PWD/discord-exports

Token priority:
1. value of env var named by DISCORD_TOKEN_ENV (default: DISCORD_TOKEN)
2. file at DISCORD_TOKEN_FILE

The token is passed to the child as DISCORD_TOKEN and redacted from output.
"""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys


def _resolve_binary() -> str:
    configured = os.environ.get("DISCORD_CHAT_EXPORTER_BIN") or os.environ.get("DISCORD_CHAT_EXPORTER_CMD")
    if configured:
        return configured
    found = shutil.which("DiscordChatExporter.Cli") or shutil.which("discord-chat-exporter")
    if found:
        return found
    raise SystemExit(
        "DiscordChatExporter CLI not found. Set DISCORD_CHAT_EXPORTER_BIN to the executable path."
    )


def _load_token() -> str:
    token_env = os.environ.get("DISCORD_TOKEN_ENV", "DISCORD_TOKEN")
    token = os.environ.get(token_env, "").strip()
    if token:
        return token

    token_file = os.environ.get("DISCORD_TOKEN_FILE")
    if token_file:
        path = pathlib.Path(token_file).expanduser()
        if path.exists():
            token = path.read_text(encoding="utf-8", errors="ignore").strip()
            if token:
                return token

    raise SystemExit(
        "No Discord token found. Set DISCORD_TOKEN or DISCORD_TOKEN_FILE. Do not pass tokens in argv."
    )


def _has_output_arg(args: list[str]) -> bool:
    return any(a in {"-o", "--output"} or a.startswith("--output=") for a in args)


def main() -> int:
    args = sys.argv[1:]
    if any(a in {"-t", "--token"} or a.startswith("--token=") for a in args):
        print("Refusing --token/-t in argv. Use environment or DISCORD_TOKEN_FILE.", file=sys.stderr)
        return 2

    binary = _resolve_binary()
    token = _load_token()

    if args and args[0] in {"export", "exportall", "exportdm", "exportguild"} and not _has_output_arg(args):
        export_dir = pathlib.Path(os.environ.get("DISCORD_EXPORT_DIR", "discord-exports"))
        export_dir.mkdir(parents=True, exist_ok=True)
        args = [*args, "--output", str(export_dir) + "/"]

    env = os.environ.copy()
    env["DISCORD_TOKEN"] = token
    env.setdefault("DOTNET_SYSTEM_GLOBALIZATION_INVARIANT", "1")

    proc = subprocess.run(
        [binary, *args],
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = proc.stdout.replace(token, "[REDACTED]")
    if output:
        print(output, end="")
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
