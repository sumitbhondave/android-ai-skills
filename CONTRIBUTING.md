# Contributing to AI Skills

Thank you for wanting to contribute! We keep the process simple so you can focus on the prompt
engineering.

## 3-Step Addition Flow

### 1. Scaffold

Use the built-in scaffolder to create the folder structure and template files:

```bash
python3 new-skill.py <skill-slug> --desc "Short description" --aliases "/alias1,/alias2"
```

Example: `python3 new-skill.py a11y-audit --desc "WCAG accessibility check" --aliases "/a11y"`

### 2. Develop

Navigate to `skills/<skill-slug>/` and edit the variants:

- **`command.md`**: The core logic. Most of the plumbing (input mode, mapping, approval gate) is
  already there. Focus your effort on **Step 3 (Analysis)**.
- **`SKILL.md`**: Adapt for Copilot's `vscode_askQuestions`.
- **`GEMINI.md`**: Ensure it's clear that it's analysis-only.
- **`skill.json`**: Update parameters and version.

### 3. Submit

Before opening a PR, you must ensure the skill is stable and the manifest is updated:

1. **Test your skill**: While the skill is a prompt, ensure your logic is sound. If you modified the
   installer or scaffolder, run the test suite:
   ```bash
   python3 tests/test_suite.py
   ```
2. **Update Manifest**: Update the authenticity checksums:
   ```bash
   python3 gen-checksums.py
   ```
3. **Push**: Commit your changes, push to a branch, and open a PR with a description of the skill's
   utility.
