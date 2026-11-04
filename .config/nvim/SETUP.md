# Neovim Setup Guide

## Dependencies

Everything below except the C compiler is in `~/.config/brew/Brewfile`. Installing Homebrew installs the Xcode Command Line Tools, which provide the compiler.

| Dependency | Purpose |
|------------|---------|
| **Neovim 0.12+** | `vim.pack`, `vim.lsp.config`, nvim-treesitter (main branch) |
| **git** | `vim.pack` clones plugins |
| **tree-sitter-cli** + C compiler (`xcode-select --install`) | nvim-treesitter builds parsers |
| **fzf**, **ripgrep**, **fd** | fzf-lua: picker, live grep, file listing |
| **lua-language-server**, **pyright**, **ruff**, **bash-language-server**, **marksman** | Language servers |
| **kotlin-lsp** (cask) | Kotlin language server |
| **stylua**, **prettierd**, **shfmt** | Formatters run by conform.nvim (Python uses ruff) |

Swift formatting uses the toolchain's own `swift format` (Swift 6+), no separate install.

## Replicating on Another Mac

1. Install Homebrew.
2. Check out the dotfiles repo (`~/.dotfiles`, fish alias `dot`), which includes `~/.config/nvim` and the Brewfile.
3. `brew bundle --file ~/.config/brew/Brewfile`.
4. Run `nvim`. On first launch:
   - `vim.pack` asks to install the plugins at the revisions in `nvim-pack-lock.json`
   - blink.cmp downloads its prebuilt fuzzy-matcher binary
   - nvim-treesitter builds the parsers in the background

## Updating Plugins

`:lua vim.pack.update()` opens a review tab: `:write` applies the updates, `:quit` discards them. Then `:restart`. Commit the changed `nvim-pack-lock.json`.

On another machine that already has the plugins, pulling a newer lockfile and restarting only installs plugins it is missing. Move the installed ones to the lockfile's revisions with `:lua vim.pack.update(nil, { target = 'lockfile' })`: it opens the same review tab, so `:write`, then `:restart`.
