"""Mechanical checks; real skill behavior is evaluated separately."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from inspect_repo import inventory
from validate_setup import validate


class HelperChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agentic-helper-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes()
                for p in self.root.rglob("*") if p.is_file() and not p.is_symlink()}

    def configured(self):
        self.write("AGENTS.md", "Read [handoff](docs/HANDOFF.md).\n")
        self.write("CLAUDE.md", "@AGENTS.md\n\nKeep custom user rules.\n")
        self.write("docs/HANDOFF.md", "Checks have not been run.\n")

    def test_empty_repository_reports_missing_entry_points(self):
        result = validate(self.root, ["codex", "claude"])
        self.assertFalse(result["ok"])
        self.assertEqual(len(result["errors"]), 2)
        self.assertEqual(inventory(self.root)["paths"], [])

    def test_configured_repo_and_repeat_are_read_only(self):
        self.configured()
        before = self.snapshot()
        first = validate(self.root, ["codex", "claude"], ["docs/HANDOFF.md"])
        self.assertTrue(first["ok"])
        self.assertEqual(first, validate(self.root, ["codex", "claude"], ["docs/HANDOFF.md"]))
        self.assertEqual(before, self.snapshot())

    def test_nested_claude_import_and_custom_rules(self):
        self.write("AGENTS.md", "Shared rules.\n")
        self.write(".claude/CLAUDE.md", "@../AGENTS.md\n\nPreserve my custom commands.\n")
        before = self.snapshot()
        self.assertTrue(validate(self.root, ["codex", "claude"],
                                 claude_file=".claude/CLAUDE.md")["ok"])
        self.assertEqual(before, self.snapshot())

    def test_helpers_never_execute_failing_check(self):
        self.configured()
        self.write("scripts/check.sh", "#!/bin/sh\ntouch EXECUTED\nexit 7\n")
        before = self.snapshot()
        self.assertIn("scripts/check.sh", inventory(self.root)["paths"])
        self.assertTrue(validate(self.root, ["codex", "claude"])["ok"])
        self.assertFalse((self.root / "EXECUTED").exists())
        self.assertEqual(before, self.snapshot())

    def test_missing_link_and_cli_exit(self):
        self.write("AGENTS.md", "Read [spec](docs/missing.md).\n")
        command = [sys.executable, "-B", str(SCRIPTS / "validate_setup.py"),
                   str(self.root), "--agents", "codex"]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["ok"])
        self.write("docs/missing.md", "Requirements.\n")
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)

    def test_external_link_and_import_are_not_read(self):
        self.write("AGENTS.md", "[outside](../outside.md)\n")
        self.write("CLAUDE.md", "@../outside.md\n")
        result = validate(self.root, ["codex", "claude"])
        self.assertFalse(result["ok"])
        self.assertNotIn("outside.md", result["checked"])

    def test_external_symlink_is_rejected(self):
        try:
            (self.root / "CLAUDE.md").symlink_to(self.root.parent / "outside.md")
        except (OSError, NotImplementedError) as error:
            self.skipTest("symlink creation unavailable: " + str(error))
        self.assertFalse(validate(self.root, ["claude"])["ok"])

    def test_cycle_and_depth(self):
        self.write("CLAUDE.md", "@AGENTS.md\n")
        self.write("AGENTS.md", "@CLAUDE.md\n")
        result = validate(self.root, ["claude"])
        self.assertTrue(any("cycle" in error for error in result["errors"]))
        self.write("CLAUDE.md", "@one.md\n")
        for index, name in enumerate(["one", "two", "three", "four", "five"]):
            names = ["one", "two", "three", "four", "five", "six"]
            self.write(name + ".md", "@" + names[index + 1] + ".md\n")
        self.write("six.md", "Too deep.\n")
        result = validate(self.root, ["claude"])
        self.assertTrue(any("depth" in error for error in result["errors"]))

    def test_markdown_subset_and_warnings(self):
        self.write("docs/my spec.md", "Spec.\n")
        self.write("AGENTS.md", '[spec](docs/my%20spec.md#heading)\n'
                   '[folder](docs/)\n[remote](https://example.com/doc)\n'
                   '```md\n[example](missing.md)\n```\n'
                   '`[example](missing.md)`\n[spec][ref]\n')
        result = validate(self.root, ["codex"])
        self.assertTrue(result["ok"])
        self.assertTrue(result["warnings"])

    def test_inline_import_requires_manual_review(self):
        self.write("CLAUDE.md", "Read @AGENTS.md before work.\n")
        result = validate(self.root, ["claude"])
        self.assertTrue(result["warnings"])

    def test_inventory_exclusions_and_limits(self):
        for name in ["package.json", "node_modules/pkg/package.json",
                     ".git/README.md", ".env", ".github/workflows/check.yml",
                     "apps/web/package.json"]:
            self.write(name, "Never execute or expose contents.\n")
        result = inventory(self.root)
        self.assertEqual(set(result["paths"]), {"package.json",
                         ".github/workflows/check.yml", "apps/web/package.json"})
        self.assertIn("results", inventory(self.root, max_results=1)["limits_reached"])
        self.assertIn("depth", inventory(self.root, max_depth=0)["limits_reached"])
        self.assertIn("entries", inventory(self.root, max_entries=1)["limits_reached"])


    def test_ci_and_manifest_discovery_across_ecosystems(self):
        for name in [".circleci/config.yml", "azure-pipelines.yml", "Dockerfile",
                     "docker-compose.yml", "CMakeLists.txt", "setup.py",
                     "composer.json", "pubspec.yaml", "Pods/Podfile"]:
            self.write(name, "Never execute or expose contents.\n")
        paths = set(inventory(self.root)["paths"])
        self.assertEqual(paths, {".circleci/config.yml", "azure-pipelines.yml",
                                 "Dockerfile", "docker-compose.yml",
                                 "CMakeLists.txt", "setup.py", "composer.json",
                                 "pubspec.yaml"})

    def test_indented_code_block_links_are_skipped(self):
        self.write("AGENTS.md", "Example:\n\n    [x](docs/nope.md)\n\nDone.\n")
        result = validate(self.root, ["codex"])
        self.assertTrue(result["ok"])
        self.assertEqual(result["errors"], [])

    def test_indented_list_item_links_are_still_validated(self):
        self.write("AGENTS.md", "- Top\n\n    - Nested [x](docs/nope.md)\n")
        result = validate(self.root, ["codex"])
        self.assertFalse(result["ok"])

    def test_errors_identify_source_document_and_reference(self):
        self.write("AGENTS.md", "[a](../secret1.md) and [b](docs/nope.md)\n")
        result = validate(self.root, ["codex"])
        joined = " ".join(result["errors"])
        self.assertIn("../secret1.md", joined)
        self.assertIn("docs/nope.md", joined)
        self.assertEqual(joined.count("(in AGENTS.md)"), 2)

    def test_suffix_rule_finds_dotnet_and_haskell_projects(self):
        for name in ["App.csproj", "App.sln", "pkg.cabal"]:
            self.write(name, "Never execute or expose contents.\n")
        self.assertEqual(set(inventory(self.root)["paths"]),
                         {"App.csproj", "App.sln", "pkg.cabal"})

    def test_unknown_ecosystem_surfaces_unclassified_root_files(self):
        self.write("shard.yml", "Crystal manifest, not on any list.\n")
        self.write("src/main.cr", "Source.\n")
        result = inventory(self.root)
        self.assertEqual(result["paths"], [])
        self.assertEqual(result["unclassified_root_files"], ["shard.yml"])

    def test_unclassified_root_listing_is_bounded_and_root_only(self):
        for index in range(12):
            self.write("file%02d.unknown" % index, "x\n")
        self.write("nested/deep.unknown", "x\n")
        result = inventory(self.root, max_root_files=5)
        self.assertEqual(len(result["unclassified_root_files"]), 5)
        self.assertIn("root_files", result["limits_reached"])
        self.assertNotIn("deep.unknown", result["unclassified_root_files"])

    def test_ci_is_found_inside_a_package_not_only_at_the_root(self):
        self.write(".github/workflows/root.yml", "x\n")
        self.write("pkg-a/.github/workflows/ci.yml", "x\n")
        self.write("pkg-b/.circleci/config.yml", "x\n")
        self.write("pkg-c/.buildkite/pipeline.yml", "x\n")
        paths = set(inventory(self.root)["paths"])
        self.assertEqual(paths, {".github/workflows/root.yml",
                                 "pkg-a/.github/workflows/ci.yml",
                                 "pkg-b/.circleci/config.yml",
                                 "pkg-c/.buildkite/pipeline.yml"})

    def test_handoff_is_found_under_any_name(self):
        self.write("docs/HANDOFF.md", "x\n")
        self.write("notes/ft-token-handoff.md", "x\n")
        self.write("notes/Session_Handoff_2026.md", "x\n")
        self.write("notes/unrelated.md", "x\n")
        paths = set(inventory(self.root)["paths"])
        self.assertEqual(paths, {"docs/HANDOFF.md", "notes/ft-token-handoff.md",
                                 "notes/Session_Handoff_2026.md"})

    def test_verified_counts_separate_a_real_pass_from_an_empty_one(self):
        self.write("AGENTS.md", "No links here at all.\n")
        empty = validate(self.root, ["codex"])
        self.assertTrue(empty["ok"])
        self.assertEqual(empty["verified"],
                         {"documents": 1, "local_links": 0, "imports": 0})
        self.write("docs/one.md", "x\n")
        self.write("docs/two.md", "x\n")
        self.write("AGENTS.md", "[a](docs/one.md) [b](docs/two.md)\n")
        self.write("CLAUDE.md", "@AGENTS.md\n")
        real = validate(self.root, ["codex", "claude"])
        self.assertTrue(real["ok"])
        self.assertEqual(real["verified"]["imports"], 1)
        self.assertGreaterEqual(real["verified"]["local_links"], 2)

if __name__ == "__main__":
    unittest.main()
