#!/usr/bin/env python3
"""
Wind turbine energy yield estimator.

Estimates instantaneous power output using the standard cubic power curve
model (IEC 61400-12):

    P = 0                               u < u_cutin
    P = P_rated * (u / u_rated) ** 3    u_cutin <= u < u_rated
    P = P_rated                         u_rated <= u < u_cutout
    P = 0                               u >= u_cutout

where:
    u        : hub height wind speed [m/s]
    u_cutin  : cut-in wind speed [m/s]
    u_rated  : rated wind speed [m/s]
    u_cutout : cut-out wind speed [m/s]
    P_rated  : rated power [MW]

Note: In operational practice, energy yield is calculated from 10-minute mean
wind speeds following IEC 61400-12. The 1-minute cycling used in this example
is chosen to make the clock trigger behaviour immediately observable during the
exercise, not to reflect standard measurement practice.

Usage:
    python estimate_yield.py <wind_file> <ancil_file> <output_file>
"""

import sys


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


def power_curve(u, u_cutin, u_rated, u_cutout, P_rated):
    """Cubic power curve model."""
    if u < u_cutin or u >= u_cutout:
        return 0.0
    elif u < u_rated:
        return round(P_rated * (u / u_rated) ** 3, 4)
    else:
        return P_rated


def main(wind_file, ancil_file, output_file):
    wind  = read_key_value(wind_file)
    ancil = read_key_value(ancil_file)

    cycle_point = wind['cycle_point']
    u_hub       = float(wind['u_hub'])
    turbine     = ancil['turbine']
    u_cutin     = float(ancil['u_cutin'])
    u_rated     = float(ancil['u_rated'])
    u_cutout    = float(ancil['u_cutout'])
    P_rated     = float(ancil['P_rated'])

    power = power_curve(u_hub, u_cutin, u_rated, u_cutout, P_rated)

    # Capacity factor: fraction of rated power being produced
    capacity_factor = round(power / P_rated, 4) if P_rated > 0 else 0.0

    with open(output_file, 'w') as f:
        f.write(f"cycle_point     = {cycle_point}\n")
        f.write(f"turbine         = {turbine}\n")
        f.write(f"u_hub           = {u_hub}\n")
        f.write(f"power_MW        = {power}\n")
        f.write(f"capacity_factor = {capacity_factor}\n")

    print(f"Cycle           : {cycle_point}")
    print(f"Turbine         : {turbine}")
    print(f"u(hub)          : {u_hub} [m/s]")
    print(f"Power           : {power} [MW]")
    print(f"Capacity factor : {capacity_factor:.1%}")
    print(f"Result written to: {output_file}")


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: estimate_yield.py <wind_file> <ancil_file> <output_file>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
