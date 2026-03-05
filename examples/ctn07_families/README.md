[← Cylc Training Notes](../../README.md)

# Example 07: Families and Include Files

This example extends the multi-park wind monitoring system from
[ctn06](../ctn06_jinja2-templating/README.md) to cover four wind parks served
by two turbine manufacturers — Vestas and Siemens Gamesa. As a real deployment
of this system would grow to cover many parks with multiple task types sharing
common configuration, two Cylc tools become essential: **families** for
eliminating runtime repetition, and **include files** for keeping `flow.cylc`
focused on workflow structure.

The workflow is defined in [flow.cylc](flow.cylc) and
[wind_parks.cylc](wind_parks.cylc). The Vestas yield model is in
[bin/estimate_yield.py](bin/estimate_yield.py); the Siemens yield model is a
Perl implementation in [bin/estimate_yield.pl](bin/estimate_yield.pl).

## The Scenario

Each of the four wind parks has its own met mast observation. All parks run a
neutral log law wind extrapolation and a yield estimate. Siemens parks
additionally run a stability-corrected extrapolation and a second yield
estimate from that corrected wind. The two manufacturers use different yield
model implementations:

- **Vestas** (alpha, beta) — Python yield model, neutral wind profile only
- **Siemens** (delta, epsilon) — Perl yield model, neutral and
  stability-corrected wind profiles

## Include Files

The `wind_parks.cylc` include file contains the Jinja2 `wind_parks` list —
the configuration data that defines which parks are processed. It is included
at the top of `flow.cylc` with:

```cylc
%include wind_parks.cylc
```

The motivation is separation of concerns: `wind_parks.cylc` is configuration
data that grows as new parks are added. `flow.cylc` is workflow structure that
changes when the processing logic changes. Keeping them in separate files means
they can evolve independently and be reviewed separately.

## Families

A family in Cylc is a named group of tasks that share runtime configuration.
Tasks join a family with the `inherit` setting:

```cylc
[[METEOROLOGY]]
    [[[environment]]]
        z0  = 0.0002
        psi = 0.0

[[extrapolate_wind_neutral_alpha]]
    inherit = METEOROLOGY
```

`extrapolate_wind_neutral_alpha` inherits `z0` and `psi` from `[[METEOROLOGY]]`
without repeating them. Without the family, `z0` and `psi` would need to appear
in every `extrapolate_wind` task block in the Jinja2 loop — repeated in the
template rather than defined once.

By convention family names are written in uppercase to distinguish them from
tasks at a glance.

### The Family Hierarchy

This example uses three families with a two-level hierarchy:

```
[[METEOROLOGY]]   — z0 and psi shared across all extrapolation tasks
[[YIELD]]         — parent family for all yield estimation tasks
    [[VESTAS]]    — inherits from YIELD, used by Python yield tasks
    [[SIEMENS]]   — inherits from YIELD, used by Perl yield tasks
```

`[[VESTAS]]` and `[[SIEMENS]]` both inherit from `[[YIELD]]`, which provides
any settings common to all yield tasks regardless of manufacturer. Each
sub-family then adds its own manufacturer-specific settings on top.

### Overriding Family Settings

A task can override a family setting at the task level. The stability
correction tasks override the `psi = 0.0` default from `[[METEOROLOGY]]`:

```cylc
[[extrapolate_wind_stability_delta]]
    inherit = METEOROLOGY
    [[[environment]]]
        psi = -0.1
```

The task-level setting takes precedence over the family setting. `z0` is still
inherited unchanged — only `psi` is overridden. This is a key pattern in
operational workflows: families provide sensible defaults, individual tasks
deviate only where necessary.

### Inspecting Inheritance

To see the fully resolved configuration of a task after inheritance processing:

```bash
cylc config ctn07_families --item '[runtime][extrapolate_wind_stability_delta]'
```

This shows exactly what settings the task will run with, which is useful for
debugging inheritance chains.

### Families and Platforms

In this example families carry environment variables. In a real operational
system families would also carry platform configuration and job directives —
platform, memory limits, CPU requests — so that all tasks of a given type
submit to the correct queue with the correct resources. That pattern is
covered in the HPC platform configuration example.

## Running the Example

```bash
cd examples/ctn07_families
cylc vip .
```

Observe in the TUI that Vestas parks (alpha, beta) run three tasks per cycle
while Siemens parks (delta, epsilon) run five — the additional stability
extrapolation and yield tasks are visible as a wider pipeline.

Inspect the inheritance hierarchy:

```bash
cylc list --tree ctn07_families
```

Compare neutral and stability-corrected yield estimates for a Siemens park:

```bash
ls ~/cylc-run/ctn07_families/run1/share/yield/delta/
```

## Student Exercise

Add a fifth wind park `zeta` with a Siemens SG 6.0-170 turbine. Edit
`wind_parks.cylc`:

```jinja2
{'name': 'zeta', 'turbine': 'SG6', 'manufacturer': 'siemens'},
```

Run the workflow and confirm that `zeta` automatically receives the full
Siemens pipeline — neutral extrapolation, stability extrapolation, and two
yield estimates — without any changes to `flow.cylc`.

## Further Reading

- [Families Tutorial](https://cylc.github.io/cylc-doc/stable/html/tutorial/runtime/configuration-consolidation/families.html) — hands-on introduction to families, inheritance, and overriding family settings
- [Inheritance Tutorial](https://cylc.github.io/cylc-doc/stable/html/tutorial/furthertopics/inheritance.html) — deeper look at nested families and multiple inheritance
- [Efficiency and Maintainability](https://cylc.github.io/cylc-doc/stable/html/workflow-design-guide/efficiency.html) — design guide covering when and how to use families effectively

## Cleaning Up

```bash
cylc clean ctn07_families
```
