---
name: update-docs
description: >
  Sync project documentation with recent git commits. Use this skill whenever the
  user says "更新文档", "同步文档", "update docs", "更新 docs", "文档同步", or asks
  you to update documentation after coding. Also trigger proactively when the user
  mentions they've finished a feature or made significant commits and the docs look
  stale. This skill reads today's (or recent) git history, identifies what changed,
  and updates CHANGELOG.md, API.md, ARCHITECTURE.md, README.md, and CLAUDE.md to
  accurately reflect the current codebase — turning "待实现" into "✅ 已完成".
---

# Update Docs

Keep documentation synchronized with code changes by reading git history and
updating all relevant docs files to match the current state of the project.

## When to use

- User says "更新文档" / "update docs" / "同步文档" / "文档同步"
- User finishes a coding session and wants docs refreshed
- Docs say something is "待实现" but the code already implements it
- After a batch of commits that added features, APIs, or refactors

## Step-by-step workflow

### 1. Discover what changed

First, read `docs/CHANGELOG.md` to find the **last recorded commit hash** in the most
recent version block. Each version block ends with a line like:

```
_last commit: `a1b2c3d`_
```

Then fetch all commits **after** that hash:

```bash
# Get all commits after the last recorded hash (exclusive)
git log <last-commit-hash>..HEAD --format="%H %ai %s"
```

If CHANGELOG.md has no recorded commit hash (first run), fall back to all commits:
```bash
git log --oneline
```

For each commit hash, run `git show --stat <hash>` to understand what files changed.
Group commits by feature/theme to determine which doc sections need updating.

> **Why hash instead of date?** Commit timestamps can be ambiguous (timezone drift,
> amended commits, rebases). A hash is an exact, unambiguous pointer — you get precisely
> the commits since the last doc update, nothing more and nothing less.

### 2. Read current docs

Read all docs that may need updating:
- `docs/CHANGELOG.md`
- `docs/API.md`
- `docs/ARCHITECTURE.md`
- `README.md`
- `CLAUDE.md`

Note which ones are out of date based on what the commits added.

### 3. Read key implementation files

For each significant change, read the actual implementation to understand:
- New API endpoints → read the router file (e.g., `backend/api/auth.py`)
- New database models → read `backend/database/models.py`
- New frontend pages/components → read relevant Vue/TS files
- New config → read `.env.example` or config files

This ensures docs reflect what was actually built, not just commit messages.

### 4. Update each doc file

#### CHANGELOG.md
- Append a new version block (bump minor version: 0.1.0 → 0.2.0) at the top
- Group changes by phase/feature
- Mark previously "待实现" items as completed
- Keep the old version's content below unchanged
- **At the end of the new version block, record the hash of the most recent commit
  covered by this update**, so the next run knows exactly where to start:
  ```
  _last commit: `<full-hash-of-HEAD>`_
  ```
  Run `git rev-parse HEAD` to get the current HEAD hash.

#### API.md
- Add complete documentation for new endpoints with request/response examples
- Include safety constraints (e.g., delete guards)
- Remove or update any sections marked "后续实现" that are now implemented
- Add new error codes if applicable

#### ARCHITECTURE.md
- Update the file organization tree to include new files
- Add new data models (with fields)
- Add new data flow diagrams if architecture changed significantly
- Document new tech stack additions (e.g., a new frontend framework)

#### README.md
- Update the features list to check off completed items
- Update quick-start instructions if startup changed (new commands, new ports)
- Update the tech stack table
- Revise the "后续计划" section to remove completed items

#### CLAUDE.md
- Mark completed phases with ✅
- Update command reference to include new dev commands
- Update data models section with new fields
- Update known issues to remove resolved ones
- Add new known issues if they came up
- Update the "最后更新" date

### 5. Verify consistency

After updating, do a quick cross-check:
- Does CHANGELOG.md mention every significant commit?
- Does API.md cover every endpoint in `backend/api/`?
- Does ARCHITECTURE.md's file tree match `find backend/ -name "*.py" | head -30`?
- Does README.md's quick-start actually work based on current scripts?

## Output

Report a summary table like:

| 文件 | 主要变更 |
|---|---|
| docs/CHANGELOG.md | 新增 v0.2.0，记录 Phase X-Y |
| docs/API.md | 新增 auth 和 categories 端点 |
| docs/ARCHITECTURE.md | 更新文件目录树，新增 Category 模型 |
| README.md | 更新技术栈，快速启动命令 |
| CLAUDE.md | Phase 12/13/14 标记 ✅，更新命令 |

## Tips

- If the user specifies a commit range (e.g., "从上次发版到现在"), use `git log <tag-or-hash>..HEAD` directly.
- If only specific docs need updating (e.g., "只更新 API.md"), skip the others.
- Prefer `Edit` over `Write` for partial updates; use `Write` only for complete rewrites.
- When in doubt whether a feature is "完成", read the implementation file rather than guessing from the commit message.
- Don't remove history from CHANGELOG.md — always prepend new versions, never replace old ones.
- If the recorded hash in CHANGELOG.md no longer exists in the repo (e.g., after a
  force-push or rebase), fall back to `git log --oneline` and ask the user which
  commit to treat as the baseline.
