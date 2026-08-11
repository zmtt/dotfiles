function fo --description "Fuzzy open file(s) with macOS open"
    set -l files (fd --type f --hidden --follow --exclude .git \
        | fzf -m --prompt='open> ' \
              --preview='bat --style=numbers --color=always --line-range :200 {}' \
              --preview-window=right:60%)
    test (count $files) -gt 0; and open $files
end

