class PerformanceMetric {
  final String modelId;
  final DateTime timestamp;
  final double responseTime;
  final double errorRate;
  final double? throughput;
  final Map<String, dynamic>? customMetrics;

  const PerformanceMetric({
    required this.modelId,
    required this.timestamp,
    required this.responseTime,
    required this.errorRate,
    this.throughput,
    this.customMetrics,
  });

  Map<String, dynamic> toMap() => {
    'model_id': modelId,
    'timestamp': timestamp.toIso8601String(),
    'response_time': responseTime,
    'error_rate': errorRate,
    'throughput': throughput,
    'custom_metrics': customMetrics,
  };

  factory PerformanceMetric.fromMap(Map<String, dynamic> map) => PerformanceMetric(
    modelId: map['model_id'],
    timestamp: DateTime.parse(map['timestamp']),
    responseTime: map['response_time'],
    errorRate: map['error_rate'],
    throughput: map['throughput'],
    customMetrics: map['custom_metrics'],
  );
} 