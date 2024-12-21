class AnalysisResult {
  final String type;
  final double confidence;
  final Map<String, dynamic> data;
  final DateTime timestamp;

  AnalysisResult({
    required this.type,
    required this.confidence,
    required this.data,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  Map<String, dynamic> toMap() => {
    'type': type,
    'confidence': confidence,
    'data': data,
    'timestamp': timestamp.toIso8601String(),
  };

  factory AnalysisResult.fromMap(Map<String, dynamic> map) => AnalysisResult(
    type: map['type'],
    confidence: map['confidence'],
    data: Map<String, dynamic>.from(map['data']),
    timestamp: DateTime.parse(map['timestamp']),
  );
} 