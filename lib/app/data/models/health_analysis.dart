class HealthReport {
  final String id;
  final DateTime generatedAt;
  final List<HealthMetric> metrics;
  final List<String> suggestions;
  final Map<String, dynamic> rawData;

  HealthReport({
    required this.id,
    required this.generatedAt,
    required this.metrics,
    required this.suggestions,
    required this.rawData,
  });

  factory HealthReport.fromJson(Map<String, dynamic> json) {
    return HealthReport(
      id: json['id'],
      generatedAt: DateTime.parse(json['generatedAt']),
      metrics: (json['metrics'] as List)
          .map((m) => HealthMetric.fromJson(m))
          .toList(),
      suggestions: List<String>.from(json['suggestions']),
      rawData: json['rawData'],
    );
  }
}

class HealthMetric {
  final String name;
  final double value;
  final String unit;
  final String status;
  final String? comment;

  HealthMetric({
    required this.name,
    required this.value,
    required this.unit,
    required this.status,
    this.comment,
  });

  factory HealthMetric.fromJson(Map<String, dynamic> json) {
    return HealthMetric(
      name: json['name'],
      value: json['value'].toDouble(),
      unit: json['unit'],
      status: json['status'],
      comment: json['comment'],
    );
  }
} 