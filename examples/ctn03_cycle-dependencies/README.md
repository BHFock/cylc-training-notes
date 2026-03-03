[← Cylc Training Notes](../../README.md)

# Example 03: Cycle Dependencies and Workflow Directory Structure

This example extends the datetime cycling introduced in [ctn02](../ctn02_datetime-cycling/README.md)
by adding inter-cycle dependencies. It models a simplified 6-hourly analysis cycle for
offshore wind, where each cycle:

1. Generates a 10 m wind analysis `u(10)` using the previous cycle's 100 m wind
   `u_prev(100)` as a first-guess, scaled back to 10 m by the inverse log law and perturbed
   by a small random analysis increment `ε`:

        u_fg(10) = u_prev(100) * ln(10/z0) / ln(100/z0)
        u(10)    = u_fg(10) * (1 + ε),   ε ~ U(-0.10, +0.10)

2. Extrapolates the new analysis to 100 m for the next cycle:

        u(100) = u(10) * ln(100/z0) / ln(10/z0)

The dependence of each cycle on the previous cycle's `u_prev(100)` is what makes the cycling
sequential — each cycle cannot start until the previous one has completed. This is the
fundamental structure of any cycling NWP or ocean forecast system.

The first cycle has no previous cycle and performs a cold start, drawing `u(10)`
randomly from the full offshore wind speed range.

The workflow is defined in [flow.cylc](flow.cylc). See
[bin/extrapolate_wind.py](bin/extrapolate_wind.py) for the log law extrapolation and
[bin/generate_forcing.py](bin/generate_forcing.py) for the stochastic forcing with
warm start perturbation.

## Inter-cycle Dependencies

### The Graph

```cylc
[scheduling]
    initial cycle point = 20000101T00Z
    final cycle point   = 20000101T18Z
    [[graph]]
        R1   = install_cold
        PT6H = install_cold[^] => generate_forcing => extrapolate_wind
        PT6H = extrapolate_wind[-PT6H] => generate_forcing
```

The key new line is:

```cylc
PT6H = extrapolate_wind[-PT6H] => generate_forcing
```

`extrapolate_wind[-PT6H]` means "the `extrapolate_wind` task from the cycle
point 6 hours earlier". This makes `generate_forcing` at each cycle wait for
the previous cycle's `extrapolate_wind` to complete before running — exactly
the dependency structure of a cycling forecast system where each cycle depends
on the previous cycle's output.

### Why `PT6H` Instead of `T00,T06,T12,T18`

Inter-cycle dependencies require the interval notation `PT6H` rather than the
explicit hour list `T00,T06,T12,T18`. The `[-PT6H]` offset is defined relative
to the cycling interval — it means "one cycle back". This only makes sense when
the cycling interval is defined as a duration (`PT6H`), not as a list of fixed
times.

Both expressions produce cycles at 00, 06, 12, and 18 UTC when anchored to the
initial cycle point at `T00Z` — but `PT6H` is required as soon as inter-cycle
references are introduced.

### The Cold Start

At the initial cycle point (`20000101T00Z`) there is no previous cycle, so
`extrapolate_wind[-PT6H]` has no upstream task to wait for. Cylc handles this
automatically — inter-cycle dependencies that would point before the initial
cycle point are silently ignored, allowing the first cycle to run as a cold
start without any special graph logic.

The cold start behaviour is implemented in `generate_forcing.py`: if no restart
file is found, a random 10 [m] wind speed is drawn from the full offshore range.
From the second cycle onwards, the previous cycle's 100 [m] wind is scaled back
to 10 [m] and perturbed by ±10% — a simplified analysis increment.

## Workflow Directory Structure

Running this workflow is a good opportunity to explore the directory structure
that Cylc creates under `~/cylc-run/`. Every workflow run has the same layout:

```
~/cylc-run/ctn03_cycle-dependencies/run1/
├── log/
│   ├── scheduler/          # scheduler logs
│   └── job/
│       └── <cyclepoint>/
│           └── <task>/
│               └── 01/
│                   ├── job        # the job script Cylc generated
│                   ├── job.out    # task stdout
│                   └── job.err    # task stderr
├── share/                  # persistent shared data between tasks
│   ├── ancil/              # static ancillary files (installed by install_cold)
│   ├── forcing/            # cycle-stamped forcing files
│   ├── output/             # cycle-stamped model output
│   └── restart/            # restart fields passed between cycles
└── work/
    └── <cyclepoint>/
        └── <task>/         # task working directory (temporary)
```

The key Cylc environment variables that map to this structure are:

| Variable | Path | Purpose |
|---|---|---|
| `$CYLC_WORKFLOW_RUN_DIR` | `~/cylc-run/<workflow>/run1` | root of the workflow run |
| `$CYLC_WORKFLOW_SHARE_DIR` | `.../share` | persistent inter-task data exchange |
| `$CYLC_TASK_WORK_DIR` | `.../work/<cycle>/<task>` | temporary task working directory |
| `$CYLC_TASK_LOG_DIR` | `.../log/job/<cycle>/<task>/01` | task stdout and stderr logs |
| `$CYLC_TASK_CYCLE_POINT` | e.g. `20000101T0600Z` | current cycle point |

### `share/` vs `work/`

The `share/` directory is persistent — files written here by one task are
available to all other tasks in the workflow, including tasks in later cycles.
This is the correct location for forcing files, model output, and restart fields.

The `work/` directory is the task's working directory — the current directory
when the task script executes. It is intended for temporary files and is
automatically cleaned up by Cylc when empty after a task completes. Files that
need to be passed between tasks must be written to `share/`, not `work/`.

### Exploring the Restart Chain

After running the workflow, the restart files illustrate the sequential nature
of the cycling clearly:

```bash
for f in ~/cylc-run/ctn03_cycle-dependencies/run1/share/restart/wind_*.txt; do
    echo "=== $f ===" && cat $f
done
```

The `u100` value should evolve smoothly between cycles, with small perturbations
reflecting the ±10% analysis increment applied at each warm start.

## Running the Example

```bash
cd examples/ctn03_cycle-dependencies
cylc vip .
```

Observe the sequential cycling in the TUI — unlike `ctn02`, tasks no longer run
in parallel. Each cycle waits for the previous cycle's `extrapolate_wind` before
`generate_forcing` can start.

## Student Exercise

Add a second day of cycling by extending the final cycle point:

```cylc
final cycle point = 20000102T18Z
```

Observe how the restart chain extends across the day boundary, with `20000102T00Z`
depending on `20000101T18Z`.

## Cleaning Up

```bash
cylc clean ctn03_cycle-dependencies
```
