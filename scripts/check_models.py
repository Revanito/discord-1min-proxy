#!/usr/bin/env python3
"""Monthly 1min.ai model-list watchdog.

Checks every model ID the given projects use against 1min.ai's live model list and posts a report to a
Discord webhook. 1min.ai renames/removes models without notice (2026: every Claude ID moved to
`us.anthropic.*`, the `grok-4-fast-*` models were dropped), which silently breaks the bot until someone
notices - this catches it within a month instead.

Stdlib only, so it runs with the LXC's system python3 - no venv, no pip.

Usage:
    python3 scripts/check_models.py /opt/discord-1min-proxy [/opt/read-later ...] [--dry-run]

For each project dir, model IDs are collected the same way the app resolves them at runtime:
`.env` (MODEL_*=...) wins over docker-compose.yml defaults (${MODEL_*:-...}), which win over
config.py defaults (model_*: str = "..."). Project dirs on other LXCs can't be read from here -
either run this script there too, or clone the repo locally to check its defaults only.

The webhook URL comes from ONEMIN_WATCH_WEBHOOK_URL (env var, or the first project's .env).
Exit code: 0 = all fine, 1 = at least one model is missing/inactive, 2 = couldn't reach the API.
"""
import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MODELS_URL = "https://api.1min.ai/models?feature=UNIFY_CHAT_WITH_AI"
WEBHOOK_VAR = "ONEMIN_WATCH_WEBHOOK_URL"
# Snapshot of the last run's full model list, to report models added/removed since then.
STATE_FILE = Path(__file__).with_name(".known_models.json")
DEPRECATION_WARN_DAYS = 90
DISCORD_LIMIT = 1900  # Discord caps message content at 2000 chars

ENV_RE = re.compile(r"^\s*(MODEL_[A-Z0-9_]+)\s*=\s*['\"]?([^'\"#\s]+)", re.MULTILINE)
COMPOSE_RE = re.compile(r"\$\{(MODEL_[A-Z0-9_]+):-([^}]+)\}")
CONFIG_RE = re.compile(r"^\s*(model_[a-z0-9_]+)\s*:\s*str\s*=\s*['\"]([^'\"]+)['\"]", re.MULTILINE)
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__"}


def http_get_json(url: str) -> dict:
    # Cloudflare in front of api.1min.ai tends to reject urllib's default User-Agent.
    req = urllib.request.Request(url, headers={"User-Agent": "discord-1min-proxy-model-watch/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def collect_models(project: Path) -> dict[str, str]:
    """Return {MODEL_VAR: model_id} with the same precedence the app uses at runtime."""
    found: dict[str, str] = {}
    for config in project.rglob("config.py"):
        if SKIP_DIRS.isdisjoint(config.parts):
            for name, value in CONFIG_RE.findall(read_text(config)):
                if name != "model_config":
                    found[name.upper()] = value
    for name, value in COMPOSE_RE.findall(read_text(project / "docker-compose.yml")):
        found[name] = value.strip()
    for name, value in ENV_RE.findall(read_text(project / ".env")):
        found[name] = value
    return found


def read_env_var(project: Path, name: str) -> str | None:
    match = re.search(rf"^\s*{name}\s*=\s*['\"]?([^'\"\s]+)", read_text(project / ".env"), re.MULTILINE)
    return match.group(1) if match else None


def post_discord(webhook: str, text: str) -> None:
    if len(text) > DISCORD_LIMIT:
        text = text[: DISCORD_LIMIT - 20] + "\n… (truncated)"
    body = json.dumps({"content": text, "allowed_mentions": {"parse": []}}).encode()
    req = urllib.request.Request(
        webhook, data=body, method="POST",
        headers={"Content-Type": "application/json", "User-Agent": "discord-1min-proxy-model-watch/1.0"},
    )
    urllib.request.urlopen(req, timeout=30).close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("projects", nargs="+", type=Path, help="project checkout dirs to scan")
    parser.add_argument("--dry-run", action="store_true", help="print the report, don't post to Discord")
    args = parser.parse_args()

    webhook = os.environ.get(WEBHOOK_VAR) or read_env_var(args.projects[0], WEBHOOK_VAR)

    try:
        live = [m for m in http_get_json(MODELS_URL).get("models", []) if m.get("modelId") != "NOT_APPLICABLE"]
    except Exception as exc:  # noqa: BLE001 - any failure here means "couldn't check", report it as such
        report = f"⚠️ **1min.ai model check failed** - couldn't fetch `{MODELS_URL}`: {exc}"
        print(report)
        if webhook and not args.dry_run:
            post_discord(webhook, report)
        return 2
    if not live:
        # An empty list means the endpoint changed shape (e.g. the feature param), not that every model is gone.
        report = f"⚠️ **1min.ai model check failed** - `{MODELS_URL}` returned no models, the endpoint may have changed."
        print(report)
        if webhook and not args.dry_run:
            post_discord(webhook, report)
        return 2

    by_id = {m["modelId"]: m for m in live}
    now = datetime.now(timezone.utc)
    broken, warnings, ok = [], [], []

    for project in args.projects:
        models = collect_models(project)
        if not models:
            warnings.append(f"`{project.name}`: no MODEL_* settings found - wrong path?")
        for var, model_id in sorted(models.items()):
            where = f"`{project.name}` {var} = `{model_id}`"
            info = by_id.get(model_id)
            if info is None:
                broken.append(f"❌ {where} - **not in 1min.ai's list anymore**")
            elif info.get("status") != "ACTIVE":
                broken.append(f"❌ {where} - status `{info.get('status')}`")
            elif info.get("deprecationDate"):
                date = datetime.fromisoformat(info["deprecationDate"].replace("Z", "+00:00"))
                days = (date - now).days
                line = f"{where} - deprecated on {date:%Y-%m-%d} ({days} days)"
                (warnings if days <= DEPRECATION_WARN_DAYS else ok).append(("⚠️ " if days <= DEPRECATION_WARN_DAYS else "") + line)
            else:
                ok.append(where)

    # Diff the full list against last run, so new models (and renames) are visible even when nothing broke.
    current_ids = sorted(by_id)
    try:
        previous = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        previous = None
    added = sorted(set(current_ids) - set(previous)) if previous is not None else []
    removed = sorted(set(previous) - set(current_ids)) if previous is not None else []

    status = "❌ action needed" if broken else ("⚠️ heads-up" if warnings else "✅ all good")
    lines = [f"**1min.ai monthly model check - {status}** ({len(live)} models live, {len(ok) + len(warnings) + len(broken)} checked)"]
    lines += broken + warnings
    if previous is None and not args.dry_run:
        lines.append("_First run - saved the model list, next month's report will show what changed._")
    if removed:
        lines.append("Removed since last check: " + ", ".join(f"`{m}`" for m in removed))
    if added:
        lines.append("New since last check: " + ", ".join(f"`{m}`" for m in added))
    if broken or removed:
        lines.append("Fix: update the model IDs in each repo (config.py, docker-compose.yml, .env.example, docs) and the LXC `.env`, then refresh MODELS.md.")
    report = "\n".join(lines)

    print(report)
    if args.dry_run:
        return 1 if broken else 0
    STATE_FILE.write_text(json.dumps(current_ids, indent=1), encoding="utf-8")
    if webhook:
        post_discord(webhook, report)
    else:
        print(f"(no {WEBHOOK_VAR} set - report not posted)", file=sys.stderr)
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
