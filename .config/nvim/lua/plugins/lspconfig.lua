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

        vim.lsp.enable({
            "lua_ls",
            "pyright",
            "ruff",
            "bashls",
            "marksman",
            "kotlin_lsp",
        })
    end,
}
