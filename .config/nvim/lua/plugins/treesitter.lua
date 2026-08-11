-- Main branch (the rewrite): master is frozen upstream. Parsers are installed
-- explicitly below; highlighting/indent are enabled per buffer via autocmd.
return {
	"nvim-treesitter/nvim-treesitter",
	branch = "main",
	lazy = false,
	build = ":TSUpdate",
	config = function()
		require("nvim-treesitter").install({
			"c",
			"lua",
			"vim",
			"vimdoc",
			"query",
			"markdown",
			"markdown_inline",
			"bash",
			"python",
			"javascript",
			"typescript",
			"json",
			"yaml",
			"toml",
			"java",
			"kotlin",
			"swift",
		})

		vim.api.nvim_create_autocmd("FileType", {
			group = vim.api.nvim_create_augroup("treesitter-start", { clear = true }),
			callback = function(ev)
				local max_filesize = 100 * 1024 -- 100 KB
				local ok, stats = pcall(vim.uv.fs_stat, vim.api.nvim_buf_get_name(ev.buf))
				if ok and stats and stats.size > max_filesize then
					return
				end
				-- No-op for filetypes without an installed parser
				if pcall(vim.treesitter.start, ev.buf) then
					vim.bo[ev.buf].indentexpr = "v:lua.require'nvim-treesitter'.indentexpr()"
				end
			end,
		})
	end,
}
