# Security Policy

## Trust Story

This library provides prompts that orchestrate your local tools. We prioritize local execution and
transparency.

### 1. Tokens & Permissions

- **No Secret Storage**: This repo never asks for, stores, or transmits your API tokens.
- **Keyring Reliance**: All skills rely on the `gh` CLI OS keyring.
- **Least Privilege**: We recommend the minimum scopes: `repo` (read/write) and `pull_requests`
  (read/write).

### 2. Data Exfiltration

- **Zero Telemetry**: No data is sent to any server other than `api.github.com` via your own `gh`
  CLI.
- **Local First**: Analysis happens within your AI tool's context.

### 3. Repo Writes

- **Human-in-the-loop**: No comments or reviews are posted to GitHub without an explicit approval
  gate (Step 4). You see every comment before it is published.

### 4. Authenticity & Integrity

- **Checksums**: Every skill file has a SHA-256 hash in `CHECKSUMS.txt`. The installer verifies
  these before copying.
- **Pinning**: We recommend installing from a signed release TAG rather than the `main` branch.
- **CI Verification**: Our GitHub Actions validate schemas, compile Python scripts, and verify
  checksums on every commit.

### 5. Vulnerability Reporting

If you find a security flaw, please open an issue or contact the maintainer. We aim to respond
within 3 business days.

**Note**: Skills are prompts. We avoid `eval()`, `curl | bash`, or obfuscated code within prompts to
ensure you can audit exactly what the AI is being told to do.
