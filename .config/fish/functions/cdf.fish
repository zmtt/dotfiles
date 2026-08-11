function cdf --description "Fuzzy cd into a directory"
    set -l dir (fd --type d --hidden --follow --exclude .git \
        | fzf --prompt='cd> ' \
              --preview='eza -la --group-directories-first --color=always {} | head -200' \
              --preview-window=right:60%)
    test -n "$dir"; and cd "$dir"
end

