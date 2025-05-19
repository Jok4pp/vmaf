////c
// filepath: /home/joel-ludwig/Dokumente/Masterarbeit_Ludwig/vmaf/libvmaf/src/feature/inverse_pq.c
// inverse_pq.c: ST.2084 Inverse EOTF => PQ -> linear
#include <math.h>
#include "inverse_pq.h"

// PQ constants per BT.2100
static const double m1 = 2610.0 / 16384.0;
static const double m2 = 2523.0 / 4096.0 * 128.0;
static const double c1 = 3424.0 / 4096.0;
static const double c2 = 2413.0 / 4096.0 * 32.0;
static const double c3 = 2392.0 / 4096.0 * 32.0;
static const double LMAX = 10000.0; 

double inverse_pq_eotf(double pqValue)
{
    // pqValue in [0..1]
    double xp = pow(pqValue, 1.0 / m2);
    double num = fmax(xp - c1, 0.0);
    double den = c2 - (c3 * xp);
    // Convert to linear light [0..LMAX]
    return pow(num / den, 1.0 / m1) * LMAX;
}