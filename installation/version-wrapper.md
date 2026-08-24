[← Installation](README.md)

# The Cylc Version Wrapper

> **Note:** This page documents an optional but recommended addition to the basic
> conda installation. It is not required to work through the [examples](../examples/),
> but it removes the need to run `conda activate` before every Cylc command and is
> the mechanism that makes multi-version and multi-host setups work.

Cylc cannot activate its own environment. The
[official documentation](https://cylc.github.io/cylc-doc/stable/html/installation.html)
recommends a wrapper script named `cylc`, placed in `$PATH`, which selects the correct
environment and re-invokes the real command inside it. The notes below record the full
setup in one place, since the official pages cover the pieces but not the end-to-end
sequence.

## Why Bother

Without the wrapper, `conda activate` must be run in every shell, and — more importantly —
in every environment where a Cylc command is invoked. That includes task job scripts on
remote hosts, where no interactive login has taken place.

Three problems the wrapper solves:

- **Convenience.** `cylc` works in any shell, whether or not conda is initialised.
- **Version pinning.** A workflow started under 8.6.5 keeps using 8.6.5, even if the
  site default is upgraded mid-run.
- **Remote consistency.** The scheduler exports `CYLC_ENV_NAME` to job hosts so the
  same environment is selected everywhere.

> **Note:** The wrapper also matters for job submission. Cylc can be configured to use a
> clean job submission environment, which requires the wrapper to be on `$PATH` for local
> jobs to run at all.

## How It Works

The wrapper is invoked instead of the real command, works out which environment to use,
and hands over with `exec`:

```
cylc play my-workflow
  └─ ~/bin/cylc                                  (the wrapper)
       ├─ resolve environment name
       │    CYLC_HOME → CYLC_ENV_NAME → CYLC_VERSION → default symlink
       ├─ search CYLC_HOME_ROOT, then CYLC_HOME_ROOT_ALT
       └─ exec $CYLC_HOME/bin/cylc play my-workflow
```

The same script is used for `isodatetime`, `rose` and `rosie` — it inspects the name it
was called under (`${0##*/}`) and runs the matching executable from the selected
environment.

> **Note:** No `conda activate` is involved. Scripts in `envs/*/bin/` carry an absolute
> shebang pointing at the interpreter of their own environment, so `exec` alone is
> sufficient — and considerably faster.

## Naming Convention

The wrapper expects environments to be named `cylc-$CYLC_VERSION` and a symlink named
`cylc` to mark the default:

```
~/miniforge3/envs/
├── cylc -> cylc-8.6.5      # default, used when nothing is set
├── cylc-8.6.5
└── cylc-8.7.0
```

A version suffix is permitted where several environments hold the same `cylc-flow`
version, e.g. `cylc-8.6.5-1`. Additional named environments can be created for selection
via `CYLC_VERSION`:

```bash
ln -s cylc-8.7.0 cylc-next     # selected with CYLC_VERSION=next
```

> **Note:** The environment name in [`environment.yml`](environment.yml) must follow this
> convention for the wrapper to find it. An environment named `cylc-training` is not
> discoverable as a version — either rename it to `cylc-<version>`, or point the default
> symlink at it (`ln -s cylc-training cylc`), in which case `CYLC_ENV_NAME` resolves to
> `cylc-training`.

## Setup

### 1. Create the Environment

```bash
conda env create -f installation/environment.yml
```

### 2. Mark the Default Version

```bash
cd ~/miniforge3/envs
ln -s cylc-8.6.5 cylc
```

Without this symlink the wrapper looks for an environment literally named `cylc` and
exits with an error.

### 3. Extract the Wrapper

Cylc ships the wrapper as a resource:

```bash
mkdir -p ~/bin
conda activate cylc-8.6.5
cylc get-resources cylc ~/bin/cylc
chmod +x ~/bin/cylc
conda deactivate
```

> **Note:** This is the only step that needs `conda activate`, and only once. Do not place
> the wrapper inside an environment's own `bin/` directory — it would `exec` itself in an
> endless loop.

### 4. Configure the Search Root

Edit the `!!! EDIT ME !!!` block near the top of `~/bin/cylc`.

**Home installation only** — no central Cylc on the machine:

```bash
CYLC_HOME_ROOT="${CYLC_HOME_ROOT:-$HOME/miniforge3/envs}"
```

**Alongside a site installation** — the usual situation on shared systems:

```bash
CYLC_HOME_ROOT="${CYLC_HOME_ROOT:-/opt}"
CYLC_HOME_ROOT_ALT="${CYLC_HOME_ROOT_ALT:-$HOME/miniforge3/envs}"
```

Environments are searched in `CYLC_HOME_ROOT` first, then `CYLC_HOME_ROOT_ALT`. In the
second variant, site environments therefore win by default and personal ones are selected
deliberately with `CYLC_VERSION`.

> **Note:** Keep the `${VAR:-default}` form rather than assigning the value outright, so
> the setting can still be overridden from the calling environment.

### 5. Create the Command Symlinks

```bash
cd ~/bin
ln -s cylc isodatetime
```

### 6. Put the Wrapper on `$PATH`

In `~/.bash_profile` (or `~/.bashrc`):

```bash
export PATH="$HOME/bin:$PATH"
```

`~/bin` must come before any conda paths. Log in again, or run `hash -r`.

> **Note:** Many distributions add `~/bin` to `$PATH` automatically, but only if the
> directory already existed at login. After creating it for the first time, start a new
> session before testing.

### 7. Verify

```bash
type -a cylc              # ~/bin/cylc must be listed first
cylc version --long       # 8.6.5 (/home/<user>/miniforge3/envs/cylc-8.6.5)
isodatetime --version
```

Then re-run the [proof-of-install workflow](README.md#proof-of-installation) — this time
without activating anything.

## Selecting a Version

| Variable | Set by | Effect |
| --- | --- | --- |
| *(nothing)* | — | uses the `cylc` symlink in the search root |
| `CYLC_VERSION` | user | selects `cylc-$CYLC_VERSION` |
| `CYLC_HOME_ROOT_ALT` | user | adds a second search location |
| `CYLC_HOME` | user | full path to an environment, bypassing the search entirely |
| `CYLC_ENV_NAME` | scheduler | pins the resolved environment for remote commands |

Examples:

```bash
cylc version                          # default
CYLC_VERSION=8.7.0 cylc version       # one-off
export CYLC_VERSION=8.7.0             # for the session
```

> **Note:** `CYLC_ENV_NAME` is set by the scheduler, not by users. When the wrapper
> resolves a symlinked environment it replaces the path with its real target and exports
> the resolved name, so re-pointing the `cylc` symlink cannot affect a running workflow.

## Multi-Host Setups

The scheduler exports `CYLC_ENV_NAME` to job hosts, so every host must be able to resolve
that name independently. On each job host:

- the wrapper is present in `$PATH`, configured the same way
- an environment with **exactly** the same name exists
- `CYLC_HOME_ROOT_ALT` is set in the login shell if personal environments are used

`CYLC_HOME` is unsuitable here — it is not passed to remote platforms. Prefer
`CYLC_VERSION` together with `CYLC_HOME_ROOT_ALT`.

> **Note:** Job scripts run via `bash -l` and therefore source login scripts. These must
> configure `$PATH` correctly and must not write anything to stdout, or job submission
> will fail in confusing ways.

## Troubleshooting

**`ERROR: cylc not found in /opt`** — no environment named `cylc` exists in the search
root. Create the default symlink (step 2) or set `CYLC_VERSION`.

**`ERROR: cylc not found in <path>`** (with a resolved path) — the environment exists but
holds no `bin/cylc`, usually because `cylc-flow` failed to install. Check with
`ls <path>/bin/cylc`.

**The wrapper runs but reports an unexpected version** — a conda `bin` directory precedes
`~/bin` in `$PATH`, or a stale entry is cached. Check with `type -a cylc` and clear the
cache with `hash -r`.

**Endless loop / `Argument list too long`** — the wrapper was placed inside an
environment's `bin/` directory and is calling itself. Move it to a neutral location.

**Commands work interactively but jobs fail** — `$PATH` is set in `~/.bashrc` behind an
interactive-shell guard, so job scripts never see it. Set it in `~/.bash_profile`, or
before the guard.

**`cylc rose` or `rosie` misbehaves** — the wrapper contains legacy branches that redirect
`rose config-edit`, `rosie` and `cylc review` to Cylc 7 / Rose 2019.01 environments. If
those are not installed, the redirect fails. Only relevant where legacy versions exist.

## References

- [Cylc installation docs](https://cylc.github.io/cylc-doc/stable/html/installation.html) — includes `cylc get-resources cylc`
- [Cylc conda environments reference](https://cylc.github.io/cylc-doc/stable/html/reference/environments/conda.html)
- [Global configuration reference](https://cylc.github.io/cylc-doc/stable/html/reference/config/global.html) — clean job submission environments
- [Wrapper source in cylc-flow](https://github.com/cylc/cylc-flow/blob/master/cylc/flow/etc/cylc)
