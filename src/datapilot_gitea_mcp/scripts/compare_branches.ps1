param (
    [Parameter(Mandatory=$true)]
    [string]$BaseBranch,

    [Parameter(Mandatory=$true)]
    [string]$HeadBranch
)

# Verify branches exist
$ErrorActionPreference = "SilentlyContinue"
git rev-parse --verify "$BaseBranch" | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Base branch '$BaseBranch' not found."
    exit 1
}

git rev-parse --verify "$HeadBranch" | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Head branch '$HeadBranch' not found."
    exit 1
}
$ErrorActionPreference = "Continue"

$date = Get-Date
$authorName = git config user.name
$authorEmail = git config user.email

Write-Output "# Pull Request Context"
Write-Output ""
Write-Output "## Metadata"
Write-Output "- **Date**: $date"
Write-Output "- **Base Branch**: $BaseBranch"
Write-Output "- **Head Branch**: $HeadBranch"
Write-Output "- **Author**: $authorName <$authorEmail>"
Write-Output ""

Write-Output "## Commit Summary"
Write-Output "List of commits included in this PR:"
Write-Output '```text'
git log --no-merges --pretty=format:"%h - %s (%an)" "$BaseBranch..$HeadBranch"
Write-Output ""
Write-Output '```'
Write-Output ""

Write-Output "## Impact Analysis"
Write-Output "Summary of files changed:"
Write-Output '```text'
git diff --stat "$BaseBranch..$HeadBranch"
Write-Output '```'
Write-Output ""

Write-Output "## Detailed Changes"
Write-Output "Full diff of changes:"
Write-Output '```diff'
git diff "$BaseBranch..$HeadBranch"
Write-Output '```'
