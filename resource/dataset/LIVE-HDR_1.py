dataset_name = 'LIVE_HDR_1'
yuv_fmt = 'yuv420p'
width = 3840
height = 2160

ref_dir = '/home/joel-ludwig/Dokumente/Masterarbeit_Ludwig/vmaf/LIVE-HDR_1/ref'
dis_dir = '/home/joel-ludwig/Dokumente/Masterarbeit_Ludwig/vmaf/LIVE-HDR_1/dis'

ref_videos = [
  {
    "content_id": 0,
    "content_name": "football2",
    "path": "LIVE-HDR_1/ref/4k_ref_football2.yuv"
  }
  ,
  {
    "content_id": 1,
    "content_name": "football3",
    "path": "LIVE-HDR_1/ref/4k_ref_football3.yuv"
  }
  ,
  {
    "content_id": 2,
    "content_name": "firework",
    "path": "LIVE-HDR_1/ref/4k_ref_firework.yuv"
  }
]

dis_videos = [
    
    {
    "asset_id": 0,
    "content_id": 0,
    "dmos": 72.14721665247458,
    "content_name": "football2",
    "path": "LIVE-HDR_1/dis/4k_15M_football2.yuv"
    }
   ,
   {
    "asset_id": 1,
    "content_id": 0,
    "dmos": 67.44390875992056,
    "content_name": "football2",
    "path": "LIVE-HDR_1/dis/4k_6M_football2.yuv"
    }
    ,
    {
    "asset_id": 2,
    "content_id": 0,
    "dmos": 47.46081054384501,
    "content_name": "football2",
    "path": "LIVE-HDR_1/dis/4k_3M_football2.yuv"
    }
  ,
  {
    "asset_id": 3,
    "content_id": 1,
    "dmos": 72.15880079966682,
    "content_name": "football3",
    "path": "LIVE-HDR_1/dis/4k_15M_football3.yuv"
  }
  ,
  {
    "asset_id": 4,
    "content_id": 1,
    "dmos": 65.81466838859363,
    "content_name": "football3",
    "path": "LIVE-HDR_1/dis/4k_6M_football3.yuv"
  }
  ,
  {
    "asset_id": 5,
    "content_id": 1,
    "dmos": 47.48824564860425,
    "content_name": "football3",
    "path": "LIVE-HDR_1/dis/4k_3M_football3.yuv"
  }
  ,
  {
    "asset_id": 6,
    "content_id": 2,
    "dmos": 32.11438210914943,
    "content_name": "firework",
    "path": "LIVE-HDR_1/dis/4k_3M_firework.yuv"
  }
  ,
    {
    "asset_id": 7,
    "content_id": 2,
    "dmos": 51.96675360620037,
    "content_name": "firework",
    "path": "LIVE-HDR_1/dis/4k_6M_firework.yuv"
  }
  ,
  {
    "asset_id": 8,
    "content_id": 2,
    "dmos": 68.50827094385428,
    "content_name": "firework",
    "path": "LIVE-HDR_1/dis/4k_15M_firework.yuv"
  }
]

