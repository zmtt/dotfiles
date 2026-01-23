# Neovim Setup Guide

## Dependencies

### System-Level Requirements

| Dependency | Purpose | Install |
|------------|---------|---------|
| **Neovim 0.10+** | Required for `vim.lsp.config` API | `brew install neovim` |
| **Git** | Plugin manager (lazy.nvim) | `brew install git` |
| **C compiler + make** | Build telescope-fzf-native | `xcode-select --install` |
| **ripgrep** | Telescope live grep | `brew install ripgrep` |
| **fd** | Faster file finding (optional) | `brew install fd` |

### Manual Tool Installs (not in Mason)

```bash
brew install swiftformat ktlint
```

- **Xcode Command Line Tools** - for sourcekit-lsp (Swift support)

### Auto-Installed via Mason

These are installed automatically on first launch:

- `stylua` - Lua formatter
- `black` - Python formatter
- `isort` - Python import sorter
- `prettierd` - JS/TS/Web formatter
- `shfmt` - Shell formatter

### LSP Servers (via Mason)

These are configured and will be installed via Mason:

- `lua_ls` - Lua
- `pyright` - Python
- `ts_ls` - TypeScript/JavaScript
- `bashls` - Bash/Shell
- `marksman` - Markdown
- `yamlls` - YAML
- `kotlin_language_server` - Kotlin
- `jdtls` - Java
- `sourcekit` - Swift (via Xcode, not Mason)

## Replicating on Another Mac

### 1. Install prerequisites

```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install neovim git ripgrep fd swiftformat ktlint

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

The `lazy-lock.json` ensures exact plugin versions are reproducible across machines.
