# 闻诊服务 API 使用文档

## 概述

闻诊服务是索克生活 APP 的核心微服务之一，基于中医"闻诊"原理，提供语音和声音特征的分析功能。本文档详细介绍了闻诊服务的 API 使用方法、参数说明和响应格式。

## 服务地址

- **生产环境**: `listen-service.suoke.internal:50052`
- **测试环境**: `listen-service.test.suoke.internal:50052`
- **开发环境**: `localhost:50052`

## API 列表

闻诊服务提供以下 gRPC API：

1. [AnalyzeVoice](#analyzevoice) - 分析语音特征
2. [AnalyzeSound](#analyzesound) - 分析非语言声音
3. [AnalyzeEmotion](#analyzeemotion) - 分析情绪
4. [DetectDialect](#detectdialect) - 检测方言
5. [TranscribeAudio](#transcribeaudio) - 语音转写
6. [BatchAnalyze](#batchanalyze) - 批量分析
7. [HealthCheck](#healthcheck) - 健康检查

## API 详细说明

### AnalyzeVoice

分析语音特征，提取与中医诊断相关的语音特性。

#### 请求参数

```protobuf
message VoiceAnalysisRequest {
  string user_id = 1;                // 用户ID（必填）
  string session_id = 2;             // 会话ID（必填）
  bytes audio_data = 3;              // 音频数据（必填，二进制格式）
  string audio_format = 4;           // 音频格式（必填，如"wav", "mp3"）
  int32 sample_rate = 5;             // 采样率（必填，常见如 16000, 44100 Hz）
  int32 channels = 6;                // 通道数（必填，常见为 1 或 2）
  map<string, string> metadata = 7;  // 元数据（可选）
  bool apply_preprocessing = 8;      // 是否应用预处理（可选，默认 true）
}
```

#### 响应

```protobuf
message VoiceAnalysisResponse {
  string analysis_id = 1;             // 分析ID
  float speech_rate = 2;              // 语速(单位：字/分钟)
  float pitch_avg = 3;                // 平均音调(Hz)
  float pitch_range = 4;              // 音调范围(Hz)
  float volume_avg = 5;               // 平均音量(dB)
  float voice_stability = 6;          // 声音稳定性得分(0-1)
  float breathiness = 7;              // 气息音特征得分(0-1)
  repeated VoiceFeature features = 8; // 详细特征列表
  map<string, float> tcm_relevance = 9; // 中医相关性得分(特征-分数)
  map<string, string> metadata = 10;   // 元数据
  string diagnostic_hint = 11;        // 诊断提示
  float confidence = 12;              // 置信度
  int64 timestamp = 13;               // 时间戳
}
```

#### 示例

```python
import grpc
from api.grpc import listen_service_pb2 as pb2
from api.grpc import listen_service_pb2_grpc as pb2_grpc

# 创建gRPC通道
channel = grpc.insecure_channel('localhost:50052')
stub = pb2_grpc.ListenServiceStub(channel)

# 读取音频文件
with open('voice_sample.wav', 'rb') as f:
    audio_data = f.read()

# 创建请求
request = pb2.VoiceAnalysisRequest(
    user_id="user123",
    session_id="session456",
    audio_data=audio_data,
    audio_format="wav",
    sample_rate=16000,
    channels=1,
    apply_preprocessing=True
)

# 发送请求
response = stub.AnalyzeVoice(request)

# 处理响应
print(f"分析ID: {response.analysis_id}")
print(f"语速: {response.speech_rate} 字/分钟")
print(f"平均音调: {response.pitch_avg} Hz")
print(f"气息音特征: {response.breathiness}")
print(f"中医相关性: {response.tcm_relevance}")
print(f"诊断提示: {response.diagnostic_hint}")
```

### AnalyzeSound

分析非语言声音特征，如咳嗽声、呼吸声等。

#### 请求参数

```protobuf
message SoundAnalysisRequest {
  string user_id = 1;                // 用户ID（必填）
  string session_id = 2;             // 会话ID（必填）
  bytes audio_data = 3;              // 音频数据（必填，二进制格式）
  string audio_format = 4;           // 音频格式（必填，如"wav", "mp3"）
  int32 sample_rate = 5;             // 采样率（必填，常见如 16000, 44100 Hz）
  SoundType sound_type = 6;          // 声音类型（必填）
  map<string, string> metadata = 7;  // 元数据（可选）
  bool apply_preprocessing = 8;      // 是否应用预处理（可选，默认 true）
}

enum SoundType {
  SOUND_UNKNOWN = 0;  // 未知
  COUGH = 1;          // 咳嗽
  BREATHING = 2;      // 呼吸
  SNORING = 3;        // 鼾声
  HEART_SOUND = 4;    // 心音
  OTHER = 5;          // 其他
}
```

#### 响应

```protobuf
message SoundAnalysisResponse {
  string analysis_id = 1;                // 分析ID
  SoundType sound_type = 2;              // 识别的声音类型
  float duration = 3;                    // 持续时间(秒)
  float amplitude = 4;                   // 振幅
  float regularity = 5;                  // 规律性得分(0-1)
  float moisture = 6;                    // 湿度特征(干-湿,0-1)
  repeated SoundPattern patterns = 7;    // 声音模式
  map<string, float> tcm_relevance = 8;  // 中医相关性得分(特征-分数)
  map<string, string> metadata = 9;      // 元数据
  string diagnostic_hint = 10;           // 诊断提示
  float confidence = 11;                 // 置信度
  int64 timestamp = 12;                  // 时间戳
}
```

#### 示例

```python
# 读取音频文件
with open('cough_sample.wav', 'rb') as f:
    audio_data = f.read()

# 创建请求
request = pb2.SoundAnalysisRequest(
    user_id="user123",
    session_id="session456",
    audio_data=audio_data,
    audio_format="wav",
    sample_rate=16000,
    sound_type=pb2.SoundType.COUGH,
    apply_preprocessing=True
)

# 发送请求
response = stub.AnalyzeSound(request)

# 处理响应
print(f"分析ID: {response.analysis_id}")
print(f"声音类型: {response.sound_type}")
print(f"持续时间: {response.duration} 秒")
print(f"规律性: {response.regularity}")
print(f"湿度特征: {response.moisture}")
print(f"中医相关性: {response.tcm_relevance}")
print(f"诊断提示: {response.diagnostic_hint}")
```

### AnalyzeEmotion

分析语音中的情绪特征，支持中医五志（喜、怒、忧、思、恐）分析。

#### 请求参数

```protobuf
message EmotionAnalysisRequest {
  string user_id = 1;               // 用户ID（必填）
  string session_id = 2;            // 会话ID（必填）
  bytes audio_data = 3;             // 音频数据（必填，二进制格式）
  string audio_format = 4;          // 音频格式（必填，如"wav", "mp3"）
  int32 sample_rate = 5;            // 采样率（必填，常见如 16000, 44100 Hz）
  string text_transcript = 6;       // 可选文本记录（可选）
  map<string, string> metadata = 7; // 元数据（可选）
}
```

#### 响应

```protobuf
message EmotionAnalysisResponse {
  string analysis_id = 1;                // 分析ID
  map<string, float> emotions = 2;       // 情绪及强度(0-1)
  float emotional_stability = 3;         // 情绪稳定性(0-1)
  map<string, float> tcm_emotions = 4;   // 中医五志(喜、怒、忧、思、恐)得分
  EmotionTrend trend = 5;                // 情绪变化趋势
  map<string, string> metadata = 6;      // 元数据
  string diagnostic_hint = 7;            // 诊断提示
  float confidence = 8;                  // 置信度
  int64 timestamp = 9;                   // 时间戳
}

enum EmotionTrend {
  TREND_UNKNOWN = 0;   // 未知
  STABLE = 1;          // 稳定
  RISING = 2;          // 上升
  FALLING = 3;         // 下降
  FLUCTUATING = 4;     // 波动
}
```

#### 示例

```python
# 读取音频文件
with open('emotion_sample.wav', 'rb') as f:
    audio_data = f.read()

# 创建请求
request = pb2.EmotionAnalysisRequest(
    user_id="user123",
    session_id="session456",
    audio_data=audio_data,
    audio_format="wav",
    sample_rate=16000,
    text_transcript="我今天感觉很不错" # 可选
)

# 发送请求
response = stub.AnalyzeEmotion(request)

# 处理响应
print(f"分析ID: {response.analysis_id}")
print(f"情绪: {response.emotions}")
print(f"情绪稳定性: {response.emotional_stability}")
print(f"中医五志得分: {response.tcm_emotions}")
print(f"情绪变化趋势: {response.trend}")
print(f"诊断提示: {response.diagnostic_hint}")
```

### DetectDialect

检测语音中的方言，识别用户使用的方言类型及地区。

#### 请求参数

```protobuf
message DialectDetectionRequest {
  string user_id = 1;               // 用户ID（必填）
  string session_id = 2;            // 会话ID（必填）
  bytes audio_data = 3;             // 音频数据（必填，二进制格式）
  string audio_format = 4;          // 音频格式（必填，如"wav", "mp3"）
  int32 sample_rate = 5;            // 采样率（必填，常见如 16000, 44100 Hz）
  string text_transcript = 6;       // 可选文本记录（可选）
  map<string, string> metadata = 7; // 元数据（可选）
}
```

#### 响应

```protobuf
message DialectDetectionResponse {
  string detection_id = 1;                // 检测ID
  string primary_dialect = 2;             // 主要方言
  string primary_dialect_region = 3;      // 主要方言地区
  float primary_dialect_confidence = 4;   // 主要方言置信度(0-1)
  repeated DialectCandidate candidates = 5; // 其他方言候选
  map<string, string> metadata = 6;       // 元数据
  int64 timestamp = 7;                    // 时间戳
}

message DialectCandidate {
  string dialect = 1;         // 方言
  string region = 2;          // 地区
  float confidence = 3;       // 置信度(0-1)
}
```

#### 示例

```python
# 读取音频文件
with open('dialect_sample.wav', 'rb') as f:
    audio_data = f.read()

# 创建请求
request = pb2.DialectDetectionRequest(
    user_id="user123",
    session_id="session456",
    audio_data=audio_data,
    audio_format="wav",
    sample_rate=16000
)

# 发送请求
response = stub.DetectDialect(request)

# 处理响应
print(f"检测ID: {response.detection_id}")
print(f"主要方言: {response.primary_dialect}")
print(f"方言地区: {response.primary_dialect_region}")
print(f"置信度: {response.primary_dialect_confidence}")

# 显示候选方言
for candidate in response.candidates:
    print(f"候选方言: {candidate.dialect}, 地区: {candidate.region}, 置信度: {candidate.confidence}")
```

### TranscribeAudio

将语音转换为文本，支持多种语言和方言。

#### 请求参数

```protobuf
message TranscriptionRequest {
  string user_id = 1;               // 用户ID（必填）
  string session_id = 2;            // 会话ID（必填）
  bytes audio_data = 3;             // 音频数据（必填，二进制格式）
  string audio_format = 4;          // 音频格式（必填，如"wav", "mp3"）
  int32 sample_rate = 5;            // 采样率（必填，常见如 16000, 44100 Hz）
  string language = 6;              // 语言代码（可选，如"zh-CN"，默认为中文）
  bool detect_dialect = 7;          // 是否检测方言（可选，默认为false）
  map<string, string> metadata = 8; // 元数据（可选）
}
```

#### 响应

```protobuf
message TranscriptionResponse {
  string transcription_id = 1;       // 转写ID
  string text = 2;                   // 转写文本
  string language = 3;               // 识别出的语言
  string dialect = 4;                // 识别出的方言(如果请求)
  float confidence = 5;              // 置信度(0-1)
  repeated TranscriptionSegment segments = 6; // 分段转写结果
  map<string, string> metadata = 7;  // 元数据
  int64 timestamp = 8;               // 时间戳
}

message TranscriptionSegment {
  string text = 1;           // 分段文本
  float start_time = 2;      // 开始时间(秒)
  float end_time = 3;        // 结束时间(秒)
  float confidence = 4;      // 置信度(0-1)
}
```

#### 示例

```python
# 读取音频文件
with open('speech_sample.wav', 'rb') as f:
    audio_data = f.read()

# 创建请求
request = pb2.TranscriptionRequest(
    user_id="user123",
    session_id="session456",
    audio_data=audio_data,
    audio_format="wav",
    sample_rate=16000,
    language="zh-CN",
    detect_dialect=True
)

# 发送请求
response = stub.TranscribeAudio(request)

# 处理响应
print(f"转写ID: {response.transcription_id}")
print(f"转写文本: {response.text}")
print(f"识别语言: {response.language}")
print(f"识别方言: {response.dialect}")
print(f"置信度: {response.confidence}")

# 显示分段结果
for segment in response.segments:
    print(f"[{segment.start_time:.2f} - {segment.end_time:.2f}] {segment.text}")
```

### BatchAnalyze

对一段音频进行批量分析，包含多种分析类型，提高效率。

#### 请求参数

```protobuf
message BatchAnalysisRequest {
  string user_id = 1;               // 用户ID（必填）
  string session_id = 2;            // 会话ID（必填）
  bytes audio_data = 3;             // 音频数据（必填，二进制格式）
  string audio_format = 4;          // 音频格式（必填，如"wav", "mp3"）
  int32 sample_rate = 5;            // 采样率（必填，常见如 16000, 44100 Hz）
  repeated string analysis_types = 6; // 请求的分析类型列表（必填，如["voice", "emotion", "transcription"]）
  map<string, string> metadata = 7;  // 元数据（可选）
}
```

#### 响应

```protobuf
message BatchAnalysisResponse {
  string batch_id = 1;                       // 批量分析ID
  VoiceAnalysisResponse voice_analysis = 2;  // 语音分析结果
  SoundAnalysisResponse sound_analysis = 3;  // 声音分析结果
  DialectDetectionResponse dialect = 4;      // 方言检测结果
  EmotionAnalysisResponse emotion = 5;       // 情绪分析结果
  TranscriptionResponse transcription = 6;   // 转写结果
  ListenDiagnosisResult diagnosis = 7;       // 综合诊断结果
  map<string, string> metadata = 8;          // 元数据
  int64 timestamp = 9;                       // 时间戳
}

message ListenDiagnosisResult {
  string diagnosis_id = 1;                      // 诊断ID
  repeated DiagnosticFeature features = 2;      // 诊断特征
  map<string, float> tcm_patterns = 3;          // 中医证型相关性得分
  map<string, float> constitution_relevance = 4; // 体质相关性得分
  string analysis_summary = 5;                  // 分析总结
  float confidence = 6;                         // 置信度
  int64 timestamp = 7;                          // 时间戳
}
```

#### 示例

```python
# 读取音频文件
with open('audio_sample.wav', 'rb') as f:
    audio_data = f.read()

# 创建请求
request = pb2.BatchAnalysisRequest(
    user_id="user123",
    session_id="session456",
    audio_data=audio_data,
    audio_format="wav",
    sample_rate=16000,
    analysis_types=["voice", "emotion", "transcription"]
)

# 发送请求
response = stub.BatchAnalyze(request)

# 处理响应
print(f"批量分析ID: {response.batch_id}")

# 处理语音分析结果
if response.HasField("voice_analysis"):
    print(f"语音分析ID: {response.voice_analysis.analysis_id}")
    print(f"语速: {response.voice_analysis.speech_rate} 字/分钟")

# 处理情绪分析结果
if response.HasField("emotion"):
    print(f"情绪分析ID: {response.emotion.analysis_id}")
    print(f"情绪: {response.emotion.emotions}")

# 处理转写结果
if response.HasField("transcription"):
    print(f"转写ID: {response.transcription.transcription_id}")
    print(f"转写文本: {response.transcription.text}")

# 处理综合诊断结果
if response.HasField("diagnosis"):
    print(f"诊断ID: {response.diagnosis.diagnosis_id}")
    print(f"诊断总结: {response.diagnosis.analysis_summary}")
    print(f"中医证型: {response.diagnosis.tcm_patterns}")
```

### HealthCheck

检查服务健康状态，用于监控和服务发现。

#### 请求参数

```protobuf
message HealthCheckRequest {
  bool include_details = 1;  // 是否包含详细信息（可选，默认为false）
}
```

#### 响应

```protobuf
message HealthCheckResponse {
  enum Status {
    UNKNOWN = 0;
    SERVING = 1;
    NOT_SERVING = 2;
  }
  Status status = 1;                  // 服务状态
  map<string, string> details = 2;    // 详细状态信息（如果请求）
}
```

#### 示例

```python
# 创建请求
request = pb2.HealthCheckRequest(include_details=True)

# 发送请求
response = stub.HealthCheck(request)

# 处理响应
status_names = {
    0: "UNKNOWN",
    1: "SERVING",
    2: "NOT_SERVING"
}
print(f"服务状态: {status_names.get(response.status, '未知')}")

# 显示详细信息
if response.details:
    print("详细信息:")
    for key, value in response.details.items():
        print(f"  {key}: {value}")
```

## 最佳实践

### 音频格式建议

- 推荐使用 **WAV** 格式（PCM编码）
- 采样率：16kHz（语音分析和转写）或 44.1kHz（音乐或精细声音分析）
- 位深度：16位
- 通道：单声道（1通道）

### 错误处理

服务使用标准gRPC错误码：

| 错误码 | 描述 | 常见原因 |
|-------|------|---------|
| INVALID_ARGUMENT | 参数无效 | 缺少必要参数或参数格式错误 |
| UNAUTHENTICATED | 未认证 | 身份验证失败 |
| PERMISSION_DENIED | 权限不足 | 无权访问请求的资源 |
| RESOURCE_EXHAUSTED | 资源耗尽 | 超出请求配额或速率限制 |
| UNAVAILABLE | 服务不可用 | 服务暂时不可用或过载 |
| INTERNAL | 内部错误 | 服务内部错误 |

建议在客户端实现以下错误处理逻辑：

```python
try:
    response = stub.AnalyzeVoice(request)
    # 处理正常响应
except grpc.RpcError as e:
    status_code = e.code()
    if status_code == grpc.StatusCode.INVALID_ARGUMENT:
        print(f"参数错误: {e.details()}")
        # 修复参数问题
    elif status_code == grpc.StatusCode.RESOURCE_EXHAUSTED:
        print(f"资源耗尽: {e.details()}")
        # 实现退避策略
    elif status_code == grpc.StatusCode.UNAVAILABLE:
        print(f"服务不可用: {e.details()}")
        # 尝试重试
    else:
        print(f"错误: {status_code}, {e.details()}")
        # 通用错误处理
```

### 性能优化

1. 对于较大的音频文件，请使用流式处理：
   - 当前API不支持流式处理，请将大于10MB的音频分割为多个较小的片段
   - 后续版本将支持流式API

2. 批量处理：
   - 尽可能使用`BatchAnalyze`API，而不是单独调用多个API
   - 这可以减少网络通信并提高服务端处理效率

3. 适当降低音频质量：
   - 对于语音分析，16kHz采样率通常足够
   - 压缩音频可以减少传输时间

### 安全最佳实践

1. 使用TLS/SSL：
   - 生产环境始终使用加密连接
   - 示例：`channel = grpc.secure_channel('listen-service.suoke.internal:50052', credentials)`

2. 身份验证：
   - 使用令牌身份验证
   - 将令牌放入元数据：`metadata = [('authorization', f'Bearer {token}')]`
   - 使用带元数据的调用：`response = stub.AnalyzeVoice(request, metadata=metadata)`

3. 敏感信息：
   - 避免在音频元数据中包含任何敏感个人信息

## 故障排除

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| 连接被拒绝 | 服务器地址或端口错误 | 验证服务器地址和端口 |
| 截止时间超过 | 请求超时 | 增加超时时间或检查网络连接 |
| 音频分析结果不准确 | 音频质量低或背景噪音大 | 使用更高质量的音频或启用预处理 |
| RESOURCE_EXHAUSTED 错误 | 超出了请求配额 | 实现退避策略或联系管理员增加配额 |

## 联系与支持

如果遇到问题或需要额外支持，请联系：

- 技术支持邮箱：tech-support@suokelife.com
- 服务负责人：listen-service-team@suokelife.com
- 问题报告：在JIRA中创建问题，项目键为"LISTEN" 