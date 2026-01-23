return {
	"williamboman/mason.nvim",
	dependencies = {
		"WhoIsSethDaniel/mason-tool-installer.nvim",
	},
	config = function()
		require("mason").setup()
		require("mason-tool-installer").setup({
			ensure_installed = {
				-- LSP servers
				"lua-language-server",
				"pyright",
				"typescript-language-server",
				"bash-language-server",
				"marksman",
				"yaml-language-server",
				"kotlin-language-server",
				"jdtls",
				-- Formatters
				"stylua",
				"black",
				"isort",
				"prettierd",
				"shfmt",
				-- Note: swiftformat and ktlint not in Mason
				-- Install manually: brew install swiftformat ktlint
			},
			auto_update = true,
			run_on_start = true,
		})
	end,
}
