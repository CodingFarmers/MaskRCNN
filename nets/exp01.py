# model settings
pretrained = 'https://github.com/SwinTransformer/storage/releases/download/v1.0.0/swin_tiny_patch4_window7_224.pth'
model = dict(type='MaskRCNN',
             backbone=dict(type='SwinTransformer',
                           embed_dims=96,
                           depths=[2, 2, 6, 2],
                           num_heads=[3, 6, 12, 24],
                           init_cfg=dict(type='Pretrained', checkpoint=pretrained)),
             neck=dict(type='FPN',
                       in_channels=[96, 192, 384, 768],
                       out_channels=256, num_outs=5),
             rpn_head=dict(type='RPNHead',
                           in_channels=256,
                           feat_channels=256,
                           anchor_generator=dict(type='AnchorGenerator',
                                                 scales=[8],
                                                 ratios=[0.5, 1.0, 2.0],
                                                 strides=[4, 8, 16, 32, 64]),
                           bbox_coder=dict(type='DeltaXYWHBBoxCoder',
                                           target_means=[.0, .0, .0, .0],
                                           target_stds=[1.0, 1.0, 1.0, 1.0]),
                           loss_cls=dict(type='CrossEntropyLoss',
                                         use_sigmoid=True,
                                         loss_weight=1.0),
                           loss_bbox=dict(type='L1Loss', loss_weight=1.0)),
             roi_head=dict(type='StandardRoIHead',
                           bbox_roi_extractor=dict(type='SingleRoIExtractor',
                                                   roi_layer=dict(type='RoIAlign',
                                                                  output_size=7,
                                                                  sampling_ratio=0),
                                                   out_channels=256,
                                                   featmap_strides=[4, 8, 16, 32]),
                           bbox_head=dict(type='Shared2FCBBoxHead',
                                          in_channels=256,
                                          fc_out_channels=1024,
                                          roi_feat_size=7,
                                          num_classes=80,
                                          bbox_coder=dict(type='DeltaXYWHBBoxCoder',
                                                          target_means=[0., 0., 0., 0.],
                                                          target_stds=[0.1, 0.1, 0.2, 0.2]),
                                          reg_class_agnostic=False,
                                          loss_cls=dict(type='CrossEntropyLoss',
                                                        use_sigmoid=False,
                                                        loss_weight=1.0),
                                          loss_bbox=dict(type='L1Loss', loss_weight=1.0)),
                           mask_roi_extractor=dict(type='SingleRoIExtractor',
                                                   roi_layer=dict(type='RoIAlign',
                                                                  output_size=14,
                                                                  sampling_ratio=0),
                                                   out_channels=256,
                                                   featmap_strides=[4, 8, 16, 32]),
                           mask_head=dict(type='FCNMaskHead',
                                          num_convs=4,
                                          in_channels=256,
                                          conv_out_channels=256,
                                          num_classes=80,
                                          loss_mask=dict(type='CrossEntropyLoss',
                                                         use_mask=True,
                                                         loss_weight=1.0))),
             # model training and testing settings
             train_cfg=dict(rpn=dict(assigner=dict(type='MaxIoUAssigner',
                                                   pos_iou_thr=0.7,
                                                   neg_iou_thr=0.3,
                                                   min_pos_iou=0.3,
                                                   match_low_quality=True,
                                                   ignore_iof_thr=-1),
                                     sampler=dict(type='RandomSampler',
                                                  num=256,
                                                  pos_fraction=0.5,
                                                  neg_pos_ub=-1,
                                                  add_gt_as_proposals=False),
                                     allowed_border=-1,
                                     pos_weight=-1,
                                     debug=False),
                            rpn_proposal=dict(nms_pre=2000,
                                              max_per_img=1000,
                                              nms=dict(type='nms', iou_threshold=0.7),
                                              min_bbox_size=0),
                            rcnn=dict(assigner=dict(type='MaxIoUAssigner',
                                                    pos_iou_thr=0.5,
                                                    neg_iou_thr=0.5,
                                                    min_pos_iou=0.5,
                                                    match_low_quality=True,
                                                    ignore_iof_thr=-1),
                                      sampler=dict(type='RandomSampler',
                                                   num=512,
                                                   pos_fraction=0.25,
                                                   neg_pos_ub=-1,
                                                   add_gt_as_proposals=True),
                                      mask_size=28,
                                      pos_weight=-1,
                                      debug=False)),
             test_cfg=dict(rpn=dict(nms_pre=1000,
                                    max_per_img=1000,
                                    nms=dict(type='nms', iou_threshold=0.7),
                                    min_bbox_size=0),
                           rcnn=dict(score_thr=0.05,
                                     nms=dict(type='nms', iou_threshold=0.5),
                                     max_per_img=100,
                                     mask_thr_binary=0.5)))
