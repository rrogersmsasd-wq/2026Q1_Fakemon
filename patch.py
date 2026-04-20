#!/usr/bin/env python3
"""
move_fakemon_to_json_subdir.py
Moves all *.json files in fakemon/ (except fakemonlist.json) into fakemon/json/,
then patches fakemon-battle.html, fakedex.html, fakemon_guide.html, and
clean_fakemonlist.py to use the new path.

Run from the repo root:
    python move_fakemon_to_json_subdir.py

Pass --dry-run to see what would happen without changing anything.
"""

import shutil
import sys
import argparse
from pathlib import Path

# ── helpers ──────────────────────────────────────────────────────────────

def read(path):
    return Path(path).read_text(encoding="utf-8")

def write(path, text):
    Path(path).write_text(text, encoding="utf-8")

def backup(path):
    shutil.copy2(path, path + ".bak")
    print(f"  backed up → {path}.bak")

def patch(path, old, new, label, dry_run=False):
    text = read(path)
    if old not in text:
        print(f"  ✗ PATCH FAILED [{label}]: target string not found in {path}")
        print(f"    First 80 chars of target: {repr(old[:80])}")
        sys.exit(1)
    count = text.count(old)
    if count > 1:
        print(f"  ✗ PATCH FAILED [{label}]: target appears {count} times (must be unique)")
        sys.exit(1)
    if not dry_run:
        write(path, text.replace(old, new, 1))
    print(f"  {'[DRY RUN] ' if dry_run else ''}✓ {label}")

# ═════════════════════════════════════════════════════════════════════════
#  fakemon-battle.html — 2 patches
# ═════════════════════════════════════════════════════════════════════════

BATTLE = "fakemon-battle.html"

# 1. loadAll(): fetch path for fakemonlist.json — unchanged, stays at fakemon/
#    (fakemonlist.json is NOT moving)

# 2. loadOneFakemon(): fetch path  fakemon/${filename}  →  fakemon/json/${filename}
OLD_BATTLE_FETCH = "    const r = await fetch(`fakemon/${filename}`);\n    dlog(`  ${filename}: HTTP ${r.status}`, r.ok ? 'info' : 'error');\n    if (!r.ok) throw new Error(`HTTP ${r.status} for fakemon/${filename}`);"

NEW_BATTLE_FETCH = "    const r = await fetch(`fakemon/json/${filename}`);\n    dlog(`  ${filename}: HTTP ${r.status}`, r.ok ? 'info' : 'error');\n    if (!r.ok) throw new Error(`HTTP ${r.status} for fakemon/json/${filename}`);"

# 3. loadOneFakemon(): dlog line that says "Loading fakemon/${filename}…"
OLD_BATTLE_DLOG = "  dlog(`Loading fakemon/${filename}…`, 'info');"

NEW_BATTLE_DLOG = "  dlog(`Loading fakemon/json/${filename}…`, 'info');"

# ═════════════════════════════════════════════════════════════════════════
#  fakedex.html — 3 patches
# ═════════════════════════════════════════════════════════════════════════

FAKEDEX = "fakedex.html"

# 1. loadEntry(): dlog line
OLD_DEX_DLOG = "  dlog(`[${num}] Loading fakemon/${id}.json…`, 'info');"

NEW_DEX_DLOG = "  dlog(`[${num}] Loading fakemon/json/${id}.json…`, 'info');"

# 2. loadEntry(): fetch call
OLD_DEX_FETCH = "    const res = await fetch(`fakemon/${id}.json`);\n    if (!res.ok) {\n      const msg = `HTTP ${res.status} — file 'fakemon/${id}.json' not found`;\n      entry._error = msg;\n      entry._errorDetails = [msg, `Make sure the file is named exactly \"${id}.json\" and is in the fakemon/ folder`];"

NEW_DEX_FETCH = "    const res = await fetch(`fakemon/json/${id}.json`);\n    if (!res.ok) {\n      const msg = `HTTP ${res.status} — file 'fakemon/json/${id}.json' not found`;\n      entry._error = msg;\n      entry._errorDetails = [msg, `Make sure the file is named exactly \"${id}.json\" and is in the fakemon/json/ folder`];"

