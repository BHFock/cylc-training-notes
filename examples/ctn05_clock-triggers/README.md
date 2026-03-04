[← Cylc Training Notes](../../README.md)

# Example 05: Clock Triggers and Real-Time Cycling

This example introduces clock triggers — the mechanism that turns a datetime
cycling workflow into a genuine real-time processing system. Rather than running
as fast as possible through a fixed set of historical cycle points, a
clock-triggered workflow waits for the wall-clock time to reach each cycle point
before allowing that cycle to proceed.

The physical scenario is a real-time wind monitoring and energy yield estimation
system for an offshore wind farm. A met mast measures the 10 m wind speed every
minute. For each new observation the workflow extrapolates the wind to turbine hub
height and estimates the instantaneous power output of a Vestas V90-3.0 MW turbine.

The workflow is defined in [flow.cylc](flow.cylc). See
[bin/estimate_yield.py](bin/estimate_yield.py) for the power curve model and
[ancil/v90.txt](ancil/v90.txt) for the turbine parameters.

## The Science

Wind speed increases with height following the logarithmic wind profile:

    u(h) = u(10) * ln(h / z0) / ln(10 / z0)

where `h` is the hub height and `z0 = 0.0002 m` is the aerodynamic roughness
length for open water. For the V90-3.0 at 80 m hub height this gives a factor
of approximately 1.35 — so a 10 m/s observation becomes roughly 13.5 m/s at
hub height.

The instantaneous power output is estimated from the standard cubic power curve
(IEC 61400-12):

    P = 0                               u < u_cutin  (3.5 m/s)
    P = P_rated * (u / u_rated) ** 3   u_cutin <= u < u_rated  (12.0 m/s)
    P = P_rated                         u_rated <= u < u_cutout  (25.0 m/s)
    P = 0                               u >= u_cutout

where `P_rated = 3.0 MW` for the V90-3.0. The cubic scaling follows directly
from the wind power equation — power in the wind is proportional to `u³` — and
above rated speed the blade pitch control system limits output to `P_rated`.

> **Note on temporal resolution:** In operational practice, wind turbine energy
> yield is calculated from 10-minute mean wind speeds following IEC 61400-12. The
> 1-minute cycling used here is chosen to make the clock trigger behaviour
> immediately observable during the exercise, not to reflect standard measurement
> practice.

## Clock Triggers

### The Problem Without Clock Triggers

In the examples up to `ctn04`, Cylc runs cycles as fast as the tasks allow.
A workflow with `initial cycle point = 20000101T00Z` and `PT6H` cycling will
run all four 6-hourly cycles in seconds, regardless of what the wall-clock time
says. This is ideal for historical reprocessing, but wrong for a real-time
system — a monitoring workflow should process the 14:00 observation at 14:00,
not several minutes early.

### `[[xtriggers]]` and `wall_clock()`

Clock triggers are declared in the `[[xtriggers]]` section:

```cylc
[[xtriggers]]
    clock = wall_clock()
```

This declares a trigger named `clock` that succeeds when the wall-clock time
reaches the cycle point. The trigger is then referenced in the graph with the
`@` prefix:

```cylc
PT1M = @clock & install_cold[^] => generate_forcing => ...
```

Until the wall clock reaches the cycle point time, `generate_forcing` will
remain in a waiting state even if all its task dependencies are satisfied.

### `initial cycle point = now`

Setting `initial cycle point = now` starts the workflow at the current
wall-clock time, rounded down to the nearest whole minute. This means the
first cycle triggers almost immediately rather than waiting for a fixed
historical date.

```cylc
initial cycle point = now
final cycle point   = +PT10M
```

The `+PT10M` final cycle point is a relative duration — ten minutes after the
initial cycle point. The workflow will run for ten 1-minute cycles and then
stop cleanly.

### Combining Triggers with `&`

The `&` operator in the graph expresses a logical AND — a task waits until
**all** listed prerequisites are satisfied:

```cylc
PT1M = @clock & install_cold[^] => generate_forcing
```

Here `generate_forcing` will not start until both conditions are met:

- `@clock` — the wall-clock time has reached this cycle point
- `install_cold[^]` — the cold start task from the first cycle has completed

Either condition alone is not sufficient. The `&` operator works with any
combination of task dependencies and xtriggers.

### Connection to the NWP Examples

The `@wall_clock` trigger introduced here applies equally to the NWP-like
cycling system built in `ctn03` and `ctn04`. In a real operational forecast
system, the 6-hourly cycle would be gated by a clock trigger to ensure each
cycle waits for its observation cut-off time before the analysis starts — the
workflow graph is otherwise identical, only the cycling interval changes from
`PT1M` to `PT6H`.

## Running the Example

```bash
cd examples/ctn05_clock-triggers
cylc vip .
```

Watch the TUI closely. Unlike the earlier examples, cycles do not all rush
forward immediately. After `install_cold` completes, you will see
`generate_forcing` waiting — indicated by the clock trigger not yet being
satisfied. At each new minute the cycle point is reached, the clock trigger
fires, and the pipeline runs.

Inspect the output after a few cycles:

```bash
cat ~/cylc-run/ctn05_clock-triggers/run1/share/yield/power_<cycle_point>.txt
```

## Student Exercise

The workflow currently runs for 10 minutes. Extend it to 30 minutes by changing
the final cycle point in `flow.cylc`:

```cylc
final cycle point = +PT30M
```

Run the workflow and collect 30 output files. Then use the shell to print a
summary of the power output across all cycles:

```bash
grep "power_MW" ~/cylc-run/ctn05_clock-triggers/run1/share/yield/power_*.txt
```

Observe how the estimated power varies with the simulated wind speed across
cycles, and how the capacity factor reflects the fraction of rated power
being produced at each observation time.

## Further Reading

- [Clock Triggered Tasks](https://cylc.github.io/cylc-doc/stable/html/tutorial/furthertopics/clock-triggered-tasks.html) — hands-on tutorial introducing `wall_clock()`, `initial cycle point = now`, and clock offsets
- [External Triggers](https://cylc.github.io/cylc-doc/stable/html/user-guide/writing-workflows/external-triggers.html) — full reference for `[[xtriggers]]`, including combining xtriggers with `&` in the graph
- [Scheduling Configuration](https://cylc.github.io/cylc-doc/stable/html/user-guide/writing-workflows/scheduling.html) — graph syntax reference covering the `&` and `|` operators in detail

## Cleaning Up

```bash
cylc clean ctn05_clock-triggers
```
