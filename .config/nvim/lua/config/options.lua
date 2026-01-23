-- [[ Setting options ]]
-- See `:help vim.o`

-- Show line numbers
vim.o.number = true

-- Show relative line numbers
vim.o.relativenumber = true

-- Use system clipboard for yanks and puts
vim.opt.clipboard = "unnamedplus"

-- Better UI defaults
vim.opt.termguicolors = true
vim.opt.signcolumn = "yes"
vim.opt.updatetime = 250
vim.opt.cursorline = true
vim.opt.scrolloff = 8
vim.opt.sidescrolloff = 8
vim.opt.numberwidth = 4
vim.opt.showmode = false

-- Indentation settings: 4 spaces
vim.o.tabstop = 4 -- Number of spaces a tab counts for
vim.o.shiftwidth = 4 -- Number of spaces for each indentation level
vim.o.softtabstop = 4 -- Number of spaces tab inserts in insert mode
vim.o.expandtab = true -- Convert tabs to spaces
vim.o.smartindent = true -- Smart autoindenting on new lines
vim.o.shiftround = true -- Round indent to multiple of shiftwidth

-- Case-insensitive search (unless uppercase is used)
vim.o.ignorecase = true
vim.o.smartcase = true

-- Diagnostics display
vim.diagnostic.config({
	virtual_text = false,
	signs = true,
	underline = true,
	update_in_insert = false,
	severity_sort = true,
	float = {
		border = "rounded",
		source = "if_many",
	},
})
