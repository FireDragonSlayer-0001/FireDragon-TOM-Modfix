# FireDragon-TOM-Modfix

FireDragonSlayer's Tale Of Immortal Mod structure fix.

## Quick start (recommended)

1. Go to the repository **Releases** page.
2. Download the latest setup zip (`FireDragon-TOM-Modfix-Setup.zip`).
3. Extract the zip to any folder.
4. Double-click `Setup.bat`.
5. Put broken mods into `Source\`.
6. Double-click `Launch.bat`.
7. Get fixed mods from `Output\`.

## Portable package contents

The release zip already includes:
- `Source\`
- `Output\`
- `programs\`
- `Readme.txt`
- `Launch.bat`
- `Setup.bat`
- `config.json`

## Configuration

Edit `config.json` to customize paths and behavior:
- `source_folder`
- `output_folder`
- `programs_folder`
- `main_script`
- `auto_update_tools`
- `do_move`
- `overwrite_files`

All Python scripts in `programs\` read this same shared config.


## Maintainer release flow

1. Commit your changes to `main`.
2. Create and push a semantic version tag (example: `v0.1.0`).
3. The `Build and Publish Release` workflow builds and uploads `FireDragon-TOM-Modfix-Setup-<tag>.zip` to a GitHub Release.
