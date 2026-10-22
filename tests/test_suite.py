import os
import sys
import json
import subprocess
import argparse
import hashlib
import shutil
from pathlib import Path

# Add the repo root to sys.path so we can import the scripts as modules
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

def get_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def test_installer_logic():
    print("Testing Installer Logic...", end=" ")
    try:
        import install
        # Test a dry run to ensure no crashes
        # We pass the absolute repo root to avoid relative path issues in tests
        install.install_skill("review-pr", "all", repo_root, dry_run=True)
        print("✅ PASS")
    except Exception as e:
        print(f"❌ FAIL ({e})")

def test_checksum_generation():
    print("Testing Checksum Generation...", end=" ")
    test_file = Path(repo_root) / "test_temp.txt"
    test_file.write_text("test content")

    h1 = get_sha256(str(test_file))
    test_file.write_text("modified content")
    h2 = get_sha256(str(test_file))

    test_file.unlink()
    if h1 != h2:
        print("✅ PASS")
    else:
        print("❌ FAIL (hashes match for different content)")

def test_skill_scaffolding():
    print("Testing Skill Scaffolding...", end=" ")
    try:
        # Instead of importing the module, we run it as a subprocess to verify it works
        # This avoids the "no module named" issue if the file doesn't have a __init__.py
        # and tests the actual CLI entry point.
        test_skill_name = "test-scaffold-skill"
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        # Clean up any previous test runs
        test_dir = os.path.join(repo_root, "skills", test_skill_name)
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

        result = subprocess.run(
            [sys.executable, os.path.join(repo_root, "new-skill.py"), test_skill_name, "--desc", "test desc"],
            capture_output=True, text=True
        )

        if result.returncode == 0 and os.path.exists(test_dir):
            # Cleanup
            shutil.rmtree(test_dir)
            print("✅ PASS")
        else:
            print(f"❌ FAIL (Exit code: {result.returncode})")
    except Exception as e:
        print(f"❌ FAIL ({e})")

def main():
    print("\n" + "="*40)
    print("  AI-SKILLS DEVELOPER TEST SUITE")
    print("="*40 + "\n")

    test_installer_logic()
    test_checksum_generation()
    test_skill_scaffolding()

    print("\n" + "="*40)
    print("Tests Completed.")
    print("="*40)

if __name__ == "__main__":
    main()
