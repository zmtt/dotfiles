return {
    "neovim/nvim-lspconfig",
    event = { "BufReadPre", "BufNewFile" },
    dependencies = {
        "saghen/blink.cmp",
    },
    config = function()
        local on_attach = require("lsp.shared").on_attach

        -- Applied to every server; per-server configs below only add what
        -- differs (a server-specific on_attach replaces this one).
        vim.lsp.config("*", {
            capabilities = require("blink.cmp").get_lsp_capabilities(),
            on_attach = on_attach,
        })

        vim.lsp.config("lua_ls", {
            settings = {
                Lua = {
                    diagnostics = {
                        globals = { "vim" },
                    },
                    workspace = {
                        library = { vim.env.VIMRUNTIME },
                    },
                },
            },
        })

        vim.lsp.config("pyright", {
            settings = {
                pyright = {
                    disableOrganizeImports = true,
                },
                python = {
                    analysis = {
                        typeCheckingMode = "basic",
                        autoSearchPaths = true,
                        useLibraryCodeForTypes = true,
                        diagnosticMode = "openFilesOnly",
                    },
                },
            },
        })

        vim.lsp.config("ruff", {
            on_attach = function(client, bufnr)
                client.server_capabilities.hoverProvider = false
                on_attach(client, bufnr)
            end,
        })

        -- Kotlin: JetBrains' official kotlin-lsp (brew: cask "kotlin-lsp").
        -- Replaces fwcd's kotlin-language-server, whose Gradle resolver is
        -- incompatible with org.gradle.configuration-cache=true and is in
        -- maintenance mode upstream.
        vim.lsp.config("kotlin_lsp", {
            -- lspconfig's default cmd is intellij-server, which only the Mason
            -- package shipped; the brew cask installs the kotlin-lsp launcher.
            cmd = { "kotlin-lsp", "--stdio" },
            -- lspconfig's default root_markers include per-module
            -- build.gradle(.kts), which roots the server at a submodule;
            -- restrict to repo-root markers.
            root_markers = { "settings.gradle", "settings.gradle.kts", "workspace.json", ".git" },
        })

        local has_xcrun = vim.fn.executable("xcrun") == 1
        if has_xcrun then
            vim.lsp.config("sourcekit", {
                cmd = { "xcrun", "sourcekit-lsp" },
                filetypes = { "swift", "objc", "objcpp" },
            })
        else
            local warned_sourcekit = false
            vim.api.nvim_create_autocmd("FileType", {
                group = vim.api.nvim_create_augroup("sourcekit-missing-warning", { clear = true }),
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
            "ruff",
            "ts_ls",
            "bashls",
            "marksman",
            "yamlls",
            "kotlin_lsp",
            has_xcrun and "sourcekit" or nil,
        })
    end,
}
