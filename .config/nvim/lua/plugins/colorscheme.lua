return {
	"craftzdog/solarized-osaka.nvim",
	lazy = false,
	priority = 1000,
	main = "solarized-osaka",
	opts = {
		transparent = false,
	},
	init = function()
		vim.cmd.colorscheme("solarized-osaka")
	end,
}
