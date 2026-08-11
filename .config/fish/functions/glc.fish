function glc --description "Fuzzy git log; Enter copies hash"
    git log --oneline --color=always \
    | fzf --ansi --no-sort --reverse --prompt='commit> ' \
          --preview='git show --color=always {1} | bat --color=always --style=plain --paging=never' \
          --preview-window=right:60% \
          --bind='enter:execute(printf %s {1} | pbcopy)+abort'
end

