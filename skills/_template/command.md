# {{SKILL_NAME}} Prompt (Claude Code)

## Execution Instructions

### Step 0: Initialization
- No telemetry or consent gates. Proceed directly to input analysis.

### Step 1: Determine Input Mode
- If input is a GitHub URL or PR number $\to$ Live PR Mode.
- If input is a file path, `.diff`, or `.patch` $\to$ Local Analysis Mode.

### Step 2: Context & Mapping (Live Mode)
- Use `gh pr view <pr> --json number,title,state,isDraft,headRefOid` to check status. Stop if NOT OPEN or is a draft.
- Fetch the diff and save to a temporary file.
- **Anti-Hallucination Map**: Execute the following Python snippet to build a line map of commentable added/context lines.
```python
import re
# Logic to parse unified diff and map file paths to valid line numbers
```
- Fetch existing comments via `gh api` to dedupe. A thread is "addressed" only if a reply starts with `fixed`, `updated`, `done`, `resolved` or contains `✅`.

### Step 3: Core Analysis
**[USER-DEFINED ANALYSIS LOGIC HERE]**

- Mandatory per-file exhaustion: Check every added line.
- Categories: Bugs, Security, Performance, Concurrency, Resource Mgmt, Quality.
- Scoring: Compute Cyclomatic/Cognitive complexity. Suggest refactor if Medium+.
- Constraints: No linter nits, no pre-existing code flags, no ungrounded claims.
- Output: `[SEVERITY] file:line — description`.

### Step 4: Approval Gate
1. Present a numbered table "Proposed Inline Comments".
2. Ask two structured questions:
   - **Selection**: (None / All / Custom)
   - **Event**: (Comment / Request Changes / Approve)
- If Selection=None and Event=Approve $\to$ Summary only.
- If Selection=None and Event=Comment $\to$ Chat only.

### Step 5: Execution
- Write approved bodies to temp files to avoid quoting bugs.
- POST to `/pulls/{pr}/comments` with `side=RIGHT` and `commit_id=<head_sha>`.
- Append watermark: `🤖 Auto-reviewed by the {{SKILL_NAME}} skill`.
- Post summary review with normalized event: `COMMENT`, `REQUEST_CHANGES`, or `APPROVE`.
- Report final URL and posted-vs-proposed counts.
