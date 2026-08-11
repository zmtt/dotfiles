# Neovim Setup Guide

## Dependencies

### System-Level Requirements

| Dependency | Purpose | Install |
|------------|---------|---------|
| **Neovim 0.12+** | Required for `vim.lsp.config` API and nvim-treesitter (main branch) | `brew install neovim` |
| **Git** | Plugin manager (lazy.nvim) | `brew install git` |
| **C compiler + make** | Build telescope-fzf-native and treesitter parsers | `xcode-select --install` |
| **ripgrep** | Telescope live grep | `brew install ripgrep` |
| **fd** | Faster file finding (optional) | `brew install fd` |

### Manual Tool Installs (not in Mason)

```bash
brew install ktlint
brew install --cask kotlin-lsp
```

- **Xcode Command Line Tools** - for sourcekit-lsp (Swift support)
- Swift formatting uses the toolchain's own `swift format` (Swift 6+), no separate install

### Auto-Installed via Mason

Declared in `lua/plugins/mason.lua`, installed automatically on first launch:

- LSP servers: `lua-language-server`, `pyright`, `ruff`, `typescript-language-server`, `bash-language-server`, `marksman`, `yaml-language-server` (kotlin-lsp comes from brew)
- Formatters: `stylua`, `prettierd`, `shfmt`

Swift's `sourcekit-lsp` comes from Xcode (`xcrun`), not Mason. Python formatting and import sorting are handled by `ruff` via conform.nvim.

## Replicating on Another Mac

### 1. Install prerequisites

```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install neovim git ripgrep fd

# Ensure Xcode CLI tools (for C compiler + sourcekit-lsp)
xcode-select --install
```

### 2. Copy your config

```bash
# Option A: Direct copy (if you have access to old machine)
scp -r oldmac:~/.config/nvim ~/.config/nvim

# Option B: If you version control it (recommended)
git clone <your-nvim-config-repo> ~/.config/nvim
```

### 3. Launch Neovim

```bash
nvim
```

On first launch:

- lazy.nvim bootstraps itself
- Plugins install automatically
- Mason auto-installs formatters/LSPs
- Treesitter parsers install in the background

## Version Control (Recommended)

To make syncing easier and track changes:

```bash
cd ~/.config/nvim
git init
git add .
git commit -m "Initial neovim config"
git remote add origin <your-repo-url>
git push -u origin main
```

Commit `lazy-lock.json`: it pins exact plugin versions so the config is reproducible across machines.
