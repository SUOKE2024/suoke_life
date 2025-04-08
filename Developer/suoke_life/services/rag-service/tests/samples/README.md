# 测试样本文件

## 简介
本目录包含RAG服务的测试样本文件，用于自动化测试和持续集成流程。

## 样本类型

### 图像样本
- `tongue.jpg` - 舌诊图像样本（用于TCM舌诊测试）
- `face.jpg` - 面诊图像样本（用于TCM面诊测试）
- `pulse.jpg` - 脉象图像样本（用于TCM脉诊测试）

### 音频样本
- `cough.wav` - 咳嗽音频样本（用于听诊测试）
- `voice.wav` - 语音样本（用于语音分析测试）

## 使用方法
使用以下命令运行多模态测试：

```bash
# 舌诊测试
go run test_multimodal.go -image samples/tongue.jpg -query "舌红苔白" -verbose

# 面诊测试
go run test_multimodal.go -image samples/face.jpg -query "面色发黄" -verbose

# 脉诊测试
go run test_multimodal.go -image samples/pulse.jpg -query "脉浮" -verbose

# 听诊测试
go run test_multimodal.go -audio samples/cough.wav -query "干咳" -verbose

# 语音分析测试
go run test_multimodal.go -audio samples/voice.wav -query "声音嘶哑" -verbose
```

## 添加新样本
向本目录添加新的测试样本时，请遵循以下规范：
1. 图像文件格式：JPG、PNG
2. 音频文件格式：WAV、MP3
3. 文件大小：不超过5MB
4. 文件命名：使用小写字母和下划线，描述样本内容

完成添加后，请更新此README文件，添加新样本的说明。 