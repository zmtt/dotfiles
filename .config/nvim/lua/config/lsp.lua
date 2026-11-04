-- Server configs live in lsp/<name>.lua. blink.cmp adds its completion
-- capabilities to vim.lsp.config("*") from its own plugin/ file.
vim.lsp.enable({
	"lua_ls",
	"pyright",
	"ruff",
	"bashls",
	"marksman",
	"kotlin_lsp",
})

-- K, grn, gra, grr, gri, grt, gO, <C-s> and CTRL-] are Neovim defaults.
vim.api.nvim_create_autocmd("LspAttach", {
	group = vim.api.nvim_create_augroup("lsp-keymaps", { clear = true }),
	callback = function(ev)
		-- ruff has no definitionProvider. Mapping gd for it would shadow the
		-- builtin gd in a Python buffer where pyright is not running.
		local client = assert(vim.lsp.get_client_by_id(ev.data.client_id))
		if client:supports_method("textDocument/definition") then
			vim.keymap.set("n", "gd", vim.lsp.buf.definition, { buffer = ev.buf, desc = "Go to definition" })
		end
	end,
})
