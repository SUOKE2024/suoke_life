# TCM-4D 数据集格式说明

TCM-4D 数据集是针对中医四诊（望、闻、问、切）的多模态数据集，用于评估智能体对中医四诊的理解和判断能力。

## 数据组织结构

```
tcm-4d/
├── tongue/                     # 舌象图像数据
│   ├── metadata.json           # 元数据信息
│   ├── train/                  # 训练集
│   ├── val/                    # 验证集
│   └── test/                   # 测试集（用于评测）
├── face/                       # 面色视频数据
│   ├── metadata.json           # 元数据信息
│   ├── train/                  # 训练集
│   ├── val/                    # 验证集
│   └── test/                   # 测试集（用于评测）
├── pulse/                      # 脉象波形数据
│   ├── metadata.json           # 元数据信息
│   ├── train/                  # 训练集
│   ├── val/                    # 验证集
│   └── test/                   # 测试集（用于评测）
└── voice/                      # 语音问诊数据
    ├── metadata.json           # 元数据信息
    ├── train/                  # 训练集
    ├── val/                    # 验证集
    └── test/                   # 测试集（用于评测）
```

## 数据格式

### 舌象数据 (tongue)

```json
{
  "id": "tongue_001",
  "image_path": "test/tongue_001.jpg",
  "width": 512,
  "height": 512,
  "diagnosis": {
    "color": "淡红",
    "coating": "薄白",
    "moisture": "正常",
    "shape": "正常",
    "body_features": ["齿痕", "裂纹"]
  },
  "syndrome": ["脾虚湿盛", "肝郁气滞"],
  "attributes": {
    "age": 45,
    "gender": "female",
    "timestamp": "2023-07-15T10:30:00Z"
  },
  "expert_notes": "舌体略胖大有齿痕，舌质淡红，苔薄白，提示脾虚湿盛"
}
```

### 面色数据 (face)

```json
{
  "id": "face_001",
  "video_path": "test/face_001.mp4",
  "duration": 10.5,
  "resolution": "1280x720",
  "color_regions": {
    "forehead": "晦暗",
    "cheeks": "偏红",
    "nose": "正常",
    "chin": "暗淡",
    "overall": "偏黄"
  },
  "diagnosis": {
    "main_color": "偏黄",
    "luster": "晦暗",
    "complexion": "不华",
    "special_features": ["颧红", "眼袋"]
  },
  "syndrome": ["脾虚湿盛", "肝阳上亢"],
  "attributes": {
    "age": 45,
    "gender": "female",
    "timestamp": "2023-07-15T10:35:00Z"
  },
  "expert_notes": "面色偏黄晦暗，颧部偏红，提示脾虚湿盛兼有肝阳上亢"
}
```

### 脉象数据 (pulse)

```json
{
  "id": "pulse_001",
  "signal_path": "test/pulse_001.dat",
  "duration": 60.0,
  "sampling_rate": 1000,
  "channels": ["左寸", "左关", "左尺", "右寸", "右关", "右尺"],
  "diagnosis": {
    "rate": 85,
    "rhythm": "不齐",
    "depth": "沉",
    "strength": "弱",
    "width": "细",
    "length": "短",
    "overall": "沉细弱"
  },
  "pulse_type": ["沉脉", "细脉", "弱脉"],
  "syndrome": ["气血两虚", "肾阴虚"],
  "attributes": {
    "age": 45,
    "gender": "female",
    "timestamp": "2023-07-15T10:40:00Z"
  },
  "expert_notes": "脉沉细弱，尤以尺部为甚，提示气血两虚，肾阴亏虚"
}
```

### 语音问诊数据 (voice)

```json
{
  "id": "voice_001",
  "audio_path": "test/voice_001.wav",
  "duration": 120.0,
  "sampling_rate": 44100,
  "transcript_path": "test/voice_001.txt",
  "diagnosis": {
    "voice_quality": "偏弱",
    "pitch": "低沉",
    "speed": "缓慢",
    "volume": "低",
    "clarity": "清晰"
  },
  "chief_complaints": ["疲乏无力", "胃口差", "睡眠不佳", "头晕目眩"],
  "syndrome": ["脾胃虚弱", "肝郁气滞"],
  "attributes": {
    "age": 45,
    "gender": "female",
    "timestamp": "2023-07-15T10:45:00Z",
    "language": "普通话",
    "dialect": null
  },
  "expert_notes": "语声低弱，语速偏慢，主诉疲乏、食欲差、失眠，提示脾胃虚弱、肝郁气滞"
}
```

## 数据集获取

完整数据集可通过以下命令下载：

```bash
python -m internal.suokebench.setup --download-data tcm-4d
```

## 引用与来源

TCM-4D 数据集由索克生活APP团队与中医专家合作收集与标注，用于研究中医四诊数据的智能分析。 