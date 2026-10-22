# review-pr Prompt (Claude Code)

## Execution Instructions

### Step 0: Initialization

- NO telemetry or consent gate. Proceed directly to input analysis.

### Step 1: Determine Input Mode

- If input is a GitHub URL or PR number $\to$ **Live PR Mode**.
- If input is a file path, `.diff`, or `.patch` $\to$ **Local Analysis Mode**.

### Step 2: Context & Mapping (Live Mode)

- Use `gh pr view <pr> --json number,title,state,isDraft,headRefOid` to check status. Stop if NOT
  OPEN or is a draft.
- **Empty Diff Check**: If the diff is empty or contains no changed lines, ask the user to clarify
  the PR/branch or check if the PR has been merged/emptied.
- Fetch the diff and save to a temporary file.
- **VALID RIGHT-SIDE LINE MAP**: You MUST execute the following Python snippet to build a line map
  of commentable added/context line numbers. Skip /dev/null hunks.

```python
import re
import sys

def parse_diff(diff_text):
    line_map = {}
    current_file = None
    line_num = 0
    for line in diff_text.splitlines():
        if line.startswith('+++ b/'):
            current_file = line[6:]
            line_map[current_file] = set()
            line_num = 0
        elif line.startswith('@@'):
            match = re.search(r'@@ -\d+,\d+ \+(\d+),(\d+) @@', line)
            if match:
                line_num = int(match.group(1)) - 1
        elif line.startswith('+') and not line.startswith('+++'):
            line_num += 1
            if current_file: line_map[current_file].add(line_num)
        elif not line.startswith('-'):
            line_num += 1
    return line_map
```

- **CRITICAL**: Every finding's (path, line) MUST exist in this map or it is dropped
  (anti-hallucination).
- **DEDUPLICATION**: Fetch existing comments via `gh api .../comments`. Treat a thread as addressed
  ONLY if a reply (lowercased, trimmed) STARTS WITH `fixed`, `updated`, `done`, `resolved` or
  contains `✅`.
- **Repo-Wide Search**: For every changed function signature or API call, search the rest of the
  repository (using grep or the AI's toolset) to identify potential ripple-effect bugs.

### Step 3: Core Analysis

- **Configuration & Profiles**: Read `config.json` for `default_profile` or check for a profile flag
  (e.g., `--profile security`). Use the `profiles` object in `config.json` to define the focus. If
  missing, use a comprehensive audit of all categories.
- **Mandatory Per-File Exhaustion**: Check EVERY added line. One finding does not conclude a file.
- **Categories**:
    - **Bugs**: Logic errors, null pointers, off-by-one.
    - **Security**: Injection, XSS, insecure defaults, secret leaks.
    - **Performance**: $O (n^2)$ loops, redundant API calls, memory leaks.
    - **Concurrency**: Race conditions, deadlocks, missing mutexes.
    - **Resource Mgmt**: Unclosed handles, leaked sockets.
    - **Code Quality**: Readability, naming, maintainability.
- **Complexity Scoring**: Compute Cyclomatic + Cognitive complexity. Provide a "Suggested Refactor"
  block if Medium+.
- **Constraints**: Do NOT flag pre-existing code, linter nits, or ungrounded findings.
- **Output**: `[SEVERITY] file:line — description`. Compile findings with a "Total findings: N"
  count.

### Step 4: Approval Gate (The Review Composer)

You must guide the user through a strict, sequential, step-by-step dialogue.

**CRITICAL RULE**: You are forbidden from printing Phase 2 or Phase 3 until the user has responded
to the current phase. Do NOT provide a preview of the upcoming questions. Print ONLY the current
phase's question and then STOP.

**Phase 1: Finding Selection**

1. Present the "Proposed Inline Comments" table (exactly N rows).
2. Print the total count: "Total findings: N".
3. Ask ONLY this question:
   *"Which findings should be posted?*
   *[A] All findings*
   *[B] None (Manual review only)*
   *[C] Custom (e.g., '1, 3, 5')"*
4. **STOP AND WAIT** for the user's response.
5. If `[C]`, ask for the specific numbers and wait. Store the result as `selected_comments`.

**Phase 2: Action Selection**

1. ONLY after Phase 1 is answered, ask ONLY this question:
   *"What is the review action?*
   *[1] APPROVE*
   *[2] REQUEST_CHANGES*
   *[3] COMMENT"*
2. **STOP AND WAIT** for the user's response.
3. Map `1` $\to$ `APPROVE`, `2` $\to$ `REQUEST_CHANGES`, `3` $\to$ `COMMENT`. Store as
   `review_event`.

**Phase 3: Customization**

1. ONLY after Phase 2 is answered, ask ONLY this question:
   *"Would you like to add a custom summary note?*
   *[Y] Yes*
   *[N] No (Use AI-generated summary)"*
2. **STOP AND WAIT** for the user's response.
3. If `[Y]`, ask for the text and wait. Store as `custom_summary`.
4. If `[N]`, generate a professional summary based on the selected findings.

**Phase 4: Final Confirmation**

1. Present a final, concise summary for verification:
   *"Final Review Plan:*
   *- Findings: {selected_comments}*
   *- Event: {review_event}*
   *- Summary: {custom_summary or AI_summary}*
   *Proceed? [Y/N]"*
2. **STOP AND WAIT** for the final `Y/N`.

Only proceed to Step 5 if the user confirms with `Y`.

### Step 5: Execution & Error Handling

- **Auth Error**: If `gh` returns an authentication error, stop and tell the user to run
  `gh auth login`.
- **API Failure**: If the POST request to GitHub fails, print the intended comment body in the chat
  and instruct the user to post it manually.
- **Successful POST**:
    - Write approved bodies to temp files to avoid multiline quoting bugs.
    - POST to `/pulls/{pr}/comments` with `side=RIGHT` and `commit_id=<head_sha>`.
    - **Watermarking**: Append the watermark from `config.json` (fallback:
      `🤖 Auto-reviewed by the review-pr skill`).
    - Post summary review with normalized event (COMMENT, REQUEST_CHANGES, APPROVE).
    - Report back review URL + posted-vs-proposed counts.
