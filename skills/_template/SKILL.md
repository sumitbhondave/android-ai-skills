---
name: {{SKILL_NAME}}
description: {{DESCRIPTION}}
argument-hint: {{ARG_HINT}}
---

# {{SKILL_NAME}} for GitHub Copilot

## Instructions
Refer to the detailed execution flow in `command.md`.
When reaching the Approval Gate (Step 4), use the `vscode_askQuestions` tool to prompt the user for:
1. Comment Selection (None/All/Custom)
2. Review Event (Comment/Request Changes/Approve)

Follow the same analysis and watermarking logic as the Claude Code variant.
