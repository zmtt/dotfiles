vim.keymap.set("n", "<leader>r", "<cmd>w | !python3 %:S<cr>", { buffer = true, desc = "Run file" })
