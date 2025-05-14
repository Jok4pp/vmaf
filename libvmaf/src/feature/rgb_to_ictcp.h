////c
// filepath: /home/joel-ludwig/Dokumente/Masterarbeit_Ludwig/vmaf/libvmaf/src/feature/rgb_to_ictcp.h
#ifndef RGB_TO_ICTCP_H
#define RGB_TO_ICTCP_H

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Converts linear RGB(Rec.2020) to ICtCp, as defined in BT.2100.
 * R_lin, G_lin, B_lin in linear light domain.
 * Outputs Ic, Ct, Cp as floats.
 */
void rgb2020_to_ictcp(
    double R_lin, double G_lin, double B_lin,
    float *Ic, float *Ct, float *Cp);

#ifdef __cplusplus
}
#endif

#endif // RGB_TO_ICTCP_H