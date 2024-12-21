class LoginRecord {
  final String id;
  final String userId;
  final DateTime timestamp;
  final String deviceInfo;
  final String ipAddress;
  final String loginType; // 'password', 'biometric', 'wechat', 'google', 'apple'
  final bool success;
  final String? errorMessage;
  final Map<String, dynamic>? metadata;

  const LoginRecord({
    required this.id,
    required this.userId,
    required this.timestamp,
    required this.deviceInfo,
    required this.ipAddress,
    required this.loginType,
    required this.success,
    this.errorMessage,
    this.metadata,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'user_id': userId,
    'timestamp': timestamp.toIso8601String(),
    'device_info': deviceInfo,
    'ip_address': ipAddress,
    'login_type': loginType,
    'success': success,
    'error_message': errorMessage,
    'metadata': metadata,
  };

  factory LoginRecord.fromJson(Map<String, dynamic> json) => LoginRecord(
    id: json['id'],
    userId: json['user_id'],
    timestamp: DateTime.parse(json['timestamp']),
    deviceInfo: json['device_info'],
    ipAddress: json['ip_address'],
    loginType: json['login_type'],
    success: json['success'],
    errorMessage: json['error_message'],
    metadata: json['metadata'],
  );
} 