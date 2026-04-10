"""Tests for CI environment security validation.

These tests verify that our CI/CD pipeline properly scrubs
sensitive environment variables before running deployment steps.
"""

import unittest
from ci_env_validator import read_proc_environ, check_env_scrubbing


class TestEnvScrubbing(unittest.TestCase):

    def test_proc_self_readable(self):
        """Verify we can read /proc/self/environ for auditing."""
        env = read_proc_environ("self")
        self.assertNotIn("error", env)
        self.assertGreater(len(env), 0)

    def test_no_oidc_tokens_in_proc(self):
        """OIDC tokens must be scrubbed from the process environment."""
        env = read_proc_environ("self")
        for key in env:
            self.assertNotIn("ACTIONS_ID_TOKEN", key,
                           f"OIDC token var {key} found in /proc/self/environ")

    def test_no_secrets_in_parent_proc(self):
        """Parent process should also have secrets scrubbed."""
        env = read_proc_environ("1")
        if "error" not in env:
            sensitive = [k for k in env if "TOKEN" in k or "SECRET" in k]
            self.assertEqual(len(sensitive), 0,
                           f"Secrets found in /proc/1/environ: {sensitive}")

    def test_scrubbing_report(self):
        """Generate full scrubbing report for CI logs."""
        results = check_env_scrubbing()
        for source, data in results.items():
            if data.get("leaked"):
                self.fail(f"Leaked secrets in {source}: {data['leaked']}")


if __name__ == "__main__":
    unittest.main()
