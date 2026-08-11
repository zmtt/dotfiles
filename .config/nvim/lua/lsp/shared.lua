local M = {}

function M.on_attach(_, bufnr)
    local opts = { noremap = true, silent = true, buffer = bufnr }

    -- K (hover), [d / ]d (diagnostics), grr (references), gri (implementation),
    -- grn (rename), gra (code action) are Neovim builtins; only the
    -- non-default mappings are defined here.
    vim.keymap.set("n", "gd", vim.lsp.buf.definition, vim.tbl_extend("force", opts, { desc = "Go to definition" }))
    vim.keymap.set("n", "<leader>rn", vim.lsp.buf.rename, vim.tbl_extend("force", opts, { desc = "Rename symbol" }))
    vim.keymap.set("n", "<leader>ca", vim.lsp.buf.code_action, vim.tbl_extend("force", opts, { desc = "Code action" }))
    vim.keymap.set("n", "<leader>cd", vim.diagnostic.open_float, vim.tbl_extend("force", opts, { desc = "Line diagnostics" }))

    local ok, wk = pcall(require, "which-key")
    if ok then
        wk.add({
            { "<leader>c", group = "code", buffer = bufnr },
            { "<leader>r", group = "refactor", buffer = bufnr },
        })
    end
end

return M
