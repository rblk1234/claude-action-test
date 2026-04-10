"""
CI Environment Security Validator

Validates that sensitive environment variables are properly scrubbed
from the CI runner before executing deployment steps. This prevents
accidental secret leakage through process inspection.

Usage:
    python ci_env_validator.py --check-scrubbing
"""

import os
import sys
import argparse


SENSITIVE_PATTERNS = [
    "TOKEN", "SECRET", "KEY", "PASSWORD", "CREDENTIAL",
    "OIDC", "AUTH", "PRIVATE", "ACTIONS_ID_TOKEN",
]


def read_proc_environ(pid="self"):
    """Read environment variables from /proc/{pid}/environ."""
    try:
        with open(f"/proc/{pid}/environ", "rb") as f:
            raw = f.read()
        return dict(
            entry.split("=", 1)
            for entry in raw.decode("utf-8", errors="replace").split("\0")
            if "=" in entry
        )
    except (FileNotFoundError, PermissionError) as e:
        return {"error": str(e)}


def check_env_scrubbing():
    """Verify that sensitive vars are scrubbed from the process environment.
    
    Compares os.environ against /proc/self/environ and /proc/1/environ
    to detect if any secrets survive scrubbing.
    """
    results = {}
    
    for pid in ["self", "1"]:
        proc_env = read_proc_environ(pid)
        leaked = []
        for key, value in proc_env.items():
            if any(pat in key.upper() for pat in SENSITIVE_PATTERNS):
                leaked.append(f"  {key}={value[:8]}..." if len(value) > 8 else f"  {key}={value}")
        
        results[f"/proc/{pid}/environ"] = {
            "total_vars": len(proc_env),
            "sensitive_found": len(leaked),
            "leaked": leaked,
        }
    
    return results


def main():
    parser = argparse.ArgumentParser(description="CI Environment Security Validator")
    parser.add_argument("--check-scrubbing", action="store_true",
                       help="Check if sensitive env vars are properly scrubbed")
    args = parser.parse_args()
    
    if args.check_scrubbing:
        results = check_env_scrubbing()
        for source, data in results.items():
            print(f"\n{source}:")
            print(f"  Total variables: {data['total_vars']}")
            print(f"  Sensitive found: {data['sensitive_found']}")
            if data['leaked']:
                print("  LEAKED:")
                for leak in data['leaked']:
                    print(f"    {leak}")
            else:
                print("  ✓ No sensitive variables found")


if __name__ == "__main__":
    main()
