[← Installation](README.md)

# Run Directory Locations

> **Note:** This page covers one specific use of `global.cylc`: moving workflow output
> out of `$HOME`. It is not a general guide to global configuration — see the
> [reference](https://cylc.github.io/cylc-doc/stable/html/reference/config/global.html)
> for everything else.

By default every installed workflow lives under `~/cylc-run/`, and everything a workflow
produces — job logs, work directories, shared data — accumulates there. On a personal
machine this is fine. On a shared server with a quota on `$HOME` it fills up quickly, and
the resulting failures are unhelpful: jobs fail at submission, or mid-run with write
errors, long after the workflow appeared healthy.

The fix is to point the run directories at a filesystem with space, keeping `~/cylc-run/`
as a directory of symlinks.

## Where `global.cylc` Lives

Cylc searches a hierarchy of locations, in ascending order of priority. For a user
configuration at version 8.6.5 the relevant files are:

```
~/.cylc/flow/global.cylc
~/.cylc/flow/8/global.cylc
~/.cylc/flow/8.6/global.cylc
~/.cylc/flow/8.6.5/global.cylc
```

Site files under `/etc/cylc/flow/` (or `$CYLC_SITE_CONF_PATH`) are read first and are
overridden by the user files. A setting present higher up and absent lower down is *not*
overridden — the files merge rather than replace.

For most purposes the unversioned file is the one to use:

```bash
mkdir -p ~/.cylc/flow
$EDITOR ~/.cylc/flow/global.cylc
```

To see what Cylc actually ended up with, use `cylc config`.

> **Note:** The version-specific directories are useful when a setting only applies to
> one Cylc version — a path that changed between releases, for instance. Reach for them
> deliberately, not by default; a stray `8.6.5/global.cylc` is easy to forget about when
> upgrading.

## Redirecting Everything

The minimal configuration — send the whole run directory elsewhere:

```
# ~/.cylc/flow/global.cylc
[install]
    [[symlink dirs]]
        [[[localhost]]]
            run = /data/users/bhfock
```

With this in place, `cylc install` creates the run directory at
`/data/users/bhfock/cylc-run/<workflow-id>` and leaves a symlink at
`~/cylc-run/<workflow-id>` pointing to it.

```
~/cylc-run/
└── proof-of-install -> /data/users/bhfock/cylc-run/proof-of-install
```

Everything else — `log/`, `work/`, `share/`, `.service/` — is created *inside* the run
directory, so redirecting `run` alone moves all of it. This is usually what you want when
the problem is a home quota.

Nothing changes in day-to-day use: `cylc scan`, `cylc tui` and `cylc clean` all still
refer to workflows by name.

## Splitting Across Filesystems

The finer-grained keys exist for a different problem — separating data by its
characteristics rather than getting it all off `/home`:

| Key | Redirects | Typical use |
| --- | --- | --- |
| `run` | the whole run directory | home quota |
| `work` | task work directories | scratch, purgeable, high-throughput |
| `share` | data shared between tasks | scratch, but must survive the whole run |
| `share/cycle` | per-cycle shared data | large cycling output |
| `log` | scheduler and job logs | small, worth keeping and backing up |
| `log/job` | job logs only | added in 8.4.0 |

Each is symlinked individually from its standard position under `~/cylc-run/<workflow-id>/`.
A configuration that keeps logs on backed-up storage and everything else on scratch:

```
[install]
    [[symlink dirs]]
        [[[localhost]]]
            run = /scratch/bhfock
            log = /data/users/bhfock
```

> **Note:** `localhost` here is an *install target*, not a hostname — it covers the
> scheduler host and any platform that shares its filesystem. Remote platforms need their
> own sections, and their symlinks are not created at install time but when the workflow
> starts.

## Verifying

Check what Cylc resolved:

```bash
cylc config -i '[install][symlink dirs]'
```

Then install the [proof-of-install workflow](README.md#proof-of-installation) and look at
where it landed:

```bash
ls -l ~/cylc-run/
du -sh /data/users/bhfock/cylc-run/
```

The entry under `~/cylc-run/` should be a symlink, and the target should hold the actual
files.

## Cleaning Up

This is the part worth internalising. `cylc clean` follows the configured symlinks and
deletes the targets as well. Deleting a run directory by hand with `rm` removes only the
symlinks — the data stays behind on the other filesystem, invisible from `~/cylc-run/`.

```bash
cylc clean my-workflow          # removes symlinks and targets
rm -r ~/cylc-run/my-workflow    # removes symlinks only — leaves the data
```

Cylc does not consult the global configuration when cleaning; it inspects which of the
possible symlinks are actually present. Changing the configuration therefore does not
strand data from earlier runs, but hand-made symlinks are not cleaned.

## Caveats

**Existing runs are not affected.** Symlinks are created at install time and cannot be
changed for a run that already exists. Change the configuration, then install again.

**Per-run override.** `cylc install --symlink-dirs="run=/other/path"` overrides the
configured locations for a single installation, and `--symlink-dirs=""` skips symlinking
entirely. Note that specifying any directory on the command line disables the configured
locations for the ones not listed.

**Targets must be writable and must exist as a filesystem.** Cylc creates the directories
below the configured path, but the path itself must be reachable — a scratch filesystem
that is auto-mounted on login may not be present when a job runs.

## Troubleshooting

**Workflow installs but `~/cylc-run/<id>` is a plain directory** — the configuration was
not picked up. Confirm with `cylc config -i '[install][symlink dirs]'`; an empty result
usually means the file is in the wrong place, or under a version directory that does not
match the running version.

**Disk still filling up despite the configuration** — check whether the workflows
predate the change. Existing runs keep the layout they were installed with.

**Space not reclaimed after deleting workflows** — `rm` was used instead of `cylc clean`.
The targets are still there; find them under `<configured-path>/cylc-run/`.

## References

- [Global configuration reference](https://cylc.github.io/cylc-doc/stable/html/reference/config/global.html) — `[install][symlink dirs]` and the file hierarchy
- [Installing workflows](https://cylc.github.io/cylc-doc/stable/html/user-guide/installing-workflows.html#symlink-directories) — how symlinks are created at install time
- [Removing workflows](https://cylc.github.io/cylc-doc/stable/html/user-guide/removing-workflows.html) — how `cylc clean` treats symlink directories
