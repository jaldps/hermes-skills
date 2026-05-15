# Publishing Zoltar Skill to GitHub — Checklist

When sharing this skill publicly, sanitization is required.

## Personal Info to Strip Before Publishing

Scan ALL files with regex for these patterns:
- Real names (replace with generic names like "Alex Morgan")
- Home directory paths (`/Users/...`, `~/.hermes/...`) — replace with relative paths (`./`)
- Email addresses
- Personal account identifiers
- References to other publications the user writes for
- Custom env var names that include the user's handle (e.g., `hermes_zoltar` → `zoltar_geonames`)

## Sanitization Commands

```python
import re

personal_patterns = {
    'real_name': r'\bRealName\b',
    'home_path': r'/Users/',
    'email': r'\S+@\S+\.\S+',
    'custom_env': r'hermes_specific_name',
}

for fname, content in all_files.items():
    for label, pattern in personal_patterns.items():
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            print(f"LEAK in {fname}: '{label}' -> {matches}")
```

## GitHub Push Permission Check

Before pushing to a repo, verify write access:

```bash
gh api repos/{owner}/{repo} --jq '.permissions'
# If push=false → fork first:
gh repo fork {owner}/{repo}
cd /tmp/{repo}
git remote add myfork https://github.com/{my_account}/{repo}.git
git push myfork main
gh pr create --repo {owner}/{repo} --head {my_account}:main
```

## Files That Need Special Attention

- `scripts/natal_chart.py` — contains example names and env var defaults
- `scripts/numerology.py` — contains example names
- `SKILL.md` — contains example commands with names

## Files Safe to Publish As-Is

- `references/tarot_cards.json` — pure dataset
- `references/runes_elder_futhark.json` — pure dataset
- `scripts/iching_reading.py` — no personal info