# 3. FATAL error hint at bottom of loadAll()
OLD_DEX_FATAL_HINT = "    dlog('Is fakemon/fakemonlist.json missing or malformed? Check the path and JSON syntax.', 'warn');\n    document.getElementById('gallery-loading').textContent = 'Failed to load fakemon list. Check the debug console.';"

NEW_DEX_FATAL_HINT = "    dlog('Is fakemon/fakemonlist.json missing or malformed? Check the path and JSON syntax.', 'warn');\n    dlog('Individual Fakemon files should be in fakemon/json/ — e.g. fakemon/json/embork.json', 'warn');\n    document.getElementById('gallery-loading').textContent = 'Failed to load fakemon list. Check the debug console.';"

# ═════════════════════════════════════════════════════════════════════════
#  fakemon_guide.html — 3 patches
# ═════════════════════════════════════════════════════════════════════════

GUIDE = "fakemon_guide.html"

# 1. Section 9 step 1 — "Put your file inside the fakemon/ folder"
OLD_GUIDE_STEP1 = "<tr><td class=\"center\" style=\"font-size:24px;\">1️⃣</td><td>Put your file (e.g. <code>myfakemon.json</code>) inside the <code>fakemon/</code> folder.</td></tr>"

NEW_GUIDE_STEP1 = "<tr><td class=\"center\" style=\"font-size:24px;\">1️⃣</td><td>Put your file (e.g. <code>myfakemon.json</code>) inside the <code>fakemon/json/</code> folder.</td></tr>"

# 2. Section 9 step 2 — "Open fakemon/fakemonlist.json"
OLD_GUIDE_STEP2 = "<tr><td class=\"center\" style=\"font-size:24px;\">2️⃣</td><td>Open <code>fakemon/fakemonlist.json</code> and add your Fakemon's filename to the list.</td></tr>"

NEW_GUIDE_STEP2 = "<tr><td class=\"center\" style=\"font-size:24px;\">2️⃣</td><td>Open <code>fakemon/fakemonlist.json</code> and add your Fakemon's ID (without <code>.json</code>) to the list.</td></tr>"

# 3. Section 9 description before the code block — "Open fakemon/fakemonlist.json"
OLD_GUIDE_DESC = "    <p>Here's what <code>fakemonlist.json</code> looks like — just add your filename at the end:</p>"

NEW_GUIDE_DESC = "    <p>Here's what <code>fakemonlist.json</code> looks like — just add your Fakemon's ID (no <code>.json</code> needed) at the end:</p>"

# 4. Bug card #7 — "is in the fakemon/ folder"
OLD_GUIDE_BUG7 = "            <p style=\"font-size:14px;\">Open <code>fakemon/fakemonlist.json</code> and add your filename to the array."

NEW_GUIDE_BUG7 = "            <p style=\"font-size:14px;\">Open <code>fakemon/fakemonlist.json</code> and add your Fakemon's ID to the array. Your JSON file should be in <code>fakemon/json/</code>."

# ═════════════════════════════════════════════════════════════════════════
#  clean_fakemonlist.py — 2 patches
# ═════════════════════════════════════════════════════════════════════════

CLEAN = "clean_fakemonlist.py"

OLD_CLEAN_DIR = 'fakemon_dir = Path("fakemon")'

NEW_CLEAN_DIR = 'fakemon_dir = Path("fakemon/json")'

OLD_CLEAN_OUTPUT = 'output_file = fakemon_dir / "fakemonlist.json"'

NEW_CLEAN_OUTPUT = 'output_file = Path("fakemon") / "fakemonlist.json"'

