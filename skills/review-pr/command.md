# review-pr Prompt (Claude Code)

## Execution Instructions

### Step 0: Initialization

- NO telemetry or consent gate. Proceed directly to input analysis.

### Step 1: Determine Input Mode

- If input is a GitHub URL or PR number $\to$ **Live PR Mode**.
- If input is a file path, `.diff`, or `.patch` $\to$ **Local Analysis Mode**.

### Step 2: Context & Mapping (Live Mode)

- **PR Status Check**: Use `gh pr view <pr> --json number,title,state,isDraft,headRefOid,author` to check status. Stop if NOT OPEN or is a draft. Store `headRefOid` as `$HEAD_SHA` (must be used as `commit_id` when posting inline comments).
- **PR Author vs Reviewer Check (Self-Review Detection)**:
  1. Retrieve current authenticated user (reviewer): `reviewer=$(gh api user --jq '.login')`
  2. Retrieve PR author username: `pr_author=$(gh pr view <pr> --json author --jq '.author.login')`
  3. Compare `reviewer` and `pr_author` (case-insensitively).
  4. Set `is_self_review = True` **ONLY** if `reviewer == pr_author`.
  5. **CRITICAL RULE**: Do NOT confuse the repository owner (the user/organization in the repo URL `github.com/{owner}/{repo}`) with the PR author (`pr_author`). Even if `reviewer` is the owner of the repository, if the PR was opened by a different developer (`pr_author != reviewer`), `is_self_review` MUST be `False`. Repository owners reviewing PRs submitted by other contributors CAN formally approve or request changes.
- **Empty Diff Check**: If the diff is empty or contains no changed lines, ask the user to clarify the PR/branch or check if the PR has been merged/emptied.
- **Large PR Batching Strategy**: If the PR diff is unusually large (>1,000 changed lines or >30 files), audit files in logical batches (e.g., Build/Gradle configuration first, then core domain models, then UI components) while maintaining mandatory per-file exhaustion.
- Fetch the diff and save to a temporary file.

