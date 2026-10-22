<#
Installs the /dual-review skill and its dual-reviewer subagent for Claude Code (Windows).

  powershell -ExecutionPolicy Bypass -File .\install.ps1                 # personal: %USERPROFILE%\.claude
  powershell -ExecutionPolicy Bypass -File .\install.ps1 -Project        # this repo: .\.claude
  powershell -ExecutionPolicy Bypass -File .\install.ps1 -AsCodeReview   # also take over /code-review
  powershell -ExecutionPolicy Bypass -File .\install.ps1 -Uninstall [-Project]

Existing files are moved to *.bak.<timestamp>, never overwritten.
#>
[CmdletBinding()]
param(
    [switch]$Project,
    [switch]$AsCodeReview,
    [switch]$Uninstall
)

$ErrorActionPreference = 'Stop'

$Src = $PSScriptRoot
$Dest = if ($Project) { Join-Path (Get-Location).Path '.claude' } else { Join-Path $HOME '.claude' }
$SkillName = if ($AsCodeReview) { 'code-review' } else { 'dual-review' }
$Stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$AgentsDir = Join-Path $Dest 'agents'
$SkillsDir = Join-Path $Dest 'skills'
$AgentFile = Join-Path $AgentsDir 'dual-reviewer.md'
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Backup-Path([string]$Path) {
    if (Test-Path -LiteralPath $Path) {
        $target = "$Path.bak.$Stamp"
        $n = 1
        while (Test-Path -LiteralPath $target) { $target = "$Path.bak.$Stamp.$n"; $n++ }
        Move-Item -LiteralPath $Path -Destination $target
        Write-Host "  backed up $Path -> $target"
    }
}

if ($Uninstall) {
    Write-Host "Removing from $Dest"
    Backup-Path $AgentFile
    foreach ($name in @('dual-review', 'code-review')) {
        $dir = Join-Path $SkillsDir $name
        $file = Join-Path $dir 'SKILL.md'
        if ((Test-Path -LiteralPath $file) -and (Select-String -LiteralPath $file -SimpleMatch 'Mode: DISCOVER' -Quiet)) {
            Backup-Path $dir
        }
    }
    Write-Host "Done. Backups are kept next to the originals; delete them when you're sure."
    return
}

$newAgentsDir = -not (Test-Path -LiteralPath $AgentsDir)
$newSkillsDir = -not (Test-Path -LiteralPath $SkillsDir)
New-Item -ItemType Directory -Force -Path $AgentsDir, $SkillsDir | Out-Null

Write-Host "Installing into $Dest"

Backup-Path $AgentFile
$agent = [System.IO.File]::ReadAllText((Join-Path (Join-Path $Src 'agents') 'dual-reviewer.md'), $Utf8NoBom)
[System.IO.File]::WriteAllText($AgentFile, $agent, $Utf8NoBom)
Write-Host "  agent  -> $AgentFile"

$SkillDir = Join-Path $SkillsDir $SkillName
Backup-Path $SkillDir
New-Item -ItemType Directory -Force -Path $SkillDir | Out-Null
$skill = [System.IO.File]::ReadAllText((Join-Path (Join-Path (Join-Path $Src 'skills') 'dual-review') 'SKILL.md'), $Utf8NoBom)
$skill = [regex]::Replace($skill, '(?m)^name: dual-review\r?$', "name: $SkillName")
$SkillFile = Join-Path $SkillDir 'SKILL.md'
[System.IO.File]::WriteAllText($SkillFile, $skill, $Utf8NoBom)
Write-Host "  skill  -> $SkillFile  (/$SkillName)"

Write-Host ''
if ($newAgentsDir) {
    Write-Host "Restart Claude Code: $AgentsDir is new, and running sessions don't watch new directories."
} elseif ($newSkillsDir) {
    Write-Host 'In running sessions run /reload-skills (new skills directory), or restart Claude Code.'
}
if ($AsCodeReview) {
    Write-Host '/code-review now runs the dual review. The /review alias still runs the built-in review.'
}
Write-Host "Try it: /$SkillName   or   /$SkillName main --fix"
