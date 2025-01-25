class HealthData {
  final String userId;
  final double height;
  final double weight;
  final String bloodPressure;
  final int heartRate;
  final int steps;
  final DateTime updatedAt;

  const HealthData({
    required this.userId,
    required this.height,
    required this.weight,
    required this.bloodPressure,
    required this.heartRate,
    required this.steps,
    required this.updatedAt,
  });

  factory HealthData.fromJson(Map<String, dynamic> json) => HealthData(
        userId: json['user_id'] as String,
        height: json['height'] as double,
        weight: json['weight'] as double,
        bloodPressure: json['blood_pressure'] as String,
        heartRate: json['heart_rate'] as int,
        steps: json['steps'] as int,
        updatedAt: DateTime.fromMillisecondsSinceEpoch(json['updated_at'] as int),
      );

  Map<String, dynamic> toJson() => {
        'user_id': userId,
        'height': height,
        'weight': weight,
        'blood_pressure': bloodPressure,
        'heart_rate': heartRate,
        'steps': steps,
        'updated_at': updatedAt.millisecondsSinceEpoch,
      };
} 