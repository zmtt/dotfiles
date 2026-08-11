function fe --description "Fuzzy edit file(s) with bat preview"
    set -l files (fd --type f --hidden --follow --exclude .git \
        | fzf -m --prompt='file> ' \
              --preview='bat --style=numbers --color=always --line-range :200 {}' \
              --preview-window=right:60%)
    test (count $files) -gt 0; and nvim $files
end

