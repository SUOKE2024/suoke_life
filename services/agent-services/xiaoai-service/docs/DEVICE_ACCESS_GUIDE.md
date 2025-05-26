# 小艾智能体设备访问指南

## 📱 概述

小艾智能体现在具备了完整的设备访问能力，可以使用摄像头、麦克风、屏幕等设备进行多模态交互。本指南将教您如何使用这些功能。

## 🎯 支持的设备

### 📷 摄像头
- **功能**: 拍摄照片、视频流
- **用途**: 舌象分析、面部诊断、环境识别
- **格式**: JPEG、PNG
- **分辨率**: 640x480（可配置）

### 🎤 麦克风
- **功能**: 录音、语音识别
- **用途**: 语音问诊、声音分析、语音交互
- **格式**: WAV、MP3
- **采样率**: 16kHz（可配置）

### 🖥️ 屏幕
- **功能**: 屏幕截图、屏幕阅读
- **用途**: 界面分析、无障碍辅助
- **格式**: PNG、JPEG
- **区域**: 全屏或指定区域

## 🚀 快速开始

### 1. 启动HTTP API服务器

```bash
cd services/agent-services/xiaoai-service
python cmd/server/http_server.py --host 0.0.0.0 --port 8000
```

### 2. 检查设备状态

```bash
curl http://localhost:8000/api/v1/device/status
```

### 3. 测试所有设备

```bash
curl -X POST http://localhost:8000/api/v1/device/test
```

## 📋 API 接口

### 设备状态检查

```http
GET /api/v1/device/status
```

**响应示例:**
```json
{
  "success": true,
  "data": {
    "camera": {
      "available": true,
      "active": true
    },
    "microphone": {
      "available": true,
      "recording": false
    },
    "screen": {
      "available": true,
      "info": {
        "width": 1920,
        "height": 1080
      }
    },
    "initialized": true
  }
}
```

### 摄像头操作

#### 拍摄照片
```http
POST /api/v1/device/camera
Content-Type: application/json

{
  "user_id": "user123",
  "action": "capture",
  "session_id": "session456"
}
```

**响应示例:**
```json
{
  "success": true,
  "data": {
    "image_base64": "data:image/jpeg;base64,/9j/4AAQ...",
    "width": 640,
    "height": 480,
    "format": "jpeg",
    "size_bytes": 45678,
    "timestamp": 1703123456
  },
  "accessibility": {
    "scene_description": "这是一张舌象图像，舌体淡红，舌苔薄白",
    "medical_features": [
      {
        "type": "tongue_color",
        "description": "淡红色",
        "confidence": 0.9
      }
    ],
    "audio_guidance": "检测到舌象，建议保持舌头平伸"
  }
}
```

### 麦克风操作

#### 录制音频
```http
POST /api/v1/device/microphone
Content-Type: application/json

{
  "user_id": "user123",
  "action": "record",
  "duration": 5.0,
  "session_id": "session456"
}
```

**响应示例:**
```json
{
  "success": true,
  "data": {
    "audio_base64": "data:audio/wav;base64,UklGRnoG...",
    "duration": 5.0,
    "sample_rate": 16000,
    "channels": 1,
    "format": "wav",
    "size_bytes": 160000,
    "timestamp": 1703123456
  },
  "accessibility": {
    "recognized_text": "我最近感觉有点咳嗽",
    "response_text": "根据您的描述，咳嗽可能与肺热有关...",
    "response_audio": "data:audio/wav;base64,UklGRnoG...",
    "confidence": 0.95
  }
}
```

### 屏幕操作

#### 截取屏幕
```http
POST /api/v1/device/screen
Content-Type: application/json

{
  "user_id": "user123",
  "action": "capture",
  "region": [100, 100, 800, 600],
  "session_id": "session456"
}
```

**响应示例:**
```json
{
  "success": true,
  "data": {
    "image_base64": "data:image/png;base64,iVBORw0KGgo...",
    "width": 800,
    "height": 600,
    "format": "png",
    "region": [100, 100, 800, 600],
    "size_bytes": 234567,
    "timestamp": 1703123456
  },
  "accessibility": {
    "screen_description": "屏幕显示健康管理界面，包含用户信息和健康数据",
    "ui_elements": [
      {
        "type": "button",
        "text": "开始检测",
        "position": [200, 300]
      }
    ],
    "audio_description": "当前界面显示健康管理功能"
  }
}
```

### 多模态输入

#### 处理多种输入类型
```http
POST /api/v1/device/multimodal
Content-Type: multipart/form-data

user_id: user123
session_id: session456
input_type: voice
audio_file: [音频文件]
settings: {"language": "zh-CN"}
```

## 🔧 配置说明

### 设备配置文件: `config/devices.yaml`

```yaml
devices:
  # 摄像头配置
  camera_enabled: true
  camera_index: 0
  camera_width: 640
  camera_height: 480
  camera_fps: 30
  
  # 麦克风配置
  microphone_enabled: true
  sample_rate: 16000
  channels: 1
  chunk_size: 1024
  audio_format: 16
  
  # 屏幕配置
  screen_enabled: true
  screen_region: null
  
  # 安全配置
  max_recording_duration: 30
  max_image_size: 1048576
```

### 无障碍配置文件: `config/accessibility.yaml`

```yaml
accessibility:
  enabled: true
  service_url: "http://localhost:50051"
  features:
    voice_assistance: true
    image_assistance: true
    screen_reading: true
    content_generation: true
```

## 🛠️ 依赖安装

### 必需的Python包

