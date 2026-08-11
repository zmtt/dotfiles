return {
	"stevearc/conform.nvim",
	event = { "BufWritePre" },
	cmd = { "ConformInfo" },
	keys = {
		{
			"<leader>cf",
			function()
				require("conform").format({ async = true, lsp_format = "fallback" })
			end,
			mode = "",
			desc = "Format buffer",
		},
	},
	opts = function()
		local has_swift = vim.fn.executable("swift") == 1
		local has_ktlint = vim.fn.executable("ktlint") == 1

		return {
			formatters_by_ft = {
				lua = { "stylua" },
				python = { "ruff_fix", "ruff_organize_imports", "ruff_format" },
				javascript = { "prettierd" },
				typescript = { "prettierd" },
				javascriptreact = { "prettierd" },
				typescriptreact = { "prettierd" },
				json = { "prettierd" },
				yaml = { "prettierd" },
				markdown = { "prettierd" },
				html = { "prettierd" },
				css = { "prettierd" },
				sh = { "shfmt" },
				-- Official Apple swift-format via the toolchain (`swift format`),
				-- bundled with Swift 6+. Style is controlled by a project-local
				-- `.swift-format` file (defaults to 2-space indent).
				swift = has_swift and { "swift" } or {},
				kotlin = has_ktlint and { "ktlint" } or {},
			},
			format_on_save = {
				timeout_ms = 500,
				lsp_format = "fallback",
			},
			formatters = {
				shfmt = {
					prepend_args = { "-i", "4" },
				},
				prettierd = {
					prepend_args = { "--tab-width=4" },
				},
				ktlint = {
					prepend_args = { "--indent-size=4" },
				},
			},
		}
	end,
}
