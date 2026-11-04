require("fzf-lua").setup({
	-- fzf-lua passes only the fg of FzfLuaFzfMatch to fzf, which drops the bold.
	fzf_colors = {
		true,
		["hl"] = { "fg", "FzfLuaFzfMatch", "bold" },
		["hl+"] = { "fg", "FzfLuaFzfMatch", "bold" },
	},
	-- fzf-lua defaults to fd --hidden; <A-h> toggles dotfiles back on.
	-- --keep-right keeps the file name visible when a long path overflows.
	files = { hidden = false, fzf_opts = { ["--keep-right"] = true } },
	buffers = { fzf_opts = { ["--keep-right"] = true } },
	winopts = {
		preview = { layout = "vertical" },
	},
	file_ignore_patterns = {
		"node_modules/",
		"dist/",
		"build/",
		"target/",
	},
})

vim.keymap.set("n", "<leader>ff", "<cmd>FzfLua files<cr>", { desc = "Find files" })
vim.keymap.set("n", "<leader>fg", "<cmd>FzfLua live_grep<cr>", { desc = "Live grep" })
vim.keymap.set("n", "<leader>fb", "<cmd>FzfLua buffers<cr>", { desc = "Buffers" })
vim.keymap.set("n", "<leader>fh", "<cmd>FzfLua helptags<cr>", { desc = "Help tags" })
