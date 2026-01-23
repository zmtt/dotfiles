return {
	"stevearc/conform.nvim",
	event = { "BufWritePre" },
	cmd = { "ConformInfo" },
	keys = {
		{
			"<leader>f",
			function()
				require("conform").format({ async = true, lsp_fallback = true })
			end,
			mode = "",
			desc = "Format buffer",
		},
	},
	opts = function()
		local has_swiftformat = vim.fn.executable("swiftformat") == 1
		local has_ktlint = vim.fn.executable("ktlint") == 1

		return {
			formatters_by_ft = {
				lua = { "stylua" },
				python = { "isort", "black" },
				javascript = { "prettierd", "prettier", stop_after_first = true },
				typescript = { "prettierd", "prettier", stop_after_first = true },
				javascriptreact = { "prettierd", "prettier", stop_after_first = true },
				typescriptreact = { "prettierd", "prettier", stop_after_first = true },
				json = { "prettierd", "prettier", stop_after_first = true },
				yaml = { "prettierd", "prettier", stop_after_first = true },
				markdown = { "prettierd", "prettier", stop_after_first = true },
				html = { "prettierd", "prettier", stop_after_first = true },
				css = { "prettierd", "prettier", stop_after_first = true },
				sh = { "shfmt" },
				swift = has_swiftformat and { "swiftformat" } or {},
				kotlin = has_ktlint and { "ktlint" } or {},
			},
			format_on_save = {
				timeout_ms = 500,
				lsp_fallback = true,
			},
			formatters = {
				shfmt = {
					prepend_args = { "-i", "4" },
				},
				prettier = {
					prepend_args = { "--tab-width", "4" },
				},
				prettierd = {
					prepend_args = { "--tab-width", "4" },
				},
				black = {
					prepend_args = { "--line-length", "88" },
				},
				swiftformat = {
					prepend_args = { "--indent", "4" },
				},
				ktlint = {
					prepend_args = { "--indent-size=4" },
				},
			},
		}
	end,
}
