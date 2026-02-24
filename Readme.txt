FireDragon TOM Modfix (Portable)

1) Put broken mods into the Source folder.
2) Run Setup.bat to verify package files and tool availability.
3) Run Launch.bat to process normal Source -> Output flow.
4) Collect fixed mods from Output (or your configured shippable_output_dir).
5) Check run logs in the Logs folder (one main log + one detailed log per program).

Optional workflow (disabled by default):
- Alternative Output is optional and disabled until enable_alternative_output=true in config.json.
- Run Launch_AlternativeOutput.bat to build Alternative Output using broken mods only.
- Safe replace is optional and disabled until enable_safe_replace=true in config.json.
- Set replace_directory in config.json, then run Launch_Replace.bat.
- Safe replace only replaces exact existing folder-name matches from Alternative Output.
- It never creates missing mods in replace_directory and never mass-deletes unrelated mods.
- Recommended: keep replace_dry_run=true for preview before real replacement.

Configuration:
- Edit config.json to change Source/Output/program paths and behavior.
- Preferred normal output key: shippable_output_dir (legacy output_folder is still supported).
