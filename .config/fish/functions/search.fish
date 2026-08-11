function search --description "Fuzzy content search with rg; Enter opens nvim at the match"
    set -l result (rg --line-number --no-heading --color=always --smart-case '' \
        | fzf --ansi --delimiter=: --prompt='rg> ' \
              --preview='bat --style=numbers --color=always --highlight-line {2} {1}' \
              --preview-window='right:60%,+{2}+3/3')
    if test -n "$result"
        set -l parts (string split : $result)
        nvim +$parts[2] $parts[1]
    end
end
