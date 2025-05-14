////c
// filepath: /home/joel-ludwig/Dokumente/Masterarbeit_Ludwig/vmaf/libvmaf/src/feature/inverse_pq.h
#ifndef INVERSE_PQ_H
#define INVERSE_PQ_H

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Inverse PQ EOTF (ST.2084):
 * Converts normalized PQ-coded value in [0..1] to linear light in [0..LMAX].
 * You can tweak LMAX or provide it as a parameter if needed.
 */
double inverse_pq_eotf(double pqValue);

#ifdef __cplusplus
}
#endif

#endif // INVERSE_PQ_H