return {
  -- Treesitter
  {
    "nvim-treesitter/nvim-treesitter",
    opts = {
      ensure_installed = { "python" },
    },
  },

  -- LSP (Pyright)
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        basedpyright = {
          settings = {
            python = {
              analysis = {
                typeCheckingMode = "off",
              },
            },
          },
        },
      },
    },
  },

  -- Formatting (Ruff)
  {
    "stevearc/conform.nvim",
    opts = {
      formatters_by_ft = {
        python = { "black" },
      },
    },
  },

  -- Linting (Ruff)
  {
    "mfussenegger/nvim-lint",
    opts = {
      linters_by_ft = {
        python = { "ruff" },
      },
    },
  },
}
