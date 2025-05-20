#include <errno.h>
#include <math.h>
#include <stddef.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#include "feature_collector.h"
#include "feature_extractor.h"
#include "mem.h"
#include "opt.h"
#include "yuv_to_rgb.h"
#include "inverse_pq.h"
#include "rgb_to_ictcp.h"

typedef struct DeltaEITPState {
    VmafPicture ref;
    VmafPicture dist;
    void (*scale_chroma_planes)(VmafPicture *in, VmafPicture *out);
} DeltaEITPState;

static void scale_chroma_planes_hbd(VmafPicture *in, VmafPicture *out)
{
    // copy luma
    memcpy(out->data[0], in->data[0], (size_t)out->h[0] * out->stride[0]);

    // input is 4:2:0 → out is 4:4:4
    const int in_h = in->h[1], in_w = in->w[1];
    const int out_h = out->h[1], out_w = out->w[1];
    const int in_stride = in->stride[1] / 2;
    const int out_stride = out->stride[1] / 2;
    uint16_t *srcU = (uint16_t*)in->data[1], *dstU = (uint16_t*)out->data[1];
    uint16_t *srcV = (uint16_t*)in->data[2], *dstV = (uint16_t*)out->data[2];

    for (int p = 1; p <= 2; p++) {
        uint16_t *src = (p == 1 ? srcU : srcV);
        uint16_t *dst = (p == 1 ? dstU : dstV);
        for (int y = 0; y < out_h; y++) {
            double gy = (double)y * in_h / out_h;
            int iy = (int)gy;
            double fy = gy - iy;
            int iy1 = iy + 1 < in_h ? iy + 1 : in_h - 1;
            uint16_t *line0 = src +  iy  * in_stride;
            uint16_t *line1 = src + iy1 * in_stride;
            uint16_t *dline = dst +  y  * out_stride;
            for (int x = 0; x < out_w; x++) {
                double gx = (double)x * in_w / out_w;
                int ix = (int)gx;
                double fx = gx - ix;
                int ix1 = ix + 1 < in_w ? ix + 1 : in_w - 1;
                double v00 = line0[ix    ];
                double v01 = line0[ix1   ];
                double v10 = line1[ix    ];
                double v11 = line1[ix1   ];
                double w00 = (1 - fx) * (1 - fy);
                double w01 = fx       * (1 - fy);
                double w10 = (1 - fx) * fy;
                double w11 = fx       * fy;
                double val = v00*w00 + v01*w01 + v10*w10 + v11*w11;
                dline[x] = (uint16_t)(val + 0.5);
            }
        }
    }
}

static void scale_chroma_planes(VmafPicture *in, VmafPicture *out)
{
    // copy luma
    memcpy(out->data[0], in->data[0], out->h[0] * out->stride[0]);

    // input is 4:2:0 → out is 4:4:4
    const int in_h = in->h[1], in_w = in->w[1];
    const int out_h = out->h[1], out_w = out->w[1];
    const int in_stride = in->stride[1];
    const int out_stride = out->stride[1];
    uint8_t *srcU =  in->data[1], *dstU = out->data[1];
    uint8_t *srcV =  in->data[2], *dstV = out->data[2];

    for (int p = 1; p <= 2; p++) {
        uint8_t *src = (p == 1 ? srcU : srcV);
        uint8_t *dst = (p == 1 ? dstU : dstV);
        for (int y = 0; y < out_h; y++) {
            double gy = (double)y * in_h / out_h;
            int iy = (int)gy;
            double fy = gy - iy;
            int iy1 = iy + 1 < in_h ? iy + 1 : in_h - 1;
            uint8_t *line0 = src +  iy  * in_stride;
            uint8_t *line1 = src + iy1 * in_stride;
            uint8_t *dline = dst +  y  * out_stride;
            for (int x = 0; x < out_w; x++) {
                double gx = (double)x * in_w / out_w;
                int ix = (int)gx;
                double fx = gx - ix;
                int ix1 = ix + 1 < in_w ? ix + 1 : in_w - 1;
                double v00 = line0[ix   ];
                double v01 = line0[ix1  ];
                double v10 = line1[ix   ];
                double v11 = line1[ix1  ];
                double w00 = (1 - fx) * (1 - fy);
                double w01 = fx       * (1 - fy);
                double w10 = (1 - fx) * fy;
                double w11 = fx       * fy;
                double val = v00*w00 + v01*w01 + v10*w10 + v11*w11;
                dline[x] = (uint8_t)(val + 0.5);
            }
        }
    }
}

