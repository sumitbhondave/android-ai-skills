# Android AI Skills

A public, open-source library of prompt-based "skills" (slash-commands) designed to work across **Claude Code**, **GitHub Copilot**, and **Gemini**, specifically tailored for Android development.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Quickstart

Get your first AI skill running in 30 seconds:

```bash
# 1. Clone the repo
git clone https://github.com/sumitbhondave/android-ai-skills
cd android-ai-skills

# 2. Install the review-pr skill
python3 install.py --skill review-pr

# 3. Authenticate with GitHub
gh auth login

# 4. Use it! (In Claude Code inside your Android project)
# You can use a PR number:
/review-pr 7

# Or a full GitHub PR URL:
/review-pr https://github.com/owner/repo/pull/7
```

## 🛠 Available Skills

| Skill | Command | Description |
| :--- | :--- | :--- |
| **review-pr** | `/review-pr` | Deep audit of GitHub PRs for bugs, security, and performance. |

## 📖 How to Use

### Claude Code
Skills are installed as `.md` files in `~/.claude/commands/`. Once installed, simply type the command (e.g., `/review-pr 7`) in your terminal.

### GitHub Copilot
Skills are installed as `SKILL.md` files in your `.github/skills/` directory. Trigger them via the Copilot chat.

### Gemini
Skills are provided as paste-ready prompts. Copy the content of `GEMINI.md` and paste it into Gemini along with your code/diff for an analysis-only review.

### 🔒 Security & Authenticity (GPG)
To ensure you are installing untampered skills, the library uses GPG-signed manifests. 

**Do I need to do anything?**
- **No.** By default, the installer will verify the checksums. If it cannot find your GPG public key or GPG is not installed, it will show a warning but **still allow the installation to proceed** so you can get started immediately.

**For Advanced Users (Verify Authenticity):**
If you want to mathematically prove the skills come from the official maintainer:
1. Install GPG (`brew install gnupg` on macOS).
2. Import the maintainer's public key: `gpg --import my-public-key.asc`.
3. Now, `install.py` will show a `✅ Manifest signature verified` message.

### ⚙️ Customization (Optional)
The library comes with a `config.json` file that allows you to personalize the AI's behavior. If you don't touch it, the skills will use high-quality professional defaults.

**What you can customize:**
- **Watermark**: Change the text appended to AI comments (e.g., `🚀 Audited by MyTeam`).
- **Default Profile**: Change the default analysis focus (e.g., set to `security` for a security-first audit).
- **Custom Profiles**: Define your own focus areas for different types of reviews.

### 🧹 Cleanup
To remove all skills installed by this library from your system:
```bash
python3 uninstall.py
```

### 🔄 Updating Skills
As the library evolves, new versions of skills are released. To sync your local installations with the latest versions from the repository, run:
```bash
python3 update.py
```
This will automatically update all skills across all your AI tools. No restart is required; changes take effect immediately.

## 🤝 Contributing
Want to add a new skill? It's a 3-step flow:
1. **Scaffold**: Run `python3 new-skill.py my-skill --desc "..." --aliases "/m"`
2. **Develop**: Edit the prompts in `skills/my-skill/` (focus on Step 3 analysis).
3. **Submit**: Run `python3 gen-checksums.py` and open a PR.
