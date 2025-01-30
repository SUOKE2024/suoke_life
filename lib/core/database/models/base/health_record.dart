class HealthRecord {
  final String id;
  final String userId;
  final double height;
  final double weight;
  final String bloodPressure;
  final int heartRate;
  final DateTime recordedAt;

  HealthRecord({
    required this.id,
    required this.userId,
    required this.height,
    required this.weight,
    required this.bloodPressure,
    required this.heartRate,
    required this.recordedAt,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'user_id': userId,
      'height': height,
      'weight': weight,
      'blood_pressure': bloodPressure,
      'heart_rate': heartRate,
      'recorded_at': recordedAt.toIso8601String(),
    };
  }

  factory HealthRecord.fromMap(Map<String, dynamic> map) {
    return HealthRecord(
      id: map['id'],
      userId: map['user_id'],
      height: map['height'],
      weight: map['weight'],
      bloodPressure: map['blood_pressure'],
      heartRate: map['heart_rate'],
      recordedAt: DateTime.parse(map['recorded_at']),
    );
  }
} 