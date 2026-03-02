[← Cylc Training Notes](../../README.md)

# Example 02: Datetime Cycling

This example introduces datetime cycling — the core scheduling mechanism for operational
environmental modelling. The workflow extrapolates 10m wind speed to 100 m using
the logarithmic wind profile, cycling at the standard synoptic hours 00, 06, 12, and 18 UTC:

```
install_cold => generate_forcing => extrapolate_wind
```

`install_cold` runs once at the start of the workflow. `generate_forcing` and
`extrapolate_wind` repeat at each synoptic cycle.

## The Science

The wind speed extrapolation follows the logarithmic wind profile:

    u(100) = u(10) * ln(100 / z0) / ln(10 / z0)

where `u(10)` is the 10 [m] wind speed [m/s], `u(100)` is the extrapolated 100 [m]
wind speed [m/s], and `z0` is the aerodynamic roughness length [m]. See
[bin/extrapolate_wind.py](bin/extrapolate_wind.py) for the implementation and
[bin/generate_forcing.py](bin/generate_forcing.py) for the stochastic forcing generator.

## The `flow.cylc` File

### [scheduling](flow.cylc#L13)

```cylc
[scheduling]
    initial cycle point = 20000101T00Z
    final cycle point   = 20000101T18Z
    [[graph]]
        R1              = install_cold
        T00,T06,T12,T18 = install_cold[^] => generate_forcing => extrapolate_wind
```

#### `initial cycle point` and `final cycle point`

These settings define the boundaries of the cycling. Cycle points follow the
ISO 8601 datetime format. The `Z` suffix denotes UTC, which is standard practice
in operational meteorology and oceanography.

#### `T00,T06,T12,T18`

This recurrence expression anchors the cycling to the standard synoptic hours.
Unlike `PT6H` — which means "every 6 hours from the initial cycle point" —
`T00,T06,T12,T18` explicitly ties the cycles to fixed UTC times. This is the
correct convention for operational NWP and ocean modelling systems.

#### `R1` and `install_cold[^]`

`R1` schedules `install_cold` to run exactly once, at the initial cycle point.

`install_cold[^]` in the cycling graph means "the instance of `install_cold` at
the initial cycle point `[^]`". This expresses that every synoptic cycle depends
on the cold start having completed, without re-running it at each cycle.

### [runtime](flow.cylc#L20)

#### `$CYLC_TASK_CYCLE_POINT`

Cylc provides each task with its cycle point as an environment variable:

```bash
${CYLC_TASK_CYCLE_POINT}   # e.g. 20000101T0000Z
```

This is used to stamp both the forcing and output filenames, so each cycle produces
distinctly named files:

```
forcing/u10_20000101T0000Z.txt
forcing/u10_20000101T0600Z.txt
...
output/wind_20000101T0000Z.txt
output/wind_20000101T0600Z.txt
...
```

This cycle-stamped file naming is standard practice in operational systems and makes
it straightforward to identify which output belongs to which cycle.

## The `ancil/` Directory

The [ancil/](ancil) directory contains static ancillary files that are installed once
by `install_cold` into the workflow share directory. Here it holds the roughness length
for an offshore wind application. Separating ancillary data from the [bin/](bin) scripts
and `flow.cylc` is good practice — it mirrors the structure of real operational systems
where surface parameters are maintained as versioned datasets.

## Parallel Cycling

In this workflow all four synoptic cycles run in parallel — each cycle only depends on
`install_cold` completing, not on the previous cycle. This is intentional here and
reflects workflows where each cycle is fully independent, such as ensemble members or
hindcast studies. It also allows Cylc to utilise multiple processors simultaneously,
making efficient use of available hardware.

In operational forecasting systems, cycles typically depend on the previous cycle
— for example to provide a model restart or a first-guess field. Inter-cycle
dependencies are introduced in a later example.

## Running the Example

```bash
cd examples/ctn02_datetime-cycling
cylc vip .
```

Verify the output for each cycle:

```bash
for f in ~/cylc-run/ctn02_datetime-cycling/run1/share/output/wind_*.txt; do
    echo "=== $f ===" && cat $f
done
```

## Student Exercise

Extend the cycling to cover a full week by changing `final cycle point`:

```cylc
final cycle point = 20000107T18Z
```

Then try changing the cycling from synoptic hours to every 3 hours. The explicit
form lists each hour:

```cylc
T00,T03,T06,T09,T12,T15,T18,T21
```

This can also be written more concisely using the interval shorthand:

```cylc
T00/PT3H
```

Both are equivalent — `T00/PT3H` means "starting at T00, repeat every 3 hours".
This shorthand becomes particularly useful when the cycling frequency increases.

## Cleaning Up

```bash
cylc clean ctn02_datetime-cycling
```
