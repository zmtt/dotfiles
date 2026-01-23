-- Keymaps configuration

-- File explorer
vim.keymap.set("n", "<leader>ee", "<cmd>Explore<cr>", { desc = "Open file explorer" })

-- LSP keymaps (will be overridden by on_attach in lspconfig.lua when LSP is active)
vim.keymap.set("n", "<leader>li", "<cmd>LspInfo<cr>", { desc = "LSP Info" })
vim.keymap.set("n", "<leader>lr", "<cmd>LspRestart<cr>", { desc = "LSP Restart" })

-- Health check
vim.keymap.set("n", "<leader>ch", "<cmd>checkhealth<cr>", { desc = "Check Health" })
