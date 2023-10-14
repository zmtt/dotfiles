-- Pull in the wezterm API
local wezterm = require 'wezterm'

-- This table will hold the configuration.
local config = {}

-- In newer versions of wezterm, use the config_builder which will
-- help provide clearer error messages
if wezterm.config_builder then
  config = wezterm.config_builder()
end

-- This is where you actually apply your config choices

-- For example, changing the color scheme:
config.color_scheme = 'tokyonight_storm'
config.font_size = 14.0
config.line_height = 1.1
config.initial_cols = 100
config.initial_rows = 30
config.hide_tab_bar_if_only_one_tab = true
config.window_close_confirmation = "NeverPrompt"


-- and finally, return the configuration to wezterm
return config

