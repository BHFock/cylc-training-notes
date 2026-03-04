#!/usr/bin/env python3
"""
Simulated met mast wind observation generator.

Simulates a 10 m wind speed observation from an offshore met mast by drawing
a random sample from a realistic offshore wind speed distribution.

In a real system this script would ingest a live observation from a met mast
data feed. Here a stochastic generator stands in for the observation source,
producing a plausible 10 m wind speed for each 1-minute cycle.

Usage:
    python generate_forcing.py <cycle_point> <output_file>
"""

import sys
import random

U10_MEAN  = 10.0  # mean 10 [m] wind speed [m/s] — typical offshore site
U10_STD   =  2.0  # standard deviation [m/s]
U10_MIN   =  0.0  # minimum plausible value [m/s]
U10_MAX   = 30.0  # maximum plausible value [m/s]


def main(cycle_point, output_file):
    # Gaussian draw clipped to physically plausible range
    u10 = random.gauss(U10_MEAN, U10_STD)
    u10 = round(max(U10_MIN, min(U10_MAX, u10)), 4)

    with open(output_file, 'w') as f:
        f.write(f"cycle_point = {cycle_point}\n")
        f.write(f"u10         = {u10}\n")

    print(f"Cycle     : {cycle_point}")
    print(f"u(10 [m]) : {u10} [m/s]")
    print(f"Observation written to: {output_file}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: generate_forcing.py <cycle_point> <output_file>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
