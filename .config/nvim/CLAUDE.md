# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Neovim configuration repository using the lazy.nvim plugin manager. The configuration follows a modular structure where plugins are organized in separate files under the `lua/plugins/` directory.

## Architecture

- **init.lua**: Entry point that loads the lazy.nvim configuration
- **lua/config/lazy.lua**: Bootstrap and setup for lazy.nvim plugin manager
- **lua/plugins/**: Directory containing individual plugin configurations
  - Each plugin should be defined in its own file returning a table specification
  - Plugins are automatically imported via `{ import = "plugins" }` in lazy.lua

## Key Configuration Details

- **Leader key**: Space ` ` (set in lua/config/lazy.lua:21)
- **Local leader**: Space ` ` (set in lua/config/lazy.lua:27)
- **Plugin manager**: lazy.nvim with automatic update checking enabled
- **Default colorscheme**: solarized-osaka.nvim (craftzdog/solarized-osaka.nvim)

## Plugin Development

When adding new plugins:
1. Create a new file in `lua/plugins/` (e.g., `lua/plugins/pluginname.lua`)
2. Return a lazy.nvim plugin specification table
3. The plugin will be automatically loaded by lazy.nvim
4. Always use `opts` instead of `config` when possible. `config` is almost never needed. E.g. Use { "folke/todo-comments.nvim", opts = {} }. Don't use { "folke/todo-comments.nvim", config = function() require("todo-comments").setup({}) end, }

Example plugin structure:
```lua
return {
    "author/plugin-name",
    lazy = false,  -- or true for lazy loading
    opts = {
        -- plugin options
    },
}
```

## File Structure

```
.
├── init.lua              # Entry point
├── lazy-lock.json        # Plugin version lockfile
└── lua/
    ├── config/
    │   └── lazy.lua       # Lazy.nvim setup
    └── plugins/
        └── colorscheme.lua # Colorscheme configuration
```

## Plugin Management

- Use `lazy-lock.json` to track exact plugin versions
- Plugins are automatically checked for updates (checker.enabled = true)
- Install colorscheme fallback is "habamax"
