# FireDragon-TOM-Modfix

FireDragonSlayer's Tale Of Immortal Mod structure fix.

<span style="color:red"><strong>WARNING 1:</strong> if you are using the "organized translation pack v1.1.rar" then apply it to the mods before you run them through this tool.</span>

WARNING 2: This tool is in BETA testing phase, make a backup of the mods that you have before you run this with the alternative setting in config enabled.

## Quick start (recommended)

1. Go to the repository **Releases** page.
2. Download the latest setup zip (`FireDragon-TOM-Modfix-Setup.zip`).
3. Extract the zip to any folder.
4. Double-click `Setup.bat`.
5. Put broken mods into `Source\`.
6. Double-click `Launch.bat`.
7. Get fixed mods from `Output\` (or your configured `shippable_output_dir`).

## Portable package contents

The release zip already includes:
- `Source\`
- `Output\`
- `Alternative Output\`
- `programs\`
- `Logs\`
- `Readme.txt`
- `Launch.bat`
- `Launch_AlternativeOutput.bat`
- `Launch_Replace.bat`
- `Setup.bat`
- `config.json`

## Configuration

Edit `config.json` to customize paths and behavior:
- `source_folder`
- `shippable_output_dir` (preferred normal final output path)
- `output_folder` (legacy/backward-compatible output path key)
- `alternative_output_dir`
- `replace_directory`
- `programs_folder`
- `main_script`
- `flatten_script`
- `rename_script`
- `validate_script`
- `alternative_builder_script`
- `safe_replace_script`
- `auto_update_tools`
- `do_move`
- `overwrite_files`
- `enable_alternative_output` (default: `false`)
- `enable_safe_replace` (default: `false`)
- `replace_dry_run` (default: `true`)
- `replace_backup_enabled` (default: `false`)

All Python scripts in `programs\` read this same shared config.

## Optional Alternative Output + Safe Replace workflow

These features are **optional** and **disabled by default**.

- `Launch.bat` remains the default normal flow (`Source -> Output`) and does not force alternative output/replacement.
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
