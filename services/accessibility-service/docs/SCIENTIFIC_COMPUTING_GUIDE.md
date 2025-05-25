# 索克生活无障碍服务 - 科学计算库使用指南

## 📚 概述

索克生活无障碍服务集成了全面的科学计算库支持，为AI智能体提供强大的数据分析、机器学习、信号处理和可视化能力。本指南将帮助您了解如何使用这些功能。

## 🚀 快速开始

### 1. 安装科学计算库

```bash
# 自动安装所有库
python scripts/install_scientific_libraries.py

# 只安装核心库
python scripts/install_scientific_libraries.py --core-only

# 跳过系统依赖安装
python scripts/install_scientific_libraries.py --no-system-deps
```

### 2. 基本使用

```python
from internal.service.scientific_computing import get_scientific_computing_service

# 获取服务实例
service = get_scientific_computing_service()

# 检查服务状态
status = service.get_service_status()
print(f"可用库数量: {status['library_count']}")
print(f"覆盖率: {status['coverage_percentage']:.1f}%")
```

## 📊 核心功能

### 1. 数据分析

#### 传感器数据分析
```python
# 分析传感器数据
sensor_data = [1.2, 1.5, 1.1, 1.8, 1.3, 1.6, 1.4]
result = service.process_data(sensor_data, 'analyze')

print(f"平均值: {result['statistics']['mean']}")
print(f"标准差: {result['statistics']['std']}")
print(f"最小值: {result['statistics']['min']}")
print(f"最大值: {result['statistics']['max']}")
```

#### 异常检测
```python
# 检测数据中的异常值
anomaly_result = service.process_data(
    sensor_data, 
    'detect_anomalies', 
    threshold=2.0
)

print(f"异常点数量: {anomaly_result['results']['anomaly_count']}")
print(f"异常比例: {anomaly_result['results']['anomaly_percentage']:.1f}%")
```

### 2. 信号处理

#### 信号滤波
```python
# 低通滤波
filtered_result = service.process_data(
    noisy_signal, 
    'filter', 
    filter_type='lowpass', 
    cutoff=0.1
)

# 高通滤波
high_pass_result = service.process_data(
    signal_data, 
    'filter', 
    filter_type='highpass', 
    cutoff=0.05
)

# 带通滤波
band_pass_result = service.process_data(
    signal_data, 
    'filter', 
    filter_type='bandpass', 
    cutoff=0.1
)
```

#### 频谱分析
```python
# 分析信号频谱
spectrum_result = service.process_data(
    audio_signal, 
    'spectrum', 
    sample_rate=44100
)

print(f"主要频率: {spectrum_result['spectrum_analysis']['dominant_frequency']} Hz")
```

### 3. 机器学习

#### 数据聚类
```python
# K-means聚类
cluster_result = service.process_data(
    feature_data, 
    'cluster', 
    n_clusters=3
)

print(f"聚类标签: {cluster_result['labels']}")
print(f"聚类中心: {cluster_result['centroids']}")
```

#### 分类器训练（需要sklearn）
```python
from internal.service.scientific_computing import ScientificComputingService
import numpy as np

service = ScientificComputingService()
ml_engine = service.machine_learning

# 准备训练数据
X = np.random.randn(100, 4)  # 特征
y = np.random.randint(0, 3, 100)  # 标签

# 训练随机森林分类器
result = ml_engine.train_classifier(X, y, model_type='random_forest')
print(f"模型准确率: {result['accuracy']:.3f}")
```

### 4. 数据可视化

#### 创建绘图数据
```python
# 线图数据
line_plot = service.process_data(
    time_series_data, 
    'plot', 
    plot_type='line'
)

# 直方图数据
histogram = service.process_data(
    distribution_data, 
    'plot', 
    plot_type='histogram'
)

# 散点图数据
scatter_plot = service.process_data(
    xy_data, 
    'plot', 
    plot_type='scatter'
)
```

## 🔧 高级功能

### 1. 直接使用引擎

```python
from internal.service.scientific_computing import (
    ScientificComputingManager,
    DataAnalysisEngine,
    SignalProcessingEngine,
    MachineLearningEngine,
    VisualizationEngine
)

# 创建管理器
manager = ScientificComputingManager()

# 使用数据分析引擎
data_engine = DataAnalysisEngine(manager)
analysis_result = data_engine.analyze_sensor_data(np.array(sensor_data))

# 使用信号处理引擎
signal_engine = SignalProcessingEngine(manager)
filter_result = signal_engine.filter_signal(signal_array, 'lowpass', 0.1)
```

### 2. 检查库可用性

```python
# 检查特定库是否可用
if manager.is_library_available('scipy'):
    print("SciPy可用，可以使用高级信号处理功能")

if manager.is_library_available('sklearn'):
    print("Scikit-learn可用，可以使用机器学习功能")

# 获取所有可用库
available_libs = manager.get_available_libraries()
for lib_name, is_available in available_libs.items():
    status = "✅" if is_available else "❌"
    print(f"{status} {lib_name}")
```

## 📦 支持的库

### 核心科学计算库
- **NumPy**: 基础数值计算
- **SciPy**: 科学计算和统计
- **Pandas**: 数据处理和分析
- **Matplotlib**: 数据可视化
- **Seaborn**: 统计可视化
- **Plotly**: 交互式可视化

### 机器学习库
- **Scikit-learn**: 机器学习算法
- **XGBoost**: 梯度提升算法
- **LightGBM**: 轻量级梯度提升
- **TensorFlow**: 深度学习框架
- **PyTorch**: 深度学习框架

### 计算机视觉库
- **OpenCV**: 计算机视觉
- **Pillow**: 图像处理
- **Scikit-image**: 图像处理算法
- **MediaPipe**: 手势识别和姿态估计

