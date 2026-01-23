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

-- return {
-- 	"folke/tokyonight.nvim",
-- 	lazy = false,
-- 	priority = 1000,
-- 	opts = {
-- 		style = "storm",
-- 		styles = {
-- 			comments = { italic = true },
-- 			keywords = { italic = true },
-- 		},
-- 	},
-- 	init = function()
-- 		vim.cmd.colorscheme("tokyonight-storm")
-- 	end,
-- }
