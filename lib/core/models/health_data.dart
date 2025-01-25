class HealthData {
  final int? id;
  final String? userId;
  final String? heartRate;
  final String? sleepPatterns;
  final String? medicalRecords;

  HealthData({
    this.id,
    this.userId,
    this.heartRate,
    this.sleepPatterns,
    this.medicalRecords,
  });

  HealthData copyWith({
    int? id,
    String? userId,
    String? heartRate,
    String? sleepPatterns,
    String? medicalRecords,
  }) {
    return HealthData(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      heartRate: heartRate ?? this.heartRate,
      sleepPatterns: sleepPatterns ?? this.sleepPatterns,
      medicalRecords: medicalRecords ?? this.medicalRecords,
    );
  }

  factory HealthData.fromJson(Map<String, dynamic> json) {
    return HealthData(
      id: json['id'],
      userId: json['user_id'],
      heartRate: json['heart_rate'],
      sleepPatterns: json['sleep_patterns'],
      medicalRecords: json['medical_records'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'heart_rate': heartRate,
      'sleep_patterns': sleepPatterns,
      'medical_records': medicalRecords,
    };
  }
} 