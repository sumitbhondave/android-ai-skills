import os
import sys
import platform
import shutil
import json
import argparse
import hashlib
import glob
import subprocess

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

def get_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def check_prereqs():
    """Verify required tools are installed, provide guidance if not."""
    print_header("Pre-flight Checks")
    missing = []

    # Check for gh CLI
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
        print_success("GitHub CLI (gh) is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("GitHub CLI (gh) is NOT installed")
        missing.append("gh")

    # Check for git
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        print_success("Git is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Git is NOT installed")
        missing.append("git")

    if missing:
        print("\n--- How to fix ---")
        os_type = platform.system()
        if os_type == "Darwin":
            print("Run: brew install gh git")
        elif os_type == "Windows":
            print("Run: winget install GitHub.cli Git.Git")
        else:
            print("Please install gh and git using your system package manager.")
        print("-" * 20)
        return False

    print_success("All prerequisites met!")
    return True

def backup_file(path):
    if os.path.exists(path):
        shutil.copy2(path, path + ".bak")

def verify_skill_integrity(skill_name, repo_path):
    """Verify all files in the skill folder against CHECKSUMS.txt and verify manifest signature"""
    checksums_path = os.path.join(repo_path, "CHECKSUMS.txt")
    signature_file = os.path.join(repo_path, "CHECKSUMS.txt.asc")

    if not os.path.exists(checksums_path):
        print_info("CHECKSUMS.txt not found; skipping integrity check.")
        return True

    # 1. Manifest Signature Check
    if os.path.exists(signature_file):
        try:
            subprocess.run(["gpg", "--verify", signature_file, checksums_path], check=True, capture_output=True)
            print_success("Manifest signature verified. The source is authentic.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_info("⚠️  Could not verify manifest signature (GPG missing or key not trusted).")
            print_info("    Installation continues, but authenticity is not guaranteed.")
    else:
        print_info("No manifest signature found. Authenticity not verified.")

    with open(checksums_path, "r") as f:
        stored = f.read().splitlines()

    skill_dir = os.path.join(repo_path, "skills", skill_name)
    for root, _, files in os.walk(skill_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, repo_path)
            actual_hash = get_hash(full_path)
            expected = f"{actual_hash}  {rel_path}"
            if expected not in stored:
                print_error(f"Integrity check failed for {rel_path}!")
                return False
    return True

def install_skill(skill_name, target, repo_path, dry_run=False):
    skill_dir = os.path.join(repo_path, "skills", skill_name)
    if not os.path.isdir(skill_dir):
        print_error(f"Skill {skill_name} not found in {skill_dir}")
        return False

    if not verify_skill_integrity(skill_name, repo_path):
        print_error(f"Skill {skill_name} is corrupted or tampered with. Aborting.")
        return False

    os_type = platform.system()
    home = os.path.expanduser("~")

    targets = []
    if target == "all" or target == "claude":
        targets.append(("Claude Code", os.path.join(home, ".claude", "commands", f"{skill_name}.md"),
                        os.path.join(skill_dir, "command.md")))
    if target == "all" or target == "copilot":
        targets.append(("GitHub Copilot", os.path.join(home, ".github", "skills", skill_name, "SKILL.md"),
                        os.path.join(skill_dir, "SKILL.md")))
    if target == "all" or target == "gemini":
        targets.append(("Gemini", os.path.join(home, ".gemini", "commands", f"{skill_name}.md"),
                        os.path.join(skill_dir, "GEMINI.md")))

    if not targets:
        print_error("No targets specified or supported on this OS.")
        return False

    print(f"\nInstalling {skill_name}...")
    for i, (name, dest, src) in enumerate(targets, 1):
        print_step(i, len(targets), f"Applying {name} variant")
        if dry_run:
            print(f" [Dry-run] {src} -> {dest}")
            continue

        try:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            backup_file(dest)
            shutil.copy2(src, dest)
            print(f" Done! -> {dest}")
        except Exception as e:
            print(f" Error installing {name}: {e}")
            return False

    return True

def main():
    parser = argparse.ArgumentParser(description="AI Skills Universal Installer")
    parser.add_argument("--list", action="store_true", help="List available skills")
    parser.add_argument("--skill", type=str, help="Install a specific skill")
    parser.add_argument("--all", action="store_true", help="Install all skills")
    parser.add_argument("--target", choices=["claude", "copilot", "gemini", "all"], default="all", help="Target AI tool")
    parser.add_argument("--repo", type=str, default=".", help="Path to the ai-skills repo")
    parser.add_argument("--dry-run", action="store_true", help="Dry run - don't modify filesystem")
    parser.add_argument("--skip-checks", action="store_true", help="Skip pre-flight prerequisite checks")

    args = parser.parse_args()
    repo_path = os.path.abspath(args.repo)

    if not args.skip_checks:
        if not check_prereqs():
            print("\n⚠️  Prerequisites missing. You can continue with --skip-checks, but the skills may not work.")

    if args.list:
        print_header("Available AI Skills")
        skills = [os.path.basename(d) for d in glob.glob(os.path.join(repo_path, "skills", "*"))
                  if os.path.isdir(d) and os.path.basename(d) != "_template"]
        for s in skills:
            print(f" 📦 {s}")
        return

    if args.skill:
        if install_skill(args.skill, args.target, repo_path, args.dry_run):
            print_header("Installation Complete")
            print_success(f"Skill '{args.skill}' is now active!")
            print("\nNext Steps:")
            print(" 1. Authenticate: `gh auth login`")
            print(" 2. Use it: `/review-pr 7` (or your specific skill command)")
        return

    if args.all:
        skills = [os.path.basename(d) for d in glob.glob(os.path.join(repo_path, "skills", "*"))
                  if os.path.isdir(d) and os.path.basename(d) != "_template"]
        for s in skills:
            install_skill(s, args.target, repo_path, args.dry_run)
        print_header("All Skills Installed")
        return

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user. Exiting...")
        sys.exit(1)
