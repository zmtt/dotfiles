-- Commit message editing.
-- Auto-wrap at 72 is already provided by nvim's built-in gitcommit ftplugin
-- (textwidth=72 + formatoptions has 't'), so the body wraps as you type.
-- This adds the visual rulers and a couple of quality-of-life touches.

vim.opt_local.textwidth = 72          -- body wrap width (explicit; matches the built-in default)
vim.opt_local.colorcolumn = "51,73"   -- rulers just past the 50-char subject and 72-char body limits
vim.opt_local.spell = true            -- spell-check the prose
