dataset_name = 'mini_dataset'
yuv_fmt = 'yuv420p'
width = 3840
height = 2160

ref_dir = '/home/joel-ludwig/Dokumente/Masterarbeit_Ludwig/vmaf/mini_dataset/ref'
dis_dir = '/home/joel-ludwig/Dokumente/Masterarbeit_Ludwig/vmaf/mini_dataset/dis'

ref_videos = [
  {
    "content_id": 0,
    "content_name": "football2",
    "path": "mini_dataset/ref/4k_ref_football2.yuv"
  }
  ,
  {
    "content_id": 1,
    "content_name": "football3",
    "path": "mini_dataset/ref/4k_ref_football3.yuv"
  }
]

dis_videos = [
    
    {
    "asset_id": 0,
    "content_id": 0,
    "dmos": 72.14721665247458,
    "content_name": "football2",
    "path": "mini_dataset/dis/4k_15M_football2.yuv"
    }
   ,
   {
    "asset_id": 1,
    "content_id": 0,
    "dmos": 67.44390875992056,
    "content_name": "football2",
    "path": "mini_dataset/dis/4k_6M_football2.yuv"
    }
  ,
  {
    "asset_id": 2,
    "content_id": 1,
    "dmos": 72.15880079966682,
    "content_name": "football3",
    "path": "mini_dataset/dis/4k_15M_football3.yuv"
  }
  ,
  {
    "asset_id": 3,
    "content_id": 1,
    "dmos": 65.81466838859363,
    "content_name": "football3",
    "path": "mini_dataset/dis/4k_6M_football3.yuv"
  }
]