# ═════════════════════════════════════════════════════════════════════════
#  MAIN
# ═════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would happen without making changes")
    args = parser.parse_args()
    dry = args.dry_run

    if dry:
        print("\n=== DRY RUN — no files will be modified ===\n")

    # ── verify required files exist ───────────────────────────────────────
    required = [BATTLE, FAKEDEX, GUIDE, CLEAN, "fakemon/fakemonlist.json"]
    for f in required:
        if not Path(f).exists():
            print(f"ERROR: {f} not found. Run from your repo root.")
            sys.exit(1)

    # ── 1. Move JSON files ────────────────────────────────────────────────
    json_dir = Path("fakemon/json")
    print(f"\nStep 1: Moving JSON files into fakemon/json/")
    if not dry:
        json_dir.mkdir(exist_ok=True)

    moved = []
    skipped = []
    for src in sorted(Path("fakemon").glob("*.json")):
        if src.name == "fakemonlist.json":
            skipped.append(src.name)
            continue
        dst = json_dir / src.name
        if dry:
            print(f"  [DRY RUN] would move: {src} → {dst}")
        else:
            shutil.move(str(src), str(dst))
            print(f"  moved: {src} → {dst}")
        moved.append(src.name)

    print(f"  {len(moved)} files moved, {len(skipped)} skipped ({', '.join(skipped)})")

    # ── 2. Patch fakemon-battle.html ──────────────────────────────────────
    print(f"\nStep 2: Patching {BATTLE}…")
    if not dry:
        backup(BATTLE)
    patch(BATTLE, OLD_BATTLE_DLOG,  NEW_BATTLE_DLOG,  "JS: loadOneFakemon dlog path",  dry)
    patch(BATTLE, OLD_BATTLE_FETCH, NEW_BATTLE_FETCH, "JS: loadOneFakemon fetch path",  dry)

    # ── 3. Patch fakedex.html ─────────────────────────────────────────────
    print(f"\nStep 3: Patching {FAKEDEX}…")
    if not dry:
        backup(FAKEDEX)
    patch(FAKEDEX, OLD_DEX_DLOG,        NEW_DEX_DLOG,        "JS: loadEntry dlog path",   dry)
    patch(FAKEDEX, OLD_DEX_FETCH,       NEW_DEX_FETCH,       "JS: loadEntry fetch path",  dry)
    patch(FAKEDEX, OLD_DEX_FATAL_HINT,  NEW_DEX_FATAL_HINT,  "JS: fatal error hint",      dry)

    # ── 4. Patch fakemon_guide.html ───────────────────────────────────────
    print(f"\nStep 4: Patching {GUIDE}…")
    if not dry:
        backup(GUIDE)
    patch(GUIDE, OLD_GUIDE_STEP1,  NEW_GUIDE_STEP1,  "Section 9 step 1 folder path",   dry)
    patch(GUIDE, OLD_GUIDE_STEP2,  NEW_GUIDE_STEP2,  "Section 9 step 2 description",   dry)
    patch(GUIDE, OLD_GUIDE_DESC,   NEW_GUIDE_DESC,   "Section 9 code block caption",   dry)
    patch(GUIDE, OLD_GUIDE_BUG7,   NEW_GUIDE_BUG7,   "Bug card #7 fix instructions",   dry)

    # ── 5. Patch clean_fakemonlist.py ─────────────────────────────────────
    print(f"\nStep 5: Patching {CLEAN}…")
    if not dry:
        backup(CLEAN)
    patch(CLEAN, OLD_CLEAN_DIR,    NEW_CLEAN_DIR,    "fakemon_dir path",                dry)
    patch(CLEAN, OLD_CLEAN_OUTPUT, NEW_CLEAN_OUTPUT, "output_file path",                dry)

    print(f"""
{'=== DRY RUN COMPLETE — nothing was changed ===' if dry else 'All patches applied successfully.'}

Final folder structure:
  fakemon/
    fakemonlist.json        ← stays here (unchanged)
    json/
      embork.json           ← all student JSON files moved here
      glopple.json
      …
    images/
      embork.png            ← images (from previous patch)
      …

{'Run without --dry-run to apply.' if dry else '''To revert file moves, manually move fakemon/json/*.json back to fakemon/.
To revert HTML/py patches, copy the .bak files back:
  cp fakemon-battle.html.bak fakemon-battle.html
  cp fakedex.html.bak fakedex.html
  cp fakemon_guide.html.bak fakemon_guide.html
  cp clean_fakemonlist.py.bak clean_fakemonlist.py'''}
""")

if __name__ == "__main__":
    main()