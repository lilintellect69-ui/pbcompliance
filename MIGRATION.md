# Migration to Claude Code — First 10 Minutes

This guide takes you from "tarball downloaded" to "OS running locally + Claude Code session ready" in about 10 minutes.

## 0. Prerequisites

- macOS, Linux, or WSL
- Python 3.11+ with `pip`
- Node.js 18+ with `npm`
- `git`
- Claude Code installed (`npm install -g @anthropic-ai/claude-code` or follow the install guide in Anthropic docs)

## 1. Extract and initialize (2 min)

```bash
# Pick a parent folder you keep code in
cd ~/code

# Extract the kit
tar -xzf privatebox-grc-os-migration-kit.tar.gz
cd privatebox-grc-os

# Initialize git
git init
git add .
git commit -m "Initial migration from claude.ai chat: 3 frameworks, OS prototype, lens toggle, 4-section user-journey spine"
```

## 2. Install dependencies (3 min)

```bash
# Python — for build scripts and validator
pip install -r build/requirements.txt

# Node — for the OS
cd os
npm install
cd ..
```

## 3. Verify the existing build pipeline still works (2 min)

```bash
make validate
# Should print: "iso-27001.yaml OK / iso-27701.yaml OK / eu-ai-act.yaml OK"
# (12 validation rules pass on all three)

make data
# Should regenerate os/src/data.json (~715KB)

make dev
# Vite serves at http://localhost:5173 — open in browser
# You should see Home with three framework cards, lens toggle in header
```

If any of the above fail, stop and triage before proceeding. The migration is verified by these three commands passing.

## 4. Open Claude Code (1 min)

```bash
# In repo root
claude
```

Claude reads `CLAUDE.md` automatically as it orients to the repo. Skills under `.claude/skills/` are also discoverable. You don't need to prime context manually.

## 5. First prompt suggestion (1 min)

Once `claude` is running, try:

```
Read CLAUDE.md, then plan the ISO 42001 build. Show me the YAML structure
you'd produce (groups, requirement count estimate, owner distribution),
the source material you need from me, and the open questions you'd flag
before authoring. Don't write the YAML yet.
```

This produces a build plan you can review before any heavy lifting. Then:

```
Source material: [paste/upload the standard text into frameworks/iso-42001/source/]
Now author iso-42001.yaml following the compliance-framework-author skill.
Run `make validate` after; iterate until it passes.
```

## What's different from claude.ai chat

- **State persists.** Files are on your disk; conversations don't need to carry context across sessions. CLAUDE.md does the priming.
- **Compaction is irrelevant.** Long conversations summarise, but the work product is the repo, not the conversation.
- **Git is your audit trail.** Every YAML edit is a commit. Reversion is one command.
- **Hot reload.** `npm run dev` shows changes instantly — no reassemble cycle.
- **Skills carry methodology.** `compliance-framework-author` codifies the YAML authoring rules so they're applied consistently regardless of session.

## Recommended workflow per new framework

```bash
# 1. Create the working folder
mkdir -p frameworks/iso-42001/source

# 2. Drop source standard text into source/ (PDF, MD, TXT, whatever)
cp ~/Downloads/iso-42001-2023.pdf frameworks/iso-42001/source/

# 3. Open Claude Code, ask it to author the YAML following the skill
claude
> Author frameworks/iso-42001/iso-42001.yaml using the compliance-framework-author skill.
> Source is in frameworks/iso-42001/source/iso-42001-2023.pdf.

# 4. Iterate
make validate       # schema check
make crosswalks     # see what crosswalks are auto-suggested
make data           # rebuild data.json
make dev            # eyeball it in the OS

# 5. Commit
git add frameworks/iso-42001/ os/src/data.json
git commit -m "Add ISO 42001 (AI management system); ~40 requirements"
```

## Troubleshooting

**`make validate` fails with schema errors:**
The validator output names the file, requirement id, and rule that failed. Most common: missing `business_models` field, missing `requirement` AND `objective` (one is required), invalid `kind` value.

**`make dev` errors on JSON parse:**
Run `make data` first. The OS imports `os/src/data.json` directly; if it's stale or malformed, vite errors immediately.

**Vite hot-reload not picking up YAML changes:**
YAML changes don't auto-rebuild — only `os/src/*` does. Run `make data` after editing a YAML; vite picks up the new data.json automatically.

**Claude not finding the skill:**
Check `.claude/skills/compliance-framework-author/SKILL.md` exists and is readable. Skills are discovered by name in conversations, but you can also explicitly point to them: "use the compliance-framework-author skill".
