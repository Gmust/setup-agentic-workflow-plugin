"""Print a bounded, read-only inventory. Does not execute or read repo files."""

import argparse
import json
import os
from pathlib import Path


EXCLUDED = {
    ".git", "node_modules", "target", "dist", "build", ".venv", "venv",
    "vendor", "__pycache__", ".next", "coverage", ".cache", "logs",
    "Pods", "DerivedData", "_build", "deps",
}
TRAVERSED_HIDDEN = {".github", ".claude", ".circleci", ".buildkite"}
NAMES = {
    "AGENTS.md", "CLAUDE.md", "HANDOFF.md", "README.md", "CONTRIBUTING.md",
    "ARCHITECTURE.md", "MVP_SPEC.md", "AGENT_GUIDE.md", "package.json",
    "Cargo.toml", "Cargo.lock", "rust-toolchain.toml", "pyproject.toml",
    "requirements.txt", "uv.lock", "go.mod", "go.sum", "go.work", "Gemfile",
    "pom.xml", "build.gradle", "build.gradle.kts", "Makefile", "justfile",
    "Taskfile.yml", "pnpm-lock.yaml", "pnpm-workspace.yaml", "yarn.lock",
    "package-lock.json", "bun.lock", "bun.lockb", "Trunk.toml",
    ".gitlab-ci.yml", "Jenkinsfile", "Earthfile",
    "azure-pipelines.yml", "azure-pipelines.yaml", ".pre-commit-config.yaml",
    ".drone.yml", ".woodpecker.yml",
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    "compose.yml", "compose.yaml",
    "setup.py", "setup.cfg", "tox.ini", "noxfile.py", "Pipfile",
    "Pipfile.lock", "poetry.lock",
    "CMakeLists.txt", "CMakePresets.json", "meson.build",
    "settings.gradle", "settings.gradle.kts",
    "composer.json", "composer.lock", "mix.exs", "mix.lock",
    "pubspec.yaml", "pubspec.lock", "deno.json", "deno.jsonc", "deno.lock",
    "Package.swift", "Podfile", "Podfile.lock",
    "BUILD.bazel", "MODULE.bazel", "WORKSPACE",
    "build.zig", "build.zig.zon", "build.sbt", "deps.edn", "project.clj",
    "Project.toml", "Manifest.toml", "dune-project", "rebar.config",
    "stack.yaml", "DESCRIPTION", "cpanfile",
    "nx.json", "turbo.json", "lerna.json", "rush.json",
}
SUFFIXES = {".csproj", ".fsproj", ".vbproj", ".sln", ".cabal"}
# CI directories, matched at any depth so a monorepo package keeps its own CI.
CI_YAML_DIRS = ((".github", "workflows"), (".circleci",), (".buildkite",))
HANDOFF_STEM = "handoff"


def inventory(root, max_entries=5000, max_results=200, max_depth=4,
              max_root_files=50):
    results = []
    unclassified = []
    limited = set()
    seen = 0

    def finish():
        return {
            "paths": results,
            "unclassified_root_files": sorted(unclassified),
            "limits_reached": sorted(limited),
        }

    for directory, dirs, files in os.walk(root, followlinks=False):
        seen += 1
        if seen > max_entries:
            limited.add("entries")
            break
        relative = Path(directory).relative_to(root)
        depth = len(relative.parts)
        dirs[:] = sorted(
            name for name in dirs
            if name not in EXCLUDED
            and (not name.startswith(".") or name in TRAVERSED_HIDDEN)
            and not (Path(directory) / name).is_symlink()
        )
        if depth >= max_depth and dirs:
            limited.add("depth")
            dirs[:] = []
        for name in sorted(files):
            seen += 1
            if seen > max_entries:
                limited.add("entries")
                return finish()
            path = Path(directory) / name
            rel = path.relative_to(root)
            if path.is_symlink() or name.startswith(".env"):
                continue
            parents = rel.parts[:-1]
            matched = (
                name in NAMES
                or path.suffix in SUFFIXES
                or (path.suffix in {".yaml", ".yml"}
                    and any(parents[index:index + len(group)] == group
                            for group in CI_YAML_DIRS
                            for index in range(len(parents) - len(group) + 1)))
                or (path.suffix.lower() == ".md"
                    and HANDOFF_STEM in path.stem.lower())
                or (relative.name in {"scripts", "bin"}
                    and name.startswith(("check", "test", "lint", "verify")))
            )
            if matched:
                if len(results) >= max_results:
                    limited.add("results")
                    return finish()
                results.append(rel.as_posix())
            elif depth == 0:
                if len(unclassified) >= max_root_files:
                    limited.add("root_files")
                else:
                    unclassified.append(name)
    return finish()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error("root must be an existing directory")
    print(json.dumps(inventory(args.root.resolve()), indent=2))


if __name__ == "__main__":
    main()