### 音频处理库
- **Librosa**: 音频分析
- **PyAudio**: 音频处理
- **SoundDevice**: 音频设备接口
- **Pydub**: 音频文件处理

### 信号处理库
- **FilterPy**: 卡尔曼滤波器
- **PyWavelets**: 小波变换
- **AHRS**: 姿态和航向参考系统

### 地理信息库
- **Geopy**: 地理编码和距离计算
- **Shapely**: 几何对象处理
- **Folium**: 地图可视化
- **GeoPandas**: 地理数据处理

## 🎯 实际应用场景

### 1. 盲人辅助服务

```python
# 分析摄像头图像数据
image_features = extract_image_features(camera_image)
obstacle_analysis = service.process_data(image_features, 'analyze')

# 检测异常障碍物
obstacles = service.process_data(
    depth_data, 
    'detect_anomalies', 
    threshold=1.5
)

# 路径规划数据处理
path_data = calculate_safe_path(obstacles['results'])
```

### 2. 语音辅助服务

```python
# 音频信号预处理
filtered_audio = service.process_data(
    raw_audio, 
    'filter', 
    filter_type='bandpass', 
    cutoff=0.1
)

# 语音特征提取
audio_features = extract_mfcc_features(filtered_audio['filtered_signal'])

# 语音识别准确率分析
recognition_stats = service.process_data(audio_features, 'analyze')
```

### 3. 手语识别服务

```python
# 手势轨迹数据分析
gesture_trajectory = capture_hand_trajectory()
trajectory_analysis = service.process_data(gesture_trajectory, 'analyze')

# 手势分类
gesture_features = extract_gesture_features(trajectory_analysis)
gesture_classification = service.process_data(
    gesture_features, 
    'cluster', 
    n_clusters=10
)
```

### 4. 屏幕阅读服务

```python
# 文本布局分析
text_positions = extract_text_positions(screen_image)
layout_analysis = service.process_data(text_positions, 'analyze')

# 阅读顺序优化
reading_order = optimize_reading_sequence(layout_analysis)
```

## ⚡ 性能优化

### 1. 使用NumPy数组
```python
# 推荐：使用NumPy数组
import numpy as np
data = np.array(sensor_readings)
result = service.process_data(data.tolist(), 'analyze')

# 避免：使用Python列表进行大量计算
```

### 2. 批量处理
```python
# 批量处理多个传感器数据
sensor_results = {}
for sensor_name, sensor_data in all_sensors.items():
    sensor_results[sensor_name] = service.process_data(sensor_data, 'analyze')
```

### 3. 缓存结果
```python
# 缓存频繁使用的分析结果
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_analysis(data_hash):
    return service.process_data(data, 'analyze')
```

## 🐛 故障排除

### 1. 库安装问题

```bash
# 更新pip
python -m pip install --upgrade pip

# 清理缓存
pip cache purge

# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ numpy scipy pandas
```

### 2. 内存问题

```python
# 处理大数据时分块处理
def process_large_dataset(large_data, chunk_size=1000):
    results = []
    for i in range(0, len(large_data), chunk_size):
        chunk = large_data[i:i+chunk_size]
        result = service.process_data(chunk, 'analyze')
        results.append(result)
    return results
```

### 3. 性能问题

```python
# 使用性能分析
import time

start_time = time.time()
result = service.process_data(data, 'analyze')
processing_time = time.time() - start_time

print(f"处理时间: {processing_time:.3f}秒")
```

## 📈 最佳实践

### 1. 错误处理
```python
try:
    result = service.process_data(data, 'analyze')
    if result['status'] == 'success':
        # 处理成功结果
        process_analysis_result(result['statistics'])
    else:
        # 处理错误
        logger.error(f"分析失败: {result['error']}")
except Exception as e:
    logger.error(f"处理异常: {e}")
```

### 2. 数据验证
```python
def validate_sensor_data(data):
    """验证传感器数据"""
    if not data:
        raise ValueError("数据不能为空")
    
    if len(data) < 10:
        logger.warning("数据点太少，分析结果可能不准确")
    
    # 检查数据范围
    if any(abs(x) > 1000 for x in data):
        logger.warning("检测到异常大的数值")
    
    return True

# 使用验证
if validate_sensor_data(sensor_data):
    result = service.process_data(sensor_data, 'analyze')
```

### 3. 配置管理
```python
# 配置科学计算参数
ANALYSIS_CONFIG = {
    'anomaly_threshold': 2.5,
    'filter_cutoff': 0.1,
    'cluster_count': 3,
    'sample_rate': 44100
}

# 使用配置
result = service.process_data(
    data, 
    'detect_anomalies', 
    threshold=ANALYSIS_CONFIG['anomaly_threshold']
)
```

## 🔮 未来扩展

### 1. 自定义算法
```python
# 扩展数据分析引擎
class CustomDataAnalysisEngine(DataAnalysisEngine):
    def custom_analysis(self, data):
        """自定义分析算法"""
        # 实现自定义逻辑
        pass
```

### 2. 新库集成
```python
# 添加新的科学计算库支持
def add_new_library_support():
    """添加新库支持的模板"""
    try:
        import new_library
        # 集成新库功能
        return True
    except ImportError:
        return False
```

## 📞 支持与反馈

如果您在使用科学计算功能时遇到问题，请：

1. 查看安装报告：`scientific_libraries_installation_report.md`
2. 检查日志文件中的错误信息
3. 运行测试验证功能：`python test/test_scientific_computing_enhanced.py`
4. 提交问题报告，包含详细的错误信息和环境配置

---

**版本**: 1.0.0  
**更新时间**: 2024年5月24日  
**维护团队**: 索克生活开发团队 