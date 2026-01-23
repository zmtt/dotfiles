# Solarized Osaka Dark (from craftzdog/solarized-osaka.nvim)
# https://github.com/craftzdog/solarized-osaka.nvim/blob/main/extras/fish/solarized_osaka_dark.fish

# Color palette
set -l foreground 839395
set -l selection 1a6397
set -l base01 576d74
set -l red db302d
set -l orange c94c16
set -l yellow b28500
set -l green 849900
set -l purple 6d71c4
set -l cyan 29a298
set -l pink d23681

# Syntax Highlighting Colors
set --global fish_color_normal $foreground
set --global fish_color_command $cyan
set --global fish_color_keyword $pink
set --global fish_color_quote $yellow
set --global fish_color_redirection $foreground
set --global fish_color_end $orange
set --global fish_color_error $red
set --global fish_color_param $purple
set --global fish_color_comment $base01
set --global fish_color_selection --background=$selection
set --global fish_color_search_match --background=$selection
set --global fish_color_operator $green
set --global fish_color_escape $pink
set --global fish_color_autosuggestion $base01
set --global fish_color_cancel -r
set --global fish_color_cwd $green
set --global fish_color_cwd_root $red
set --global fish_color_history_current --bold
set --global fish_color_host $foreground
set --global fish_color_host_remote $yellow
set --global fish_color_status $red
set --global fish_color_user $green
set --global fish_color_valid_path --underline

# Completion Pager Colors
set --global fish_pager_color_progress $base01
set --global fish_pager_color_prefix $cyan
set --global fish_pager_color_completion $foreground
set --global fish_pager_color_description $base01
set --global fish_pager_color_selected_background --background=$selection
