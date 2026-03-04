# Cylc Training Notes

Personal training notes and worked examples for learning [Cylc](https://cylc.github.io/),
a workflow engine for cycling systems used in operational meteorology and oceanography.

## Scope

This repository is a self-contained learning resource built around hands-on examples.
It is not a replacement for the official [Cylc documentation](https://cylc.github.io/cylc-doc/stable/html/)
or the [Cylc tutorial](https://cylc.github.io/cylc-doc/stable/html/tutorial/index.html),
but rather a personal companion that explores Cylc features step by step with annotated examples.

## Contents

### Getting Started

- [Installation](installation/README.md) — setting up Cylc for local development, including a proof-of-install workflow

### Examples

- [01: Workflow Structure](examples/ctn01_workflow-structure/README.md) — the `flow.cylc` file, task dependencies, and the `bin/` directory, illustrated with a log wind profile model
- [02: Datetime Cycling](examples/ctn02_datetime-cycling/README.md) — datetime cycling, cold start initialisation, synoptic hour anchoring, and cycle-stamped output files, illustrated with a wind speed extrapolation model
- [03: Cycle Dependencies](examples/ctn03_cycle-dependencies/README.md) — inter-cycle dependencies, sequential cycling, warm start restarts, and the Cylc workflow directory structure, illustrated with a DA-like NWP cycling system
- [04: Parametrised Ensembles](examples/ctn04_parametrised-ensembles/README.md) — parametrised tasks, fan-out / fan-in patterns, and parameter templates for ensemble IO, illustrated with a 5-member offshore wind ensemble forecast
- [05: Clock Triggers](examples/ctn05_clock-triggers/README.md) — clock triggers, real-time cycling, and combining xtriggers with task dependencies, illustrated with a real-time wind monitoring and energy yield estimation system
- [06: Jinja2 Templating](examples/ctn06_jinja2-templating/README.md) — Jinja2 variables, loops, and conditionals in `flow.cylc`, illustrated with a multi-park wind monitoring system processing three wind parks in parallel

## Intended Audience

Primarily written for my own learning, but structured so that it may eventually serve as
introductory material for students or colleagues new to workflow management.

## Status

🚧 Work in progress.

## License

BSD 3-Clause License – see [LICENSE](LICENSE) for details.
