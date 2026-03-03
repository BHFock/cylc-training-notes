[← Cylc Training Notes](../../README.md)

# Example 04: Parametrised Tasks and Ensemble Forecasting

This example extends the cycling system from [ctn03](../ctn03_cycle-dependencies/README.md)
to run an ensemble forecast. Rather than a single deterministic 100 m wind forecast,
each cycle now produces five parallel member forecasts, each with an independent random
perturbation of the 10 m wind analysis. The ensemble mean and spread quantify forecast
uncertainty and the mean is passed as the restart field to the next cycle.

The workflow is defined in [flow.cylc](flow.cylc). See
[bin/generate_ensemble_forcing.py](bin/generate_ensemble_forcing.py) for the member
perturbation logic and [bin/ensemble_mean.py](bin/ensemble_mean.py) for the mean and
spread calculation.

## The Science

Each ensemble member receives an independent perturbation of the deterministic 10 m
wind analysis `u_det(10)`:

    u_member(10) = u_det(10) * (1 + ε),   ε ~ U(-0.15, +0.15)

Each member is then extrapolated to 100 m independently:

    u_member(100) = u_member(10) * ln(100/z0) / ln(10/z0)

The ensemble mean and standard deviation across all members give a probabilistic
estimate of the 100 m wind:

    mean(u100)   = (1/N) * Σ u_member(100)
    spread(u100) = std(u_member(100))

The ensemble mean is written as the restart field, closing the inter-cycle dependency
loop established in `ctn03`.

## Parametrised Tasks

### `[task parameters]`

```cylc
[task parameters]
    member = 1..5
```

This declares a parameter `member` with values 1 to 5. Cylc expands any task
that uses `<member>` notation into five separate task instances — one per member.
Changing `1..5` to `1..10` scales the ensemble to ten members with no other
changes required.

### The Graph

```cylc
[[graph]]
    R1   = install_cold
    PT6H = install_cold[^] => generate_forcing \
                           => generate_ensemble_forcing<member> \
                           => extrapolate_wind<member> \
                           => ensemble_mean
    PT6H = ensemble_mean[-PT6H] => generate_forcing
```

Reading the cycling graph as a pipeline makes the ensemble structure immediately
visible:

- `generate_forcing` runs once per cycle — the deterministic analysis
- `<member>` appears at `generate_ensemble_forcing` — **fan-out**: Cylc spawns 5
  parallel task instances here
- `<member>` disappears at `ensemble_mean` — **fan-in**: Cylc waits for all 5
  members to complete before triggering `ensemble_mean`

The fan-in is inferred automatically — because `ensemble_mean` has no `<member>`
parameter, Cylc knows it depends on all instances of the upstream parametrised tasks.
No explicit listing of members is required in the graph.

### Parameter Templates in `[[[environment]]]`

Each parametrised task receives its member number via a parameter template:

```cylc
[[generate_ensemble_forcing<member>]]
    [[[environment]]]
        MEMBER_ID = %(member)s
```

`%(member)s` is substituted with the parameter value at runtime — `1`, `2`, `3`,
and so on. This environment variable is then used to construct member-stamped
filenames in the task script:

```bash
u10_${CYLC_TASK_CYCLE_POINT}_m${MEMBER_ID}.txt   # e.g. u10_20000101T0000Z_m3.txt
```

This pattern — parameter template to environment variable to filename — is the
standard way to handle IO in parametrised Cylc tasks.

### The Cold Start

As in `ctn03`, the inter-cycle dependency `ensemble_mean[-PT6H]` points before
the initial cycle point at `20000101T00Z`. Cylc silently ignores this, allowing
`generate_forcing` to run immediately as a cold start. No special graph logic is
needed for the first cycle.

## Running the Example

```bash
cd examples/ctn04_parametrised-ensembles
cylc vip .
```

Observe the fan-out and fan-in in the TUI — after `generate_forcing` completes,
five `generate_ensemble_forcing` tasks appear in parallel, followed by five
`extrapolate_wind` tasks, before converging on a single `ensemble_mean`.

Inspect the ensemble output for one cycle:

```bash
cat ~/cylc-run/ctn04_parametrised-ensembles/run1/share/ensemble/mean_20000101T0000Z.txt
```

## Student Exercises

### Exercise 1 — Scale the Ensemble

Change the ensemble size from 5 to 10 members by editing `[task parameters]`:

```cylc
[task parameters]
    member = 1..10
```

Run the workflow and observe how the TUI graph scales automatically. Check that
the ensemble output now shows 10 member values and a different spread.

### Exercise 2 — Make the Perturbation Configurable

Currently `PERTURB_MAX = 0.15` is hardcoded in `generate_ensemble_forcing.py`.
Make it configurable from `flow.cylc` by following these steps:

**Step 1** — Add `PERTURB_MAX` to the task environment in `flow.cylc`:

```cylc
[[generate_ensemble_forcing<member>]]
    [[[environment]]]
        MEMBER_ID   = %(member)s
        PERTURB_MAX = 0.15
```

**Step 2** — Read `PERTURB_MAX` from the environment in `generate_ensemble_forcing.py`.
Replace the hardcoded constant at the top of the script:

```python
# Before:
PERTURB_MAX = 0.15

# After:
import os
PERTURB_MAX = float(os.environ.get('PERTURB_MAX', 0.15))
```

`os.environ.get('PERTURB_MAX', 0.15)` reads the environment variable if present,
falling back to `0.15` if it is not set — a safe pattern for configurable parameters.

**Step 3** — Run the workflow twice with different values of `PERTURB_MAX`:

```cylc
PERTURB_MAX = 0.05   # tight perturbations
PERTURB_MAX = 0.30   # wide perturbations
```

Compare the `u100_spread` values in the ensemble output between the two runs.

## Cleaning Up

```bash
cylc clean ctn04_parametrised-ensembles
```
