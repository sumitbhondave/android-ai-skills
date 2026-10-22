# review-pr

Review an already-raised GitHub PR (or a local `.diff`), surface bugs/security/perf/quality issues,
and post inline comments ONLY after user approval.

## 5-Step Summary

1. **Input**: Detects if input is a live PR (via `gh`) or a local file.
2. **Map**: Builds an anti-hallucination line map to ensure comments land on added lines.
3. **Analyze**: Exhaustive audit across 6 categories (Bugs, Security, Perf, etc.).
4. **Gate**: User selects which comments to post and the review event.
5. **Post**: Applies comments via GitHub API with a mandatory watermark.

## Limitations

- Requires `gh` CLI for live PRs.
- Only supports "Right-side" (new code) comments.
- Analysis is based on the provided diff; full repo context is preferred but not always available.

## Required `gh` Scopes

- `repo` (read/write)
- `pull_requests` (read/write)
