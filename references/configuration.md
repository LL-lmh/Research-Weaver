# Configuration

Use a private per-user configuration rather than a file inside the GitHub clone. Resolve its location in this order:

1. `RESEARCH_WEAVER_CONFIG`, when explicitly set;
2. `%APPDATA%/research-weaver/config.json` on Windows;
3. `$XDG_CONFIG_HOME/research-weaver/config.json`, or `~/.config/research-weaver/config.json`, on macOS/Linux.

## First-run admission

When a task first needs to read or write the Obsidian literature library and no valid configuration exists, ask for exactly the missing decisions:

1. **Obsidian Vault absolute path** — an existing directory;
2. **paper-notes directory** — a relative path inside that Vault, such as `Research/Papers`;
3. **default output language** — `zh-CN`, `en`, or `both`.

Restate the resulting `<vault>/<papers_root>` destination, then save it with:

```powershell
python scripts/note_store.py configure --vault "C:/path/to/Vault" --papers-root "Research/Papers" --default-language zh-CN
```

Do not create the Vault, select an unrelated folder, or store a personal path in the Skill repository. On later runs, execute `show-config`, display the resolved destination and language, and continue unless the user requests a change. A one-run path or language override does not change saved defaults.

## Automatic weaving

Automatic relation discovery for each new paper-note task requires no additional configuration. Once the ordinary Vault settings exist, inspect plausible notes and write verified relations into the new note by default. The user can disable this for one task by asking not to connect existing notes; the opt-out does not change future runs.

## Fields

Required fields:

- `vault`: absolute path to the user's Obsidian vault at runtime.
- `papers_root`: path relative to the vault for paper notes.
- `default_language`: `zh-CN`, `en`, or `both`.
- `note_naming`: currently `slug-language`, producing `<title-slug>.<language>.md`.
- `index_note`: reserved optional path for a future index updater. The current release does not modify this file; use an empty string or rely on Dataview discovery.

Never publish a filled personal configuration. Never infer a writable vault from unrelated directories.

The repository example uses `"vault": "."` only as a portable schema example; do not use it as a runtime configuration. When `default_language` is `both`, expand it into separate `zh-CN` and `en` preflight/save operations that share the same paper identity and evidence model.
