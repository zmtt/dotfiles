return {
	"mason-org/mason.nvim",
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
				"ruff",
				"typescript-language-server",
				"bash-language-server",
				"marksman",
				"yaml-language-server",
				-- kotlin-lsp comes from brew (cask "kotlin-lsp")
				-- Formatters
				"stylua",
				"prettierd",
				"shfmt",
				-- swift-format ships with the Swift/Xcode toolchain (`swift format`).
				-- ktlint is not in Mason: brew install ktlint
			},
			auto_update = false,
			run_on_start = true,
		})
	end,
}
