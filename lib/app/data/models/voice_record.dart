class VoiceRecord {
  final String content;
  final DateTime timestamp;
  final String type;
  
  VoiceRecord({
    required this.content,
    required this.timestamp,
    required this.type,
  });
  
  Map<String, dynamic> toJson() {
    return {
      'content': content,
      'timestamp': timestamp.toIso8601String(),
      'type': type,
    };
  }
  
  factory VoiceRecord.fromJson(Map<String, dynamic> json) {
    return VoiceRecord(
      content: json['content'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      type: json['type'] as String,
    );
  }
} 