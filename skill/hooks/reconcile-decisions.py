#!/usr/bin/env python3
"""Stop hook for the Decision Tree skill.

Fires when Claude finishes a turn. Throttled to at most once per COOLDOWN seconds
per session (and guarded against the stop-hook loop), it asks Claude to reconcile the
decision log with the conversation: log new decisions, revise changed/reversed ones,
and regenerate the viewer. This keeps the per-decision files + graph.html complete and
current so that by the end of any session every decision (and its changes) is shown.

Portable: the project directory comes from $CLAUDE_PROJECT_DIR (set by Claude Code),
falling back to the current working directory — so this works in any project, not just
the one it was authored in.

Output protocol: print {"decision":"block","reason":...} to force one more turn in
which Claude does the reconciliation; otherwise exit 0 silently to allow the stop.
"""
import sys, json, os, time, subprocess

PROJ = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
COOLDOWN = 900  # seconds between forced reconciliations per session

GEN = os.path.join(PROJ, ".claude", "skills", "decision-tree", "generate.py")
SRC_DIR = os.path.join(PROJ, "decisions")  # holds _project.json + [v<version>/]NNNN-*.json files
OUT = os.path.join(SRC_DIR, "graph.html")


def regenerate_if_stale():
    """Rebuild graph.html whenever any decision file changed (or the viewer is missing).
    Decisions are one file per decision under decisions/ (including per-version sub-folders),
    so we compare the viewer's mtime against the newest *.json anywhere in that tree. Runs
    every turn, silently; failure never blocks the stop. Auto-regenerate backstop (decision d8)."""
    try:
        if not os.path.isdir(SRC_DIR):
            return
        newest = 0.0
        for root, _dirs, files in os.walk(SRC_DIR):
            for fn in files:
                if fn.endswith(".json"):
                    try:
                        newest = max(newest, os.path.getmtime(os.path.join(root, fn)))
                    except OSError:
                        pass
        if newest == 0.0:
            return
        if os.path.exists(OUT) and os.path.getmtime(OUT) >= newest:
            return  # viewer already up to date
        subprocess.run([sys.executable, GEN, SRC_DIR, OUT],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
    except Exception:
        pass  # never let regeneration break the hook


REASON = (
    "Decision-log backstop. Capture model is CONFIRM-AT-THE-MOMENT, so most decisions should "
    "already be logged. This is only a safety check.\n"
    "Scan the conversation since the last check for any decision that was MADE, CHANGED, or "
    "REVERSED but NOT yet logged-and-confirmed.\n"
    "If you find one, do NOT write it silently. PROPOSE it to the user — draft the title, "
    "options, and tradeoffs (and for a change, what it was and why) — and ask them to confirm "
    "or edit. Only after they approve, update the per-decision files in '" + SRC_DIR + "/' "
    "(create a new NNNN-slug.json, or for a change edit that decision's file: set old option "
    "chosen=false / new chosen=true and append {from, reason} to history[]) and regenerate:\n"
    "  python3 '" + GEN + "' '" + SRC_DIR + "' '" + OUT + "'\n"
    "If everything is already captured, just say so briefly. Do NOT run this check more than once."
)


def main():
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except Exception:
        data = {}

    # Keep the viewer current on every turn, regardless of the reconcile throttle (decision d8).
    regenerate_if_stale()

    # Avoid the infinite stop-hook loop: if we already forced a continue, let it stop.
    if data.get("stop_hook_active"):
        return 0

    sid = str(data.get("session_id", "session"))
    state_dir = os.path.join(PROJ, ".claude", "state")
    os.makedirs(state_dir, exist_ok=True)
    marker = os.path.join(state_dir, "reconcile-" + sid)

    now = time.time()
    if os.path.exists(marker):
        try:
            last = float((open(marker).read() or "0").strip())
        except Exception:
            last = 0.0
        if now - last < COOLDOWN:
            return 0  # within cooldown -> allow stop silently

    with open(marker, "w") as f:
        f.write(str(now))

    print(json.dumps({"decision": "block", "reason": REASON}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
