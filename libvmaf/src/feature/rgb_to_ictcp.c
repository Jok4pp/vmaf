////c
// filepath: /home/joel-ludwig/Dokumente/Masterarbeit_Ludwig/vmaf/libvmaf/src/feature/rgb_to_ictcp.c
// rgb_to_ictcp.c: transform from linear RGB(2020) to ICtCp (Version 7.1 formula)

#include <math.h>
#include "rgb_to_ictcp.h"

//-------------------------------------------------------------------
// 1) RGB -> LMS (per ITU definitions, integer coefficients method):
//    L = (1688*R + 2146*G +  262*B) / 4096
//    M = ( 683*R + 2951*G +  462*B) / 4096
//    S = (  99*R +  309*G + 3688*B) / 4096
//-------------------------------------------------------------------
static void rgb2020_to_lms(double R_lin, double G_lin, double B_lin,
                           double *L, double *M, double *S)
{
    *L = (1688.0 * R_lin + 2146.0 * G_lin + 262.0  * B_lin) / 4096.0;
    *M = (683.0  * R_lin + 2951.0 * G_lin + 462.0  * B_lin) / 4096.0;
    *S = (99.0   * R_lin + 309.0  * G_lin + 3688.0 * B_lin) / 4096.0;
}

//-------------------------------------------------------------------
// 2) Apply ST 2084 "forward" (OETF) to get L′, M′, S′ from linear LMS.
//    This is sometimes called the "inverse EOTF" in some documents.
//    Provide a local pq_encode() function here for completeness.
//    
//    If you already have a separate code for PQ encode, you can call it.
//-------------------------------------------------------------------
static const double c1 = 3424.0  / 4096.0;
static const double c2 = 2413.0  / 4096.0 * 32.0;
static const double c3 = 2392.0  / 4096.0 * 32.0;
static const double m1 = 2610.0  / 16384.0;
static const double m2 = 2523.0  / 4096.0  * 128.0;

static inline double pq_encode(double linear)
{
    // ST 2084 forward: from linear [0..∞) to code value [0..1].
    // Typically we clamp negative or extremely large linear values.
    double L = linear/ 10000.0;
    double num = c1 + c2*pow(L, m1);
    double den = 1.0 + c3*pow(L, m1);
    return pow(num/den, m2);
}

//-------------------------------------------------------------------
// 3) LMS -> ICtCp (with L’, M’, S’ = PQ encoded):
//    I  = 0.5*L’   + 0.5*M’
//    Ct = ( 6610*L’ - 13613*M’ +  7003*S’) / 4096
//    Cp = (17933*L’ - 17390*M’ -   543*S’) / 4096
//    
// Note that the official BT.2100 text might have different or 
// updated constants; verify them with your reference spec.
//-------------------------------------------------------------------
void rgb2020_to_ictcp(
    double R_lin, double G_lin, double B_lin,
    float *Ic, float *Ct, float *Cp)
{
    // Step 1: get linear LMS
    double L_lin, M_lin, S_lin;
    rgb2020_to_lms(R_lin, G_lin, B_lin, &L_lin, &M_lin, &S_lin);



    // Step 2: PQ encode each channel => L’, M’, S’
    double Lp = pq_encode(L_lin);
    double Mp = pq_encode(M_lin);
    double Sp = pq_encode(S_lin);

    // Step 3: compute ICtCp
    double I_val  = 0.5 * Lp + 0.5 * Mp;
    double Ct_val = (6610.0  * Lp - 13613.0 * Mp + 7003.0  * Sp) / 4096.0;
    double Cp_val = (17933.0 * Lp - 17390.0 * Mp - 543.0   * Sp) / 4096.0;

    *Ic = (float)I_val;
    *Ct = (float)Ct_val;
    *Cp = (float)Cp_val;
}