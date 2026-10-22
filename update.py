import os
import sys
import platform
import shutil
import json
import argparse
import glob

# --- UI Helpers ---
def print_header(text):
    print(f"\n{'='*60}\n{text.center(60)}\n{'='*60}")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def print_step(step, total, text):
    print(f"[{step}/{total}] {text}...", end="\r")

# --- Core Logic ---

def get_skill_version(skill_json_path):
    """Extracts version string from skill.json"""
    try:
        with open(skill_json_path, "r") as f:
            data = json.load(f)
            return data.get("version", "0.0.0")
    except Exception:
        return "0.0.0"

def backup_file(path):
    if os.path.exists(path):
        shutil.copy2(path, path + ".bak")

def update_skill(skill_name, target, repo_path):
    """Updates a specific skill for a specific target if a newer version exists."""
    skill_dir = os.path.join(repo_path, "skills", skill_name)
    skill_json = os.path.join(skill_dir, "skill.json")

    if not os.path.exists(skill_json):
        return "error", "skill.json missing"

    repo_version = get_skill_version(skill_json)
    home = os.path.expanduser("~")

    # Map target to destination path and source file
    target_map = {
        "claude": (os.path.join(home, ".claude", "commands", f"{skill_name}.md"), os.path.join(skill_dir, "command.md")),
        "copilot": (os.path.join(home, ".github", "skills", skill_name, "SKILL.md"), os.path.join(skill_dir, "SKILL.md")),
        "gemini": (os.path.join(home, ".gemini", "commands", f"{skill_name}.md"), os.path.join(skill_dir, "GEMINI.md")),
    }

    if target not in target_map:
        return "error", "Invalid target"

    dest, src = target_map[target]

    if not os.path.exists(dest):
        return "installed", f"Skill not found on system. Performing fresh install."

    # Note: Since the installed .md files don't contain the version,
    # we rely on the user's intent to update.
    # In a more complex system, we would store a .version file next to the .md.
    # For this prompt-based system, 'update' means 'sync with repo'.

    try:
        backup_file(dest)
        shutil.copy2(src, dest)
        return "updated", f"Updated to version {repo_version}"
    except Exception as e:
        return "error", str(e)

def main():
    parser = argparse.ArgumentParser(description="AI Skills Universal Updater")
    parser.add_argument("--target", choices=["claude", "copilot", "gemini", "all"], default="all", help="Target AI tool to update")
    parser.add_argument("--repo", type=str, default=".", help="Path to the ai-skills repo")
    parser.add_argument("--dry-run", action="store_true", help="Dry run - don't modify filesystem")

    args = parser.parse_args()
    repo_path = os.path.abspath(args.repo)

    print_header("AI Skills Update Engine")

    # Auto-discover all skills
    skills = [os.path.basename(d) for d in glob.glob(os.path.join(repo_path, "skills", "*"))
              if os.path.isdir(d) and os.path.basename(d) != "_template"]

    if not skills:
        print_error("No skills found in the repository to update.")
        return

    targets = []
    if args.target == "all" or args.target == "claude": targets.append("claude")
    if args.target == "all" or args.target == "copilot": targets.append("copilot")
    if args.target == "all" or args.target == "gemini": targets.append("gemini")

    total_updates = 0

    for target in targets:
        target_display = target.capitalize() if target != "claude" else "Claude Code"
        print(f"\nChecking {target_display}...")

        for i, skill in enumerate(skills, 1):
            print_step(i, len(skills), f"Syncing {skill}")

            if args.dry_run:
                print(f" [Dry-run] Would update {skill}")
                continue

            status, msg = update_skill(skill, target, repo_path)

            if status == "updated":
                print(f" ✅ {msg}")
                total_updates += 1
            elif status == "installed":
                print(f" 📦 {msg}")
                total_updates += 1
            else:
                print(f" ❌ Error: {msg}")

    print_header(f"Update Complete: {total_updates} files synced")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nUpdate cancelled by user. Exiting...")
        sys.exit(1)
