////c
// filepath: /home/joel-ludwig/Dokumente/Masterarbeit_Ludwig/vmaf/libvmaf/src/feature/yuv_to_rgb.c
// yuv_to_rgb.c: Convert YUV(Rec.2020) to PQ R′G′B′ (approx)
#include <math.h>
#include "yuv_to_rgb.h"

// // Example constants for a typical Rec.2020 Y′CbCr -> R′G′B′ transform (full range).
// // If your YUV is PQ-coded differently, you may need adjustments.
// static const double KR = 0.2627; 
// static const double KB = 0.0593;
// static const double KG = 1.0 - KR - KB;

// // Typically, Y' ranges [0..1], Cb/Cr [-0.5..0.5] for full-range. 
// // This function returns R′, G′, B′ in [0..1] (still PQ-coded domain).
// // In real code, confirm your bitdepth/offset usage.
// void yuv2020_to_rgbPQ(
//     double Yp, double Cb, double Cr,
//     double *Rp, double *Gp, double *Bp)
// {
//     // Simple approach: 
//     // R′ = Y′ + 1.4746*(Cr)
//     // G′ = Y′ - 0.1645*(Cb) - 0.5711*(Cr)
//     // B′ = Y′ + 1.8814*(Cb)
//     // We shift Cb/Cr by 0.5 if needed. 
//     // Here assume Cb,Cr are already in [-0.5..0.5].
//     double cR = Yp + 1.4746 * Cr;
//     double cG = Yp - 0.1645 * Cb - 0.5711 * Cr;
//     double cB = Yp + 1.8814 * Cb;

//     // Clip range
//     if (cR < 0.0) cR = 0.0; 
//     if (cR > 1.0) cR = 1.0;
//     if (cG < 0.0) cG = 0.0; 
//     if (cG > 1.0) cG = 1.0;
//     if (cB < 0.0) cB = 0.0; 
//     if (cB > 1.0) cB = 1.0;

//     *Rp = cR;
//     *Gp = cG;
//     *Bp = cB;
// }


static inline double clamp(double x, double lo, double hi) {
    return x < lo ? lo : (x > hi ? hi : x);
}

// Rec.2020 matrix, studio-range offsets
void yuv2020_to_rgbPQ(
    double Yp, double Cb, double Cr,
    double *Rp, double *Gp, double *Bp)
{
    // Using exact ITU-R BT.2020 coefficients
    const double KR = 0.2627;
    const double KB = 0.0593;
    const double KG = 1.0 - KR - KB;

    // Yp, Cb, Cr are already normalized to [0..1] & [–0.5..+0.5]
    double R = Yp + (2.0 - 2.0*KR)*Cr;        // = Yp + 1.4746*Cr
    double B = Yp + (2.0 - 2.0*KB)*Cb;        // = Yp + 1.8814*Cb
    double G = (Yp - KR*R - KB*B) / KG;       // = Yp – 0.571353*Cr – 0.164553*Cb


    
    // clip
    R = clamp(R, 0.0, 1.0);
    G = clamp(G, 0.0, 1.0);
    B = clamp(B, 0.0, 1.0);

    *Rp = R;
    *Gp = G;
    *Bp = B;
}


// void yuv2020_to_rgbPQ(
//     double Yc, double Cbc, double Crc,
//     double *Rp, double *Gp, double *Bp)
// {
//     // BT.2020 neutral weights
//     const double KR = 0.2627;
//     const double KB = 0.0593;
//     const double KG = 1.0 - KR - KB;

//     // Pb/Nb/Pr/Nr (practical limits)
//     const double Pb =  0.7910;
//     const double Nb = -0.9702;
//     const double Pr =  0.4969;
//     const double Nr = -0.8591;

//     // Recover B′
//     double Bp_local = (Cbc < 0.0)
//         ? (Yc - 2.0 * Nb * Cbc)
//         : (Yc + 2.0 * Pb * Cbc);

//     // Recover R′
//     double Rp_ = (Crc < 0.0)
//         ? (Yc - 2.0 * Nr * Crc)
//         : (Yc + 2.0 * Pr * Crc);

//     // Recover G′ by solving Yc = KR·R′ + KG·G′ + KB·B′
//     double Gp_ = (Yc - KR * Rp_ - KB * Bp_local) / KG;

//     // Clamp and store
//     *Rp = clamp(Rp_, 0.0, 1.0);
//     *Gp = clamp(Gp_, 0.0, 1.0);
//     *Bp = clamp(Bp_local,  0.0, 1.0);
// }