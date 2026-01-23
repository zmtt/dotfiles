return {
	"lewis6991/gitsigns.nvim",
	event = { "BufReadPre", "BufNewFile" },
	opts = {
		signcolumn = true,
		current_line_blame = false,
	},
}
