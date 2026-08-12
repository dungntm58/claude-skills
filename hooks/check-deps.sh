#!/usr/bin/env bash
# claude-skills SessionStart hook
# Checks deps for chaining-openspec-superpowers skill.
# Silent if everything present; emits install instructions otherwise.

set -u

missing=()

# 1. openspec CLI (required)
if ! command -v openspec >/dev/null 2>&1; then
  missing+=("openspec-cli")
fi

# 2. superpowers plugin (required)
claude_dir="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
if ! find "$claude_dir/plugins/cache" -maxdepth 3 -type d -name superpowers 2>/dev/null | grep -q .; then
  missing+=("superpowers-plugin")
fi

# nano-banana-sprites deps (optional; only warn, never fail)
if ! python3 -c "import PIL" >/dev/null 2>&1; then
  echo "nano-banana-sprites: Pillow not installed (pip install Pillow) — needed to pixelize sprites."
fi
if [ -z "${GEMINI_API_KEY:-}" ] && [ -z "${GOOGLE_API_KEY:-}" ]; then
  echo "nano-banana-sprites: no global GEMINI_API_KEY/GOOGLE_API_KEY set — export one, or add a project .nano-banana.env, to generate sprites."
fi

if [ ${#missing[@]} -eq 0 ]; then
  exit 0
fi

if [ ${#missing[@]} -gt 0 ]; then
  cat <<'MSG'
[chaining-openspec-superpowers] Missing REQUIRED dependencies. Install before invoking the skill:

MSG
  for dep in "${missing[@]}"; do
    case "$dep" in
      openspec-cli)
        cat <<'MSG'
- openspec CLI:
    npm install -g @fission-ai/openspec@latest
  Then in your project (one-time, drops openspec-* skills into .claude/skills/):
    openspec init --tools claude

MSG
        ;;
      superpowers-plugin)
        cat <<'MSG'
- superpowers plugin (run inside Claude Code):
    /plugin marketplace add anthropics/claude-plugins-official
    /plugin install superpowers@claude-plugins-official

MSG
        ;;
    esac
  done
fi

exit 0
