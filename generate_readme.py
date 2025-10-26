#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0.1"]
# ///

from pathlib import Path
import re
import sys
import yaml

ROOT = Path(__file__).parent.resolve()
README = ROOT / "README.md"
YAML_PATH = ROOT / "skills.yaml"

# Build delimiter strings without writing angle brackets into source
START = chr(60) + "!-- SKILLS_START --" + chr(62)
END = chr(60) + "!-- SKILLS_END --" + chr(62)

def load_skills():
    try:
        with open(YAML_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Failed to load {YAML_PATH}: {e}", file=sys.stderr)
        sys.exit(1)
    skills = data.get("skills", [])
    if not isinstance(skills, list):
        print("skills.yaml must contain a top-level 'skills' list", file=sys.stderr)
        sys.exit(1)
    return skills

def render_card(s):
    title = s.get("title", "").strip()
    desc = s.get("description", "").strip()
    author = s.get("author", "").strip()
    author_url = s.get("author_url", "").strip()
    author_gh = s.get("author_github", "").strip()
    license_name = s.get("license", "").strip()
    license_url = s.get("license_url") or ""
    license_url = license_url.strip() if license_url else ""
    skill_url = s.get("skill_url", "").strip()
    dl = s.get("skill_download_url", "").strip()
    tags = s.get("tags", []) or []
    # Wrap each tag in backticks
    tags_str = ", ".join(f"`{tag}`" for tag in tags)
    lines = []
    # Use ### heading and link to skill URL
    lines.append(f"### [{title}]({skill_url})")
    if desc:
        lines.append("")
        lines.append(desc)
    lines.append("")
    # Link GitHub handle to author's GitHub profile with backticks
    lines.append(f"- **Author**: [{author}]({author_url}) ([`@{author_gh}`](https://github.com/{author_gh}))")
    # Only show license link if URL is available
    if license_url:
        lines.append(f"- **License**: [{license_name}]({license_url})")
    else:
        lines.append(f"- **License**: {license_name}")
    lines.append(f"- **Skill**: {skill_url}")
    # Only show download URL if it's different from skill URL
    if dl and dl != skill_url:
        lines.append(f"- **Download**: {dl}")
    if tags_str:
        lines.append(f"- **Tags**: {tags_str}")
    lines.append("")
    # Add horizontal separator
    lines.append("---")
    lines.append("")
    return "\n".join(lines)

def render_all(skills):
    # Sort by title for a stable, readable output
    skills_sorted = sorted(skills, key=lambda x: (x.get("title") or "").lower())
    return "\n".join(render_card(s) for s in skills_sorted)

def replace_section(readme_text, new_body):
    pattern = re.compile(rf"({re.escape(START)})(.*?)({re.escape(END)})", re.DOTALL)
    if pattern.search(readme_text):
        return pattern.sub(rf"\1\n{new_body}\n\3", readme_text)
    else:
        # Append a new section at the end if markers are missing
        sep = "" if readme_text.endswith("\n") else "\n"
        return f"{readme_text}{sep}\n{START}\n{new_body}\n{END}\n"

def main():
    skills = load_skills()
    body = render_all(skills)
    try:
        text = README.read_text(encoding="utf-8")
    except FileNotFoundError:
        print("README.md not found", file=sys.stderr)
        sys.exit(1)
    updated = replace_section(text, body)
    if updated != text:
        README.write_text(updated, encoding="utf-8")
        print("README.md updated")
    else:
        print("README.md already up to date")

if __name__ == "__main__":
    main()
