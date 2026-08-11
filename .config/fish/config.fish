# --- Environment ---
set -gx EDITOR nvim
set -gx MANPAGER "sh -c 'col -bx | bat -l man -p'"

# fzf: shared UI options + fd-powered file/dir sources (Ctrl-T / Alt-C)
set -gx FZF_DEFAULT_OPTS "--height=80% --layout=reverse --border"
set -gx FZF_DEFAULT_COMMAND "fd --type f --hidden --follow --exclude .git"
set -gx FZF_CTRL_T_COMMAND $FZF_DEFAULT_COMMAND
set -gx FZF_ALT_C_COMMAND "fd --type d --hidden --follow --exclude .git"

# Homebrew (unconditional: non-interactive fish needs brew tools on PATH too)
eval (/opt/homebrew/bin/brew shellenv)

# PATH (fish_add_path is idempotent, keeps fish_user_paths reproducible from here)
fish_add_path ~/.local/bin

set -g fish_greeting ""

if status is-interactive
    # Prompt, cd frecency, fzf key bindings
    starship init fish | source
    zoxide init fish | source
    fzf --fish | source

    # eza ls family (color/icons auto-disable when piped)
    set -l eza "eza --icons --group-directories-first"
    alias ls="$eza"
    alias ll="$eza -l --sort=newest"
    alias la="$eza -la --sort=newest"
    alias lt="$eza -aT --level=3 --ignore-glob=.git"

    alias vim="nvim"

    # Brew upgrade and cleanup
    alias brew-up="brew upgrade && brew cleanup --prune=all"
    alias brewfile="brew bundle --file=~/.config/brew/Brewfile"

    # Dotfiles bare repo
    alias dot='git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME'

    # Bear
    alias bearcli="/Applications/Bear.app/Contents/MacOS/bearcli"
end
