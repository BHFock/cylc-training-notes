#!/usr/bin/env python3
"""
Log wind profile model.

Computes the logarithmic wind profile:

    u(z) = (u_star / kappa) * ln(z / z0)

where:
    u_star  : friction velocity (m/s)
    z0      : aerodynamic roughness length (m)
    kappa   : von Karman constant (0.4)
    z       : height above surface (m)

Reads input parameters from a forcing file and writes the wind profile to a CSV file.

Usage:
    python log_wind_profile.py <forcing_file> <output_file>
"""

import sys
import math
import csv

KAPPA = 0.4  # von Karman constant


def log_wind_speed(u_star, z0, z):
    """Return wind speed at height z using the log wind law."""
    if z <= z0:
        return 0.0
    return (u_star / KAPPA) * math.log(z / z0)


def read_forcing(forcing_file):
    """Read forcing parameters from a simple key=value file."""
    params = {}
    with open(forcing_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, value = line.split('=')
            params[key.strip()] = value.strip()
    return params


def main(forcing_file, output_file):
    params = read_forcing(forcing_file)

    u_star = float(params['u_star'])
    z0     = float(params['z0'])
    levels = [float(z) for z in params['levels'].split(',')]

    print(f"Friction velocity u*  : {u_star} m/s")
    print(f"Roughness length z0   : {z0} m")
    print(f"Computing profile at  : {levels} m")

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['height_m', 'wind_speed_ms'])
        for z in levels:
            u = log_wind_speed(u_star, z0, z)
            writer.writerow([z, round(u, 4)])
            print(f"  z = {z:6.1f} m   u = {u:.4f} m/s")

    print(f"Profile written to: {output_file}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: log_wind_profile.py <forcing_file> <output_file>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
