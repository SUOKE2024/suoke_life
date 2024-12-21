class AnalysisConfig {
  final int maxSampleSize;
  final Duration timeWindow;
  final List<String> metrics;

  const AnalysisConfig({
    required this.maxSampleSize,
    required this.timeWindow,
    required this.metrics,
  });
}

class AnalysisResult {
  final String type;
  final DateTime timestamp;
  final Map<String, dynamic> data;
  final Map<String, dynamic>? metadata;

  const AnalysisResult({
    required this.type,
    required this.timestamp,
    required this.data,
    this.metadata,
  });

  Map<String, dynamic> toMap() => {
    'type': type,
    'timestamp': timestamp.toIso8601String(),
    'data': data,
    'metadata': metadata,
  };

  factory AnalysisResult.fromMap(Map<String, dynamic> map) => AnalysisResult(
    type: map['type'],
    timestamp: DateTime.parse(map['timestamp']),
    data: Map<String, dynamic>.from(map['data']),
    metadata: map['metadata'] != null ? 
      Map<String, dynamic>.from(map['metadata']) : null,
  );
} 