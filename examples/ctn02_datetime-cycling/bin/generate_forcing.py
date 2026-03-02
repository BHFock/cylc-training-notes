#!/usr/bin/env python3
"""
Stochastic NWP wind forcing generator.

Simulates a 10m wind speed analysis for a given cycle time by drawing
a random sample from a realistic offshore wind speed distribution.

Writes the cycle time and wind speed to a cycle-stamped forcing file.

Usage:
    python generate_forcing.py <cycle_point> <output_file>
"""

import sys
import random

U10_MIN = 5.0   # minimum 10m wind speed [m/s]
U10_MAX = 20.0  # maximum 10m wind speed [m/s]


def main(cycle_point, output_file):
    u10 = round(random.uniform(U10_MIN, U10_MAX), 4)

    with open(output_file, 'w') as f:
        f.write(f"cycle_point = {cycle_point}\n")
        f.write(f"u10         = {u10}\n")

    print(f"Cycle     : {cycle_point}")
    print(f"u(10 [m]) : {u10} [m/s]")
    print(f"Forcing written to: {output_file}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: generate_forcing.py <cycle_point> <output_file>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
