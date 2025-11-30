#!/bin/bash

# Script to generate context for an LLM to write a Pull Request description
# Usage: ./compare_branches.sh <base_branch> <head_branch>

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <base_branch> <head_branch>"
    echo "Example: $0 main feature/login-page"
    exit 1
fi

BASE=$1
HEAD=$2

# Verify branches exist
if ! git rev-parse --verify "$BASE" >/dev/null 2>&1; then
    echo "Error: Base branch '$BASE' not found."
    exit 1
fi

if ! git rev-parse --verify "$HEAD" >/dev/null 2>&1; then
    echo "Error: Head branch '$HEAD' not found."
    exit 1
fi

echo "# Pull Request Context"
echo ""
echo "## Metadata"
echo "- **Date**: $(date)"
echo "- **Base Branch**: $BASE"
echo "- **Head Branch**: $HEAD"
echo "- **Author**: $(git config user.name) <$(git config user.email)>"
echo ""

echo "## Commit Summary"
echo "List of commits included in this PR:"
echo "\`\`\`text"
git log --no-merges --pretty=format:"%h - %s (%an)" "$BASE..$HEAD"
echo ""
echo "\`\`\`"
echo ""

echo "## Impact Analysis"
echo "Summary of files changed:"
echo "\`\`\`text"
git diff --stat "$BASE..$HEAD"
echo "\`\`\`"
echo ""

echo "## Detailed Changes"
echo "Full diff of changes:"
echo "\`\`\`diff"
# Exclude package-lock.json or similar large generated files if necessary
# git diff "$BASE..$HEAD" -- . ':(exclude)package-lock.json' ':(exclude)yarn.lock'
git diff "$BASE..$HEAD"
echo "\`\`\`"
