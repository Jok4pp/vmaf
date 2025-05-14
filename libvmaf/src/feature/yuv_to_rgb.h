////c
// filepath: /home/joel-ludwig/Dokumente/Masterarbeit_Ludwig/vmaf/libvmaf/src/feature/yuv_to_rgb.h
#ifndef YUV_TO_RGB_H
#define YUV_TO_RGB_H

#ifdef __cplusplus
extern "C" {
#endif

/* 
 * Converts YUV(Rec.2020) with PQ-coded Y prime to approximate R′G′B′ (also PQ-coded).
 * Parameters:
 *   Yp, Cb, Cr range in [0..1], [-0.5..+0.5] if full range 
 *   (already normalized from 8-bit or 10-bit).
 * Result: 
 *   R′, G′, B′ in [0..1] PQ-coded domain.
 */
void yuv2020_to_rgbPQ(
    double Yp,  /* Y prime */
    double Cb,  /* Cb shifted to ±0.5 if needed */
    double Cr,  /* Cr shifted to ±0.5 if needed */
    double *Rp, double *Gp, double *Bp);

#ifdef __cplusplus
}
#endif

#endif // YUV_TO_RGB_H