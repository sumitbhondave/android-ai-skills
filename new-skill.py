import os
import sys
import argparse
import shutil
from datetime import datetime

def scaffold_skill(name, description, aliases, repo_root):
    template_dir = os.path.join(repo_root, "skills", "_template")
    skill_dir = os.path.join(repo_root, "skills", name)

    if os.path.exists(skill_dir):
        print(f"Error: Skill {name} already exists.")
        sys.exit(1)

    os.makedirs(skill_dir)

    # Tokens for replacement
    tokens = {
        "{{SKILL_NAME}}": name,
        "{{DESCRIPTION}}": description,
        "{{ALIASES}}": f'["{",".join(aliases)}"]' if isinstance(aliases, list) else f'["{aliases}"]',
        "{{COMMAND}}": f"/{name}",
        "{{VERSION}}": "0.1.0",
        "{{DATE}}": datetime.now().strftime("%Y-%m-%d"),
        "{{LIMITATIONS}}": "TBD",
        "{{REQUIREMENTS}}": "TBD",
        "{{ARG_HINT}}": "TBD"
    }

    for filename in os.listdir(template_dir):
        src_path = os.path.join(template_dir, filename)
        dest_path = os.path.join(skill_dir, filename)

        with open(src_path, "r") as f:
            content = f.read()

        for token, value in tokens.items():
            content = content.replace(token, value)

        with open(dest_path, "w") as f:
            f.write(content)

    print(f"Successfully scaffolded skill {name} at {skill_dir}")

def main():
    parser = argparse.ArgumentParser(description="Scaffold a new AI skill from template")
    parser.add_argument("name", help="Name of the new skill")
    parser.add_argument("--desc", required=True, help="Description of the skill")
    parser.add_argument("--aliases", default="", help="Comma-separated aliases (e.g. /x,/y)")

    args = parser.parse_args()
    repo_root = os.path.dirname(os.path.abspath(__file__))

    aliases_list = args.aliases.split(",") if args.aliases else []
    scaffold_skill(args.name, args.desc, aliases_list, repo_root)

if __name__ == "__main__":
    main()
