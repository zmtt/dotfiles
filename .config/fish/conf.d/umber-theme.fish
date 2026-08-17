# Slot names, not hex: Ghostty swaps umber/umber-light with the macOS appearance
# and hex cannot follow that. All slots clear 4.5:1 on both grounds.

# Syntax highlighting
set --global fish_color_normal normal
set --global fish_color_command cyan
set --global fish_color_keyword magenta
set --global fish_color_quote yellow
set --global fish_color_redirection blue
set --global fish_color_operator blue
set --global fish_color_escape bryellow
set --global fish_color_end brblack
set --global fish_color_comment brblack
set --global fish_color_autosuggestion brblack
set --global fish_color_param normal
set --global fish_color_error brred
set --global fish_color_valid_path --underline

# Prompt identity
set --global fish_color_cwd green
set --global fish_color_cwd_root brred
set --global fish_color_user green
set --global fish_color_host normal
set --global fish_color_host_remote yellow
set --global fish_color_status brred

# Reverse video: the only highlight that stays correct in both palettes.
set --global fish_color_selection --reverse
set --global fish_color_search_match --reverse
set --global fish_color_history_current --bold
set --global fish_color_cancel -r

# Completion pager
set --global fish_pager_color_progress brblack
set --global fish_pager_color_prefix cyan --bold
set --global fish_pager_color_completion normal
set --global fish_pager_color_description brblack
set --global fish_pager_color_selected_background --reverse
