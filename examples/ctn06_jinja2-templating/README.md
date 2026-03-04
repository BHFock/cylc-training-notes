[← Cylc Training Notes](../../README.md)

# Example 06: Jinja2 Templating

This example extends the real-time wind monitoring system from
[ctn05](../ctn05_clock-triggers/README.md) to process observations from three
wind parks simultaneously. Rather than duplicating the pipeline three times in
`flow.cylc`, the workflow is generated from a Jinja2 template — a list of wind
parks at the top of the file expands automatically into three parallel processing
pipelines at parse time.

The workflow is defined in [flow.cylc](flow.cylc). The scripts are unchanged from
`ctn05`, with the exception of
[bin/extrapolate_wind.py](bin/extrapolate_wind.py), which now reads the roughness
length from an environment variable set by Jinja2 rather than from the ancil file.

## Jinja2 in Cylc

Jinja2 is a templating language that is processed before Cylc parses `flow.cylc`.
The result after Jinja2 processing must be valid Cylc syntax — Jinja2 is not
executed at runtime, only at parse time when the workflow is installed.

To enable Jinja2, the first line of `flow.cylc` must be:

```
#!jinja2
```

Cylc then processes all Jinja2 code before reading the workflow configuration.
The rendered output can be inspected with:

```bash
cylc view --process ctn06_jinja2-templating
```

This is useful for debugging — it shows exactly what Cylc sees after the
template has been expanded.

## The Wind Park Configuration

All configurable parameters are declared at the top of `flow.cylc` in a single
Jinja2 data structure:

```jinja2
{% set wind_parks = [
    {'name': 'alpha', 'turbine': 'V90',  'site': 'offshore'},
    {'name': 'beta',  'turbine': 'V150', 'site': 'offshore'},
    {'name': 'gamma', 'turbine': 'V236', 'site': 'onshore'},
] %}
```

Adding a new wind park requires only a new entry in this list. The graph and
all runtime task definitions are generated automatically.

## Jinja2 Syntax

### `{% set %}` — Variables

`{% set %}` declares a Jinja2 variable. Here it defines the list of wind parks
as a list of dictionaries, one entry per park.

### `{{ }}` — Substitution

Double curly braces substitute a Jinja2 expression into the surrounding text:

```cylc
[[generate_forcing_{{ park.name }}]]
```

When `park.name` is `alpha`, this renders to `[[generate_forcing_alpha]]`. The
`|` pipe operator applies a filter — `{{ park.turbine | lower }}` converts `V90`
to `v90` for the ancil filename.

### `{% for %}` — Loops

The `{% for %}` loop generates repeated blocks of Cylc configuration:

```jinja2
{% for park in wind_parks %}
    @clock & install_cold[^] \
        => generate_forcing_{{ park.name }} \
        => extrapolate_wind_{{ park.name }} \
        => estimate_yield_{{ park.name }}
{% endfor %}
```

This renders to three separate graph lines — one independent pipeline per park.
All three pipelines run in parallel within each cycle.

### `{% if %}` — Conditionals

The roughness length `z0` depends on site type. Offshore sites have a much
smaller roughness length than onshore sites, which significantly affects the
log law extrapolation to hub height:

```jinja2
[[[environment]]]
    {% if park.site == 'offshore' %}
        z0 = 0.0002
    {% else %}
        z0 = 0.03
    {% endif %}
```

This sets `z0` as a task environment variable, which `extrapolate_wind.py`
reads at runtime via `os.environ['z0']`.

### `{# #}` — Comments

Jinja2 comments use `{# #}` syntax and are removed entirely from the rendered
output — they do not appear in the parsed workflow configuration:

```jinja2
{# To add or remove a wind park, edit this list #}
```

## Configuration Design Principles

The turbine engineering parameters — hub height, cut-in speed, rated power —
live in ancil files under `ancil/`. These are manufacturer data that do not
change between deployments.

The roughness length `z0` lives in `flow.cylc` via Jinja2. This is a site
configuration choice made by the operator, not a physical property of the
turbine. The distinction matters: ancil files are turbine data, `flow.cylc`
is deployment configuration.

## Running the Example

```bash
cd examples/ctn06_jinja2-templating
cylc vip .
```

Inspect the rendered `flow.cylc` to see what Cylc actually parsed after
Jinja2 processing:

```bash
cylc view --process ctn06_jinja2-templating
```

Observe in the TUI that after `install_cold` completes, nine tasks appear in
parallel — three pipelines of three tasks each — all gated by the same clock
trigger.

Compare the power output across the three parks for the same cycle point:

```bash
grep "power_MW" ~/cylc-run/ctn06_jinja2-templating/run1/share/yield/*/power_<cycle_point>.txt
```

The V236-15.0 at 119 m hub height will consistently show higher hub-height wind
speeds — and therefore higher power output — than the V90-3.0 at 80 m, even
from the same 10 m observation.

## Student Exercise

Add a fourth wind park `delta` using a V150-4.0 turbine on an onshore site.
Edit the `wind_parks` list in `flow.cylc`:

```jinja2
{'name': 'delta', 'turbine': 'V150', 'site': 'onshore'},
```

Run the workflow and compare the power output of `delta` (onshore V150) against
`beta` (offshore V150). The only difference is `z0` — observe how the higher
roughness length of the onshore site reduces the hub-height wind speed and
therefore the estimated power output.

## Further Reading

- [Jinja2 in Cylc](https://cylc.github.io/cylc-doc/stable/html/user-guide/writing-workflows/jinja2.html) — full reference for Jinja2 in `flow.cylc`, including filters, conditionals, and the `cylc view --process` debugging tool
- [Jinja2 Tutorial](https://cylc.github.io/cylc-doc/stable/html/tutorial/runtime/configuration-consolidation/jinja2.html) — hands-on introduction using a weather station example

## Cleaning Up

```bash
cylc clean ctn06_jinja2-templating
```
