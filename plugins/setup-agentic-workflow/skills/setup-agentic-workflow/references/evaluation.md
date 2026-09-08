# Behavioral evaluation

Use this when maintaining the skill. Helper tests validate mechanics only.
Evaluate actual skill use in disposable repositories without real user data.
Run each setup twice with the same answers; compare file bytes after each run.
Second runs should make no changes when the requested setup is already complete.
Do not regenerate timestamps or handoff text solely because setup was invoked.
Every scenario below also requires a handoff that exists and records what was
actually verified, including checks not run and the reason. A run that produces
instructions but no handoff fails its scenario, however good the instructions are.

| Scenario | Request and starting state | Expected observable outcome |
| --- | --- | --- |
| Empty | Empty directory; ask for setup for both agents, no stack provided | Ask for intended stack before suggesting build checks; no invented product scaffold or passing checks. After answers, create appropriate instructions and a truthful handoff. |
| Configured | Valid AGENTS, CLAUDE import, handoff, shared local/CI gate | No file changes, duplicate documents, or needless questions. |
| Custom Claude | Existing CLAUDE.md with custom rules; request both agents | Preserve original rules; add compatible shared instructions without cycles or duplicated imports. |
| Failing baseline | Existing check exits nonzero; request setup | Report the baseline failure separately; retain failing exit status and source behavior; do not weaken tests or fix unrelated code. |
| Monorepo | Workspace config with three packages; request setup for two of them | Shared rules stay in the root AGENTS.md; each in-scope package gets an AGENTS.md of deltas only; the untouched package gains no files; root command runs the in-scope checks; the root code map links each in-scope package's AGENTS.md and the validator resolves those links. |
| Platform claim | Repository claims Linux, macOS and Windows; only Linux checks exist | Propose the repository's own runner rather than an OS-specific script; record which platforms were actually exercised. |
| Unknown stack | Repository in an ecosystem the inventory does not recognize | Locate manifests and checks by reading the repository; never report that no build or checks exist because the helper returned an empty inventory. |
| Sibling repositories | Parent folder without version control; three subfolders that each have it | Set up each subfolder as its own repository; create no files in the parent and do not call it a monorepo. |
| Workspace file, no members | `pnpm-workspace.yaml` present but declaring only unrelated settings, one manifest | Treat it as a single project; no per-package instructions for packages that do not exist. |
| No runner available | Bare Cargo or single-binary repository with several separate check commands | Ask before introducing a new tool to chain them; record it in the handoff as a new requirement; do not commit an OS-specific script. |
| Existing gate | Repository already has a check command wired to a hook and CI, missing one step | Document the existing command and report the missing step; no edit to the manifest, no script narrowed, no hook made slower without agreement. |

Also exercise nested `.claude/CLAUDE.md`, missing local links, import cycles,
external symlinks, links inside fenced and indented code blocks, and
unavailable Python. A helper must not execute any command it discovers or
inspect referenced files outside the target repository.

Run mechanical tests using the standard library:

```sh
python3 -B -m unittest discover -s <skill-dir>/tests -v
```

Record what actually ran and remaining limitations. Do not call a hypothetical
walkthrough an observed agent evaluation, or a passing helper test proof that
Claude/Codex loaded the generated instructions in a fresh session.
