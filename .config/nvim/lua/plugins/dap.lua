-- Swift debugging: nvim-dap + lldb-dap. lldb-dap ships with the Xcode/Swift
-- toolchain and is located via `xcrun --find lldb-dap` (no separate install).
-- Build first with `swift build`, then launch the binary from .build/debug/.
return {
	"mfussenegger/nvim-dap",
	dependencies = {
		{ "rcarriga/nvim-dap-ui", dependencies = { "nvim-neotest/nvim-nio" } },
	},
	keys = {
		{ "<leader>db", function() require("dap").toggle_breakpoint() end, desc = "Toggle breakpoint" },
		{ "<leader>dc", function() require("dap").continue() end, desc = "Continue / start" },
		{ "<leader>di", function() require("dap").step_into() end, desc = "Step into" },
		{ "<leader>do", function() require("dap").step_over() end, desc = "Step over" },
		{ "<leader>dO", function() require("dap").step_out() end, desc = "Step out" },
		{ "<leader>dr", function() require("dap").repl.toggle() end, desc = "Toggle REPL" },
		{ "<leader>dt", function() require("dap").terminate() end, desc = "Terminate" },
		{ "<leader>du", function() require("dapui").toggle() end, desc = "Toggle DAP UI" },
	},
	config = function()
		local dap = require("dap")
		local dapui = require("dapui")

		dapui.setup()

		-- Open/close the UI automatically around a debug session.
		dap.listeners.before.attach.dapui_config = dapui.open
		dap.listeners.before.launch.dapui_config = dapui.open
		dap.listeners.before.event_terminated.dapui_config = dapui.close
		dap.listeners.before.event_exited.dapui_config = dapui.close

		-- Resolve lldb-dap from the active toolchain via xcrun.
		local lldb_dap = "lldb-dap"
		if vim.fn.executable("xcrun") == 1 then
			local found = vim.fn.system({ "xcrun", "--find", "lldb-dap" })
			if vim.v.shell_error == 0 then
				lldb_dap = vim.trim(found)
			end
		end

		dap.adapters.lldb = {
			type = "executable",
			command = lldb_dap,
			name = "lldb",
		}

		local function pick_program()
			return vim.fn.input("Executable: ", vim.fn.getcwd() .. "/.build/debug/", "file")
		end

		dap.configurations.swift = {
			{
				name = "Launch (.build/debug)",
				type = "lldb",
				request = "launch",
				program = pick_program,
				cwd = "${workspaceFolder}",
				stopOnEntry = false,
				args = {},
			},
			{
				name = "Launch with arguments",
				type = "lldb",
				request = "launch",
				program = pick_program,
				cwd = "${workspaceFolder}",
				stopOnEntry = false,
				args = function()
					return vim.split(vim.fn.input("Arguments: "), " ", { trimempty = true })
				end,
			},
			{
				name = "Attach to process",
				type = "lldb",
				request = "attach",
				pid = require("dap.utils").pick_process,
				cwd = "${workspaceFolder}",
			},
		}
	end,
}
