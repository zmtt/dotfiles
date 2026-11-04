return {
	cmd = { "pyright-langserver", "--stdio" },
	filetypes = { "python" },
	root_markers = {
		"pyrightconfig.json",
		"pyproject.toml",
		"setup.py",
		"setup.cfg",
		"requirements.txt",
		"Pipfile",
		".git",
	},
	settings = {
		pyright = {
			-- Unreachable/unreferenced/deprecated hints are too noisy as Nvim
			-- diagnostics (neovim/neovim#30444).
			disableTaggedHints = true,
			-- ruff organizes imports.
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
}
