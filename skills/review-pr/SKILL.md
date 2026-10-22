---
name: review-pr
description: Review a GitHub PR for bugs, security, and performance issues.
argument-hint: "PR number or URL (e.g., 7 or https://github.com/owner/repo/pull/7)"
---

# review-pr for GitHub Copilot

## Instructions

Refer to the detailed execution flow in `command.md`. When reaching the Approval Gate (Step 4), use
the `vscode_askQuestions` tool to prompt the user for:

1. Comment Selection (None/All/Custom)
2. Review Event (Comment/Request Changes/Approve)

Follow the same analysis and watermarking logic as the Claude Code variant.
