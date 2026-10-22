import os
import sys
import platform
import shutil
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

# --- Core Logic ---

def uninstall_skills(repo_path, target="all", dry_run=False):
    """Remove all skills installed by this repo from the target AI tools."""
    home = os.path.expanduser("~")

    # Auto-discover all skill names from the repo to ensure we clean up everything
    skills = [os.path.basename(d) for d in glob.glob(os.path.join(repo_path, "skills", "*"))
              if os.path.isdir(d) and os.path.basename(d) != "_template"]

    # Define where the files are located based on the tool
    tool_paths = []
    if target == "all" or target == "claude":
        tool_paths.append(("Claude Code", os.path.join(home, ".claude", "commands")))
    if target == "all" or target == "copilot":
        tool_paths.append(("GitHub Copilot", os.path.join(home, ".github", "skills")))
    if target == "all" or target == "gemini":
        tool_paths.append(("Gemini", os.path.join(home, ".gemini", "commands")))

    if not tool_paths:
        print_error("No targets specified or supported on this OS.")
        return

    print_header("Universal Uninstallation")

    for tool_name, base_path in tool_paths:
        print(f"\nCleaning {tool_name}...")
        if not os.path.exists(base_path):
            print_info(f" Path {base_path} does not exist. Skipping.")
            continue

        removed_count = 0
        for skill in skills:
            # Claude and Gemini use flat files (.md)
            # Copilot uses subdirectories
            paths_to_check = [
                os.path.join(base_path, f"{skill}.md"),
                os.path.join(base_path, skill) # For Copilot dirs
            ]

            for p in paths_to_check:
                if os.path.exists(p):
                    if dry_run:
                        print(f" [Dry-run] Would remove: {p}")
                        continue

                    try:
                        if os.path.isdir(p):
                            shutil.rmtree(p)
                        else:
                            os.remove(p)

                        # Verify removal
                        if not os.path.exists(p):
                            removed_count += 1
                    except Exception as e:
                        print_error(f" Failed to remove {p}: {e}")

        if removed_count > 0:
            print_success(f"Removed {removed_count} skill(s) from {tool_name}.")
        else:
            print_info(f"No matching skills found for {tool_name}.")

    print_header("Uninstallation Complete")

def main():
    parser = argparse.ArgumentParser(description="AI Skills Universal Uninstaller")
    parser.add_argument("--target", choices=["claude", "copilot", "gemini", "all"], default="all", help="Target AI tool to clean")
    parser.add_argument("--repo", type=str, default=".", help="Path to the ai-skills repo (to discover skill names)")
    parser.add_argument("--dry-run", action="store_true", help="Dry run - don't modify filesystem")

    args = parser.parse_args()
    repo_path = os.path.abspath(args.repo)

    uninstall_skills(repo_path, args.target, args.dry_run)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nUninstallation cancelled by user. Exiting...")
        sys.exit(1)
