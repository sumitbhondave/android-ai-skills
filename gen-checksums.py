import os
import sys
import hashlib
import argparse
import glob
import subprocess

def get_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def main():
    parser = argparse.ArgumentParser(description="Generate/Verify CHECKSUMS.txt and SIGNATURE for ai-skills")
    parser.add_argument("--check", action="store_true", help="Verify existing checksums")
    parser.add_argument("--sign", action="store_true", help="Sign the CHECKSUMS.txt file using GPG")
    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.abspath(__file__))
    checksums_file = os.path.join(repo_root, "CHECKSUMS.txt")
    signature_file = os.path.join(repo_root, "CHECKSUMS.txt.asc")

    # Find all skill files except _template and the checksums file itself
    files = sorted(glob.glob(os.path.join(repo_root, "skills", "**", "*"), recursive=True))
    files = [f for f in files if os.path.isfile(f) and "_template" not in f]

    if args.check:
        if not os.path.exists(checksums_file):
            print("Error: CHECKSUMS.txt not found.")
            sys.exit(1)

        # 1. Verify the signature of the checksum file first
        if os.path.exists(signature_file):
            try:
                # This checks if the file is signed by a trusted key in the user's keyring
                subprocess.run(["gpg", "--verify", signature_file, checksums_file], check=True, capture_output=True)
                print("✅ Manifest signature verified.")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️  Warning: Manifest signature verification failed or gpg not found. Proceeding with checksums only.")
        else:
            print("ℹ️  No signature file found. Skipping signature verification.")

        with open(checksums_file, "r") as f:
            stored_checksums = f.read().splitlines()

        for file_path in files:
            rel_path = os.path.relpath(file_path, repo_root)
            current_hash = get_sha256(file_path)
            expected = f"{current_hash}  {rel_path}"
            if expected not in stored_checksums:
                print(f"FAIL: {rel_path} checksum mismatch!")
                sys.exit(1)
        print("✅ All checksums verified successfully.")

    elif args.sign:
        if not os.path.exists(checksums_file):
            print("Error: Please generate CHECKSUMS.txt first.")
            sys.exit(1)
        try:
            # Clearsign the file: creates a text file containing the signature and the original content
            subprocess.run(["gpg", "--clearsign", checksums_file], check=True)
            # We use the detached signature for the installer to check efficiently
            subprocess.run(["gpg", "--detach-sign", "-a", checksums_file], check=True)
            print(f"✅ Successfully signed {checksums_file}. Signature saved to {signature_file}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: GPG failed or is not installed. Please install gpg to sign the manifest.")
            sys.exit(1)

    else:
        with open(checksums_file, "w") as f:
            for file_path in files:
                rel_path = os.path.relpath(file_path, repo_root)
                f.write(f"{get_sha256(file_path)}  {rel_path}\n")
        print(f"Generated {checksums_file}")

if __name__ == "__main__":
    main()
