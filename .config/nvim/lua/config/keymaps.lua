-- Keymaps configuration

-- Clear search highlight on Escape
vim.keymap.set("n", "<Esc>", "<cmd>nohlsearch<cr>", { desc = "Clear search highlight" })

-- File explorer
vim.keymap.set("n", "<leader>ee", "<cmd>Explore<cr>", { desc = "Open file explorer" })

-- LSP keymaps (will be overridden by on_attach in lspconfig.lua when LSP is active)
vim.keymap.set("n", "<leader>li", "<cmd>LspInfo<cr>", { desc = "LSP Info" })
vim.keymap.set("n", "<leader>lr", "<cmd>LspRestart<cr>", { desc = "LSP Restart" })

-- Health check
vim.keymap.set("n", "<leader>ch", "<cmd>checkhealth<cr>", { desc = "Check Health" })

-- Buffer navigation
vim.keymap.set("n", "<S-h>", "<cmd>bp<cr>", { desc = "Previous buffer" })
vim.keymap.set("n", "<S-l>", "<cmd>bn<cr>", { desc = "Next buffer" })

-- Move lines up/down in visual mode
vim.keymap.set("v", "J", ":m '>+1<CR>gv=gv", { desc = "Move selection down" })
vim.keymap.set("v", "K", ":m '<-2<CR>gv=gv", { desc = "Move selection up" })

-- Keep cursor centered when scrolling
vim.keymap.set("n", "<C-d>", "<C-d>zz")
vim.keymap.set("n", "<C-u>", "<C-u>zz")

-- Keep cursor centered when searching
vim.keymap.set("n", "n", "nzzzv")
vim.keymap.set("n", "N", "Nzzzv")

-- Window navigation
vim.keymap.set("n", "<C-h>", "<C-w>h", { desc = "Move to left split" })
vim.keymap.set("n", "<C-j>", "<C-w>j", { desc = "Move to below split" })
vim.keymap.set("n", "<C-k>", "<C-w>k", { desc = "Move to above split" })
vim.keymap.set("n", "<C-l>", "<C-w>l", { desc = "Move to right split" })
