[← Cylc Training Notes](../README.md)

# Installation

> **Note:** This section documents the installation process for a local development setup
> for self-learning purposes. If you already have Cylc installed and running, you can skip
> straight to the [examples](../examples/).

Follow the [official Cylc installation documentation](https://cylc.github.io/cylc-doc/stable/html/installation.html)
as the primary guide. The notes below capture supplementary steps and observations that
may not be covered there.

## Conda Environment

If conda is not already installed, [Miniforge](https://github.com/conda-forge/miniforge)
is recommended — a minimal conda installer that comes preconfigured for conda-forge.

The simplest way to get a reproducible Cylc installation is via conda using the provided
environment file. This installs `cylc-flow` (the scheduler and CLI) and `cylc-uiserver`
(the browser-based GUI) from conda-forge into an isolated environment.

Create and activate the environment:

```bash
conda env create -f installation/environment.yml
conda activate cylc-training
```

Verify the installation:

```bash
cylc version
```

To update the environment later if `environment.yml` changes:

```bash
conda env update -f installation/environment.yml --prune
```

> **Note:** The `--prune` flag removes any packages no longer listed in the environment
> file, keeping the environment clean and consistent.

> **Note on job environments:** The `cylc-training` environment is for running the Cylc
> scheduler only. Environments for the workflows themselves (e.g. with GRIB or NetCDF
> support) are kept separate and documented within the relevant examples.

## Post-Install Configuration

<!-- Any configuration steps beyond the basic installation, e.g.:
- Global config file locations (~/.cylc/)
- Platform definitions
- Any environment variables worth setting
-->

## Proof of Installation

The `proof-of-install/` directory contains a minimal two-task workflow that verifies
Cylc is correctly installed and functioning. The tasks do nothing more than print a
message — the point is simply to confirm that the scheduler can run a workflow to completion.

Ensure the `cylc-training` conda environment is active:

```bash
conda activate cylc-training
```

Install and run the workflow:

```bash
cd installation/proof-of-install
cylc install . --no-run-name
cylc play proof-of-install
```

Monitor progress on the command line:

```bash
cylc tui proof-of-install
```

Or open the browser GUI:

```bash
cylc gui
```

Both tasks (`hello` and `world`) should complete with status **succeeded**, after which
the workflow stops automatically.

To remove the workflow run directory once done:

```bash
cylc clean proof-of-install
```

## Troubleshooting

**`WorkflowFilesError: Could not find workflow`** — `cylc install` searches `~/cylc-src`
by default, not the current directory. Always `cd` into the workflow directory and use
`cylc install .` rather than referring to the workflow by name from elsewhere.

## References

- [Cylc installation docs](https://cylc.github.io/cylc-doc/stable/html/installation.html)
- [Cylc conda environments reference](https://cylc.github.io/cylc-doc/stable/html/reference/environments/conda.html)
- [Cylc GitHub](https://github.com/cylc/cylc-flow)
