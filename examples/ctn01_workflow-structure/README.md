[← Cylc Training Notes](../../README.md)

# Example 01: Workflow Structure

This example introduces the structure of a Cylc workflow file (`flow.cylc`) using a
minimal three-task workflow that models the logarithmic wind profile over a surface.
The workflow follows a pattern common to real environmental modelling systems:

```
prepare_forcing => run_model => archive_output
```

## The `flow.cylc` File

Every Cylc workflow is defined by a [flow.cylc](flow.cylc) file. It is divided into sections,
each enclosed in square brackets. The three sections introduced here are `[meta]`,
`[scheduling]`, and `[runtime]`.

### [meta](flow.cylc#L1)

```cylc
[meta]
    title = Log Wind Profile
    description = """
        ...
    """
```

The `[meta]` section contains human-readable metadata about the workflow. It is
optional but good practice — the `title` and `description` are displayed in the
TUI and GUI, making it easier to identify workflows at a glance. Multi-line strings
are enclosed in triple quotes.

### [scheduling](flow.cylc#L13)

```cylc
[scheduling]
    [[graph]]
        R1 = prepare_forcing => run_model => archive_output
```

The `[scheduling]` section defines the workflow graph — which tasks exist and how
they depend on each other. The `[[graph]]` subsection contains the dependency graph.

`R1` is a recurrence expression meaning "run once". It is the simplest possible
scheduling expression and is used here to keep the focus on the workflow structure.
Date-time cycling — the basis of real operational modelling workflows — is introduced
in the next example.

The `=>` operator expresses a dependency: `prepare_forcing => run_model` means
`run_model` will not start until `prepare_forcing` has succeeded.

### [runtime](flow.cylc#L17)

```cylc
[runtime]
    [[prepare_forcing]]
        [[[environment]]]
            z0 = 0.01
        script = """
            ...
        """
    [[run_model]]
        script = """
            ...
        """
    [[archive_output]]
        script = """
            ...
        """
```

The `[runtime]` section defines what each task actually does. Each task is defined
as a subsection with a name matching one of the tasks in the graph. The `script`
setting contains the shell commands that will be executed when the task runs.

#### `[[[environment]]]`

The `[[[environment]]]` subsection defines environment variables that are passed to
the task's job script. Here `z0` — the aerodynamic roughness length — is defined at
the workflow level rather than hardcoded in the script:

```cylc
[[[environment]]]
    z0 = 0.01
```

This is good practice: keeping tuneable parameters visible at the workflow level
makes the workflow self-documenting and easy to modify between runs. The variable
is then available in the script as `${z0}`.

Two Cylc environment variables are also used in the task scripts:

- `$CYLC_WORKFLOW_SHARE_DIR` — a shared directory available to all tasks in the
  workflow, used here to pass files between tasks. This is the standard Cylc pattern
  for inter-task data exchange.
- `$CYLC_WORKFLOW_RUN_DIR` — the workflow run directory, used here to locate the
  `bin/log_wind_profile.py` script.

## The `bin/` Directory

The [bin/](bin) directory contains scripts and executables that are local to the workflow.
Cylc automatically makes `$CYLC_WORKFLOW_RUN_DIR/bin` available on the `PATH` for
all tasks, so scripts placed here can be called by name without specifying their
full path. Keeping model code in `bin/` is good practice — it separates the workflow
logic (`flow.cylc`) from the scientific code.

## Running the Example

```bash
cd examples/ctn01_workflow-structure
cylc vip .
```

Verify the output by inspecting the wind profile CSV in the share directory:

```bash
cat ~/cylc-run/ctn01_workflow-structure/run1/share/output/wind_profile.csv
```

Expected output for the default `z0 = 0.01` m (short grass):

```
height_m,wind_speed_ms
2.0,5.2983
5.0,6.2146
10.0,6.9078
20.0,7.6009
50.0,8.5172
100.0,9.2103
```

Or observe the workflow interactively using any of the methods introduced in the
[installation section](../../installation/README.md#monitoring-with-tui-and-gui).

## Parameter Study: Roughness Length

The roughness length `z0` characterises the aerodynamic properties of a surface.
Typical values for different surface types are:

| Surface type  | z0 (m)  |
|---------------|---------|
| Open sea      | 0.0002  |
| Short grass   | 0.01    |
| Farmland      | 0.1     |

Each time `cylc vip .` is run, Cylc installs the workflow into a new numbered run
directory — `run1`, `run2`, `run3` — leaving the previous results intact. This makes
it straightforward to compare results across runs.

To run the parameter study, edit `z0` in `flow.cylc` and run `cylc vip .` for each
surface type:

```bash
# run1 — short grass (default, already run)

# Edit flow.cylc: z0 = 0.0002
cylc vip .   # creates run2

# Edit flow.cylc: z0 = 0.1
cylc vip .   # creates run3
```

Compare the results across runs:

```bash
echo "=== run1: short grass (z0=0.01) ===" && \
    cat ~/cylc-run/ctn01_workflow-structure/run1/share/output/wind_profile.csv
echo "=== run2: open sea (z0=0.0002) ===" && \
    cat ~/cylc-run/ctn01_workflow-structure/run2/share/output/wind_profile.csv
echo "=== run3: farmland (z0=0.1) ===" && \
    cat ~/cylc-run/ctn01_workflow-structure/run3/share/output/wind_profile.csv
```

The run directories are managed by Cylc under `~/cylc-run/ctn01_workflow-structure/`
and can be listed at any time:

```bash
ls ~/cylc-run/ctn01_workflow-structure/
```

## Cleaning Up

To remove all runs:

```bash
cylc clean ctn01_workflow-structure
```

To remove a specific run only:

```bash
cylc clean ctn01_workflow-structure/run2
```
