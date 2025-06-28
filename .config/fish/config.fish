if status is-interactive
	# Commands to run in interactive sessions can go here
end

# Homebrew
eval (/opt/homebrew/bin/brew shellenv)

# Empty the text in the default greeting function.
set -U fish_greeting

# Aliases

# Brew upgrade and cleanup
alias brew-up="brew upgrade && brew cleanup --prune=all"

# Changing "cat" to "bat"
alias cat="bat"

# Changing "vim" to "nvim"
alias vim="nvim"

# Changing "ls" to "eza"
alias ls="eza -al --color=always --icons --group-directories-first -snewest"
alias la="eza -a --color=always --icons --group-directories-first -snewest"
alias ll="eza -l --color=always --icons --group-directories-first -snewest"
alias lt="eza -aT --level=3 --color=always --icons --group-directories-first -snewest"

# Dotfile
alias df="/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME"

# zoxide
zoxide init fish | source

# Starship
starship init fish | source
