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
    memcpy(out->data[0], in->data[0], (size_t)out->h[0] * out->stride[0]);
    const int ss_hor = in->pix_fmt != VMAF_PIX_FMT_YUV444P;
    const int ss_ver = in->pix_fmt == VMAF_PIX_FMT_YUV420P;

    for (unsigned p = 1; p < 3; p++) { // U and V
        for (unsigned i = 0; i < out->h[p]; i++) {
            uint16_t *src_line = (uint16_t*)in->data[p] + (i / (ss_ver ? 2 : 1)) * (in->stride[p] / 2);
            uint16_t *dst_line = (uint16_t*)out->data[p] + i * (out->stride[p] / 2);
            for (unsigned j = 0; j < out->w[p]; j++) {
                dst_line[j] = src_line[j / (ss_hor ? 2 : 1)];
            }
        }
    }
}

static void scale_chroma_planes(VmafPicture *in, VmafPicture *out)
{
    memcpy(out->data[0], in->data[0], out->h[0] * out->stride[0]);
    const int ss_hor = in->pix_fmt != VMAF_PIX_FMT_YUV444P;
    const int ss_ver = in->pix_fmt == VMAF_PIX_FMT_YUV420P;

    for (unsigned p = 1; p < 3; p++) { // U and V
        for (unsigned i = 0; i < out->h[p]; i++) {
            uint8_t *src_line = in->data[p] + (i / (ss_ver ? 2 : 1)) * in->stride[p];
            uint8_t *dst_line = out->data[p] + i * out->stride[p];
            for (unsigned j = 0; j < out->w[p]; j++) {
                dst_line[j] = src_line[j / (ss_hor ? 2 : 1)];
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
            const double Cmax =1000.0; // motion-picture range U/V

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