static int init(VmafFeatureExtractor *fex, enum VmafPixelFormat pix_fmt,
                unsigned bpc, unsigned w, unsigned h)
{
    DeltaEITPState *s = fex->priv;
    int err = 0;

    fprintf(stderr, "Initializing DeltaEITP feature extractor\n");

    if (pix_fmt == VMAF_PIX_FMT_YUV400P) {
        fprintf(stderr, "Unsupported pixel format: YUV400P\n");
        return -EINVAL;
    }

    if (pix_fmt == VMAF_PIX_FMT_YUV444P)
        return 0;

    switch (bpc) {
    case 8:
        s->scale_chroma_planes = scale_chroma_planes;
        break;
    case 10:
    case 12:
    case 16:
        s->scale_chroma_planes = scale_chroma_planes_hbd;
        break;
    default:
        fprintf(stderr, "Unsupported bit depth: %u\n", bpc);
        return -EINVAL;
    }

    err |= vmaf_picture_alloc(&s->ref, VMAF_PIX_FMT_YUV444P, bpc, w, h);
    err |= vmaf_picture_alloc(&s->dist, VMAF_PIX_FMT_YUV444P, bpc, w, h);
    if (err) {
        fprintf(stderr, "Failed to allocate memory for pictures\n");
        return err;
    }

    return 0;
}

