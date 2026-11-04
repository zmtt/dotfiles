return {
	cmd = { "ruff", "server" },
	filetypes = { "python" },
	root_markers = { "pyproject.toml", "ruff.toml", ".ruff.toml", ".git" },
	on_attach = function(client)
		-- pyright's hover has the type information.
		client.server_capabilities.hoverProvider = false
	end,
}
