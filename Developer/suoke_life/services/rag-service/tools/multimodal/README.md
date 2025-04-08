# 索克生活RAG服务多模态搜索测试工具

本工具用于测试索克生活RAG服务的多模态搜索功能，包括文本、图像和音频模态的组合查询，以及舌诊和音频分析功能。

## 功能特点

- 健康检查测试
- 基本搜索测试
- 舌诊分析测试（图像分析）
- 音频分析测试（声音分析）
- 多模态组合搜索测试
- 支持自定义查询、服务器URL和输出格式
- 详细的测试报告和JSON输出

## 使用方法

### Go版本工具

#### 编译

```bash
cd /path/to/tools/multimodal
go build
```

#### 运行

```bash
# 基本使用
./multimodal

# 显示详细输出
./multimodal -verbose

# 指定服务器URL
./multimodal -server http://example.com:8080

# 指定图像和音频文件
./multimodal -image /path/to/image.jpg -audio /path/to/audio.mp3

# 自定义查询
./multimodal -query "中医针灸疗法分析"

# 完整选项
./multimodal -server http://localhost:8080 \
  -image assets/tongue_sample.jpg \
  -audio assets/audio_sample.mp3 \
  -query "中医舌诊健康分析" \
  -domain "TCM" \
  -max-results 10 \
  -output-dir ./results \
  -verbose
```

### Bash脚本版本

我们也提供了Bash脚本版本的测试工具，支持类似功能：

```bash
# 基本使用
./test-multimodal.sh

# 显示详细输出
./test-multimodal.sh --verbose

# 指定服务器URL
./test-multimodal.sh --server http://example.com:8080

# 指定图像和音频文件
./test-multimodal.sh --image /path/to/image.jpg --audio /path/to/audio.mp3

# 自定义查询
./test-multimodal.sh --query "中医针灸疗法分析"
```

## 命令行选项

### Go版本

```
Usage of ./multimodal:
  -audio string
        音频文件路径 (默认 "assets/audio_sample.mp3")
  -audio-type string
        音频MIME类型 (默认 "audio/mpeg")
  -domain string
        查询领域 (默认 "TCM")
  -image string
        图像文件路径 (默认 "assets/tongue_sample.jpg")
  -image-type string
        图像MIME类型 (默认 "image/jpeg")
  -max-results int
        最大结果数量 (默认 5)
  -output string
        输出JSON文件路径
  -output-dir string
        输出目录 (默认 "output")
  -query string
        查询文本 (默认 "中医舌诊健康分析")
  -server string
        服务器基础URL (默认 "http://localhost:8080")
  -single-tests
        运行单独的测试 (默认 true)
  -use-cache
        使用缓存 (默认 true)
  -verbose
        详细输出
```

### Bash脚本版本

```
用法: ./test-multimodal.sh [选项]

选项:
  -s, --server URL      设置服务器URL (默认: http://localhost:8080)
  -i, --image PATH      设置测试图像路径 (默认: tests/assets/tongue_sample.jpg)
  -a, --audio PATH      设置测试音频路径 (默认: tests/assets/audio_sample.mp3)
  -q, --query TEXT      设置查询文本 (默认: 中医舌诊健康分析)
  -o, --output DIR      设置输出目录 (默认: tests/output)
  -v, --verbose         显示详细输出
  -h, --help            显示帮助信息
```

## 测试资源

在`assets`目录下提供了默认的测试资源：

- `tongue_sample.jpg`: 舌诊测试图像
- `audio_sample.mp3`: 音频测试文件

## 输出文件

测试结果保存在`output`目录下（或通过`-output-dir`指定的目录）：

- `health_check_result.json`: 健康检查结果
- `basic_search_result.json`: 基本搜索结果
- `tongue_analysis_result.json`: 舌诊分析结果
- `audio_analysis_result.json`: 音频分析结果
- `multimodal_search_result.json`: 多模态搜索结果

## 服务端点

工具测试以下服务端点：

- `GET /health`: 健康检查
- `GET /api/search`: 基本搜索
- `POST /api/analyze/tongue`: 舌诊分析
- `POST /api/analyze/audio`: 音频分析
- `POST /api/search/multimodal`: 多模态搜索

## 使用示例

### 本地测试

```bash
# 启动本地服务
cd /path/to/services/rag-service
./scripts/run-local-minimal.sh start

# 运行测试
cd tools/multimodal
./multimodal -verbose
```

### 远程测试

```bash
# 测试开发环境
./multimodal -server http://dev.suoke.life:8080 -verbose

# 测试生产环境
./multimodal -server https://api.suoke.life -verbose
``` 