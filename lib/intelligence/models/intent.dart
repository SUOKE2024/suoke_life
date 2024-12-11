class Intent {
  final String type;
  final Map<String, dynamic> parameters;
  final double confidence;
  
  Intent({
    required this.type,
    this.parameters = const {},
    this.confidence = 1.0,
  });
  
  static const String GENERAL_CHAT = 'general_chat';
  static const String TASK_EXECUTION = 'task_execution';
  static const String INFORMATION_QUERY = 'information_query';
  static const String SYSTEM_CONTROL = 'system_control';
  static const String UNKNOWN = 'unknown';
  
  Map<String, dynamic> toJson() {
    return {
      'type': type,
      'parameters': parameters,
      'confidence': confidence,
    };
  }
  
  factory Intent.fromJson(Map<String, dynamic> json) {
    return Intent(
      type: json['type'] as String,
      parameters: json['parameters'] as Map<String, dynamic>,
      confidence: json['confidence'] as double,
    );
  }
  
  @override
  String toString() {
    return 'Intent{type: $type, parameters: $parameters, confidence: $confidence}';
  }
} 