class AnalyticsEvent {
  final String name;
  final Map<String, dynamic>? parameters;
  final DateTime timestamp;
  final Map<String, dynamic> deviceInfo;

  AnalyticsEvent({
    required this.name,
    this.parameters,
    required this.timestamp,
    required this.deviceInfo,
  });

  Map<String, dynamic> toJson() => {
    'name': name,
    'parameters': parameters,
    'timestamp': timestamp.toIso8601String(),
    'device_info': deviceInfo,
  };
} 