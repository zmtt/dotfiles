return {
    "neovim/nvim-lspconfig",
    event = { "BufReadPre", "BufNewFile" },
    dependencies = {
        "saghen/blink.cmp",
    },
    config = function()
        local capabilities = require("blink.cmp").get_lsp_capabilities()

        local on_attach = function(client, bufnr)
            local opts = { noremap = true, silent = true, buffer = bufnr }

            vim.keymap.set("n", "gd", vim.lsp.buf.definition, vim.tbl_extend("force", opts, { desc = "Go to definition" }))
            vim.keymap.set("n", "K", vim.lsp.buf.hover, vim.tbl_extend("force", opts, { desc = "Hover documentation" }))
            vim.keymap.set("n", "gi", vim.lsp.buf.implementation, vim.tbl_extend("force", opts, { desc = "Go to implementation" }))
            vim.keymap.set("n", "<leader>rn", vim.lsp.buf.rename, vim.tbl_extend("force", opts, { desc = "Rename symbol" }))
            vim.keymap.set("n", "<leader>ca", vim.lsp.buf.code_action, vim.tbl_extend("force", opts, { desc = "Code action" }))
            vim.keymap.set("n", "gr", vim.lsp.buf.references, vim.tbl_extend("force", opts, { desc = "References" }))
            vim.keymap.set("n", "<leader>d", vim.diagnostic.open_float, vim.tbl_extend("force", opts, { desc = "Line diagnostics" }))
            vim.keymap.set("n", "[d", vim.diagnostic.goto_prev, vim.tbl_extend("force", opts, { desc = "Previous diagnostic" }))
            vim.keymap.set("n", "]d", vim.diagnostic.goto_next, vim.tbl_extend("force", opts, { desc = "Next diagnostic" }))

            local ok, wk = pcall(require, "which-key")
            if ok then
                wk.add({
                    { "<leader>c", group = "code", buffer = bufnr },
                    { "<leader>r", group = "refactor", buffer = bufnr },
                })
            end
        end

        -- Configure LSP servers using vim.lsp.config
        vim.lsp.config.lua_ls = {
            capabilities = capabilities,
            on_attach = on_attach,
            settings = {
                Lua = {
                    diagnostics = {
                        globals = { "vim" },
                    },
                    workspace = {
                        library = vim.api.nvim_get_runtime_file("", true),
                    },
                    telemetry = {
                        enable = false,
                    },
                },
            },
        }

        vim.lsp.config.pyright = {
            capabilities = capabilities,
            on_attach = on_attach,
        }

        vim.lsp.config.ts_ls = {
            capabilities = capabilities,
            on_attach = on_attach,
        }

        vim.lsp.config.bashls = {
            capabilities = capabilities,
            on_attach = on_attach,
        }

        vim.lsp.config.marksman = {
            capabilities = capabilities,
            on_attach = on_attach,
        }

        vim.lsp.config.yamlls = {
            capabilities = capabilities,
            on_attach = on_attach,
        }

        vim.lsp.config.kotlin_language_server = {
            capabilities = capabilities,
            on_attach = on_attach,
            filetypes = { "kotlin" },
        }

        vim.lsp.config.jdtls = {
            capabilities = capabilities,
            on_attach = on_attach,
            filetypes = { "java" },
        }

        local has_xcrun = vim.fn.executable("xcrun") == 1
        if has_xcrun then
            vim.lsp.config.sourcekit = {
                cmd = { "xcrun", "sourcekit-lsp" },
                capabilities = capabilities,
                on_attach = on_attach,
                filetypes = { "swift", "objc", "objcpp" },
            }
        else
            local warned_sourcekit = false
            vim.api.nvim_create_autocmd("FileType", {
                pattern = { "swift", "objc", "objcpp" },
                callback = function()
                    if warned_sourcekit then
                        return
                    end
                    warned_sourcekit = true
                    vim.notify(
                        "sourcekit-lsp unavailable: install Xcode Command Line Tools",
                        vim.log.levels.WARN
                    )
                end,
            })
        end

        vim.lsp.enable({
            "lua_ls",
            "pyright",
            "ts_ls",
            "bashls",
            "marksman",
            "yamlls",
            "kotlin_language_server",
            "jdtls",
            has_xcrun and "sourcekit" or nil,
        })
    end,
}
