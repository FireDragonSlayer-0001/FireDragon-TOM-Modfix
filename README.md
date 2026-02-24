# FireDragon-TOM-Modfix

FireDragonSlayer's Tale Of Immortal Mod structure fix.

| :warning:  This is very important   |
|-----------------------------------------|
If you are using the "organized translation pack v1.1.rar" then apply it to the mods before you run them through this tool.
This tool is in BETA testing phase, make a backup of the mods that you have before you run this with the alternative setting in config enabled.

## Quick start (recommended)

1. Go to the repository **Releases** page.
2. Download the latest setup zip (`FireDragon-TOM-Modfix-Setup.zip`).
3. Extract the zip to any folder.
4. Double-click `Setup.bat`.
5. Put broken mods into `Source\`.
6. Double-click `Launch.bat`.
7. Get fixed mods from `Output\` (or your configured `shippable_output_dir`).
8. Check `Manual Fixing Required\` (or your configured `manual_fixing_required_dir`) for error mods that require manual repair.

## Portable package contents

The release zip already includes:
- `Source\`
- `Output\`
- `Alternative Output\`
- `programs\`
- `Logs\`
- `Manual Fixing Required\`
- `Readme.txt`
- `Launch.bat`
- `Launch_AlternativeOutput.bat`
- `Launch_Replace.bat`
- `Setup.bat`
- `config.json`

## Configuration

Edit `config.json` to customize behavior and paths.

### Most important settings (set these first)

- `source_folder`  
  Folder where you place broken mods before running the tool.
- `shippable_output_dir`  
  Main final output path for fixed mods in the normal `Launch.bat` flow.
- `manual_fixing_required_dir`  
  Folder where mods are moved when automation cannot safely fix them.
- `enable_alternative_output` (default: `false`)  
  Turns on the optional alternative-output pipeline used to isolate broken/problem mods.
- `alternative_output_dir`  
  Destination folder used by the alternative-output workflow.
- `enable_safe_replace` (default: `false`)  
  Enables safe replacement logic so only matching existing folders are replaced.
- `replace_directory`  
  Target game/mod directory that safe replace checks against.
- `replace_dry_run` (default: `true`)  
  Preview mode for safe replace; shows what would change without applying writes.
- `replace_backup_enabled` (default: `false`)  
  Creates backups during safe replace when enabled.

### General/advanced config options

- `do_move`  
  Controls whether extracted items are moved instead of copied during processing.
- `overwrite_files`  
  Allows overwriting existing files where workflows support it.
- `auto_update_tools`  
  Lets setup/update flows refresh helper scripts from the repository source.

### Base directory and script path keys (usually keep defaults)

- `output_folder`  
  Legacy/backward-compatible output path key.
- `programs_folder`
- `main_script`
- `flatten_script`
- `rename_script`
- `validate_script`
- `alternative_builder_script`
- `safe_replace_script`

All Python scripts in `programs\` read this same shared config.

## Optional Alternative Output + Safe Replace workflow

These features are **optional** and **disabled by default**.

- `Launch.bat` remains the default normal flow (`Source -> Output`) and does not force alternative output/replacement.
- After each run, always review `Manual Fixing Required\` and manually fix any mods that were moved there.
- To build alternative output for only broken mods, enable `enable_alternative_output=true`, then run `Launch_AlternativeOutput.bat`.
- To perform safe replacement, enable `enable_safe_replace=true`, set `replace_directory`, then run `Launch_Replace.bat`.

### Safe replacement rules

- Replacements are considered only for mod folders found in `Alternative Output\`.
- A mod is replaced **only** when the exact same folder name already exists in `replace_directory`.
- If a mod is missing in `replace_directory`, it is skipped (never created).
- Mods present only in `replace_directory` are left untouched.
- No mass delete is performed; only matched target mod folders are replaced.
- Dry-run is recommended first (`replace_dry_run=true`).

## Maintainer release flow

1. Open the **Actions** tab and confirm `Build and Publish Release` runs on your branch push/PR (or trigger it manually via `workflow_dispatch`).
2. Commit your changes to `main`.
3. Create and push a semantic version tag (example: `v0.1.0`).
4. Tag pushes matching `v*.*.*` publish `FireDragon-TOM-Modfix-Setup-<tag>.zip` to a GitHub Release.