- **ACCURACY FIRST: BUILD INTEGRITY AUDIT**: If the diff contains changes to `gradle/`, `build.gradle`, `build.gradle.kts`, `libs.versions.toml`, or `gradle-wrapper.properties`, you MUST execute an "Evidence-Based Audit":
    1. **Verification Mandate**: You are strictly forbidden from flagging a version as "wrong" or "non-existent" based on internal memory.
    2. **Authoritative Source Check**: For every updated version, use `WebFetch` to verify existence on official sources (Android Developers, Gradle, Kotlin release pages).
    3. **Proof Requirement**: If you cannot verify a version via official sources, you may flag it, but you MUST include the URL of the page you checked as evidence.
    4. **Coupling Check**: Verify that tightly coupled tools (e.g., KSP $\leftrightarrow$ Kotlin, AGP $\leftrightarrow$ Gradle Wrapper) align according to official compatibility matrices.
    5. **Verdict**: If an official source confirms a mismatch or if a version is truly unverified after a search, create a `Blocker` finding.

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
            if current_file != '/dev/null':
                line_map[current_file] = set()
            line_num = 0
        elif line.startswith('@@'):
            match = re.search(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
            if match:
                line_num = int(match.group(1)) - 1
        elif line.startswith('+') and not line.startswith('+++'):
            line_num += 1
            if current_file and current_file != '/dev/null':
                line_map[current_file].add(line_num)
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
- **Severity Level Decision Parameters**:
    - **🚨 BLOCKER (P0 / Build-Breaking)**: Prevents compilation, packaging, or app startup. Zero workaround. Examples: Incompatible AGP / Kotlin / KSP / Gradle wrapper versions, missing required manifest attributes (`android:exported` on Android 12+), unresolved compilation/symbol errors.
    - **🔴 CRITICAL (P1 / High Impact)**: Causes runtime crashes, security vulnerabilities (OWASP), data loss/corruption, or ANRs. Examples: NPEs or unhandled exceptions on UI thread, Main Thread disk/network I/O, missing Room DB migration, hardcoded API keys/secrets in repo, unsafe Intent redirection.
    - **🟠 MAJOR (P2 / Medium-High)**: Significant logic errors, performance bottlenecks, race conditions, or architecture violations. Examples: Incorrect ViewModel state flow emissions, memory leaks holding `Activity`/`Context`, Jetpack Compose unnecessary recomposition loops (missing `key` in `LazyColumn`), unsafe shared mutable state without mutex/atomics across coroutines.
    - **🟡 MINOR (P3 / Low Impact)**: Minor maintainability issues, code smells, or non-critical edge cases. Examples: Deprecated API usage, hardcoded strings (missing `strings.xml`), hardcoded dimensions (missing `dp`/`sp`), suboptimal Kotlin scope functions, missing edge-case validation.
    - **💡 SUGGESTION / NIT (P4 / Info)**: Readability, naming conventions, KDoc improvements, or optional refactoring ideas.
- **Complexity Scoring**: Compute Cyclomatic + Cognitive complexity. Provide a "Suggested Refactor"
  block if Medium+.
- **Constraints**: Do NOT flag pre-existing code, linter nits, or ungrounded findings.
- **Output**: `SEVERITY file:line — description`. Compile findings with a "Total findings: N"
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
   *[1] All findings*
   *[2] None (Manual review only)*
   *[3] Custom (e.g., '1, 3, 5')"*
4. **STOP AND WAIT** for the user's response.
5. If `[3]`, ask for the specific numbers and wait. Store the result as `selected_comments`.

**Phase 2: Action Selection**

1. ONLY after Phase 1 is answered, ask ONLY this question:
   - If `is_self_review` is TRUE:
     *"Since you are the author of this PR (`{pr_author}`), GitHub restricts self-approval or requesting changes on your own PR.*
     *What is the review action?*
     *[1] POST AS COMMENT"*
   - If `is_self_review` is FALSE:
     *"What is the review action?*
     *[1] APPROVE*
     *[2] REQUEST_CHANGES*
     *[3] COMMENT"*
2. **STOP AND WAIT** for the user's response.
3. Map `1` $\to$ `APPROVE` (if not self-review) or `COMMENT` (if self-review), `2` $\to$ `REQUEST_CHANGES`, `3` $\to$ `COMMENT`. Store as
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

- **STRICT EXECUTION RULE**: You MUST execute all `gh` commands directly using your terminal tools. NEVER tell the user to "run the following commands in your terminal" for posting comments, labeling, or approving.

- **Auth Error**: If `gh` returns an authentication error, stop and tell the user to run `gh auth login`.

- **Unified Execution Pipeline (Linear Order)**:
  1. **Post Inline Comments**: Execute `gh api` calls for selected findings using the `headRefOid` (`head_sha`) retrieved in Step 2:
     ```bash
     gh api repos/{owner}/{repo}/pulls/{pr}/comments \
       -f body="$COMMENT_BODY" \
       -f commit_id="$HEAD_SHA" \
       -f path="$FILE_PATH" \
       -F line=$LINE_NUM \
       -f side="RIGHT"
     ```
     - **Grouping Rule**: If multiple findings occur in the same file and are related (e.g., multiple Build Integrity issues), you MUST combine them into a single, well-formatted comment using a bulleted list. Do NOT spam the PR with multiple small comments for the same issue type.
     - **CRITICAL**: If any inline post fails (e.g., 422 Validation Failed/line resolution error), you MUST print a high-visibility warning block in the chat: 
       *"⚠️ CRITICAL: Inline comments failed to post due to GitHub line-mapping errors. These findings were NOT posted to the PR. Please see the summary below for the details."*
     - **NO BACKUP COMMENTS**: You are STRICTLY FORBIDDEN from posting these findings as a general PR comment to avoid duplication.
  2. **Apply Label (Independent Task)**: Check if the label exists in the repository first; if missing, create it before applying:
     ```bash
     gh label list --json name --jq '.[].name' | grep -q "^after-ai-reviewed 🤖$" || \
       gh label create "after-ai-reviewed 🤖" --color "0E8A16" --description "Reviewed by AI Skill"

     gh pr edit <pr> --add-label "after-ai-reviewed 🤖"
     ```
     This must happen regardless of the approval outcome.
  3. **The Integrated Verdict (The One-Post Rule)**: 
     - **Construct the Body**: The final review body MUST be a rich, visually engaging GitHub Markdown document using GitHub-native Callout Alerts (`> [!CAUTION]`, `> [!WARNING]`, `> [!TIP]`), summary tables, collapsible details, and code diff blocks:
       
       - **Header (GitHub Alert Callout)**:
         - If Blocker/Critical findings > 0:
           ```markdown
           > [!CAUTION]
           > ### 🤖 AI Code Review Verdict: REQUIRES ATTENTION
           > Critical build or runtime safety issues detected in this PR. Merge is blocked until resolved.
           ```
         - If Major/Minor findings > 0 (No Blockers/Critical):
           ```markdown
           > [!WARNING]
           > ### 🤖 AI Code Review Verdict: REVIEW COMMENTS
           > Code quality, performance, or logic improvements identified. Please review findings before merging.
           ```
         - If 0 findings:
           ```markdown
           > [!TIP]
           > ### 🤖 AI Code Review Verdict: PASSED
           > ✅ **Build & Code Audit Passed**: No issues were identified. This PR meets all quality and integrity standards.
           ```

       - **Summary Breakdown Table**:
         Include a clean breakdown table summarizing findings by severity level:
         | Severity | Status | Findings |
         | :--- | :---: | :---: |
         | 🚨 **Blocker** | ❌ Failed / ✅ Passed | **N** |
         | 🔴 **Critical** | ❌ Failed / ✅ Passed | **N** |
         | 🟠 **Major** | ⚠️ Review / ✅ Passed | **N** |
         | 🟡 **Minor** | ℹ️ Notice / ✅ Passed | **N** |
         | 💡 **Suggestion** | 💡 Info / ✅ Passed | **N** |

       - **Rich Collapsible Detailed Analysis (`<details>`)**:
         Group findings into structured collapsible sections:
         - For **BLOCKER** and **CRITICAL** issues: Use **expanded** details (`<details open>`).
         - For **MAJOR**, **MINOR**, and **SUGGESTION** issues: Use **collapsed** details (`<details>`).
         - Structure inside each `<details>` block:
````markdown
<details open>
<summary><b>🚨 [BLOCKER] Incompatible KSP Version</b> (<code>libs.versions.toml:21</code>)</summary>

<br>

> **Impact**: Explanation of runtime or compilation impact.

```diff
- problematic_code_line
+ recommended_fix_line
```

* **Action**: Concise, step-by-step recommendation.
</details>
````

       - **Footer**: Add the user's custom summary note (if provided) below a horizontal rule `---` and the attribution `🤖 Generated with [Claude Code](https://claude.com/claude-code)` at the bottom.

     - **Requirement**: The AI's detailed analysis must be preserved. The user's custom note AUGMENTS the AI's summary; it DOES NOT replace it.
     - **Execute**: Run the `review_event` command (APPROVE, REQUEST_CHANGES, or COMMENT) using this Integrated Body.
     - **Fallback Logic**: If `gh pr review --approve` or `--request-changes` fails (due to permissions, author restrictions, or branch protection):
       - Catch the error and inform the user: *"Formal status was blocked by GitHub/repository settings; automatically falling back to a general review comment."*
       - Immediately execute `gh pr review --comment` using the same Integrated Body.
     - **Constraint**: Only ONE summary-level post is allowed on the PR.

- **API Failure**: Only if the `Bash` tool fails to communicate with the API entirely, print the intended body and instruct the user to post it manually.

- **Successful Completion**:
    - Report back the final review URL + posted-vs-proposed counts.
    - Confirm that the `after-ai-reviewed 🤖` label was applied.

### Step 6: Cleanup

- **Purge Temporary Files**: Immediately after reporting the successful completion, execute a command to delete all temporary files created during this session (e.g., `.diff` files, `map_diff.py`, and any other transient mapping files).
- **Verification**: Confirm to the user that the working directory has been cleaned.
