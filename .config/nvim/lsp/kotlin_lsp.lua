-- JetBrains' official kotlin-lsp (brew: cask "kotlin-lsp"). Replaces fwcd's
-- kotlin-language-server, whose Gradle resolver is incompatible with
-- org.gradle.configuration-cache=true and is in maintenance mode upstream.
return {
	-- lspconfig's cmd is intellij-server. The cask ships it in its own bin/ but
	-- links only the kotlin-lsp launcher onto PATH, which warns that it is
	-- deprecated in favour of bin/intellij-server. Switch once the cask links it.
	cmd = { "kotlin-lsp", "--stdio" },
	filetypes = { "kotlin" },
	-- Repo-root markers only: per-module build.gradle(.kts) would root the
	-- server at a submodule.
	root_markers = { "settings.gradle", "settings.gradle.kts", "workspace.json", ".git" },
}