```bash
# 摄像头支持
pip install opencv-python

# 麦克风支持
pip install pyaudio

# 屏幕截图支持
pip install pyautogui Pillow

# HTTP API支持
pip install fastapi uvicorn

# 系统监控
pip install psutil
```

### 系统权限

#### macOS
```bash
# 摄像头权限
# 系统偏好设置 > 安全性与隐私 > 隐私 > 摄像头

# 麦克风权限
# 系统偏好设置 > 安全性与隐私 > 隐私 > 麦克风

# 屏幕录制权限
# 系统偏好设置 > 安全性与隐私 > 隐私 > 屏幕录制
```

#### Linux
```bash
# 确保用户在audio和video组中
sudo usermod -a -G audio,video $USER

# 检查设备权限
ls -l /dev/video* /dev/audio*
```

## 🎨 使用示例

### Python客户端示例

```python
import requests
import base64
import json

# 设备状态检查
def check_device_status():
    response = requests.get("http://localhost:8000/api/v1/device/status")
    return response.json()

# 拍摄照片
def capture_photo(user_id, session_id=None):
    data = {
        "user_id": user_id,
        "action": "capture",
        "session_id": session_id
    }
    response = requests.post("http://localhost:8000/api/v1/device/camera", json=data)
    return response.json()

# 录制音频
def record_audio(user_id, duration=5.0, session_id=None):
    data = {
        "user_id": user_id,
        "action": "record",
        "duration": duration,
        "session_id": session_id
    }
    response = requests.post("http://localhost:8000/api/v1/device/microphone", json=data)
    return response.json()

# 截取屏幕
def capture_screen(user_id, region=None, session_id=None):
    data = {
        "user_id": user_id,
        "action": "capture",
        "region": region,
        "session_id": session_id
    }
    response = requests.post("http://localhost:8000/api/v1/device/screen", json=data)
    return response.json()

# 使用示例
if __name__ == "__main__":
    user_id = "test_user"
    
    # 检查设备状态
    status = check_device_status()
    print("设备状态:", status)
    
    # 拍摄照片
    if status["data"]["camera"]["available"]:
        photo = capture_photo(user_id)
        print("拍摄结果:", photo["success"])
    
    # 录制音频
    if status["data"]["microphone"]["available"]:
        audio = record_audio(user_id, duration=3.0)
        print("录音结果:", audio["success"])
    
    # 截取屏幕
    if status["data"]["screen"]["available"]:
        screen = capture_screen(user_id)
        print("截图结果:", screen["success"])
```

### JavaScript客户端示例

```javascript
// 设备状态检查
async function checkDeviceStatus() {
    const response = await fetch('http://localhost:8000/api/v1/device/status');
    return await response.json();
}

// 拍摄照片
async function capturePhoto(userId, sessionId = null) {
    const data = {
        user_id: userId,
        action: 'capture',
        session_id: sessionId
    };
    
    const response = await fetch('http://localhost:8000/api/v1/device/camera', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    
    return await response.json();
}

// 多模态文件上传
async function uploadAudioFile(userId, audioFile, sessionId = null) {
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('session_id', sessionId || '');
    formData.append('input_type', 'voice');
    formData.append('audio_file', audioFile);
    formData.append('settings', JSON.stringify({language: 'zh-CN'}));
    
    const response = await fetch('http://localhost:8000/api/v1/device/multimodal', {
        method: 'POST',
        body: formData
    });
    
    return await response.json();
}

// 使用示例
async function main() {
    const userId = 'test_user';
    
    // 检查设备状态
    const status = await checkDeviceStatus();
    console.log('设备状态:', status);
    
    // 拍摄照片
    if (status.data.camera.available) {
        const photo = await capturePhoto(userId);
        console.log('拍摄结果:', photo.success);
        
        if (photo.success) {
            // 显示图片
            const img = document.createElement('img');
            img.src = photo.data.image_base64;
            document.body.appendChild(img);
        }
    }
}
```

## 🔍 故障排除

### 常见问题

1. **摄像头无法访问**
   - 检查摄像头是否被其他应用占用
   - 确认系统权限设置
   - 尝试更改摄像头索引

2. **麦克风录音失败**
   - 检查音频设备驱动
   - 确认麦克风权限
   - 调整采样率设置

3. **屏幕截图权限被拒绝**
   - 在系统设置中授予屏幕录制权限
   - 重启应用程序

4. **无障碍服务不可用**
   - 确认无障碍服务正在运行
   - 检查服务地址配置
   - 查看服务日志

### 调试命令

```bash
# 检查设备能力
curl http://localhost:8000/api/v1/device/capabilities

# 测试所有设备
curl -X POST http://localhost:8000/api/v1/device/test

# 查看详细健康状态
curl http://localhost:8000/api/v1/health/detailed

# 查看服务状态
curl http://localhost:8000/api/v1/status
```

## 🔐 安全注意事项

1. **权限控制**: 确保只有授权用户可以访问设备
2. **数据加密**: 敏感音频和图像数据应加密传输
3. **时长限制**: 设置合理的录音和录像时长限制
4. **存储清理**: 及时清理临时文件和缓存数据
5. **网络安全**: 在生产环境中使用HTTPS

## 📚 更多资源

- [小艾智能体文档](../README.md)
- [无障碍服务集成指南](../ACCESSIBILITY_INTEGRATION_SUMMARY.md)
- [API文档](http://localhost:8000/docs)
- [配置参考](../config/)

---

**注意**: 使用设备功能前，请确保已获得用户的明确授权，并遵守相关隐私法规。 