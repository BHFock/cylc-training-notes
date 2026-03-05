#!/usr/bin/env python3
"""
Log law wind speed extrapolation to hub height — stability correction.

Extrapolates 10 m wind speed to turbine hub height using the logarithmic
wind profile with a stability correction term:

    u(h) = u(10) * [ln(h/z0) - psi] / [ln(10/z0) - psi]

where psi is the stability correction function (Monin-Obukhov similarity
theory). Negative psi indicates stable conditions (suppressed mixing,
stronger wind shear, higher hub-height winds than neutral); positive psi
indicates unstable conditions (enhanced mixing, weaker wind shear, lower
hub-height winds than neutral).

Both z0 and psi are read from the task environment. This task overrides
the family default psi = 0.0 with psi = -0.1 at the task level in flow.cylc,
representing mildly stable offshore conditions — typical when warm air
is advected over a cooler sea surface.

This script is identical in structure to extrapolate_wind_neutral.py —
the distinction is in the environment variable values set by Cylc, not
in the script logic.

Usage:
    python extrapolate_wind_stability.py <forcing_file> <ancil_file> <output_file>
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
    psi         = float(os.environ['psi'])

    u_hub = round(
        u10 * (math.log(hub_height / z0) - psi) / (math.log(10 / z0) - psi),
        4
    )

    with open(output_file, 'w') as f:
        f.write(f"cycle_point = {cycle_point}\n")
        f.write(f"u10         = {u10}\n")
        f.write(f"hub_height  = {hub_height}\n")
        f.write(f"z0          = {z0}\n")
        f.write(f"psi         = {psi}\n")
        f.write(f"u_hub       = {u_hub}\n")

    print(f"Cycle       : {cycle_point}")
    print(f"u(10 m)     : {u10} m/s")
    print(f"Hub height  : {hub_height} m")
    print(f"z0          : {z0} m")
    print(f"psi         : {psi}")
    print(f"u(hub)      : {u_hub} m/s (stability-corrected)")
    print(f"Result written to: {output_file}")


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: extrapolate_wind_stability.py <forcing_file> <ancil_file> <output_file>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