# dataset settings
img_scale = (1280, 1280)
dataset_type = 'CocoDataset'
data_root = '../Dataset/COCO/'
samples_per_gpu = 4
workers_per_gpu = 4
img_norm_cfg = dict(mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
train_pipeline = [dict(type='LoadAnnotations', with_bbox=True, with_mask=True),
                  dict(type='RandomHSV'),
                  dict(type='Resize', img_scale=img_scale, keep_ratio=True),
                  dict(type='RandomFlip', flip_ratio=0.5),
                  dict(type='Normalize', **img_norm_cfg),
                  dict(type='Pad', pad_to_square=True),
                  dict(type='DefaultFormatBundle'),
                  dict(type='Collect', keys=['img', 'gt_bboxes', 'gt_labels', 'gt_masks'])]
test_pipeline = [dict(type='LoadImageFromFile'),
                 dict(type='MultiScaleFlipAug',
                      img_scale=img_scale,
                      flip=False,
                      transforms=[dict(type='Resize', keep_ratio=True),
                                  dict(type='RandomFlip'),
                                  dict(type='Normalize', **img_norm_cfg),
                                  dict(type='Pad', pad_to_square=True),
                                  dict(type='ImageToTensor', keys=['img']),
                                  dict(type='Collect', keys=['img'])])]
data = dict(samples_per_gpu=samples_per_gpu,
            workers_per_gpu=workers_per_gpu,
            train=dict(type='MOSAICDataset',
                       dataset=dict(type=dataset_type,
                                    ann_file=data_root + 'annotation/train2017.json',
                                    img_prefix=data_root + 'images/train2017/',
                                    pipeline=[dict(type='LoadImageFromFile')]),
                       image_size=img_scale,
                       pipeline=train_pipeline),
            val=dict(type=dataset_type,
                     ann_file=data_root + 'annotation/val2017.json',
                     img_prefix=data_root + 'images/val2017/',
                     pipeline=test_pipeline),
            test=dict(type=dataset_type,
                      ann_file=data_root + 'annotation/test2017.json',
                      img_prefix=data_root + 'images/test2017/',
                      pipeline=test_pipeline))
evaluation = dict(interval=1, metric=['bbox', 'segm'])
optimizer = dict(type='AdamW', lr=0.0001,
                 betas=(0.9, 0.999), weight_decay=0.05,
                 paramwise_cfg=dict(custom_keys={'absolute_pos_embed': dict(decay_mult=0.),
                                                 'relative_position_bias_table': dict(decay_mult=0.),
                                                 'norm': dict(decay_mult=0.)}))
optimizer_config = dict(grad_clip=None)
fp16 = dict(loss_scale=dict(init_scale=512))
lr_config = dict(policy='step',
                 warmup='linear',
                 warmup_iters=1000,
                 warmup_ratio=0.001,
                 step=[27, 33])
runner = dict(type='EpochBasedRunner', max_epochs=36)
checkpoint_config = dict(interval=36)
log_config = dict(interval=100, hooks=[dict(type='TextLoggerHook')])
custom_hooks = [dict(type='NumClassCheckHook')]
dist_params = dict(backend='nccl')
log_level = 'INFO'
load_from = None
resume_from = None
workflow = [('train', 1)]
