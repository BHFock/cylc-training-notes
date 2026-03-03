#!/usr/bin/env python3
"""
Stochastic NWP wind forcing generator.

Generates a 10 [m] wind speed analysis for a given cycle time.

Cold start (no restart file):
    Draws randomly from the full offshore wind speed range.

Warm start (restart file provided):
    Uses the previous cycle's 100 [m] wind as a first-guess, scaled back to
    10 [m] using the inverse log law, then applies a small random perturbation
    representing the analysis increment:

        u_firstguess(10) = u_restart(100) * ln(10 / z0) / ln(100 / z0)
        u_new(10)        = u_firstguess(10) * (1 + epsilon)

    where epsilon is drawn from [-PERTURB_MAX, +PERTURB_MAX].

Usage:
    python generate_forcing.py <cycle_point> <z0> <output_file> [restart_file]
"""

import sys
import math
import random

U10_MIN     = 5.0   # minimum 10 [m] wind speed for cold start [m/s]
U10_MAX     = 20.0  # maximum 10 [m] wind speed for cold start [m/s]
PERTURB_MAX = 0.10  # maximum perturbation fraction for warm start


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


def main(cycle_point, z0, output_file, restart_file=None):
    z0 = float(z0)

    if restart_file:
        restart = read_key_value(restart_file)
        u100_prev = float(restart['u100'])
        u10_firstguess = u100_prev * math.log(10 / z0) / math.log(100 / z0)
        epsilon = random.uniform(-PERTURB_MAX, PERTURB_MAX)
        u10 = round(u10_firstguess * (1 + epsilon), 4)
        print(f"Warm start  : u(100 [m]) from previous cycle = {u100_prev} [m/s]")
        print(f"First-guess : u(10 [m])                      = {round(u10_firstguess, 4)} [m/s]")
        print(f"Perturbation: epsilon                        = {round(epsilon, 4)}")
    else:
        u10 = round(random.uniform(U10_MIN, U10_MAX), 4)
        print(f"Cold start  : random u(10 [m]) = {u10} [m/s]")

    with open(output_file, 'w') as f:
        f.write(f"cycle_point = {cycle_point}\n")
        f.write(f"u10         = {u10}\n")

    print(f"Cycle     : {cycle_point}")
    print(f"u(10 [m]) : {u10} [m/s]")
    print(f"Forcing written to: {output_file}")


if __name__ == '__main__':
    if len(sys.argv) not in (4, 5):
        print("Usage: generate_forcing.py <cycle_point> <z0> <output_file> [restart_file]")
        sys.exit(1)
    restart_file = sys.argv[4] if len(sys.argv) == 5 else None
    main(sys.argv[1], sys.argv[2], sys.argv[3], restart_file)
