#!/usr/bin/env python3
"""
Ensemble member forcing generator.

Takes the deterministic 10 [m] wind analysis from the current cycle and applies
a member-specific random perturbation to generate an ensemble of initial
conditions:

    u_member(10) = u_det(10) * (1 + epsilon),   epsilon ~ U(-PERTURB_MAX, +PERTURB_MAX)

Each member receives an independent perturbation, producing a spread of initial
conditions that represents uncertainty in the wind analysis.

Usage:
    python generate_ensemble_forcing.py <cycle_point> <member_id> <det_forcing_file> <output_file>
"""

import sys
import random

PERTURB_MAX = 0.15  # maximum perturbation fraction per member


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


def main(cycle_point, member_id, det_forcing_file, output_file):
    det = read_key_value(det_forcing_file)
    u10_det = float(det['u10'])

    epsilon = round(random.uniform(-PERTURB_MAX, PERTURB_MAX), 4)
    u10_member = round(u10_det * (1 + epsilon), 4)

    with open(output_file, 'w') as f:
        f.write(f"cycle_point = {cycle_point}\n")
        f.write(f"member      = {member_id}\n")
        f.write(f"u10_det     = {u10_det}\n")
        f.write(f"epsilon     = {epsilon}\n")
        f.write(f"u10         = {u10_member}\n")

    print(f"Cycle        : {cycle_point}")
    print(f"Member       : {member_id}")
    print(f"u(10) det    : {u10_det} [m/s]")
    print(f"epsilon      : {epsilon}")
    print(f"u(10) member : {u10_member} [m/s]")
    print(f"Forcing written to: {output_file}")


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: generate_ensemble_forcing.py <cycle_point> <member_id> <det_forcing_file> <output_file>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
