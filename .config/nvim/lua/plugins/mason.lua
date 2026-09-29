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
				"bash-language-server",
				"marksman",
				-- kotlin-lsp comes from brew (cask "kotlin-lsp")
				-- Formatters
				"stylua",
				"prettierd",
				"shfmt",
				-- swift-format ships with the Swift/Xcode toolchain (`swift format`).
			},
			auto_update = false,
			run_on_start = true,
		})
	end,
}
