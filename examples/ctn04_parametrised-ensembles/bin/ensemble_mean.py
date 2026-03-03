#!/usr/bin/env python3
"""
Ensemble mean and spread calculator.

Reads the 100 [m] wind extrapolation from each ensemble member and computes:

    mean(u100)   : ensemble mean — best estimate of the 100 [m] wind
    spread(u100) : ensemble standard deviation — measure of forecast uncertainty

The ensemble mean is written as the restart field for the next cycle's
deterministic first-guess, closing the cycling loop.

Usage:
    python ensemble_mean.py <cycle_point> <output_file> <restart_file> <member_file> [<member_file> ...]
"""

import sys
import math


def read_key_value(filepath):
    """Read a simple key=value file into a dictionary."""
    params = {}
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, value = line.split('=')
            params[key.strip()] = value.strip()
    return params


def main(cycle_point, output_file, restart_file, member_files):
    u100_values = []
    for mf in member_files:
        data = read_key_value(mf)
        u100_values.append(float(data['u100']))

    n = len(u100_values)
    mean   = round(sum(u100_values) / n, 4)
    spread = round(math.sqrt(sum((v - mean) ** 2 for v in u100_values) / n), 4)

    with open(output_file, 'w') as f:
        f.write(f"cycle_point  = {cycle_point}\n")
        f.write(f"n_members    = {n}\n")
        for i, v in enumerate(u100_values, start=1):
            f.write(f"u100_m{i:02d}     = {v}\n")
        f.write(f"u100_mean    = {mean}\n")
        f.write(f"u100_spread  = {spread}\n")

    # restart file contains only the mean for use as next cycle's first-guess
    with open(restart_file, 'w') as f:
        f.write(f"cycle_point = {cycle_point}\n")
        f.write(f"u100        = {mean}\n")

    print(f"Cycle        : {cycle_point}")
    print(f"Members      : {n}")
    print(f"u(100) values: {u100_values}")
    print(f"u(100) mean  : {mean} [m/s]")
    print(f"u(100) spread: {spread} [m/s]")
    print(f"Output written to : {output_file}")
    print(f"Restart written to: {restart_file}")


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Usage: ensemble_mean.py <cycle_point> <output_file> <restart_file> <member_file> [<member_file> ...]")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
