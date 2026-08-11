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
├── ftplugin/             # Per-filetype settings (buffer-local)
└── lua/
    ├── config/           # lazy.nvim bootstrap, options, keymaps
    ├── lsp/
    │   └── shared.lua    # Shared LSP on_attach (keymaps)
    └── plugins/          # One spec file per plugin
```

Machine-local files excluded from this repo (via the dotfiles repo's
`info/exclude`): work-specific Java/Android tooling.

## Plugin Management

- Use `lazy-lock.json` to track exact plugin versions
- Plugins are automatically checked for updates (checker.enabled = true)
- Install colorscheme fallback is "habamax"

## LSP Architecture

This config uses the modern Neovim 0.11+ LSP approach:
- `vim.lsp.config()` to define server configurations
- `vim.lsp.enable()` to activate servers
- No `mason-lspconfig.nvim` needed — Mason just installs binaries

## Session History

### 2026-08-05: Swift Development Setup
Followed swift.org's "Zero to Swift Neovim" guide. sourcekit-lsp, treesitter, and blink.cmp completion were already in place (blink.cmp is the modern replacement for the guide's nvim-cmp).
- conform.nvim: swift formatter switched from third-party `swiftformat` (Nick Lockwood, needed `brew install`) to the official bundled `swift format` (Apple swift-format, Swift 6+, zero install). Style is controlled per-project by a `.swift-format` file.
- Added `nvim-dap` + `nvim-dap-ui` for debugging via `lldb-dap` (bundled with the toolchain, resolved through `xcrun --find lldb-dap`). Three Swift configs: launch, launch-with-args, attach. Keys under `<leader>d` (debug group).
- Line-diagnostics float moved from `<leader>d` to `<leader>cd` (under the existing "code" group) to free `<leader>d` for the debug group.

### 2026-07-31: Declutter + Official Recommendations
- nvim-treesitter migrated from frozen `master` to the `main` rewrite (requires Neovim 0.12+): parsers via `require("nvim-treesitter").install()`, highlight/indent via `FileType` autocmd
- mason.nvim repo updated to `mason-org/mason.nvim` (project moved orgs)
- LSP: shared `capabilities`/`on_attach` now applied once via `vim.lsp.config("*")`; servers needing no extra settings (ts_ls, bashls, marksman, yamlls) have no per-server block
- Removed keymaps that duplicate Neovim builtins (`K`, `[d`, `]d`) and deprecated `vim.diagnostic.goto_*` calls
- conform.nvim `lsp_fallback` renamed to `lsp_format = "fallback"` (upstream rename)
- Deleted dead commented code, default-identical lualine/gitsigns options, obsolete lua_ls telemetry setting; `workspace.library` trimmed to `$VIMRUNTIME`
- Removed `.gitignore` that excluded `lazy-lock.json` (lockfile should be committed)

### 2026-01-21: Config Cleanup
- Removed `mason-lspconfig.nvim` (redundant with `vim.lsp.config/enable`)
- Deleted `mason-tool-installer.lua` and merged into `mason.lua`
- Plugin count reduced from 19 to 17
- LSP servers and formatters now managed in single `mason.lua` file
