enum HealthMetricType {
  steps, // 步数
  heartRate, // 心率
  bloodPressure, // 血压
  bloodOxygen, // 血氧
  sleep, // 睡眠
  weight, // 体重
  temperature, // 体温
  mood, // 心情
  water, // 饮水量
  nutrition, // 营养摄入
}

class HealthMetric {
  final HealthMetricType type;
  final double value;
  final String unit;
  final DateTime timestamp;
  final Map<String, dynamic>? metadata;

  const HealthMetric({
    required this.type,
    required this.value,
    required this.unit,
    required this.timestamp,
    this.metadata,
  });

  factory HealthMetric.fromJson(Map<String, dynamic> json) {
    return HealthMetric(
      type: HealthMetricType.values.firstWhere(
        (e) => e.toString() == 'HealthMetricType.${json['type']}',
      ),
      value: json['value'].toDouble(),
      unit: json['unit'],
      timestamp: DateTime.parse(json['timestamp']),
      metadata: json['metadata'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'type': type.toString().split('.').last,
      'value': value,
      'unit': unit,
      'timestamp': timestamp.toIso8601String(),
      'metadata': metadata,
    };
  }
}

class HealthData {
  final String userId;
  final List<HealthMetric> metrics;
  final DateTime lastSync;
  final Map<String, dynamic>? deviceInfo;

  const HealthData({
    required this.userId,
    required this.metrics,
    required this.lastSync,
    this.deviceInfo,
  });

  factory HealthData.fromJson(Map<String, dynamic> json) {
    return HealthData(
      userId: json['userId'],
      metrics: (json['metrics'] as List)
          .map((metric) => HealthMetric.fromJson(metric))
          .toList(),
      lastSync: DateTime.parse(json['lastSync']),
      deviceInfo: json['deviceInfo'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'userId': userId,
      'metrics': metrics.map((metric) => metric.toJson()).toList(),
      'lastSync': lastSync.toIso8601String(),
      'deviceInfo': deviceInfo,
    };
  }
}