static int extract(VmafFeatureExtractor *fex,
                   VmafPicture *ref_pic, VmafPicture *ref_pic_90,
                   VmafPicture *dist_pic, VmafPicture *dist_pic_90,
                   unsigned index, VmafFeatureCollector *feature_collector)
{
    DeltaEITPState *s = fex->priv;
    (void) ref_pic_90;
    (void) dist_pic_90;

    VmafPicture *ref;
    VmafPicture *dist;

    

    if (ref_pic->pix_fmt == VMAF_PIX_FMT_YUV444P) {
        // Reuse the provided buffers
        ref = ref_pic;
        dist = dist_pic;
    } else {
        ref = &s->ref;
        dist = &s->dist;
        s->scale_chroma_planes(ref_pic, ref);
        s->scale_chroma_planes(dist_pic, dist);
    }

    unsigned w = ref->w[0];
    unsigned h = ref->h[0];

    if (w == 0 || h == 0) {
        fprintf(stderr, "Invalid dimensions in extract: width=%u, height=%u\n", w, h);
        return -EINVAL;
    }

    /* normalization divisor based on bits-per-channel */
    double max_val = (double)((1u << ref->bpc) - 1u);
    double sum_delta_eitp = 0.0;

    // Process each pixel
    for (unsigned i = 0; i < h; i++) {
        for (unsigned j = 0; j < w; j++) {
            float r_y, r_u, r_v, d_y, d_u, d_v;

            switch (ref->bpc) {
            case 8:
                r_y = ((uint8_t*)ref->data[0])[i * ref->stride[0] + j];
                r_u = ((uint8_t*)ref->data[1])[i * ref->stride[1] + j];
                r_v = ((uint8_t*)ref->data[2])[i * ref->stride[2] + j];
                d_y = ((uint8_t*)dist->data[0])[i * dist->stride[0] + j];
                d_u = ((uint8_t*)dist->data[1])[i * dist->stride[1] + j];
                d_v = ((uint8_t*)dist->data[2])[i * dist->stride[2] + j];
                break;
            case 10:
            case 12:
            case 16:
                r_y = ((uint16_t*)ref->data[0])[i * (ref->stride[0] / 2) + j];
                r_u = ((uint16_t*)ref->data[1])[i * (ref->stride[1] / 2) + j];
                r_v = ((uint16_t*)ref->data[2])[i * (ref->stride[2] / 2) + j];
                d_y = ((uint16_t*)dist->data[0])[i * (dist->stride[0] / 2) + j];
                d_u = ((uint16_t*)dist->data[1])[i * (dist->stride[1] / 2) + j];
                d_v = ((uint16_t*)dist->data[2])[i * (dist->stride[2] / 2) + j];
                break;
            default:
                fprintf(stderr, "Unsupported bit depth: %u\n", ref->bpc);
                return -EINVAL;
            }
            
            if (i == 0 && j == 0)
                fprintf(stderr,
                    "[debug] YUV      @ (0,0): refY=%f refU=%f refV=%f | "
                    "distY=%f distU=%f distV=%f\n",
                    r_y, r_u, r_v, d_y, d_u, d_v);  
            
            // /* Normalize YUV values */
            // double refYp  =  r_y / max_val;
            // double refCb = (r_u / max_val) - 0.5;
            // double refCr = (r_v / max_val) - 0.5;

            // double distYp  =  d_y / max_val;
            // double distCb = (d_u / max_val) - 0.5;
            // double distCr = (d_v / max_val) - 0.5;

            const double Ymin =  64.0;
            const double Ymax = 940.0;
            const double Cmin =  64.0;
            const double Cmax = 960.0; // motion-picture range U/V

            double refYp  = (r_y - Ymin)/(Ymax - Ymin);
            double refCb = (r_u - (1<<9))/(Cmax - Cmin);
            double refCr = (r_v - (1<<9))/(Cmax - Cmin);


            double distYp  = (d_y - Ymin)/(Ymax - Ymin);
            double distCb = (d_u - (1<<9))/(Cmax - Cmin);
            double distCr = (d_v - (1<<9))/(Cmax - Cmin);
            
            if (i == 0 && j == 0)
                fprintf(stderr,
                       "[debug] Norm YUV @ (0,0): refYp=%f refCb=%f refCr=%f | "
                       "distYp=%f distCb=%f distCr=%f\n",
                        refYp, refCb, refCr, distYp, distCb, distCr);

            // Convert YUV to RGB
            double refRp, refGp, refBp;
            yuv2020_to_rgbPQ(refYp, refCb, refCr, &refRp, &refGp, &refBp);

            double distRp, distGp, distBp;
            yuv2020_to_rgbPQ(distYp, distCb, distCr, &distRp, &distGp, &distBp);

            if (i == 0 && j == 0)
                fprintf(stderr,
                    "[debug] RGB PQ   @ (0,0): refRp=%f refGp=%f refBp=%f | "
                    "distRp=%f distGp=%f distBp=%f\n",
                    refRp, refGp, refBp, distRp, distGp, distBp);
 

            // Convert RGB to linear
            double refRlin = inverse_pq_eotf(refRp);
            double refGlin = inverse_pq_eotf(refGp);
            double refBlin = inverse_pq_eotf(refBp);

            double distRlin = inverse_pq_eotf(distRp);
            double distGlin = inverse_pq_eotf(distGp);
            double distBlin = inverse_pq_eotf(distBp);
            
            if (i == 0 && j == 0)
                fprintf(stderr,
                    "[debug] Linear RGB @ (0,0): refRlin=%f refGlin=%f refBlin=%f | "
                    "distRlin=%f distGlin=%f distBlin=%f\n",
                    refRlin, refGlin, refBlin, distRlin, distGlin, distBlin);

            // Convert linear RGB to ICtCp
            float Ic_ref, Ct_ref, Cp_ref;
            rgb2020_to_ictcp(refRlin, refGlin, refBlin, &Ic_ref, &Ct_ref, &Cp_ref);

            float Ic_dist, Ct_dist, Cp_dist;
            rgb2020_to_ictcp(distRlin, distGlin, distBlin, &Ic_dist, &Ct_dist, &Cp_dist);

            if (i == 0 && j == 0)
                fprintf(stderr,
                    "[debug] ICtCp     @ (0,0): ref(I=%f,T=%f,P=%f) | "
                    "dist(I=%f,T=%f,P=%f)\n",
                    Ic_ref, Ct_ref, Cp_ref, Ic_dist, Ct_dist, Cp_dist);

            // Compute ΔEITP
            double delta_I = Ic_ref - Ic_dist;
            double delta_T = 0.5 * (Ct_ref - Ct_dist);
            double delta_P = Cp_ref - Cp_dist;

            double delta_eitp_pixel = 720.0 * sqrt(delta_I * delta_I + delta_T * delta_T + delta_P * delta_P);
            sum_delta_eitp += delta_eitp_pixel;
            
        }
    }

    double avg_delta_eitp = sum_delta_eitp / (w * h);
    fprintf(stderr, "Image index %u: deltaEITP = %f\n", index, avg_delta_eitp);

    // Append result to feature collector
    return vmaf_feature_collector_append(feature_collector, "delta_eitp", avg_delta_eitp, index);
}

static int close(VmafFeatureExtractor *fex)
{
    DeltaEITPState *s = fex->priv;
    if (s->ref.data[0] && s->dist.data[0]) {
        vmaf_picture_unref(&s->ref);
        vmaf_picture_unref(&s->dist);
    }
    return 0;
}

static const char *provided_features[] = {
    "delta_eitp",
    NULL
};

VmafFeatureExtractor vmaf_fex_delta_eitp = {
    .name = "delta_eitp",
    .init = init,
    .extract = extract,
    .close = close,
    .priv_size = sizeof(DeltaEITPState),
    .provided_features = provided_features,
};