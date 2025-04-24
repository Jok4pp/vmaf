dataset_name = 'LIVE_HDR_test'
yuv_fmt = 'yuv420p'
width = 3840
height = 2160

ref_dir = 'C:/Users/jokap/OneDrive/Dokumente/Masterarbeit/vmaf/test_dataset/ref'
dis_dir = 'C:/Users/jokap/OneDrive/Dokumente/Masterarbeit/vmaf/test_dataset/dis'

ref_videos = [
  {
    "content_id": 0,
    "content_name": "4k_ref_football2",
    "path": "test_dataset/ref/4k_ref_football2.yuv"
  }
]

dis_videos = [
    {
    "asset_id": 0,
    "content_id": 0,
    "dmos": 47.46081054384501,
    "content_name": "4k_3M_football2",
    "path": "test_dataset/dis/4k_3M_football2.yuv"
    }
  ,
   {
    "asset_id": 1,
    "content_id": 0,
    "dmos": 67.44390875992056,
    "content_name": "4k_3M_football2",
    "path": "test_dataset/dis/4k_3M_football2.yuv"
    }
]
