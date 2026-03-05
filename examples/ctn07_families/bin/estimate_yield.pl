#!/usr/bin/env perl
# estimate_yield.pl
#
# Wind turbine energy yield estimator — Perl implementation.
#
# Estimates instantaneous power output using the standard cubic power curve
# model (IEC 61400-12):
#
#   P = 0                               u < u_cutin
#   P = P_rated * (u / u_rated) ** 3    u_cutin <= u < u_rated
#   P = P_rated                         u_rated <= u < u_cutout
#   P = 0                               u >= u_cutout
#
# This script implements the same physics as estimate_yield.py. It is used
# for Siemens turbine parks, where the yield calculation is provided by a
# legacy Perl-based tool.
#
# Usage:
#   perl estimate_yield.pl <wind_file> <ancil_file> <output_file>

use strict;
use warnings;

die "Usage: estimate_yield.pl <wind_file> <ancil_file> <output_file>\n"
    unless @ARGV == 3;

my ($wind_file, $ancil_file, $output_file) = @ARGV;

sub read_key_value {
    my ($filepath) = @_;
    my %params;
    open(my $fh, '<', $filepath) or die "Cannot open $filepath: $!\n";
    while (my $line = <$fh>) {
        chomp $line;
        $line =~ s/#.*//;
        $line =~ s/^\s+|\s+$//g;
        next unless $line;
        my ($key, $value) = split(/\s*=\s*/, $line, 2);
        $params{$key} = $value;
    }
    close($fh);
    return %params;
}

sub power_curve {
    my ($u, $u_cutin, $u_rated, $u_cutout, $P_rated) = @_;
    if ($u < $u_cutin || $u >= $u_cutout) {
        return 0.0;
    } elsif ($u < $u_rated) {
        return $P_rated * ($u / $u_rated) ** 3;
    } else {
        return $P_rated;
    }
}

my %wind  = read_key_value($wind_file);
my %ancil = read_key_value($ancil_file);

my $cycle_point = $wind{cycle_point};
my $u_hub       = $wind{u_hub};
my $turbine     = $ancil{turbine};
my $u_cutin     = $ancil{u_cutin};
my $u_rated     = $ancil{u_rated};
my $u_cutout    = $ancil{u_cutout};
my $P_rated     = $ancil{P_rated};

my $power = power_curve($u_hub, $u_cutin, $u_rated, $u_cutout, $P_rated);
my $capacity_factor = $P_rated > 0 ? $power / $P_rated : 0.0;

open(my $out, '>', $output_file) or die "Cannot open $output_file: $!\n";
printf $out "cycle_point     = %s\n",  $cycle_point;
printf $out "turbine         = %s\n",  $turbine;
printf $out "u_hub           = %s\n",  $u_hub;
printf $out "power_MW        = %.4f\n", $power;
printf $out "capacity_factor = %.4f\n", $capacity_factor;
close($out);

printf "Cycle           : %s\n",   $cycle_point;
printf "Turbine         : %s\n",   $turbine;
printf "u(hub)          : %s m/s\n", $u_hub;
printf "Power           : %.4f MW\n", $power;
printf "Capacity factor : %.1f%%\n",  $capacity_factor * 100;
printf "Result written to: %s\n",  $output_file;
