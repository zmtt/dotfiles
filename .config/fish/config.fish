if status is-interactive
    # Commands to run in interactive sessions can go here
end

# Homebrew
eval (/opt/homebrew/bin/brew shellenv)

# Greeting is disabled via fish_variables (universal variable)

# Aliases

# Changing "cat" to "bat"
alias cat="bat"

# Changing "vim" to "nvim"
alias vim="nvim"

# Changing "ls" to "eza"
alias ls="eza -al --color=always --icons --group-directories-first -snewest"
alias la="eza -a --color=always --icons --group-directories-first -snewest"
alias ll="eza -l --color=always --icons --group-directories-first -snewest"
alias lt="eza -aT --level=3 --color=always --icons --group-directories-first -snewest"

# Use Extended Regular Expressions (ERE) as default
alias grep="grep -E"

# Brew upgrade and cleanup
alias brew-up="brew upgrade && brew cleanup --prune=all"

# Dotfiles bare repo
alias dot="git --git-dir=\$HOME/.dotfiles/ --work-tree=\$HOME"

# Brewfile
alias brewfile="brew bundle --file=~/.config/brew/Brewfile"

# Set up fzf key bindings
fzf --fish | source

# Starship
starship init fish | source

# zoxide
zoxide init fish | source

