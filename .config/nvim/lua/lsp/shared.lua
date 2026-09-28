local M = {}

function M.on_attach(_, bufnr)
    local opts = { noremap = true, silent = true, buffer = bufnr }

    -- K (hover), [d / ]d and <C-w>d (diagnostics), grr (references),
    -- gri (implementation), grn (rename), gra (code action) are Neovim
    -- builtins; only the non-default mappings are defined here.
    vim.keymap.set("n", "gd", vim.lsp.buf.definition, vim.tbl_extend("force", opts, { desc = "Go to definition" }))
end

return M
