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

The `proof-of-install/` directory contains a minimal two-task [workflow](proof-of-install/flow.cylc)
that verifies Cylc is correctly installed and functioning. The tasks do nothing more than
print a message and sleep briefly — the sleep gives enough time to observe the workflow
in a running state.

Ensure the `cylc-training` conda environment is active:

```bash
conda activate cylc-training
```

### Quick Run with `cylc vip`

The quickest way to verify the installation is with `cylc vip` (validate, install, play),
which combines all three steps into a single command:

```bash
cd installation/proof-of-install
cylc vip .
```

Once the workflow has completed, verify the results by inspecting the job log files directly:

```bash
nl $HOME/cylc-run/proof-of-install/run1/log/job/1/hello/01/job.out
nl $HOME/cylc-run/proof-of-install/run1/log/job/1/world/01/job.out
```

Expected output for each task:

```
1  Workflow : proof-of-install/run1
2  Job      : 1/hello/01 (try 1)
3  User@Host: <user>@<host>

4  Hello from Cylc!
5  2026-03-01T16:39:55+01:00 INFO - started
6  2026-03-01T16:40:05+01:00 INFO - succeeded
```

```
1  Workflow : proof-of-install/run1
2  Job      : 1/world/01 (try 1)
3  User@Host: <user>@<host>

4  Cylc proof of installation successful!
5  2026-03-01T16:40:07+01:00 INFO - started
6  2026-03-01T16:40:17+01:00 INFO - succeeded
```

Both tasks reporting `succeeded` confirms the installation is working correctly.

To remove the workflow run directory once done:

```bash
cylc clean proof-of-install
```

### Observed Run with `cylc validate`, `cylc install`, `cylc play`

Under the hood, `cylc vip` is shorthand for three separate steps. Running them explicitly
allows the workflow state to be observed at each stage from the command line — a useful
habit that maps directly to how Cylc is used in operational settings.

First clean the previous run:

```bash
cylc clean proof-of-install
```

Validate the workflow definition (still in `installation/proof-of-install/`):

```bash
cylc validate .
```

Install the workflow into `~/cylc-run/`:

```bash
cylc install .
```

Start the scheduler:

```bash
cylc play proof-of-install
```

While the tasks are running, observe the workflow state from the command line:

```bash
cylc scan                                # list all running workflows
cylc workflow-state proof-of-install     # state of all tasks in the workflow
```

`cylc show` can display individual task details but only works for active tasks.

The sleep statements in each task provide a window to see them in a `running` state
before they complete.

### Observed Run with the TUI

As an alternative to the CLI commands above, open the TUI before playing the workflow
and observe the task states interactively:

```bash
cylc install .
cylc tui proof-of-install
```

From the TUI, select the workflow and trigger it to play. The tasks can be seen moving
through `waiting`, `running`, and `succeeded` states.

### Observed Run with the GUI

The browser-based GUI provides a richer graphical view but depends on `cylc-uiserver`
running correctly:

```bash
cylc install .
cylc play proof-of-install
cylc gui
```

## Troubleshooting

**`WorkflowFilesError: Could not find workflow`** — `cylc install` searches `~/cylc-src`
by default, not the current directory. Always `cd` into the workflow directory and use
`cylc install .` rather than referring to the workflow by name from elsewhere.

## References

- [Cylc installation docs](https://cylc.github.io/cylc-doc/stable/html/installation.html)
- [Cylc conda environments reference](https://cylc.github.io/cylc-doc/stable/html/reference/environments/conda.html)
- [Cylc GitHub](https://github.com/cylc/cylc-flow)
