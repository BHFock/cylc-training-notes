#!/usr/bin/env python3
"""
Log law wind speed extrapolation to hub height — neutral stability.

Extrapolates 10 m wind speed to turbine hub height using the standard
logarithmic wind profile:

    u(h) = u(10) * ln(h/z0) / ln(10/z0)

where z0 (roughness length) is read from the task environment, set via
family inheritance from [[METEOROLOGY]] in flow.cylc.

Usage:
    python extrapolate_wind_neutral.py <forcing_file> <ancil_file> <output_file>
"""

import sys
import math
import os


def read_key_value(filepath):
    """Read a simple key=value file into a dictionary."""
    params = {}
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, value = line.split('=', 1)
            params[key.strip()] = value.strip()
    return params


def main(forcing_file, ancil_file, output_file):
    forcing = read_key_value(forcing_file)
    ancil   = read_key_value(ancil_file)

    cycle_point = forcing['cycle_point']
    u10         = float(forcing['u10'])
    hub_height  = float(ancil['hub_height'])
    z0          = float(os.environ['z0'])

    u_hub = round(
        u10 * math.log(hub_height / z0) / math.log(10 / z0),
        4
    )

    with open(output_file, 'w') as f:
        f.write(f"cycle_point = {cycle_point}\n")
        f.write(f"u10         = {u10}\n")
        f.write(f"hub_height  = {hub_height}\n")
        f.write(f"z0          = {z0}\n")
        f.write(f"u_hub       = {u_hub}\n")

    print(f"Cycle       : {cycle_point}")
    print(f"u(10 m)     : {u10} m/s")
    print(f"Hub height  : {hub_height} m")
    print(f"z0          : {z0} m")
    print(f"u(hub)      : {u_hub} m/s")
    print(f"Result written to: {output_file}")


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: extrapolate_wind_neutral.py <forcing_file> <ancil_file> <output_file>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])