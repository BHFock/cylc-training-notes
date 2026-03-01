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

Once installed, run the [proof-of-install workflow](./proof-of-install/) to confirm everything
is working correctly:

```bash
# commands to run the proof-of-install workflow go here
```

Expected output:

```
# paste expected terminal output here
```

## Troubleshooting

<!-- Issues encountered and how they were resolved. -->

## References

- [Cylc installation docs](https://cylc.github.io/cylc-doc/stable/html/installation.html)
- [Cylc conda environments reference](https://cylc.github.io/cylc-doc/stable/html/reference/environments/conda.html)
- [Cylc GitHub](https://github.com/cylc/cylc-flow)
